**Municípios e estados do Brasil** com códigos IBGE e SIAFI, DDD, fusos horários IANA, coordenadas e a gramática de cada estado para geração de texto. **Brazilian municipalities and states** with IBGE and SIAFI codes, phone area codes, IANA time zones, coordinates and the grammar each state name takes in Portuguese.

![States by time zone](https://raw.githubusercontent.com/CaiqueDourado/municipios-e-estados-do-brasil/main/docs/img/mapa-estados.png)

![Watercourse density per municipality (FBDS)](https://raw.githubusercontent.com/CaiqueDourado/municipios-e-estados-do-brasil/main/docs/img/mapa-hidrografia.png)

![Municipalities by time zone](https://raw.githubusercontent.com/CaiqueDourado/municipios-e-estados-do-brasil/main/docs/img/mapa-fusos.png)

![Municipalities by region](https://raw.githubusercontent.com/CaiqueDourado/municipios-e-estados-do-brasil/main/docs/img/mapa-regioes.png)

## Files

- `municipios.csv`: the 5,570 municipalities (5,568 + Federal District + Fernando de Noronha). IBGE code, name, ASCII name, URL slug, state, region, capital flag, latitude/longitude, DDD, SIAFI code, canonical IANA time zone, UTC offset, IBGE boundary API URL.
- `estados.csv`: the 27 federative units. IBGE code, region, capital, centre coordinates, time zone, and the article and prepositions for text generation: `no Acre`, `na Bahia`, `em Goiás`, `do Acre`, `de São Paulo`.
- Each table also comes as typed Parquet and as JSON.
- `municipios.geojson`: all municipal seats as GeoJSON points, ready for QGIS, Kepler.gl, Folium or any web map.
- `estados.geojson`: boundaries of the 27 states (IBGE API v3) as GeoJSON polygons, joined to `estados.csv`.

- Enrichment joined by IBGE code: regional divisions, 2022 Census population, area and density, latest population estimate, seat elevation and FBDS hydrography totals (springs, km of rivers, water bodies) for 5,470 municipalities (98%).
- Interactive explorer: https://caiquedourado.github.io/municipios-e-estados-do-brasil/

## How a state is structured

![One state and its municipalities as nested JSON](https://raw.githubusercontent.com/CaiqueDourado/municipios-e-estados-do-brasil/main/docs/img/state-json.png)

One row of `estados`, Acre, with its columns grouped and its 22 municipalities from `municipios` nested under it by `state_ibge_code`, the capital first. The state takes an article ("no Acre", "do Acre") and has 830,018 people in the 2022 Census; Rio Branco, its capital, has 364,756, DDD 68, SIAFI code `0139` and UTC offset `-05:00`. Full record: [`docs/example-state.json`](https://github.com/CaiqueDourado/municipios-e-estados-do-brasil/blob/main/docs/example-state.json), built by [`scripts/make_json.py`](https://github.com/CaiqueDourado/municipios-e-estados-do-brasil/blob/main/scripts/make_json.py).

## Why another municipalities table

- **Joins:** IBGE code for census and IBGE data, SIAFI code for federal transfer and Treasury data, DDD for phone data.
- **Correct time zones:** 15 canonical IANA zones instead of the 4 generic ones common in other tables, including `America/Eirunepe` for western Amazonas.
- **Text generation:** the state grammar fields let a template write "Cartórios em Goiás" and "Cartórios no Acre" without mistakes.
- **Tested:** IBGE check digits (with the 9 official exceptions), unique keys, coordinates inside Brazil and one capital per state.

Base fields credited to kelvins/municipios-brasileiros (MIT). Full data dictionary, methodology, quality report and scripts: **https://github.com/CaiqueDourado/municipios-e-estados-do-brasil**

License: CC BY 4.0. Author: Caique Dourado.

Same project: Brazilian e-commerce product catalog, 114.6 million offers from 7,179 stores: https://www.kaggle.com/datasets/caiquedourado/catalogo-produtos-ecommerce-brasil
