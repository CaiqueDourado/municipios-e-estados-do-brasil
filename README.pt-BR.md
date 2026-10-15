# Municípios e estados do Brasil

[![validate](https://github.com/CaiqueDourado/municipios-e-estados-do-brasil/actions/workflows/validate.yml/badge.svg)](https://github.com/CaiqueDourado/municipios-e-estados-do-brasil/actions/workflows/validate.yml)
[![Dados: CC BY 4.0](https://img.shields.io/badge/dados-CC%20BY%204.0-lightgrey.svg)](LICENSE-DATA.md)
[![Código: MIT](https://img.shields.io/badge/c%C3%B3digo-MIT-blue.svg)](LICENSE)
[![Kaggle](https://img.shields.io/badge/Kaggle-dataset-20BEFF.svg)](https://www.kaggle.com/datasets/caiquedourado/municipios-e-estados-do-brasil)

**Os 5.570 municípios e as 27 UFs do Brasil** com códigos IBGE e SIAFI, DDD, fusos horários IANA, coordenadas, slug e a gramática de cada estado ("no Acre", "em Goiás") para geração de texto. CSV, Parquet e JSON.

[Read in English](README.md)

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

## Qualidade

O perfil da exportação encontrou estes problemas, todos corrigidos em código:

- 2.389 municípios com nome de fuso não canônico.
- 9 UFs com o artigo errado.
- URLs de malha numa versão antiga da API.
- Chaves internas no lugar dos códigos IBGE.

O perfil também confirmou que os 9 dígitos verificadores "inválidos" do IBGE são oficiais. O relatório completo está em [data-quality.md](docs/data-quality.md).

## Licença

Dados: [CC BY 4.0](LICENSE-DATA.md), com o aviso MIT da base em [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md). Código: [MIT](LICENSE).

## Autor

**Caique Dourado**: 20 anos construindo crawlers, pipelines de dados e SEO programático em .NET e SQL Server. Mais em [github.com/CaiqueDourado](https://github.com/CaiqueDourado).
