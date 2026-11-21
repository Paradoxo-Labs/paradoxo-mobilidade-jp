# Paradoxo Mobilidade JP

Uma iniciativa da Paradoxo Labs, desenvolvida por Jailson Silva, para inteligência, dados e visualização da mobilidade urbana de João Pessoa/PB.

## Visão

O Paradoxo Mobilidade JP nasce como uma iniciativa técnica e cívica para transformar dados públicos de mobilidade urbana em informação estruturada, mapas, análises e propostas.

O projeto possui dois eixos complementares:

1. Rede atual observada

Coleta, organização e visualização dos dados reais disponíveis publicamente sobre linhas, horários, itinerários e geometrias do transporte coletivo de João Pessoa.

Este eixo mantém o projeto sincronizado com a realidade operacional atual.

2. Proposta de rede BRS/BHLS

Estudo conceitual inicial de reorganização da rede de transporte coletivo de João Pessoa com base em corredores BRS/BHLS, terminais, estações, miniestações, alimentadoras, linhas interterminais, metropolitanas e especiais.

Este eixo ainda não possui linhas definitivas. Os códigos, traçados e agrupamentos propostos são hipóteses iniciais de trabalho e precisam ser refinados a partir dos dados reais, validação territorial, análise de demanda, estimativa de frota, frequências, mapas e fases de implantação.

## Objetivo

Construir uma base técnica para:

- entender a rede atual;
- coletar dados públicos de forma reprodutível;
- visualizar itinerários e horários;
- comparar a rede atual com propostas futuras;
- apoiar diagnósticos urbanos;
- desenvolver uma proposta BRS/BHLS para João Pessoa;
- evoluir futuramente para plataforma web com API, banco geográfico e dashboards.

## Status

Projeto em fase inicial.

A proposta conta também com um [estudo complementar de rede integrada, revisão de 21/11/2026](docs/proposta-brs-bhls/INTEGRACAO_REDE_INTEGRADA.md), com 23 linhas propostas, 39 traçados de referência e mapa interativo offline. O estudo amplia o material disponível para análise; a codificação e os traçados ainda precisam ser conciliados com o conceito inicial.

A estrutura base do repositório já está criada e preparada para:

- coletor local em Python/Streamlit;
- futura API Laravel;
- futuro frontend Next.js;
- Docker;
- dados geográficos;
- documentação para humanos e agentes de IA;
- proposta conceitual BRS/BHLS.

## Aviso importante

Este projeto é uma iniciativa independente da Paradoxo Labs.

A proposta BRS/BHLS aqui documentada é um estudo conceitual em refinamento. Ela não representa decisão oficial da SEMOB-JP, Prefeitura Municipal de João Pessoa ou qualquer órgão público.

As linhas propostas ainda não devem ser interpretadas como desenho final de rede. São sugestões iniciais para orientar estudos posteriores.

## Estrutura

apps/collector  - Coletor atual em Python/Streamlit
apps/api        - Futuro backend Laravel
apps/web        - Futuro frontend Next.js
docker/         - Infraestrutura Docker
data/           - Dados locais coletados/processados
exports/        - Arquivos exportados
docs/           - Documentação técnica e conceitual
ai/             - Contextos, agentes e prompts para IA/LLMs
scripts/        - Scripts auxiliares

## Repositórios

GitHub público:
https://github.com/Paradoxo-Labs/paradoxo-mobilidade-jp

GitLab técnico:
https://gitlab.com/paradoxo-labs/products/paradoxo-mobilidade-jp
