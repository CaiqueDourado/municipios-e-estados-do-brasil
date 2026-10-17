"""Join the public data saved by scripts/fetch_enrichment.py (raw/enrichment/) to the tables.

Used by scripts/build.py. Every enrichment column always exists; it stays empty when its raw
file is missing, so the schema does not depend on which sources were downloaded.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

import pandas as pd

RAW = Path(__file__).resolve().parents[1] / "raw" / "enrichment"

CITY_COLUMNS = [
    "immediate_region_code", "immediate_region", "intermediate_region_code", "intermediate_region",
    "microregion_code", "microregion", "mesoregion_code", "mesoregion",
    "population_2022", "area_km2", "density_2022", "population_estimate", "population_estimate_year",
    "elevation_m",
    "hydro_springs", "hydro_rivers_km", "hydro_double_rivers_ha", "hydro_water_bodies", "hydro_water_bodies_ha",
    "hydro_artificial_water_bodies", "hydro_source_updated",
]
INTEGER_COLUMNS = [
    "immediate_region_code", "intermediate_region_code", "microregion_code", "mesoregion_code",
    "population_2022", "population_estimate", "population_estimate_year", "elevation_m",
    "hydro_springs", "hydro_water_bodies", "hydro_artificial_water_bodies",
]


def load(name: str):
    path = RAW / name
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def number(value) -> float | None:
    try:
        return float(str(value).replace(",", "."))
    except ValueError:
        return None  # SIDRA uses "-", "..." and "X" for missing or confidential values


def key_name(text: str) -> str:
    text = "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", text.lower())


def regions(payload) -> pd.DataFrame:
    rows = []
    for m in payload or []:
        micro = m.get("microrregiao") or {}
        meso = micro.get("mesorregiao") or {}
        immediate = m.get("regiao-imediata") or {}
        intermediate = immediate.get("regiao-intermediaria") or {}
        rows.append(
            {
                "ibge_code": int(m["id"]),
                "immediate_region_code": immediate.get("id"), "immediate_region": immediate.get("nome"),
                "intermediate_region_code": intermediate.get("id"), "intermediate_region": intermediate.get("nome"),
                "microregion_code": micro.get("id"), "microregion": micro.get("nome"),
                "mesoregion_code": meso.get("id"), "mesoregion": meso.get("nome"),
            }
        )
    return pd.DataFrame(rows)


def sidra(payload, variables: dict[str, str]) -> pd.DataFrame:
    """Turns a SIDRA /values answer into one row per municipality, one column per variable."""
    if not payload:
        return pd.DataFrame(columns=["ibge_code", *variables.values()])
    header, *rows = payload
    find = lambda label: next(k for k, v in header.items() if v.startswith(label))  # noqa: E731
    city, variable = find("Município (Código)"), find("Variável (Código)")
    year = next((k for k, v in header.items() if v.startswith("Ano (Código)")), None)
    out: dict[int, dict] = {}
    for row in rows:
        code = variables.get(row[variable])
        if code is None:
            continue
        record = out.setdefault(int(row[city]), {"ibge_code": int(row[city])})
        record[code] = number(row["V"])
        if year:
            record["_year"] = int(row[year])
    return pd.DataFrame(out.values())


def elevation(payload) -> pd.DataFrame:
    frame = pd.DataFrame(payload or [], columns=["ibge_code", "elevation_m"])
    frame["elevation_m"] = frame["elevation_m"].round()
    return frame


def cptec(payload, cities: pd.DataFrame) -> pd.DataFrame:
    ids = {(key_name(c["nome"]), c["estado"]): c["id"] for c in payload or []}
    keys = [(key_name(name), uf) for name, uf in zip(cities["name"], cities["uf"])]
    return pd.DataFrame({"ibge_code": cities["ibge_code"], "cptec_id": [ids.get(k) for k in keys]})


def hydrography() -> pd.DataFrame:
    """Per-municipality totals written by scripts/fetch_fbds.py (FBDS hydrography)."""
    path = RAW / "fbds_hidrografia.csv"
    if not path.exists():
        return pd.DataFrame(columns=["ibge_code"])
    frame = pd.read_csv(path, dtype={"source_updated": str}).drop_duplicates("ibge_code", keep="last")
    return frame.rename(columns={
        "springs": "hydro_springs", "rivers_km": "hydro_rivers_km", "double_rivers_ha": "hydro_double_rivers_ha",
        "water_bodies": "hydro_water_bodies", "water_bodies_ha": "hydro_water_bodies_ha",
        "artificial_water_bodies": "hydro_artificial_water_bodies", "source_updated": "hydro_source_updated",
    })[["ibge_code", "hydro_springs", "hydro_rivers_km", "hydro_double_rivers_ha", "hydro_water_bodies",
        "hydro_water_bodies_ha", "hydro_artificial_water_bodies", "hydro_source_updated"]]


def enrich(cities: pd.DataFrame, states: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    census = sidra(load("sidra_4714_censo_2022.json"), {"93": "population_2022", "6318": "area_km2", "614": "density_2022"})
    census = census.drop(columns="_year", errors="ignore")
    estimate = sidra(load("sidra_6579_estimativa.json"), {"9324": "population_estimate"})
    estimate = estimate.rename(columns={"_year": "population_estimate_year"})

    parts = [
        regions(load("ibge_localidades_municipios.json")),
        census,
        estimate,
        elevation(load("open_meteo_elevation.json")),
        # cptec(load("brasilapi_cptec_cidades.json"), cities): out of v1.2, CPTEC refuses public access (HTTP 403).
        # When fetch_enrichment.py cptec works again, restore this line and "cptec_id" in CITY_COLUMNS.
        hydrography(),
    ]
    out = cities.copy()
    report = {}
    for part in parts:
        if part.empty or len(part.columns) == 1:
            continue
        extra = set(part["ibge_code"]) - set(out["ibge_code"])
        if extra:
            report["codes_not_in_table"] = sorted(set(report.get("codes_not_in_table", [])) | extra)
        out = out.merge(part, on="ibge_code", how="left")
    for column in CITY_COLUMNS:
        if column not in out:
            out[column] = None
    for column in INTEGER_COLUMNS:
        out[column] = pd.to_numeric(out[column], errors="coerce").round().astype("Int64")
    for column in ("area_km2", "density_2022", "hydro_rivers_km", "hydro_double_rivers_ha", "hydro_water_bodies_ha"):
        out[column] = pd.to_numeric(out[column], errors="coerce").astype("Float64").round(2)
    for column in ("immediate_region", "intermediate_region", "microregion", "mesoregion", "hydro_source_updated"):
        out[column] = out[column].astype("string")
    report["coverage"] = {c: int(out[c].notna().sum()) for c in CITY_COLUMNS}

    by_uf = out.groupby("uf").agg(
        municipality_count=("ibge_code", "size"),
        population_2022=("population_2022", lambda s: s.sum(min_count=1)),
        area_km2=("area_km2", lambda s: s.sum(min_count=1)),
        hydro_springs=("hydro_springs", lambda s: s.sum(min_count=1)),
        hydro_rivers_km=("hydro_rivers_km", lambda s: s.sum(min_count=1)),
    )
    states = states.drop(columns=[c for c in by_uf.columns if c in states], errors="ignore")
    states = states.merge(by_uf.reset_index(), on="uf", how="left")
    states["population_2022"] = states["population_2022"].astype("Int64")
    states["area_km2"] = states["area_km2"].astype("Float64").round(2)
    states["hydro_springs"] = states["hydro_springs"].astype("Int64")
    states["hydro_rivers_km"] = states["hydro_rivers_km"].astype("Float64").round(2)
    return out[[*cities.columns, *CITY_COLUMNS]], states, report
