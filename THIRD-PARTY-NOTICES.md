# Third-party notices

## kelvins/municipios-brasileiros

The base fields of the municipalities and states tables (IBGE code, name, coordinates,
capital flag, SIAFI code, DDD, time zone, state centre coordinates) match the public
dataset [kelvins/municipios-brasileiros](https://github.com/kelvins/municipios-brasileiros),
credited here as their likely origin. That project is distributed under the MIT License:

> Copyright (c) Kelvin S. do Prado
>
> Permission is hereby granted, free of charge, to any person obtaining a copy of this
> software and associated documentation files (the "Software"), to deal in the Software
> without restriction, including without limitation the rights to use, copy, modify,
> merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
> permit persons to whom the Software is furnished to do so, subject to the following
> conditions:
>
> The above copyright notice and this permission notice shall be included in all copies
> or substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
> INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
> PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
> HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
> CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
> THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Open-Meteo / Copernicus DEM

`elevation_m` comes from the [Open-Meteo Elevation API](https://open-meteo.com/en/docs/elevation-api), data licensed under CC BY 4.0, based on the Copernicus DEM GLO-90 (© DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018, provided under COPERNICUS by the European Union and ESA).

## BrasilAPI / CPTEC-INPE

The explorer (`index.html`) shows weather forecasts fetched live from [BrasilAPI](https://brasilapi.com.br), which mirrors the Centro de Previsão de Tempo e Estudos Climáticos (CPTEC/INPE). No CPTEC data is stored in this dataset.

## FBDS

Hydrography totals (`hydro_*`) are derived from the high-resolution mapping of the Fundação Brasileira para o Desenvolvimento Sustentável. Source: "Hidrografia: Fundação Brasileira para o Desenvolvimento Sustentável (FBDS), disponível em geo.fbds.org.br". Data are free to use with attribution; only per-municipality totals are redistributed here, not the original geometries.

## IBGE

Municipality and state codes, names, regional divisions, 2022 Census population and area, population estimates and boundary API: Instituto Brasileiro de Geografia
e Estatística (IBGE), public data.
