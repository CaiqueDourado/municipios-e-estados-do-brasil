# Data quality report

What was found while profiling the raw export, and what was done about it. Every fix is code in `scripts/build.py`; `raw/` keeps the original values.

## Fixed in the clean version

| # | Problem in `raw/` | Rows | Fix |
|---|---|---|---|
| 1 | Only four IANA zone names were used. Mato Grosso, Mato Grosso do Sul, Amazonas and Roraima were `America/Porto_Velho`; the whole Northeast was `America/Sao_Paulo`; western Amazonas was `America/Rio_Branco`. Offsets were right, names were not, which breaks historical conversions (zones had different daylight saving rules until 2019). | 2,389 | Canonical zone per state (`America/Cuiaba`, `America/Campo_Grande`, `America/Manaus`, `America/Boa_Vista`, `America/Fortaleza`, `America/Recife`, `America/Maceio`, `America/Bahia`, `America/Belem`, `America/Araguaina`); the 13 western Amazonas municipalities → `America/Eirunepe`; Fernando de Noronha keeps `America/Noronha` |
| 2 | `artigo` = "o" for the 9 states whose names take no article (Alagoas, Goiás, Minas Gerais, Pernambuco, Rondônia, Roraima, Santa Catarina, Sergipe, São Paulo) | 9 states | Empty, consistent with `em`/`de` |
| 3 | Column names `pronome`/`preposicao` described prepositions as pronouns | — | Renamed `prep_em` / `prep_de` |
| 4 | Boundary URL on the IBGE API v2 | 5,570 | API v3 (`/api/v3/malhas/municipios/{code}`); states got their own URL |
| 5 | Decimal comma, no header, semicolon separator, BOM | all | Standard CSV with header, decimal point, UTF-8 without BOM |
| 6 | Internal ids as keys (`idEstado` 29–55, city `id` with a gap at 3205) | all | IBGE codes as keys; internal ids dropped |
| 7 | SIAFI code stored twice (`codigo_municipio` padded, `siafi_id` unpadded) | all | One column, `siafi_code`, 4 digits as text |
| 8 | No region, no ASCII name, no slug, no offset | — | Added (`region`, `name_ascii`, `slug`, `utc_offset`) |

## Checked and correct (do not "fix")

- **9 IBGE codes fail the usual check-digit rule:** 2201919 Bom Princípio do Piauí, 2201988 Brejo do Piauí, 2202251 Canavieira, 2611533 Quixabá, 3117836 Cônego Marinho, 3152131 Ponto Chique, 4305871 Coronel Barros, 5203939 Buriti de Goiás, 5203962 Buritinópolis. They are the official codes; the validator allows exactly these.
- **3 municipalities use the neighbouring state's area code:** Barracão (PR) uses 49, Rio Negro (PR) uses 47 and Porto União (SC) uses 42. They are twin border towns that share a phone area with Dionísio Cerqueira (SC), Mafra (SC) and União da Vitória (PR). Every other DDD matches its state, and the validator checks this.
- **5,570 rows** is the full IBGE list: 5,568 municipalities, plus the Federal District (Brasília) and the state district of Fernando de Noronha.
- **Coordinates** were compared with each state's centre: no municipality falls outside its state's plausible range. The farthest is Fernando de Noronha (PE), 786 km offshore, as expected.

## Known limitations

- **Coordinates** have variable precision (0 to 6 decimals); Carvalhos (MG) has `-22` with no decimals. The seat location, not the centroid.
- **State coordinates** are rough centres with 2 decimals.
- **Western Pará** uses `America/Belem`; the IANA database also has `America/Santarem` for that area, with identical rules since 2008.
- **Western Amazonas** follows the raw offsets: 13 municipalities at UTC-5, including Lábrea and Jutaí.
- **DDD** is the main code of the municipality; a few municipalities are served by more than one.
- **Name spelling** follows the source (`Alta Floresta D'Oeste`, `Itapejara d'Oeste`); IBGE itself is not uniform on `D'`/`d'`.
