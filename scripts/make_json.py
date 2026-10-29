"""One state with its municipalities as nested JSON (docs/example-state.json), from data/estados.json and
data/municipios.json.

    python scripts/make_json.py

The state's columns are grouped (grammar, 2022 Census, FBDS hydrography) and its municipalities, joined by
state_ibge_code, are nested under it: capital first, then by 2022 population. Column names are kept as they are;
only the grouping is added. Standard library only.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UF = "AC"  # Acre: a state that takes an article ("no Acre"), with its own time zone and 22 municipalities

STATE_GROUPS = {
    "grammar": ("article", "prep_em", "prep_de", "name_with_em", "name_with_de"),
    "census_2022": ("population_2022", "area_km2"),
    "hydrography": ("hydro_springs", "hydro_rivers_km"),
}
CITY_GROUPS = {
    "regional_division": ("immediate_region_code", "immediate_region", "intermediate_region_code", "intermediate_region",
                          "microregion_code", "microregion", "mesoregion_code", "mesoregion"),
    "census_2022": ("population_2022", "area_km2", "density_2022"),
    "estimate": ("population_estimate", "population_estimate_year"),
    "hydrography": ("hydro_springs", "hydro_rivers_km", "hydro_double_rivers_ha", "hydro_water_bodies",
                    "hydro_water_bodies_ha", "hydro_artificial_water_bodies", "hydro_source_updated"),
}


def grouped(row: dict, groups: dict[str, tuple[str, ...]], skip: tuple[str, ...] = ()) -> dict:
    """Ungrouped columns first, in file order, then one object per group."""
    inside = {c for cols in groups.values() for c in cols}
    out = {k: v for k, v in row.items() if k not in inside and k not in skip}
    for name, cols in groups.items():
        out[name] = {c: row[c] for c in cols}
    return out


def build() -> dict:
    states = json.loads((ROOT / "data" / "estados.json").read_text(encoding="utf-8"))
    cities = json.loads((ROOT / "data" / "municipios.json").read_text(encoding="utf-8"))
    state = next(s for s in states if s["uf"] == UF)
    mine = [c for c in cities if c["state_ibge_code"] == state["ibge_code"]]
    mine.sort(key=lambda c: (not c["is_capital"], -(c["population_2022"] or 0), c["ibge_code"]))
    rec = grouped(state, STATE_GROUPS)
    rec["municipios"] = [grouped(c, CITY_GROUPS, skip=("uf", "state_ibge_code", "region")) for c in mine]
    return rec


def main() -> None:
    out = ROOT / "docs" / "example-state.json"
    out.write_text(json.dumps(build(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
