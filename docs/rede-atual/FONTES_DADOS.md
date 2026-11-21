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

## Verificação da primeira implementação — 21/11/2026

O coletor implementado em `apps/collector` percorreu o catálogo paginado e encontrou 85 códigos de linha nesta consulta. Foram coletados para validação os dados das linhas 0002 e 0003, sem assumir que o restante do catálogo foi baixado.

O mapa da SEMOB usa Leaflet, tiles OpenStreetMap e uma requisição ao endpoint GeoJSON. Para a linha 0002, a resposta contém duas features LineString, identificadas por `ITINERARIO` como IDA e VOLTA. Os atributos incluem `CODIGO_LIN`, `LINHA`, `EMPRESA`, `TIPO`, `EXTENSAO`, `ROUTE_ID` e `ATUALIZACA`. Nesta resposta, a atualização declarada é de 02/08/2024; por isso o coletor preserva separadamente a data da consulta e a data publicada pela fonte. A unidade de `EXTENSAO` não é reinterpretada pelo coletor.

Itinerários textuais podem estar divididos em abas de variantes. O coletor mantém variante, sentido e ordem das ruas. Os horários são agrupados pelos dias efetivamente publicados; um dia ausente não é convertido em uma declaração de ausência de serviço.

A consulta histórica disponível no painel tem outra procedência: 296 geometrias associadas a 111 códigos e 3.047 paradas Bus4/EMS, com coleta declarada de 02/11/2026. Esses números descrevem o arquivo importado, não o catálogo oficial atual, e não devem ser combinados por igualdade presumida de códigos.
