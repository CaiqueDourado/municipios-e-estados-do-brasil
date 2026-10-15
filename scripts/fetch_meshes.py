"""Download state (and optionally municipal) boundaries from the IBGE API v3.

Usage:
    python scripts/fetch_meshes.py                 # data/estados.geojson (27 polygons, small)
    python scripts/fetch_meshes.py --municipios    # also data/municipios-malhas.geojson (large)
    python scripts/fetch_meshes.py --qualidade intermediaria

Each polygon is joined to data/estados.csv / data/municipios.csv, so the GeoJSON carries the
same keys and names as the tables. GitHub renders the resulting files as interactive maps.
Run scripts/build.py first. Needs pandas; on Windows also `pip install truststore` (see below).
"""

from __future__ import annotations

import argparse
import gzip
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

try:
    # Use the operating system's certificate store (Windows, macOS). The IBGE server does not always
    # send its intermediate certificate; the OS store can complete the chain, Python's own cannot.
    import truststore

    truststore.inject_into_ssl()
except ImportError:
    truststore = None

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
API = "https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR"
GITHUB_FILE_LIMIT_MB = 95  # GitHub rejects files over 100 MB


def download(division: str, quality: str) -> dict:
    query = urllib.parse.urlencode(
        {"formato": "application/vnd.geo+json", "intrarregiao": division, "qualidade": quality}
    )
    url = f"{API}?{query}"
    for attempt in range(1, 4):
        try:
            print(f"GET {url}")
            request = urllib.request.Request(url, headers={"Accept-Encoding": "gzip", "User-Agent": "municipios-e-estados-do-brasil"})
            with urllib.request.urlopen(request, timeout=120) as response:
                body = response.read()
            if body[:2] == b"\x1f\x8b":  # IBGE answers gzip-compressed, even when not asked
                body = gzip.decompress(body)
            payload = json.loads(body.decode("utf-8"))
            if payload.get("type") != "FeatureCollection" or not payload.get("features"):
                raise ValueError(f"unexpected answer: {str(payload)[:200]}")
            return payload
        except (urllib.error.URLError, TimeoutError, ValueError) as error:
            print(f"  attempt {attempt} failed: {error}", file=sys.stderr)
            if "CERTIFICATE_VERIFY_FAILED" in str(error) and truststore is None:
                raise SystemExit("SSL certificate check failed. Run: python -m pip install --user truststore, then retry.")
            time.sleep(5 * attempt)
    raise SystemExit("IBGE API did not answer; try again later or with --qualidade minima")


def area_code(feature: dict) -> int:
    props = feature.get("properties") or {}
    for key in ("codarea", "CD_UF", "CD_MUN", "codigo", "id"):
        if key in props:
            return int(str(props[key])[:7])
    raise SystemExit(f"no area code in feature properties: {list(props)}")


def rounded(geometry: dict, digits: int = 5) -> dict:
    """Rounds coordinates to ~1 m to keep the file small."""

    def walk(value):
        if isinstance(value, list):
            return [walk(v) for v in value]
        return round(value, digits) if isinstance(value, float) else value

    return {"type": geometry["type"], "coordinates": walk(geometry["coordinates"])}


def write(path: Path, features: list[dict]) -> None:
    text = json.dumps({"type": "FeatureCollection", "features": features}, ensure_ascii=False, separators=(",", ":"))
    path.write_text(text + "\n", encoding="utf-8")
    size = path.stat().st_size / 1e6
    print(f"{path.relative_to(ROOT)}: {len(features)} features, {size:.1f} MB")
    if size > GITHUB_FILE_LIMIT_MB:
        print(f"  WARNING: over {GITHUB_FILE_LIMIT_MB} MB, GitHub will reject it; use --qualidade minima", file=sys.stderr)


def states(quality: str) -> None:
    table = pd.read_csv(DATA / "estados.csv", keep_default_na=False).set_index("ibge_code")
    payload = download("UF", quality)
    features = []
    for feature in payload["features"]:
        code = area_code(feature)
        row = table.loc[code]
        features.append(
            {
                "type": "Feature",
                "geometry": rounded(feature["geometry"]),
                "properties": {
                    "ibge_code": code, "uf": row["uf"], "name": row["name"], "region": row["region"],
                    "capital": row["capital"], "timezone": row["timezone"],
                },
            }
        )
    features.sort(key=lambda f: f["properties"]["ibge_code"])
    if len(features) != 27:
        raise SystemExit(f"expected 27 states, got {len(features)}")
    write(DATA / "estados.geojson", features)


def municipalities(quality: str) -> None:
    table = pd.read_csv(DATA / "municipios.csv", dtype={"siafi_code": str}).set_index("ibge_code")
    payload = download("municipio", quality)
    features = []
    for feature in payload["features"]:
        code = area_code(feature)
        if code not in table.index:
            print(f"  skipping unknown code {code}", file=sys.stderr)
            continue
        row = table.loc[code]
        features.append(
            {
                "type": "Feature",
                "geometry": rounded(feature["geometry"], 4),
                "properties": {"ibge_code": code, "name": row["name"], "uf": row["uf"], "ddd": int(row["ddd"])},
            }
        )
    features.sort(key=lambda f: f["properties"]["ibge_code"])
    write(DATA / "municipios-malhas.geojson", features)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--municipios", action="store_true", help="also download the 5,570 municipal boundaries")
    parser.add_argument("--qualidade", default="minima", choices=["minima", "intermediaria", "maxima"])
    args = parser.parse_args()
    states(args.qualidade)
    if args.municipios:
        municipalities(args.qualidade)


if __name__ == "__main__":
    main()
