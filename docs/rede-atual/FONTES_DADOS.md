# Fontes de Dados

## SEMOB-JP

Fonte inicial:

https://servicos.semobjp.pb.gov.br/linhas-de-onibus/

Dados esperados:

- código da linha;
- nome da linha;
- link de itinerário;
- link de horário.

## Página de itinerário

Formato esperado:

/linhas-de-onibus/{codigo}/itinerario/

Dados extraídos:

- sentido ida;
- sentido volta;
- lista textual de ruas;
- variantes quando existirem.

## Endpoint GeoJSON

Formato esperado:

/linhas-de-onibus/{codigo}/itinerario/geojson

Uso:

- obter traçado oficial usado pelo mapa da própria página;
- separar ida e volta quando a propriedade ITINERARIO estiver disponível;
- exportar para GeoJSON geral.

## Página de horário

Formato esperado:

/linhas-de-onibus/{codigo}/horario/

Dados extraídos:

- dia útil;
- sábado;
- domingo/feriado;
- horários de saída;
- quantidade de viagens.
