# Changelog

Versions follow [Semantic Versioning](https://semver.org/): a new major version renames or removes columns.

## [1.0.0] - 2026-10-15

### Added
- `municipios` (5,570 rows, 15 columns) and `estados` (27 rows, 14 columns) in CSV, Parquet and JSON.
- Data dictionary in English and Portuguese, methodology, data quality report, third-party notices.
- `scripts/build.py`, `scripts/validate.py`, `scripts/docs.py`; validation in GitHub Actions.
- Kaggle metadata and exploratory notebook.

### Fixed (relative to the raw export)
- Canonical IANA time zones, state articles, IBGE API v3 boundary URLs and the other items in `docs/data-quality.md`.
