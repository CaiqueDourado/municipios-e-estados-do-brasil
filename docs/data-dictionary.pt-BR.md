# Dicionário de dados: Municípios e estados do Brasil: códigos IBGE e SIAFI, DDD, fusos, coordenadas e gramática para geração de texto

Gerado por `scripts/docs.py` a partir de `schema/columns.json`. Tipos, nulos e exemplos vêm dos arquivos em `data/`.

## `municipios.csv`

Os 5.570 municípios do Brasil: códigos IBGE e SIAFI, UF, região, capital, coordenadas, DDD, fuso IANA e URL da malha do IBGE.

| Coluna | Tipo | Nulos | Exemplo | Descrição | Padrão | Origem |
|---|---|---|---|---|---|---|
| `ibge_code` | integer | 0,0% | `3146305` | Código IBGE do município (7 dígitos, o último é verificador). Chave primária. | IBGE | fonte |
| `name` | string | 0,0% | `Padre Paraíso` | Nome oficial do município, com acentos. | IBGE | fonte |
| `name_ascii` | string | 0,0% | `Padre Paraiso` | Nome sem acentos (NFKD), para busca e cruzamento. | — | derivado |
| `slug` | string | 0,0% | `padre-paraiso-mg` | Slug para URL: nome sem acentos, minúsculo, com hífens, mais a UF (sao-paulo-sp). Único. | — | derivado |
| `uf` | string | 0,0% | `MG` | Sigla da UF (SP, BA…). | IBGE | fonte |
| `state_ibge_code` | integer | 0,0% | `31` | Código IBGE da UF (2 dígitos); igual aos dois primeiros dígitos de ibge_code. | IBGE | fonte |
| `region` | string | 0,0% | `Sudeste` | Região: Norte, Nordeste, Sudeste, Sul, Centro-Oeste. | IBGE | derivado |
| `is_capital` | boolean | 0,0% | `False` | Verdadeiro para as 27 capitais (Brasília inclusa). | — | fonte |
| `latitude` | float | 0,0% | `-17.0758` | Latitude da sede do município, em graus decimais. | WGS 84 | fonte |
| `longitude` | float | 0,0% | `-41.4821` | Longitude da sede do município, em graus decimais. | WGS 84 | fonte |
| `ddd` | integer | 0,0% | `33` | Código DDD de telefonia. | Anatel | fonte |
| `siafi_code` | string | 0,0% | `4925` | Código do município no SIAFI (Tesouro Nacional), 4 dígitos com zeros à esquerda. Usado nos dados de transferências federais. | SIAFI | fonte |
| `timezone` | string | 0,0% | `America/Sao_Paulo` | Fuso IANA canônico (America/Sao_Paulo, America/Manaus, America/Eirunepe…). | IANA tzdb | corrigido |
| `utc_offset` | string | 0,0% | `-03:00` | Deslocamento UTC padrão (o Brasil não tem horário de verão desde 2019). | — | derivado |
| `mesh_url` | string | 0,0% | `https://servicodados.ibge.gov.br/api/…` | URL da API v3 do IBGE com a malha do município. Acrescente ?formato=application/vnd.geo+json para GeoJSON. | IBGE API | derivado |

## `estados.csv`

As 27 unidades da federação: código IBGE, região, capital, coordenadas, fuso e as preposições e o artigo que cada nome leva em português.

| Coluna | Tipo | Nulos | Exemplo | Descrição | Padrão | Origem |
|---|---|---|---|---|---|---|
| `ibge_code` | integer | 0,0% | `27` | Código IBGE da UF (2 dígitos). Chave primária. | IBGE | fonte |
| `uf` | string | 0,0% | `AL` | Sigla da UF. | IBGE | fonte |
| `name` | string | 0,0% | `Alagoas` | Nome da UF. | IBGE | fonte |
| `region` | string | 0,0% | `Nordeste` | Região (pelo primeiro dígito de ibge_code). | IBGE | derivado |
| `capital` | string | 0,0% | `Maceió` | Capital (de municipios.csv). | — | derivado |
| `latitude` | float | 0,0% | `-9.62` | Latitude aproximada do centro da UF. | WGS 84 | fonte |
| `longitude` | float | 0,0% | `-36.82` | Longitude aproximada do centro da UF. | WGS 84 | fonte |
| `article` | string | 33,3% | `a` | Artigo usado com o nome: o, a, ou vazio quando o nome não leva artigo (Goiás, São Paulo). | — | Caique Dourado, corrigido |
| `prep_em` | string | 0,0% | `em` | "em" + artigo: no, na ou em (no Acre, na Bahia, em Goiás). | — | Caique Dourado |
| `prep_de` | string | 0,0% | `de` | "de" + artigo: do, da ou de (do Acre, da Bahia, de Goiás). | — | Caique Dourado |
| `name_with_em` | string | 0,0% | `em Alagoas` | Expressão pronta: prep_em + nome ("na Bahia"). | — | derivado |
| `name_with_de` | string | 0,0% | `de Alagoas` | Expressão pronta: prep_de + nome ("de São Paulo"). | — | derivado |
| `timezone` | string | 0,0% | `America/Maceio` | Fuso IANA canônico da capital. | IANA tzdb | corrigido |
| `mesh_url` | string | 0,0% | `https://servicodados.ibge.gov.br/api/…` | URL da API v3 do IBGE com a malha da UF. | IBGE API | derivado |

## Convenções

- Codificação UTF-8 sem BOM, separador vírgula, cabeçalho na primeira linha, quebra de linha `\n`.
- Separador decimal é o ponto `.`. Booleanos são `True` / `False`.
- `ibge_code` cruza com qualquer tabela do IBGE; `siafi_code`, com dados do Tesouro (SIAFI); `uf` liga `municipios.csv` a `estados.csv`.
