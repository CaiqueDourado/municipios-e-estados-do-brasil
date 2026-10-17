"""Download the public data used to enrich municipios.csv and save the raw answers in raw/enrichment/.

Usage:
    python scripts/fetch_enrichment.py            # everything
    python scripts/fetch_enrichment.py ibge cptec # only some sources

Sources (all public, no key needed):
    ibge       IBGE Localidades API: meso/micro regions, immediate and intermediate regions
    censo      IBGE SIDRA table 4714: population, area and density, 2022 Census
    estimativa IBGE SIDRA table 6579: latest official population estimate
    altitude   Open-Meteo Elevation API: elevation of each municipal seat (Copernicus DEM, 90 m)
    cptec      BrasilAPI: CPTEC/INPE city ids, the key of the weather forecast endpoints
               (falls back to CPTEC's XML, then to a city-by-city search)
    cptec_busca  only the city-by-city search (skip the list endpoints)

The raw answers are committed, so scripts/build.py stays reproducible without network.
Run scripts/build.py afterwards. On Windows: python -m pip install --user truststore
"""

from __future__ import annotations

import gzip
import xml.etree.ElementTree as ET
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

try:
    import truststore  # use the OS certificate store (some government servers send incomplete chains)

    truststore.inject_into_ssl()
except ImportError:
    truststore = None

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "raw" / "enrichment"
AGENT = "municipios-e-estados-do-brasil (+https://github.com/CaiqueDourado/municipios-e-estados-do-brasil)"


def get_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"Accept-Encoding": "gzip", "User-Agent": AGENT})
    with urllib.request.urlopen(request, timeout=180) as response:
        body = response.read()
    return gzip.decompress(body) if body[:2] == b"\x1f\x8b" else body


def get(url: str, retries: int = 4) -> object:
    attempt = 0
    while True:
        attempt += 1
        try:
            request = urllib.request.Request(url, headers={"Accept-Encoding": "gzip", "User-Agent": AGENT})
            with urllib.request.urlopen(request, timeout=120) as response:
                body = response.read()
            if body[:2] == b"\x1f\x8b":
                body = gzip.decompress(body)
            return json.loads(body.decode("utf-8"))
        except urllib.error.HTTPError as error:
            if error.code == 429:  # rate limit: wait as long as the server asks (or a minute) and keep going
                wait = int(error.headers.get("Retry-After") or 0) or 65
                print(f"  rate limited (HTTP 429), waiting {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            if error.code == 404:  # not found: retrying will not help
                raise SystemExit(f"not found: {url}")
            print(f"  attempt {attempt} failed: {error}", file=sys.stderr)
        except (urllib.error.URLError, TimeoutError, ValueError) as error:
            print(f"  attempt {attempt} failed: {error}", file=sys.stderr)
            if "CERTIFICATE_VERIFY_FAILED" in str(error) and truststore is None:
                raise SystemExit("SSL certificate check failed. Run: python -m pip install --user truststore")
        if attempt >= retries:
            raise SystemExit(f"giving up on {url}")
        time.sleep(5 * attempt)


def save(name: str, payload: object) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    size = len(payload) if isinstance(payload, list) else 1
    print(f"raw/enrichment/{name}: {size} records")


def ibge() -> None:
    save("ibge_localidades_municipios.json", get("https://servicodados.ibge.gov.br/api/v1/localidades/municipios"))


def censo() -> None:
    # Variables: 93 = population, 6318 = area (km2), 614 = density (inhab/km2); n6 = every municipality.
    save("sidra_4714_censo_2022.json", get("https://apisidra.ibge.gov.br/values/t/4714/n6/all/v/93,6318,614/p/2022"))


def estimativa() -> None:
    # Variable 9324 = estimated resident population; "last 1" = most recent year published.
    save("sidra_6579_estimativa.json", get("https://apisidra.ibge.gov.br/values/t/6579/n6/all/v/9324/p/last%201"))


def altitude() -> None:
    """Open-Meteo counts every coordinate as a call (free tier: ~600/minute, 5,000/hour), so this
    goes slowly on purpose: 100 coordinates every 15 s. Progress is saved; rerun to resume."""
    cities = pd.read_csv(ROOT / "data" / "municipios.csv")
    partial = OUT / "open_meteo_elevation.partial.json"
    rows = json.loads(partial.read_text(encoding="utf-8")) if partial.exists() else []
    done = {r["ibge_code"] for r in rows}
    todo = cities[~cities["ibge_code"].isin(done)]
    print(f"  {len(done)} already done, {len(todo)} to go (about {len(todo) // 100 * 15 // 60 + 1} min)")
    for start in range(0, len(todo), 100):  # the API takes up to 100 coordinates per call
        chunk = todo.iloc[start:start + 100]
        query = urllib.parse.urlencode(
            {"latitude": ",".join(map(str, chunk["latitude"])), "longitude": ",".join(map(str, chunk["longitude"]))}
        )
        answer = get(f"https://api.open-meteo.com/v1/elevation?{query}")
        rows += [{"ibge_code": int(code), "elevation_m": value} for code, value in zip(chunk["ibge_code"], answer["elevation"])]
        OUT.mkdir(parents=True, exist_ok=True)
        partial.write_text(json.dumps(rows), encoding="utf-8")
        print(f"  elevation {len(rows)}/{len(cities)}")
        time.sleep(15)
    rows.sort(key=lambda r: r["ibge_code"])
    save("open_meteo_elevation.json", rows)
    partial.unlink(missing_ok=True)


def parse_cptec_xml(body: bytes) -> list[dict]:
    root = ET.fromstring(body)  # the XML declares its own encoding (ISO-8859-1)
    return [
        {"nome": c.findtext("nome"), "estado": c.findtext("uf"), "id": int(c.findtext("id"))}
        for c in root.iter("cidade") if c.findtext("id")
    ]


def cptec() -> None:
    """CPTEC city ids. BrasilAPI's list endpoint is a proxy of CPTEC and sometimes fails (HTTP 500);
    in that case read the same list straight from CPTEC's XML service."""
    saved = OUT / "cptec_listaCidades.xml"  # the same list saved by hand from a browser
    if saved.exists():
        cities = parse_cptec_xml(saved.read_bytes())
        if cities:
            save("brasilapi_cptec_cidades.json", cities)
            return
        print(f"  {saved.name} has no <cidade> entries; trying the network", file=sys.stderr)
    try:
        cities = get("https://brasilapi.com.br/api/cptec/v1/cidade", retries=2)
        if isinstance(cities, list) and cities:
            save("brasilapi_cptec_cidades.json", cities)
            return
    except SystemExit:
        pass
    print("  BrasilAPI failed; trying CPTEC directly (servicos.cptec.inpe.br/XML/listaCidades)")
    for attempt in range(1, 4):
        try:
            cities = parse_cptec_xml(get_bytes("http://servicos.cptec.inpe.br/XML/listaCidades"))
            if cities:
                save("brasilapi_cptec_cidades.json", cities)
                return
        except (urllib.error.URLError, TimeoutError, ET.ParseError, ValueError) as error:
            print(f"  attempt {attempt} failed: {error}", file=sys.stderr)
            time.sleep(10 * attempt)
    print("  CPTEC XML unavailable; searching BrasilAPI city by city (resumable, about 40 min)")
    cptec_by_name()


def cptec_by_name() -> None:
    """Last resort: BrasilAPI's search endpoint (/cidade/{name}) usually works when the full list fails.
    One call per distinct municipality name, 0.4 s apart; progress is saved, rerun to resume."""
    names = sorted(set(pd.read_csv(ROOT / "data" / "municipios.csv")["name"]))
    partial = OUT / "brasilapi_cptec_busca.partial.json"
    state = json.loads(partial.read_text(encoding="utf-8")) if partial.exists() else {"done": [], "cities": []}
    done = set(state["done"])
    todo = [n for n in names if n not in done]
    print(f"  {len(done)} names already searched, {len(todo)} to go")
    OUT.mkdir(parents=True, exist_ok=True)
    failures = 0
    for i, name in enumerate(todo, 1):
        url = f"https://brasilapi.com.br/api/cptec/v1/cidade/{urllib.parse.quote(name)}"
        try:
            found = get(url, retries=2)
            failures = 0
        except SystemExit as error:
            if "not found" not in str(error):  # server error: do not mark the name as searched
                failures += 1
                if failures >= 5:
                    partial.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
                    raise SystemExit("  BrasilAPI's CPTEC service is down (5 names failed in a row). "
                                     "Progress saved; try again later.")
                continue
            found = []  # 404: CPTEC has no city with this name
        if isinstance(found, list):
            state["cities"] += [{"nome": c["nome"], "estado": c["estado"], "id": c["id"]} for c in found]
        state["done"].append(name)
        if i % 50 == 0 or i == len(todo):
            partial.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            print(f"  searched {len(state['done'])}/{len(names)} names, {len(state['cities'])} CPTEC cities found")
        time.sleep(0.4)
    unique = {c["id"]: c for c in state["cities"]}
    save("brasilapi_cptec_cidades.json", sorted(unique.values(), key=lambda c: c["id"]))
    partial.unlink(missing_ok=True)


SOURCES = {"ibge": ibge, "censo": censo, "estimativa": estimativa, "altitude": altitude, "cptec": cptec, "cptec_busca": cptec_by_name}


def main() -> None:
    chosen = sys.argv[1:] or list(SOURCES)
    unknown = set(chosen) - set(SOURCES)
    if unknown:
        raise SystemExit(f"unknown source(s): {', '.join(sorted(unknown))}; choose from {', '.join(SOURCES)}")
    for name in chosen:
        print(f"== {name}")
        SOURCES[name]()
        time.sleep(1)


if __name__ == "__main__":
    main()
