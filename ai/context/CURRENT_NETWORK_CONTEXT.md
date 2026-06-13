# Current Network Context

O eixo de rede atual observada tem como objetivo manter o projeto conectado à realidade operacional do transporte coletivo de João Pessoa.

## Objetivos

- Coletar dados reais da SEMOB-JP.
- Estruturar linhas, horários, itinerários e GeoJSON.
- Permitir análise da rede existente.
- Servir como base de comparação para a proposta BRS/BHLS.

## Dados esperados

- linhas.csv;
- itinerarios.csv;
- horarios.csv;
- geometrias.json;
- semob_jp_export.xlsx;
- semob_jp_geometrias.geojson.

## Decisão técnica

A geometria principal deve vir do endpoint oficial:

/linhas-de-onibus/{codigo}/itinerario/geojson

A geocodificação por rua deve ser fallback.
