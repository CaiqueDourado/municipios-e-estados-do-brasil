# Changelog

Versions follow [Semantic Versioning](https://semver.org/): a new major version renames or removes columns.

## [1.2.0] - 2026-10-17

### Added
- Enrichment from public APIs, joined by `ibge_code`: immediate, intermediate, micro and meso regions (IBGE), 2022 Census population, area and density, latest population estimate (IBGE SIDRA) and seat elevation (Open-Meteo / Copernicus DEM).
- `municipality_count`, `population_2022` and `area_km2` in `estados`.
- `scripts/fetch_enrichment.py` (raw answers saved in `raw/enrichment/`) and `scripts/enrich.py`.
- Hydrography totals per municipality from FBDS (`hydro_*` columns and state sums), via `scripts/fetch_fbds.py`: 5,470 of 5,570 municipalities; the 100 without an FBDS folder are listed in `docs/hydro-missing.csv`.
- `docs/img/mapa-hidrografia.png`: watercourse density per municipality (`scripts/maps.py`).
- `index.html`: interactive explorer for GitHub Pages, with live weather forecasts from BrasilAPI / CPTEC.

### Not included
- `cptec_id`: the CPTEC city list was unavailable (BrasilAPI HTTP 500, CPTEC HTTP 403). The collector is kept in `scripts/fetch_enrichment.py`.

## [1.1.0] - 2026-10-15

### Added
- `data/municipios.geojson`: every municipal seat as a GeoJSON point; GitHub renders it as an interactive map.
- Map section in the READMEs: time zone map, regional small multiples and an interactive map of the 27 capitals.
- `scripts/fetch_meshes.py`: downloads state (and optionally municipal) boundaries from the IBGE API v3 into `data/estados.geojson`.
- `scripts/maps.py`, which generates `docs/img/mapa-estados.png` (when the boundaries exist), `docs/img/mapa-fusos.png` and `docs/img/mapa-regioes.png`.

## [1.0.0] - 2026-10-15

### Added
- `municipios` (5,570 rows, 15 columns) and `estados` (27 rows, 14 columns) in CSV, Parquet and JSON.
- Data dictionary in English and Portuguese, methodology, data quality report, third-party notices.
- `scripts/build.py`, `scripts/validate.py`, `scripts/docs.py`; validation in GitHub Actions.
- Kaggle metadata and exploratory notebook.

### Fixed (relative to the raw export)
- Canonical IANA time zones, state articles, IBGE API v3 boundary URLs and the other items in `docs/data-quality.md`.
