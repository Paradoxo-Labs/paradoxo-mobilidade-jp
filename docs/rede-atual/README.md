# Rede Atual Observada

Este diretório documenta o eixo do projeto responsável por entender a rede atual de transporte coletivo de João Pessoa.

## Objetivo

Coletar, organizar e visualizar os dados públicos disponíveis sobre:

- linhas;
- itinerários;
- horários;
- geometrias;
- sentidos de viagem;
- exportações para análise.

## Fonte principal

A fonte inicial é o serviço público da SEMOB-JP de linhas de ônibus.

## Decisão técnica importante

A geometria das linhas deve ser obtida preferencialmente pelo endpoint GeoJSON usado pela própria página de itinerário:

/linhas-de-onibus/{codigo}/itinerario/geojson

A geocodificação por nome de rua deve ser apenas fallback, pois pode gerar trajetos imprecisos.

## Relação com a proposta BRS/BHLS

A rede atual observada será usada para:

- entender a cobertura existente;
- evitar perda de capilaridade;
- identificar linhas redundantes;
- comparar cenários;
- alimentar a tabela linha atual para nova função;
- validar a proposta BRS/BHLS.
