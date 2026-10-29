# Municípios e estados do Brasil

[![validate](https://github.com/CaiqueDourado/municipios-e-estados-do-brasil/actions/workflows/validate.yml/badge.svg)](https://github.com/CaiqueDourado/municipios-e-estados-do-brasil/actions/workflows/validate.yml)
[![Dados: CC BY 4.0](https://img.shields.io/badge/dados-CC%20BY%204.0-lightgrey.svg)](LICENSE-DATA.md)
[![Código: MIT](https://img.shields.io/badge/c%C3%B3digo-MIT-blue.svg)](LICENSE)
[![Kaggle](https://img.shields.io/badge/Kaggle-dataset-20BEFF.svg)](https://www.kaggle.com/datasets/caiquedourado/municipios-e-estados-do-brasil)

**Os 5.570 municípios e as 27 UFs do Brasil** com códigos IBGE e SIAFI, DDD, fusos horários IANA, coordenadas, slug e a gramática de cada estado ("no Acre", "em Goiás") para geração de texto. CSV, Parquet e JSON.

[Read in English](README.md) · **[Abrir o explorador interativo](https://caiquedourado.github.io/municipios-e-estados-do-brasil/)**

## Prévia

| ibge_code | name | uf | region | ddd | siafi_code | timezone | utc_offset | slug |
|---|---|---|---|---|---|---|---|---|
| 3550308 | São Paulo | SP | Sudeste | 11 | 7107 | America/Sao_Paulo | -03:00 | sao-paulo-sp |
| 2927408 | Salvador | BA | Nordeste | 71 | 3849 | America/Bahia | -03:00 | salvador-ba |
| 1302405 | Lábrea | AM | Norte | 97 | 0251 | America/Eirunepe | -05:00 | labrea-am |
| 2605459 | Fernando de Noronha | PE | Nordeste | 81 | 3001 | America/Noronha | -02:00 | fernando-de-noronha-pe |

| uf | name | capital | article | name_with_em | name_with_de |
|---|---|---|---|---|---|
| AC | Acre | Rio Branco | o | no Acre | do Acre |
| BA | Bahia | Salvador | a | na Bahia | da Bahia |
| GO | Goiás | Goiânia | | em Goiás | de Goiás |

## Como um estado é estruturado

![Um estado e seus municípios em JSON aninhado](docs/img/state-json.png)

Uma linha de `estados`, o Acre, com as colunas agrupadas e os 22 municípios de `municipios` aninhados por
`state_ibge_code`, a capital primeiro. O estado leva artigo ("no Acre", "do Acre") e tem 830.018 habitantes no
Censo 2022; Rio Branco, a capital, tem 364.756, DDD 68, código SIAFI `0139` e fuso `-05:00`. Registro completo:
[`docs/example-state.json`](docs/example-state.json), gerado por [`scripts/make_json.py`](scripts/make_json.py).

## Mapa

**[Explorador interativo](https://caiquedourado.github.io/municipios-e-estados-do-brasil/)**: escolha qualquer município para ver o contorno, os dados e a previsão do tempo. Troque o código no endereço (`?ibge=2927408`) para ir direto a outro.

![Municípios por fuso horário](docs/img/mapa-fusos.png)

![Municípios por região](docs/img/mapa-regioes.png)

Toda linha tem coordenadas, então os dados desenham o Brasil sozinhos. Duas formas de explorar de forma interativa no GitHub:

- **Os 5.570 municípios:** abra [`data/municipios.geojson`](data/municipios.geojson). O GitHub mostra um mapa com zoom; clique num ponto para ver o código IBGE, o DDD e o fuso.
- **As 27 capitais**, aqui mesmo (o GitHub transforma o bloco abaixo num mapa):

```geojson
{"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": {"type": "Point", "coordinates": [-67.8243, -9.97499]}, "properties": {"capital": "Rio Branco", "uf": "AC", "ibge_code": 1200401, "ddd": 68, "timezone": "America/Rio_Branco"}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-35.735, -9.66599]}, "properties": {"capital": "Maceió", "uf": "AL", "ibge_code": 2704302, "ddd": 82, "timezone": "America/Maceio"}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-60.0212, -3.11866]}, "properties": {"capital": "Manaus", "uf": "AM", "ibge_code": 1302603, "ddd": 92, "timezone": "America/Manaus"}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-51.0694, 0.034934]}, "properties": {"capital": "Macapá", "uf": "AP", "ibge_code": 1600303, "ddd": 96, "timezone": "America/Belem"}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-38.5011, -12.9718]}, "properties": {"capital": "Salvador", "uf": "BA", "ibge_code": 2927408, "ddd": 71, "timezone": "America/Bahia"}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-38.5423, -3.71664]}, "properties": {"capital": "Fortaleza", "uf": "CE", "ibge_code": 2304400, "ddd": 85, "timezone": "America/Fortaleza"}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-47.9297, -15.7795]}, "properties": {"capital": "Brasília", "uf": "DF", "ibge_code": 5300108, "ddd": 61, "timezone": "America/Sao_Paulo"}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-40.3128, -20.3155]}, "properties": {"capital": "Vitória", "uf": "ES", "ibge_code": 3205309, "ddd": 27, "timezone": "America/Sao_Paulo"}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-49.2643, -16.6864]}, "properties": {"capital": "Goiânia", "uf": "GO", "ibge_code": 5208707, "ddd": 62, "timezone": "America/Sao_Paulo"}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-44.2825, -2.53874]}, "properties": {"capital": "São Luís", "uf": "MA", "ibge_code": 2111300, "ddd": 98, "timezone": "America/Fortaleza"}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-43.9266, -19.9102]}, "properties": {"capital": "Belo Horizonte", "uf": "MG", "ibge_code": 3106200, "ddd": 31, "timezone": "America/Sao_Paulo"}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-54.6295, -20.4486]}, "properties": {"capital": "Campo Grande", "uf": "MS", "ibge_code": 5002704, "ddd": 67, "timezone": "America/Campo_Grande"}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-56.0974, -15.601]}, "properties": {"capital": "Cuiabá", "uf": "MT", "ibge_code": 5103403, "ddd": 65, "timezone": "America/Cuiaba"}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-48.4898, -1.4554]}, "properties": {"capital": "Belém", "uf": "PA", "ibge_code": 1501402, "ddd": 91, "timezone": "America/Belem"}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-34.8641, -7.11509]}, "properties": {"capital": "João Pessoa", "uf": "PB", "ibge_code": 2507507, "ddd": 83, "timezone": "America/Fortaleza"}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-34.8771, -8.04666]}, "properties": {"capital": "Recife", "uf": "PE", "ibge_code": 2611606, "ddd": 81, "timezone": "America/Recife"}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-42.8034, -5.09194]}, "properties": {"capital": "Teresina", "uf": "PI", "ibge_code": 2211001, "ddd": 86, "timezone": "America/Fortaleza"}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-49.2646, -25.4195]}, "properties": {"capital": "Curitiba", "uf": "PR", "ibge_code": 4106902, "ddd": 41, "timezone": "America/Sao_Paulo"}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-43.2003, -22.9129]}, "properties": {"capital": "Rio de Janeiro", "uf": "RJ", "ibge_code": 3304557, "ddd": 21, "timezone": "America/Sao_Paulo"}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-35.1986, -5.79357]}, "properties": {"capital": "Natal", "uf": "RN", "ibge_code": 2408102, "ddd": 84, "timezone": "America/Fortaleza"}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-63.8999, -8.76077]}, "properties": {"capital": "Porto Velho", "uf": "RO", "ibge_code": 1100205, "ddd": 69, "timezone": "America/Porto_Velho"}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-60.6753, 2.82384]}, "properties": {"capital": "Boa Vista", "uf": "RR", "ibge_code": 1400100, "ddd": 95, "timezone": "America/Boa_Vista"}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-51.2065, -30.0318]}, "properties": {"capital": "Porto Alegre", "uf": "RS", "ibge_code": 4314902, "ddd": 51, "timezone": "America/Sao_Paulo"}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-48.5477, -27.5945]}, "properties": {"capital": "Florianópolis", "uf": "SC", "ibge_code": 4205407, "ddd": 48, "timezone": "America/Sao_Paulo"}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-37.0677, -10.9091]}, "properties": {"capital": "Aracaju", "uf": "SE", "ibge_code": 2800308, "ddd": 79, "timezone": "America/Maceio"}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-46.6395, -23.5329]}, "properties": {"capital": "São Paulo", "uf": "SP", "ibge_code": 3550308, "ddd": 11, "timezone": "America/Sao_Paulo"}}, {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-48.3558, -10.24]}, "properties": {"capital": "Palmas", "uf": "TO", "ibge_code": 1721000, "ddd": 63, "timezone": "America/Araguaina"}}]}
```

![Estados por fuso horário](docs/img/mapa-estados.png)

![Densidade de cursos d'água por município](docs/img/mapa-hidrografia.png)

- **Hidrografia:** cada sede municipal colorida pelos km de cursos d'água por km² de área, do mapeamento em alta resolução da FBDS. As sedes em cinza (Pampa, Pantanal e Fernando de Noronha) não têm mapeamento da FBDS; a lista está em [`docs/hydro-missing.csv`](docs/hydro-missing.csv).
- **Contornos das UFs:** abra [`data/estados.geojson`](data/estados.geojson) para um mapa interativo dos 27 estados (polígonos da API v3 do IBGE, ligados a `estados.csv`).

`scripts/fetch_meshes.py` baixa as malhas da API do IBGE (`--municipios` baixa também os polígonos dos 5.570 municípios); `scripts/maps.py` desenha as imagens acima.

## Como usar

```python
import pandas as pd

base = "https://raw.githubusercontent.com/CaiqueDourado/municipios-e-estados-do-brasil/main/data/"
estados = pd.read_csv(base + "estados.csv", keep_default_na=False)

for e in estados.itertuples():
    print(f"Cartórios {e.name_with_em}: lista completa {e.name_with_de}")
# Cartórios no Acre: lista completa do Acre
# Cartórios em Goiás: lista completa de Goiás
```

## Por que esta tabela

- **Cruza com dados públicos:** `ibge_code` com IBGE e censo, `siafi_code` com Tesouro e transferências federais, `ddd` com telefonia.
- **Fusos corretos:** usa 15 fusos IANA canônicos. Muitas tabelas usam só `America/Sao_Paulo` e mais três; o deslocamento de hoje fica certo, mas o histórico fica errado, porque os estados tinham regras de horário de verão diferentes até 2019.
- **Enriquecida com APIs públicas:** divisões regionais do IBGE (regiões imediata, intermediária, micro e mesorregião), população, área e densidade do Censo 2022, estimativa de população mais recente, altitude da sede e totais de hidrografia da FBDS (nascentes, km de rios, massas d'água) para 98% dos municípios. As respostas brutas ficam versionadas em `raw/enrichment/`.
- **Pronta para geração de texto:** um template escreve "em Goiás" e "no Acre" sem exceções feitas à mão.
- **Testada:** a cada push, são revalidados:
  - os dígitos verificadores do IBGE, aceitando só as 9 exceções oficiais;
  - as chaves únicas;
  - as coordenadas dentro do Brasil;
  - uma capital por UF.

Coluna por coluna: **[dicionário de dados](docs/data-dictionary.pt-BR.md)**.

## Como foi construída

Estas tabelas eram a base geográfica dos sites programáticos do autor, entre eles um portal com 15 mil cartórios coletados do sistema [Justiça Aberta](https://justicaaberta.cnj.jus.br/), do CNJ.

- **Campos base:** creditados ao [kelvins/municipios-brasileiros](https://github.com/kelvins/municipios-brasileiros) (MIT).
- **Acrescentados pelo autor:** a gramática dos estados, as URLs de malha e o código SIAFI com zeros.

Em 2026 a exportação foi perfilada, corrigida e ganhou um build reproduzível. Detalhes em [methodology.md](docs/methodology.md).

## Como os dados são coletados

O enriquecimento da v1.2 vem de fontes públicas, cada uma com seu script de coleta em [`scripts/`](scripts/). As respostas brutas ficam em [`raw/enrichment/`](raw/enrichment/), então o build roda sem rede e o CI confere que ele reproduz exatamente os arquivos de `data/`.

| Script | Fonte | O que mostra |
|---|---|---|
| [`fetch_enrichment.py`](scripts/fetch_enrichment.py) | APIs do IBGE (Localidades, SIDRA) | Consulta a tabelas do SIDRA e leitura de respostas compactadas em gzip |
| | Open-Meteo (altitude) | Respeita a cota da API gratuita (100 coordenadas a cada 15 s), espera o `Retry-After` quando recebe 429 e retoma de onde parou |
| | BrasilAPI / CPTEC | Usa o XML do próprio CPTEC e, se falhar, busca cidade por cidade (serviço indisponível em out/2026, por isso fora da v1.2) |
| [`fetch_fbds.py`](scripts/fetch_fbds.py) | FBDS, hidrografia por município | Navega listagens de pastas sem API e reprojeta os shapefiles com pyproj. Calcula comprimentos e áreas sobre o elipsoide GRS80, com diferença abaixo de 0,1% em relação à própria FBDS. Retoma de onde parou e guarda só os totais |
| [`fetch_meshes.py`](scripts/fetch_meshes.py) | API de malhas v3 do IBGE | Gera o GeoJSON dos estados e usa o repositório de certificados do sistema quando o servidor envia a cadeia SSL incompleta |

Todos os coletores se identificam pelo User-Agent, aguardam entre as requisições e não desativam a verificação TLS.

## Qualidade

O perfil da exportação encontrou estes problemas, todos corrigidos em código:

- 2.389 municípios com nome de fuso não canônico.
- 9 UFs com o artigo errado.
- URLs de malha numa versão antiga da API.
- Chaves internas no lugar dos códigos IBGE.

O perfil também confirmou que os 9 dígitos verificadores "inválidos" do IBGE são oficiais. O relatório completo está em [data-quality.md](docs/data-quality.md).

## Relacionados

- Artigo: [Enriquecendo cadastros com APIs abertas](https://github.com/CaiqueDourado/articles/blob/main/open-apis/README.pt-BR.md): como juntar um cadastro a esta tabela pelo código IBGE.
- [portuguese-entity-gazetteer](https://github.com/CaiqueDourado/portuguese-entity-gazetteer): 307 mil entidades do português com seus tipos, 10 mil delas cidades e 5 mil bairros.
- [brazilian-notary-registry-offices](https://github.com/CaiqueDourado/brazilian-notary-registry-offices): os cartórios do Brasil, ligados a esta tabela por `codigo_ibge` = `ibge_code`.
- [search-pattern-miner](https://github.com/CaiqueDourado/search-pattern-miner): o gazetteer de exemplo de lugares vem desta base (estados, siglas e municípios com 100 mil habitantes ou mais).

## Licença

Dados: [CC BY 4.0](LICENSE-DATA.md), com o aviso MIT da base em [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md). Código: [MIT](LICENSE).

## Autor

**Caique Dourado**: 20 anos construindo crawlers, pipelines de dados e SEO programático em .NET e SQL Server. Mais em [github.com/CaiqueDourado](https://github.com/CaiqueDourado): [paises-do-mundo-ptbr](https://github.com/CaiqueDourado/paises-do-mundo-ptbr), [brazilian-names-surnames](https://github.com/CaiqueDourado/brazilian-names-surnames) (nomes brasileiros com o estado onde cada um é mais comum), [PtBr.Text](https://github.com/CaiqueDourado/PtBr.Text).
