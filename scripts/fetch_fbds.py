"""Crawl the FBDS hydrography repository and summarise it per municipality.

FBDS (Fundação Brasileira para o Desenvolvimento Sustentável) publishes high-resolution
hydrography for every Brazilian municipality at https://geo.fbds.org.br/, one folder per
municipality: /UF/MUNICIPIO/HIDROGRAFIA/UF_<ibge_code>_<LAYER>.shp (+ .dbf .shx .prj).
Credit: "Hidrografia: Fundação Brasileira para o Desenvolvimento Sustentável (FBDS), geo.fbds.org.br".

For each municipality the script downloads only the HIDROGRAFIA shapefiles, computes totals and
appends one row to raw/enrichment/fbds_hidrografia.csv (committed, small). The shapefiles go to
.cache/fbds/ (git-ignored) and are deleted after processing unless --keep is given.

Usage:
    python -m pip install --user pyshp pyproj truststore
    python scripts/fetch_fbds.py --uf BA            # one state first, to try it
    python scripts/fetch_fbds.py                    # every state; resumable, skips finished municipalities
    python scripts/fetch_fbds.py --uf BA --keep     # keep the shapefiles in .cache/fbds/
    python scripts/fetch_fbds.py --workers 2        # municipalities in parallel (default 3)

Then run scripts/build.py: the totals become columns of municipios.csv.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import re
import shutil
import sys
import threading
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import shapefile  # pyshp
from pyproj import CRS, Geod, Transformer

try:
    import truststore

    truststore.inject_into_ssl()
except ImportError:
    pass

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://geo.fbds.org.br"
CACHE = ROOT / ".cache" / "fbds"
OUT = ROOT / "raw" / "enrichment" / "fbds_hidrografia.csv"
AGENT = "municipios-e-estados-do-brasil (+https://github.com/CaiqueDourado/municipios-e-estados-do-brasil)"
UFS = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE",
       "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"]
LAYERS = ("NASCENTES", "RIOS_SIMPLES", "RIOS_DUPLOS", "MASSAS_DAGUA")
PARTS = (".shp", ".shx", ".dbf", ".prj")
FIELDS = ["ibge_code", "uf", "folder", "springs", "rivers_km", "double_rivers_ha", "water_bodies",
          "water_bodies_ha", "artificial_water_bodies", "layers", "source_updated"]
GEOD = Geod(ellps="GRS80")  # SIRGAS 2000 / WGS 84 share this ellipsoid to the millimetre
LOCK = threading.Lock()
DELAY = 0.5  # seconds between requests; be gentle with a non-profit server


def fetch(url: str, retries: int = 4) -> bytes:
    attempt = 0
    while attempt < retries:
        attempt += 1
        try:
            request = urllib.request.Request(url, headers={"User-Agent": AGENT, "Accept-Encoding": "gzip"})
            with urllib.request.urlopen(request, timeout=120) as response:
                body = response.read()
            time.sleep(DELAY)
            return gzip.decompress(body) if body[:2] == b"\x1f\x8b" else body
        except urllib.error.HTTPError as error:
            if error.code == 404:
                raise
            if error.code in (429, 503):  # rate limited or busy: wait and try again without counting
                wait = int(error.headers.get("Retry-After") or 0) or 60
                print(f"  {url}: HTTP {error.code}, waiting {wait}s...", file=sys.stderr)
                time.sleep(wait)
                attempt -= 1
                continue
            print(f"  {url}: {error} (attempt {attempt})", file=sys.stderr)
        except (urllib.error.URLError, TimeoutError) as error:
            print(f"  {url}: {error} (attempt {attempt})", file=sys.stderr)
        time.sleep(5 * attempt)
    raise SystemExit(f"giving up on {url}")


def listing(path: str) -> list[tuple[str, str]]:
    """Links of an h5ai folder page as (href, last-modified) pairs."""
    page = fetch(BASE + urllib.parse.quote(path)).decode("utf-8", "replace")
    out = []
    for row in re.split(r"<tr[ >]", page)[1:]:  # one table row per entry
        href = re.search(r'href="(/[^"]+)"', row)
        modified = re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", row)
        if href and modified:
            link = urllib.parse.unquote(href.group(1))
            if link.startswith(path) and link != path:
                out.append((link, modified.group(0)))
    return out


def to_lonlat(prj_text: str):
    crs = CRS.from_wkt(prj_text) if prj_text.strip() else CRS.from_epsg(4674)
    if crs.is_geographic:
        return None
    transformer = Transformer.from_crs(crs, "EPSG:4674", always_xy=True)
    return lambda points: [transformer.transform(x, y) for x, y in points]


def parts_of(shape) -> list[list[tuple[float, float]]]:
    bounds = list(shape.parts) + [len(shape.points)]
    return [shape.points[bounds[i]:bounds[i + 1]] for i in range(len(shape.parts))]


def ascii_key(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Z0-9]", "", text.upper())


_NAMES: dict[str, str] | None = None


def known_codes() -> dict[str, str]:
    """IBGE code -> ASCII name key, from data/municipios.csv (when the build has run)."""
    global _NAMES
    with LOCK:  # several worker threads may ask at once: load the table only once, completely
        if _NAMES is None:
            names = {}
            path = ROOT / "data" / "municipios.csv"
            if path.exists():
                with path.open(encoding="utf-8", newline="") as handle:
                    names = {r["ibge_code"]: ascii_key(r["name"]) for r in csv.DictReader(handle)}
            _NAMES = names
    return _NAMES


def pick_code(uf: str, folder: str, codes: list[str]) -> str | None:
    """Some FBDS folders also hold files with a second code (a neighbour or an old code).
    Keep the code whose municipality name matches the folder; otherwise the only code found."""
    if len(codes) == 1:
        return codes[0]
    names = known_codes()
    matching = [c for c in codes if names.get(c) == ascii_key(folder)]
    return matching[0] if len(matching) == 1 else None


def summarise(folder: Path, prefix: str) -> dict:
    totals = {"springs": 0, "rivers_km": 0.0, "double_rivers_ha": 0.0, "water_bodies": 0,
              "water_bodies_ha": 0.0, "artificial_water_bodies": 0}
    found = []
    for layer in LAYERS:
        shp = folder / f"{prefix}_{layer}.shp"
        if not shp.exists():
            continue
        found.append(layer)
        prj = shp.with_suffix(".prj")
        convert = to_lonlat(prj.read_text(encoding="latin-1") if prj.exists() else "")
        reader = shapefile.Reader(str(shp), encoding="latin-1")
        names = [f[0].upper() for f in reader.fields[1:]]
        for record in reader.iterShapeRecords():
            geometry = record.shape
            if not geometry.points:
                continue
            pieces = [convert(p) if convert else p for p in parts_of(geometry)]
            if layer == "NASCENTES":
                totals["springs"] += len(geometry.points)
            elif layer == "RIOS_SIMPLES":
                for piece in pieces:
                    lons, lats = zip(*piece)
                    totals["rivers_km"] += GEOD.line_length(lons, lats) / 1000
            else:
                area = 0.0
                for piece in pieces:  # ESRI rule: outer rings clockwise (positive here), holes counter-clockwise
                    lons, lats = zip(*piece)
                    area += -GEOD.polygon_area_perimeter(lons, lats)[0]
                area = abs(area)  # some FBDS files store the rings the other way round; the size is the same
                if layer == "RIOS_DUPLOS":
                    totals["double_rivers_ha"] += area / 10_000
                else:
                    totals["water_bodies"] += 1
                    totals["water_bodies_ha"] += area / 10_000
                    attributes = dict(zip(names, record.record))
                    if str(attributes.get("NATUREZA", "")).lower().startswith("artificial"):
                        totals["artificial_water_bodies"] += 1
    totals = {k: round(v, 2) if isinstance(v, float) else v for k, v in totals.items()}
    return {**totals, "layers": "|".join(found)}


def done() -> set[str]:
    if not OUT.exists():
        return set()
    with OUT.open(encoding="utf-8", newline="") as handle:
        return {f"{r['uf']}/{r['folder']}" for r in csv.DictReader(handle)}



def append(row: dict) -> None:
    with LOCK:
        _append(row)


def _append(row: dict) -> None:
    new = not OUT.exists()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        if new:
            writer.writeheader()
        writer.writerow(row)


def municipality(uf: str, folder: str, keep: bool) -> dict | None:
    path = f"/{uf}/{folder}/HIDROGRAFIA/"
    try:
        files = listing(path)
    except urllib.error.HTTPError:
        print(f"  {uf}/{folder}: no HIDROGRAFIA folder")
        return None
    wanted = [(href, modified) for href, modified in files if href.endswith(PARTS)]
    codes = sorted({m.group(1) for href, _ in wanted if (m := re.search(r"_(\d{7})_", href))})
    code = pick_code(uf, folder, codes)
    if code is None:
        print(f"  {uf}/{folder}: could not read the IBGE code (found {codes or 'none'})")
        return None
    wanted = [(href, modified) for href, modified in wanted if f"_{code}_" in href]
    local = CACHE / uf / folder
    local.mkdir(parents=True, exist_ok=True)
    for href, _ in wanted:
        target = local / Path(href).name
        if not target.exists():
            target.write_bytes(fetch(BASE + urllib.parse.quote(href)))
    row = {"ibge_code": code, "uf": uf, "folder": folder, **summarise(local, f"{uf}_{code}"),
           "source_updated": max(modified for _, modified in wanted)[:10]}
    if not keep:
        shutil.rmtree(local, ignore_errors=True)
    return row


def redo_negative() -> None:
    """Remove rows whose areas came out negative (computed before the abs() fix) so they are crawled again."""
    if not OUT.exists():
        return
    with OUT.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    bad = [r for r in rows if any(float(r[k] or 0) < 0 for k in ("double_rivers_ha", "water_bodies_ha"))]
    keep = [r for r in rows if r not in bad]
    with OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(keep)
    print(f"{len(bad)} municipalities with negative areas removed, they will be crawled again: "
          f"{', '.join(r['uf'] + '/' + r['folder'] for r in bad[:20])}{' ...' if len(bad) > 20 else ''}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--uf", nargs="*", default=UFS, help="states to crawl (default: all)")
    parser.add_argument("--keep", action="store_true", help="keep the downloaded shapefiles in .cache/fbds/")
    parser.add_argument("--limit", type=int, default=0, help="stop after N municipalities (for a quick test)")
    parser.add_argument("--workers", type=int, default=3, help="municipalities crawled in parallel (default 3; keep it small)")
    parser.add_argument("--redo-negative", action="store_true",
                        help="drop the rows with a negative area (rings stored the other way round) and crawl them again")
    args = parser.parse_args()

    if args.redo_negative:
        redo_negative()
    finished = done()
    todo = []
    for uf in [u.upper() for u in args.uf]:
        folders = [href.rstrip("/").rsplit("/", 1)[-1] for href, _ in listing(f"/{uf}/") if href.endswith("/")]
        print(f"== {uf}: {len(folders)} municipalities, {sum(f'{uf}/{f}' in finished for f in folders)} already done")
        todo += [(uf, f) for f in folders if f"{uf}/{f}" not in finished]
    if args.limit:
        todo = todo[:args.limit]
    print(f"{len(todo)} municipalities to crawl with {args.workers} worker(s)")

    def work(item: tuple[str, str]) -> None:
        uf, folder = item
        try:
            row = municipality(uf, folder, args.keep)
        except SystemExit as error:  # one municipality failing must not stop the others
            print(f"  {uf}/{folder}: {error}", file=sys.stderr)
            return
        if row:
            append(row)
            print(f"  {uf}/{folder} ({row['ibge_code']}): {row['springs']} springs, {row['rivers_km']} km of rivers, "
                  f"{row['water_bodies']} water bodies", flush=True)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(work, todo))


if __name__ == "__main__":
    main()
