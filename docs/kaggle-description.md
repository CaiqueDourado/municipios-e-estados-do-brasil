**Municípios e estados do Brasil** com códigos IBGE e SIAFI, DDD, fusos horários IANA, coordenadas e a gramática de cada estado para geração de texto. **Brazilian municipalities and states** with IBGE and SIAFI codes, phone area codes, IANA time zones, coordinates and the grammar each state name takes in Portuguese.

## Files

- `municipios.csv`: the 5,570 municipalities (5,568 + Federal District + Fernando de Noronha). IBGE code, name, ASCII name, URL slug, state, region, capital flag, latitude/longitude, DDD, SIAFI code, canonical IANA time zone, UTC offset, IBGE boundary API URL.
- `estados.csv`: the 27 federative units. IBGE code, region, capital, centre coordinates, time zone, and the article and prepositions for text generation: `no Acre`, `na Bahia`, `em Goiás`, `do Acre`, `de São Paulo`.
- Each table also comes as typed Parquet and as JSON.

## Why another municipalities table

- **Joins:** IBGE code for census and IBGE data, SIAFI code for federal transfer and Treasury data, DDD for phone data.
- **Correct time zones:** 15 canonical IANA zones instead of the 4 generic ones common in other tables, including `America/Eirunepe` for western Amazonas.
- **Text generation:** the state grammar fields let a template write "Cartórios em Goiás" and "Cartórios no Acre" without mistakes.
- **Tested:** IBGE check digits (with the 9 official exceptions), unique keys, coordinates inside Brazil and one capital per state.

Base fields credited to kelvins/municipios-brasileiros (MIT). Full data dictionary, methodology, quality report and scripts: **https://github.com/CaiqueDourado/municipios-e-estados-do-brasil**

License: CC BY 4.0. Author: Caique Dourado.
