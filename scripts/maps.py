"""Render the README maps from data/ into docs/img/.

Usage:  python scripts/maps.py   (needs matplotlib; run after build.py)

docs/img/mapa-fusos.png    every municipal seat, shaded by UTC offset
docs/img/mapa-regioes.png  small multiples, one panel per region
docs/img/mapa-estados.png  state boundaries shaded by UTC offset (only if data/estados.geojson exists;
                           create it with scripts/fetch_meshes.py)
docs/img/mapa-hidrografia.png  every municipal seat shaded by watercourse density (FBDS km per km² of area)
"""

from __future__ import annotations

import json

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "docs" / "img"

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#dddcd7"
# One-hue ordinal ramp (validated: monotone lightness, light end >= 2:1 on the surface).
OFFSET_COLOURS = {"-02:00": "#86b6ef", "-03:00": "#3987e5", "-04:00": "#1c5cab", "-05:00": "#0d366b"}
OFFSET_LABELS = {
    "-02:00": "UTC−2 · Fernando de Noronha",
    "-03:00": "UTC−3 · Brasília",
    "-04:00": "UTC−4 · AM, RR, RO, MT, MS",
    "-05:00": "UTC−5 · Acre e oeste do AM",
}
REGIONS = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]


def style(ax: plt.Axes) -> None:
    ax.set_facecolor(SURFACE)
    ax.set_aspect("equal")
    ax.set_xlim(-74.5, -31.5)
    ax.set_ylim(-34.5, 6)
    ax.axis("off")


def offsets_map(cities: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 7.5), dpi=120, facecolor=SURFACE)
    style(ax)
    for offset, colour in OFFSET_COLOURS.items():
        group = cities[cities["utc_offset"] == offset]
        size = 28 if len(group) < 5 else (3 if len(group) > 1000 else 7)
        count = f"{len(group):,}".replace(",", ".")
        ax.scatter(group["longitude"], group["latitude"], s=size, color=colour, linewidth=0,
                   label=f"{OFFSET_LABELS[offset]} ({count})")
    ax.set_title("Municípios por fuso horário", loc="left", fontsize=15, fontweight="bold", color=INK, pad=12)
    legend = ax.legend(loc="lower left", frameon=False, fontsize=9, markerscale=3, labelcolor=INK_2)
    legend.set_title("5.570 sedes municipais", prop={"size": 9})
    fig.tight_layout()
    fig.savefig(IMG / "mapa-fusos.png", facecolor=SURFACE)
    plt.close(fig)


def regions_map(cities: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 5, figsize=(14, 3.6), dpi=120, facecolor=SURFACE)
    for ax, region in zip(axes, REGIONS):
        style(ax)
        inside = cities["region"] == region
        ax.scatter(cities.loc[~inside, "longitude"], cities.loc[~inside, "latitude"], s=0.6, color=MUTED, linewidth=0)
        ax.scatter(cities.loc[inside, "longitude"], cities.loc[inside, "latitude"], s=1.2, color="#2a78d6", linewidth=0)
        ax.set_title(f"{region}\n{inside.sum():,} municípios".replace(",", "."), fontsize=11, color=INK)
    fig.tight_layout()
    fig.savefig(IMG / "mapa-regioes.png", facecolor=SURFACE)
    plt.close(fig)


ZONE_OFFSET = {
    "America/Noronha": "-02:00", "America/Rio_Branco": "-05:00", "America/Eirunepe": "-05:00",
    "America/Manaus": "-04:00", "America/Boa_Vista": "-04:00", "America/Porto_Velho": "-04:00",
    "America/Cuiaba": "-04:00", "America/Campo_Grande": "-04:00",
}


def rings(geometry: dict) -> list[list[list[float]]]:
    """Outer rings of a Polygon or MultiPolygon."""
    if geometry["type"] == "Polygon":
        return [geometry["coordinates"][0]]
    return [polygon[0] for polygon in geometry["coordinates"]]


def states_map(states: pd.DataFrame) -> bool:
    path = ROOT / "data" / "estados.geojson"
    if not path.exists():
        print("data/estados.geojson not found: run scripts/fetch_meshes.py to draw the state map")
        return False
    features = json.loads(path.read_text(encoding="utf-8"))["features"]
    fig, ax = plt.subplots(figsize=(7.5, 7.5), dpi=120, facecolor=SURFACE)
    style(ax)
    for feature in features:
        offset = ZONE_OFFSET.get(feature["properties"]["timezone"], "-03:00")
        for ring in rings(feature["geometry"]):
            ax.add_patch(Polygon(ring, closed=True, facecolor=OFFSET_COLOURS[offset], edgecolor=SURFACE, linewidth=1.2))
    for row in states.itertuples():
        light = ZONE_OFFSET.get(row.timezone, "-03:00") in ("-02:00", "-03:00")
        ax.text(row.longitude, row.latitude, row.uf, ha="center", va="center", fontsize=8,
                fontweight="bold", color=INK if light else SURFACE)
    handles = [plt.Rectangle((0, 0), 1, 1, color=OFFSET_COLOURS[o]) for o in ("-03:00", "-04:00", "-05:00")]
    labels = ["UTC−3", "UTC−4", "UTC−5 (Acre)"]
    ax.legend(handles, labels, loc="lower left", frameon=False, fontsize=9, labelcolor=INK_2,
              title="Fuso da capital", title_fontsize=9)
    ax.set_title("Estados e fusos horários", loc="left", fontsize=15, fontweight="bold", color=INK, pad=12)
    fig.tight_layout()
    fig.savefig(IMG / "mapa-estados.png", facecolor=SURFACE)
    plt.close(fig)
    return True


# Watercourse density classes (km of rivers per km² of area), close to the quartiles of the 5,470 municipalities.
DENSITY_BREAKS = [0.9, 1.3, 1.8]
DENSITY_COLOURS = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]  # same validated one-hue ramp, light = low


def fmt(value: float) -> str:
    return f"{value:.1f}".replace(".", ",")


def hydro_map(cities: pd.DataFrame) -> bool:
    if cities["hydro_rivers_km"].notna().sum() == 0:
        print("no hydrography in data/: run scripts/fetch_fbds.py and build.py to draw the hydrography map")
        return False
    density = cities["hydro_rivers_km"].astype("float") / cities["area_km2"].astype("float")
    fig, ax = plt.subplots(figsize=(7.5, 7.5), dpi=120, facecolor=SURFACE)
    style(ax)
    outlines = ROOT / "data" / "estados.geojson"
    if outlines.exists():
        for feature in json.loads(outlines.read_text(encoding="utf-8"))["features"]:
            for ring in rings(feature["geometry"]):
                ax.add_patch(Polygon(ring, closed=True, fill=False, edgecolor=MUTED, linewidth=0.6, zorder=1))
    edges = [-1.0, *DENSITY_BREAKS, float("inf")]
    names = [f"menos de {fmt(DENSITY_BREAKS[0])}", f"{fmt(DENSITY_BREAKS[0])} a {fmt(DENSITY_BREAKS[1])}",
             f"{fmt(DENSITY_BREAKS[1])} a {fmt(DENSITY_BREAKS[2])}", f"{fmt(DENSITY_BREAKS[2])} ou mais"]
    for low, high, colour, name in zip(edges, edges[1:], DENSITY_COLOURS, names):
        group = cities[(density >= low) & (density < high)]
        count = f"{len(group):,}".replace(",", ".")
        ax.scatter(group["longitude"], group["latitude"], s=4, color=colour, linewidth=0, zorder=3,
                   label=f"{name} ({count})")
    missing = density.isna()  # drawn last so it ends the legend; Pampa, Pantanal and Noronha
    ax.scatter(cities.loc[missing, "longitude"], cities.loc[missing, "latitude"], s=6, color="#b9b8b2", linewidth=0,
               zorder=2, label=f"sem mapeamento FBDS ({missing.sum()})")
    ax.set_title("Densidade de cursos d'água", loc="left", fontsize=15, fontweight="bold", color=INK, pad=12)
    legend = ax.legend(loc="lower right", frameon=False, fontsize=9, markerscale=3, labelcolor=INK_2)  # over the ocean
    legend.set_title("km de rios por km² de área", prop={"size": 9})
    fig.tight_layout()
    fig.savefig(IMG / "mapa-hidrografia.png", facecolor=SURFACE)
    plt.close(fig)
    return True


def main() -> None:
    IMG.mkdir(parents=True, exist_ok=True)
    cities = pd.read_parquet(ROOT / "data" / "municipios.parquet")
    offsets_map(cities)
    regions_map(cities)
    print("docs/img/mapa-fusos.png, docs/img/mapa-regioes.png")
    if states_map(pd.read_csv(ROOT / "data" / "estados.csv", keep_default_na=False)):
        print("docs/img/mapa-estados.png")
    if hydro_map(cities):
        print("docs/img/mapa-hidrografia.png")


if __name__ == "__main__":
    main()
