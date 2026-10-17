"""Validate data/municipios.csv and data/estados.csv. Exits with code 1 on any failure.

Usage:  python scripts/validate.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
failures: list[str] = []

# Official IBGE codes whose last digit does not follow the usual check-digit rule.
IBGE_CHECK_DIGIT_EXCEPTIONS = {2201919, 2201988, 2202251, 2611533, 3117836, 3152131, 4305871, 5203939, 5203962}
VALID_DDD = {
    11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 24, 27, 28, 31, 32, 33, 34, 35, 37, 38, 41, 42, 43, 44, 45, 46, 47,
    48, 49, 51, 53, 54, 55, 61, 62, 63, 64, 65, 66, 67, 68, 69, 71, 73, 74, 75, 77, 79, 81, 82, 83, 84, 85, 86, 87,
    88, 89, 91, 92, 93, 94, 95, 96, 97, 98, 99,
}
# Area codes per state (Anatel numbering plan). DDD 61 also covers GO towns around Brasília.
DDD_BY_UF = {
    "SP": {11, 12, 13, 14, 15, 16, 17, 18, 19}, "RJ": {21, 22, 24}, "ES": {27, 28},
    "MG": {31, 32, 33, 34, 35, 37, 38}, "PR": {41, 42, 43, 44, 45, 46}, "SC": {47, 48, 49},
    "RS": {51, 53, 54, 55}, "DF": {61}, "GO": {61, 62, 64}, "TO": {63}, "MT": {65, 66}, "MS": {67},
    "AC": {68}, "RO": {69}, "BA": {71, 73, 74, 75, 77}, "SE": {79}, "PE": {81, 87}, "AL": {82},
    "PB": {83}, "RN": {84}, "CE": {85, 88}, "PI": {86, 89}, "PA": {91, 93, 94}, "AM": {92, 97},
    "RR": {95}, "AP": {96}, "MA": {98, 99},
}
# Twin border towns that use the neighbouring state's area code (correct, not errors).
DDD_EXCEPTIONS = {4102604: 49, 4122305: 47, 4213609: 42}  # Barracão-PR, Rio Negro-PR, Porto União-SC
OFFSETS = {
    "America/Noronha": "-02:00", "America/Rio_Branco": "-05:00", "America/Eirunepe": "-05:00",
    "America/Manaus": "-04:00", "America/Boa_Vista": "-04:00", "America/Porto_Velho": "-04:00",
    "America/Cuiaba": "-04:00", "America/Campo_Grande": "-04:00", "America/Sao_Paulo": "-03:00",
    "America/Fortaleza": "-03:00", "America/Recife": "-03:00", "America/Maceio": "-03:00",
    "America/Bahia": "-03:00", "America/Belem": "-03:00", "America/Araguaina": "-03:00",
}


def check(condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def ibge_check_digit(code: int) -> int:
    total = 0
    for i, ch in enumerate(str(code)[:6]):
        product = int(ch) * (1 if i % 2 == 0 else 2)
        total += product // 10 + product % 10
    return (10 - total % 10) % 10


def main() -> int:
    cities = pd.read_csv(ROOT / "data" / "municipios.csv", dtype={"siafi_code": str}, keep_default_na=False)
    states = pd.read_csv(ROOT / "data" / "estados.csv", keep_default_na=False)

    check(len(cities) == 5570, f"expected 5570 municipalities, got {len(cities)}")
    check(len(states) == 27, f"expected 27 states, got {len(states)}")
    check(len(pd.read_parquet(ROOT / "data" / "municipios.parquet")) == len(cities), "Parquet and CSV differ")

    check(cities["ibge_code"].is_unique, "duplicated ibge_code")
    check(cities["siafi_code"].is_unique, "duplicated siafi_code")
    check(cities["slug"].is_unique, "duplicated slug")
    check(cities["ibge_code"].between(1_000_000, 9_999_999).all(), "ibge_code must have 7 digits")
    check(cities["siafi_code"].str.fullmatch(r"\d{4}").all(), "siafi_code must have 4 digits")

    prefix_mismatch = cities[cities["ibge_code"] // 100_000 != cities["state_ibge_code"]]
    check(prefix_mismatch.empty, f"ibge_code prefix differs from state: {prefix_mismatch['ibge_code'].tolist()[:5]}")

    wrong_digit = {
        code for code in cities["ibge_code"] if ibge_check_digit(code) != code % 10
    } - IBGE_CHECK_DIGIT_EXCEPTIONS
    check(not wrong_digit, f"invalid IBGE check digit: {sorted(wrong_digit)}")

    check(set(cities["ddd"]) <= VALID_DDD, f"unknown DDD: {sorted(set(cities['ddd']) - VALID_DDD)}")
    off_plan = [
        row.ibge_code
        for row in cities.itertuples()
        if row.ddd not in DDD_BY_UF[row.uf] and DDD_EXCEPTIONS.get(row.ibge_code) != row.ddd
    ]
    check(not off_plan, f"DDD does not belong to the state: {off_plan}")
    check(cities["latitude"].between(-34, 6).all() and cities["longitude"].between(-74, -28).all(), "coordinates outside Brazil")

    capitals = cities[cities["is_capital"]]
    check(len(capitals) == 27 and capitals["uf"].is_unique, "exactly one capital per state expected")

    expected_offset = cities["timezone"].map(OFFSETS)
    check(expected_offset.notna().all(), f"unknown time zones: {sorted(set(cities['timezone']) - set(OFFSETS))}")
    check((expected_offset == cities["utc_offset"]).all(), "utc_offset differs from the time zone")

    check(set(cities["uf"]) == set(states["uf"]), "states in municipios.csv differ from estados.csv")
    joined = cities.merge(states[["uf", "ibge_code", "region"]], on="uf", suffixes=("", "_state"))
    check((joined["state_ibge_code"] == joined["ibge_code_state"]).all(), "state_ibge_code differs from estados.csv")
    check((joined["region"] == joined["region_state"]).all(), "region differs from estados.csv")

    article = {"no": "o", "na": "a", "em": ""}
    de = {"no": "do", "na": "da", "em": "de"}
    check((states["article"] == states["prep_em"].map(article)).all(), "article inconsistent with prep_em")
    check((states["prep_de"] == states["prep_em"].map(de)).all(), "prep_de inconsistent with prep_em")
    check((states["name_with_em"] == states["prep_em"] + " " + states["name"]).all(), "name_with_em inconsistent")

    # Enrichment columns (filled by scripts/fetch_enrichment.py + build.py). Checked only when present.
    enriched = pd.read_parquet(ROOT / "data" / "municipios.parquet")
    for column, minimum in {"immediate_region_code": 0.99, "population_2022": 0.99, "elevation_m": 0.99}.items():
        filled = enriched[column].notna().mean()
        if filled > 0:
            check(filled >= minimum, f"{column}: only {filled:.1%} filled (expected >= {minimum:.0%})")
    for column, digits in {"immediate_region_code": 6, "intermediate_region_code": 4, "microregion_code": 5, "mesoregion_code": 4}.items():
        codes = enriched[column].dropna().astype(int)
        uf = enriched.loc[codes.index, "state_ibge_code"]
        check((codes // 10 ** (digits - 2) == uf).all(), f"{column} does not start with the state code")
    with_census = enriched.dropna(subset=["population_2022", "area_km2", "density_2022"])
    if not with_census.empty:
        density = with_census["population_2022"] / with_census["area_km2"]
        off = with_census[(density - with_census["density_2022"]).abs() > density * 0.02 + 0.1]
        check(off.empty, f"density_2022 differs from population/area: {off['ibge_code'].tolist()[:5]}")
        check((with_census["population_2022"] > 0).all(), "population_2022 must be positive")
    check(enriched["elevation_m"].dropna().between(-20, 3100).all(), "elevation_m out of Brazil's range")
    if "cptec_id" in enriched:
        check(enriched["cptec_id"].dropna().is_unique, "cptec_id is not unique")
    hydro_filled = enriched["hydro_springs"].notna().mean()
    if hydro_filled > 0:
        check(hydro_filled >= 0.95, f"hydro_springs: only {hydro_filled:.1%} filled (expected >= 95%)")
    for column in ("hydro_springs", "hydro_rivers_km", "hydro_double_rivers_ha", "hydro_water_bodies", "hydro_water_bodies_ha"):
        check((enriched[column].dropna() >= 0).all(), f"{column} must not be negative")
    hydro = enriched.dropna(subset=["hydro_water_bodies", "hydro_artificial_water_bodies"])
    check((hydro["hydro_artificial_water_bodies"] <= hydro["hydro_water_bodies"]).all(), "more artificial than total water bodies")

    # Optional boundary file produced by scripts/fetch_meshes.py.
    meshes = ROOT / "data" / "estados.geojson"
    if meshes.exists():
        features = json.loads(meshes.read_text(encoding="utf-8"))["features"]
        codes = sorted(f["properties"]["ibge_code"] for f in features)
        check(codes == sorted(states["ibge_code"]), "estados.geojson does not have exactly the 27 states")

    for message in failures:
        print("FAIL", message)
    print(f"{len(cities)} municipalities and {len(states)} states checked, {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
