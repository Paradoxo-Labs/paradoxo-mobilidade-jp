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

## Consulta local disponível

Execute `bash scripts/run-dashboard.sh` e abra `http://127.0.0.1:8000`. A aba Rede atual permite alternar entre a referência histórica Bus4/EMS (111 códigos, 296 traçados/variantes e 3.047 paradas) e a base coletada da SEMOB, com busca, seleção de sentido e detalhes disponíveis.

A aba Coletor SEMOB executa a coleta paginada de linhas, itinerários, horários e GeoJSON. Dados de execução ficam fora do Git e preservam as datas de coleta e atualização declarada pela fonte. Instruções completas: [coletor e servidor](../../apps/collector/README.md).

## Fonte oficial de coleta

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
