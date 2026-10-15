"""Build the clean dataset from raw/cidades.csv and raw/estados.csv.

Usage:  python scripts/build.py

The raw files are the SQL Server export, untouched: semicolon separated, no header,
decimal comma. The column order is documented in docs/methodology.md. This script
types the columns, applies the corrections listed in docs/data-quality.md and writes
data/municipios.{csv,parquet,json}, data/estados.{csv,parquet,json} and stats.json.
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data"

RAW_STATE_COLUMNS = ["id", "estado", "uf", "cod_ibge", "pronome", "artigo", "preposicao", "latitude", "longitude"]
RAW_CITY_COLUMNS = [
    "id", "cidade", "idEstado", "codigo_municipio", "latitude", "longitude",
    "codigo_ibge", "siafi_id", "ddd", "capital", "fuso_horario", "mapa",
]

REGIONS = {"1": "Norte", "2": "Nordeste", "3": "Sudeste", "4": "Sul", "5": "Centro-Oeste"}

# Canonical IANA zone per state. The raw data used only four zone names (Sao_Paulo,
# Porto_Velho, Rio_Branco, Noronha); offsets were right, names were not.
STATE_ZONE = {
    "AC": "America/Rio_Branco", "AL": "America/Maceio", "AM": "America/Manaus", "AP": "America/Belem",
    "BA": "America/Bahia", "CE": "America/Fortaleza", "DF": "America/Sao_Paulo", "ES": "America/Sao_Paulo",
    "GO": "America/Sao_Paulo", "MA": "America/Fortaleza", "MG": "America/Sao_Paulo", "MS": "America/Campo_Grande",
    "MT": "America/Cuiaba", "PA": "America/Belem", "PB": "America/Fortaleza", "PE": "America/Recife",
    "PI": "America/Fortaleza", "PR": "America/Sao_Paulo", "RJ": "America/Sao_Paulo", "RN": "America/Fortaleza",
    "RO": "America/Porto_Velho", "RR": "America/Boa_Vista", "RS": "America/Sao_Paulo", "SC": "America/Sao_Paulo",
    "SE": "America/Maceio", "SP": "America/Sao_Paulo", "TO": "America/Araguaina",
}
ZONE_OFFSET = {
    "America/Noronha": "-02:00", "America/Rio_Branco": "-05:00", "America/Eirunepe": "-05:00",
    "America/Manaus": "-04:00", "America/Boa_Vista": "-04:00", "America/Porto_Velho": "-04:00",
    "America/Cuiaba": "-04:00", "America/Campo_Grande": "-04:00",
}
MESH_URL = "https://servicodados.ibge.gov.br/api/v3/malhas/{kind}/{code}"


def number(text: str) -> float:
    return float(text.replace(",", "."))


def ascii_name(name: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", name) if not unicodedata.combining(c))


def slugify(text: str) -> str:
    text = ascii_name(text).lower().replace("'", "")
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def read(name: str, columns: list[str]) -> list[dict[str, str]]:
    with (ROOT / "raw" / name).open(encoding="utf-8-sig", newline="") as handle:
        return [dict(zip(columns, row)) for row in csv.reader(handle, delimiter=";") if row]


def zone_for(city: dict[str, str], uf: str) -> str:
    if city["fuso_horario"] == "America/Noronha":
        return "America/Noronha"
    if uf == "AM" and city["fuso_horario"] == "America/Rio_Branco":
        return "America/Eirunepe"  # western Amazonas, UTC-5 like Acre
    return STATE_ZONE[uf]


def build_states(raw_states: list[dict[str, str]], capitals: dict[str, str]) -> pd.DataFrame:
    rows = []
    for s in raw_states:
        em = s["pronome"]  # "no" / "na" / "em"
        article = {"no": "o", "na": "a", "em": ""}[em]
        de = s["preposicao"]
        rows.append(
            {
                "ibge_code": int(s["cod_ibge"]),
                "uf": s["uf"],
                "name": s["estado"],
                "region": REGIONS[s["cod_ibge"][0]],
                "capital": capitals[s["uf"]],
                "latitude": number(s["latitude"]),
                "longitude": number(s["longitude"]),
                "article": article or None,
                "prep_em": em,
                "prep_de": de,
                "name_with_em": f"{em} {s['estado']}",
                "name_with_de": f"{de} {s['estado']}",
                "timezone": STATE_ZONE[s["uf"]],
                "mesh_url": MESH_URL.format(kind="estados", code=s["cod_ibge"]),
            }
        )
    return pd.DataFrame(rows).sort_values("ibge_code").reset_index(drop=True)


def build_cities(raw_cities: list[dict[str, str]], states_by_id: dict[str, dict[str, str]]) -> pd.DataFrame:
    rows = []
    for c in raw_cities:
        state = states_by_id[c["idEstado"]]
        uf = state["uf"]
        zone = zone_for(c, uf)
        rows.append(
            {
                "ibge_code": int(c["codigo_ibge"]),
                "name": c["cidade"],
                "name_ascii": ascii_name(c["cidade"]),
                "slug": f"{slugify(c['cidade'])}-{uf.lower()}",
                "uf": uf,
                "state_ibge_code": int(state["cod_ibge"]),
                "region": REGIONS[state["cod_ibge"][0]],
                "is_capital": c["capital"] == "1",
                "latitude": number(c["latitude"]),
                "longitude": number(c["longitude"]),
                "ddd": int(c["ddd"]),
                "siafi_code": c["codigo_municipio"],
                "timezone": zone,
                "utc_offset": ZONE_OFFSET.get(zone, "-03:00"),
                "mesh_url": MESH_URL.format(kind="municipios", code=c["codigo_ibge"]),
            }
        )
    return pd.DataFrame(rows).sort_values("ibge_code").reset_index(drop=True)


def column_stats(frame: pd.DataFrame) -> dict:
    return {
        name: {
            "dtype": str(frame[name].dtype),
            "non_null": int(frame[name].notna().sum()),
            "null_pct": round(float(frame[name].isna().mean() * 100), 2),
            "distinct": int(frame[name].nunique(dropna=True)),
        }
        for name in frame.columns
    }


def write(frame: pd.DataFrame, stem: str) -> None:
    frame.to_csv(OUT / f"{stem}.csv", index=False, encoding="utf-8", lineterminator="\n")
    frame.to_parquet(OUT / f"{stem}.parquet", index=False)
    records = json.loads(frame.to_json(orient="records", force_ascii=False))
    (OUT / f"{stem}.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def geojson(cities: pd.DataFrame) -> dict:
    """Municipal seats as GeoJSON points; GitHub renders this file as an interactive map."""
    features = []
    for row in cities.itertuples():
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [row.longitude, row.latitude]},
                "properties": {
                    "ibge_code": row.ibge_code, "name": row.name, "uf": row.uf, "region": row.region,
                    "ddd": row.ddd, "timezone": row.timezone, "is_capital": bool(row.is_capital),
                },
            }
        )
    return {"type": "FeatureCollection", "features": features}


def main() -> None:
    raw_states = read("estados.csv", RAW_STATE_COLUMNS)
    raw_cities = read("cidades.csv", RAW_CITY_COLUMNS)
    states_by_id = {s["id"]: s for s in raw_states}
    capitals = {states_by_id[c["idEstado"]]["uf"]: c["cidade"] for c in raw_cities if c["capital"] == "1"}

    states = build_states(raw_states, capitals)
    cities = build_cities(raw_cities, states_by_id)

    OUT.mkdir(exist_ok=True)
    write(cities, "municipios")
    write(states, "estados")
    (OUT / "municipios.geojson").write_text(
        json.dumps(geojson(cities), ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    stats = {
        "dataset": "municipios-e-estados-do-brasil",
        "municipios": {"rows": len(cities), "by_uf": cities["uf"].value_counts().sort_index().to_dict(), "fields": column_stats(cities)},
        "estados": {"rows": len(states), "fields": column_stats(states)},
    }
    (ROOT / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(cities)} municipalities, {len(states)} states -> data/")


if __name__ == "__main__":
    main()
