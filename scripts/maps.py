"""Render the README maps from data/ into docs/img/.

Usage:  python scripts/maps.py   (needs matplotlib; run after build.py)

docs/img/mapa-fusos.png    every municipal seat, shaded by UTC offset
docs/img/mapa-regioes.png  small multiples, one panel per region
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
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


def main() -> None:
    IMG.mkdir(parents=True, exist_ok=True)
    cities = pd.read_parquet(ROOT / "data" / "municipios.parquet")
    offsets_map(cities)
    regions_map(cities)
    print("docs/img/mapa-fusos.png, docs/img/mapa-regioes.png")


if __name__ == "__main__":
    main()
