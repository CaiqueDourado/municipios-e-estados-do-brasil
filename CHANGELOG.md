# Changelog

Versions follow [Semantic Versioning](https://semver.org/): a new major version renames or removes columns.

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
