# Municípios e estados do Brasil · Brazilian municipalities and states

[![validate](https://github.com/CaiqueDourado/municipios-e-estados-do-brasil/actions/workflows/validate.yml/badge.svg)](https://github.com/CaiqueDourado/municipios-e-estados-do-brasil/actions/workflows/validate.yml)
[![Data: CC BY 4.0](https://img.shields.io/badge/data-CC%20BY%204.0-lightgrey.svg)](LICENSE-DATA.md)
[![Code: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)
[![Kaggle](https://img.shields.io/badge/Kaggle-dataset-20BEFF.svg)](https://www.kaggle.com/datasets/caiquedourado/municipios-e-estados-do-brasil)

**pt-BR:** Os 5.570 municípios e as 27 UFs do Brasil com códigos IBGE e SIAFI, DDD, fusos horários IANA, coordenadas, slug e a gramática de cada estado ("no Acre", "em Goiás") para geração de texto.
**en:** All 5,570 Brazilian municipalities and 27 states with IBGE and SIAFI codes, phone area codes, IANA time zones, coordinates, URL slugs and the grammar each state name takes in Portuguese, for text generation.

[Leia em português](README.pt-BR.md)

| Table | Rows | Columns | Formats | Checks |
|---|---|---|---|---|
| `municipios` | 5,570 | 15 | CSV · Parquet · JSON | IBGE check digit, unique keys, coordinates, DDD, zones |
| `estados` | 27 | 14 | CSV · Parquet · JSON | grammar consistency, joins with `municipios` |

## Preview

| ibge_code | name | uf | region | ddd | siafi_code | timezone | utc_offset | slug |
|---|---|---|---|---|---|---|---|---|
| 3550308 | São Paulo | SP | Sudeste | 11 | 7107 | America/Sao_Paulo | -03:00 | sao-paulo-sp |
| 2927408 | Salvador | BA | Nordeste | 71 | 3849 | America/Bahia | -03:00 | salvador-ba |
| 1302405 | Lábrea | AM | Norte | 97 | 0251 | America/Eirunepe | -05:00 | labrea-am |
| 2605459 | Fernando de Noronha | PE | Nordeste | 81 | 3001 | America/Noronha | -02:00 | fernando-de-noronha-pe |
| 5300108 | Brasília | DF | Centro-Oeste | 61 | 9701 | America/Sao_Paulo | -03:00 | brasilia-df |

| uf | name | capital | article | name_with_em | name_with_de |
|---|---|---|---|---|---|
| AC | Acre | Rio Branco | o | no Acre | do Acre |
| BA | Bahia | Salvador | a | na Bahia | da Bahia |
| GO | Goiás | Goiânia | | em Goiás | de Goiás |
| SP | São Paulo | São Paulo | | em São Paulo | de São Paulo |

## Use it

```python
import pandas as pd

base = "https://raw.githubusercontent.com/CaiqueDourado/municipios-e-estados-do-brasil/main/data/"
cities = pd.read_csv(base + "municipios.csv", dtype={"siafi_code": str})
states = pd.read_csv(base + "estados.csv", keep_default_na=False)

# Programmatic SEO: one title per state, grammatically correct
for s in states.itertuples():
    print(f"Cartórios {s.name_with_em}: lista completa {s.name_with_de}")
```

```sql
-- DuckDB: municipalities per time zone
SELECT timezone, utc_offset, count(*) AS municipios
FROM 'data/municipios.parquet' GROUP BY ALL ORDER BY municipios DESC;
```

## Why this table

- **Joins across government data:** `ibge_code` for IBGE and census data, `siafi_code` for Treasury and federal transfers, `ddd` for telephony.
- **Correct time zones:** 15 canonical IANA zones. Many public tables use only `America/Sao_Paulo` and a handful of others; that gives the right offset today but the wrong history, because the states had different daylight saving rules until 2019.
- **Ready for text generation:** a template can write "em Goiás" and "no Acre" without hand-written exceptions.
- **Tested:** every push revalidates the IBGE check digits, allowing exactly the 9 official exceptions. It also checks unique keys, coordinates inside Brazil and one capital per state.

Column by column: **[data dictionary](docs/data-dictionary.md)** ([pt-BR](docs/data-dictionary.pt-BR.md)).

## How it was built

These tables were the geographic backbone of the author's programmatic sites, among them a portal of 15,000 registry offices crawled from the CNJ [Justiça Aberta](https://justicaaberta.cnj.jus.br/) system. Base fields are credited to [kelvins/municipios-brasileiros](https://github.com/kelvins/municipios-brasileiros) (MIT). The state grammar, map URLs and padded SIAFI codes were added by the author. In 2026 the export was profiled, corrected and given a reproducible build. Details in [methodology](docs/methodology.md).

## Data quality

Profiling the raw export found several problems:

- 2,389 municipalities had a non-canonical time zone name.
- 9 states had the wrong article.
- The boundary URLs pointed to an outdated API version.
- The export used internal ids as keys.

All of it is fixed in code. It also confirmed that the 9 "invalid" IBGE check digits are official. The full report is in [data-quality.md](docs/data-quality.md).

## Repository layout

```text
data/          municipios.* and estados.* (CSV, Parquet, JSON) + dataset-metadata.json (Kaggle)
raw/           SQL Server export, untouched (semicolon, no header, decimal comma)
schema/        column definitions and dataset metadata
scripts/       build.py, validate.py, docs.py
notebooks/     eda.ipynb
docs/          data dictionary, methodology, data quality
```

```bash
pip install -r requirements.txt
python scripts/build.py && python scripts/validate.py && python scripts/docs.py
```

## License

Data: [CC BY 4.0](LICENSE-DATA.md), with the MIT notice of the base data in [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md). Code: [MIT](LICENSE). Citation: [CITATION.cff](CITATION.cff).

## Author

**Caique Dourado**: 20 years building crawlers, data pipelines and programmatic SEO in .NET and SQL Server. More at [github.com/CaiqueDourado](https://github.com/CaiqueDourado): [paises-do-mundo-ptbr](https://github.com/CaiqueDourado/paises-do-mundo-ptbr), [PtBr.Text](https://github.com/CaiqueDourado/PtBr.Text) (CEP, DDD, CPF/CNPJ and Portuguese text utilities for .NET).
