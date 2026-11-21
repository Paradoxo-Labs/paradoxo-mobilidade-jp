# Contexto Atual

O Paradoxo Mobilidade JP está em fase inicial de estruturação.

O projeto começou a partir da necessidade de construir uma ferramenta local para trabalhar com dados reais das linhas de ônibus de João Pessoa, coletados a partir de fontes públicas da SEMOB-JP.

Durante a evolução do trabalho, o projeto passou a incorporar também uma proposta conceitual maior: uma reorganização da rede de transporte coletivo baseada em corredores BRS/BHLS.

## Dois eixos do projeto

### 1. Rede atual observada

Este eixo responde à pergunta:

Como a rede funciona hoje?

Inclui:

- coleta de linhas atuais;
- coleta de horários;
- coleta de itinerários textuais;
- coleta de GeoJSON oficial;
- exportação para CSV, Excel e GeoJSON;
- visualização em painel local;
- análise da rede existente.

Este eixo é essencial porque impede que a proposta fique desconectada da realidade.

### 2. Proposta de rede BRS/BHLS

Este eixo responde à pergunta:

Como a rede poderia ser reorganizada?

Inclui:

- corredores estruturais BRS/BHLS;
- terminais;
- estações;
- miniestações;
- linhas expressas;
- linhas paradoras;
- linhas alimentadoras;
- linhas interterminais;
- linhas metropolitanas;
- linhas especiais;
- fases de implantação;
- comparação futura com a rede atual.

Importante: as linhas da proposta ainda não estão definidas de forma final. Elas representam uma sugestão inicial de arquitetura da rede e precisam de refinamento.

## Estado atual do repositório

O repositório possui estrutura preparada para:

- coletor Python/Streamlit em apps/collector;
- futura API Laravel em apps/api;
- futuro frontend Next.js em apps/web;
- documentação técnica em docs;
- contextos para IA em ai;
- dados locais em data;
- exportações em exports.

## Próxima etapa técnica

### Estudo complementar incorporado em 21/11/2026

O pacote `mobilidade-jp-projeto-codex.zip` foi incorporado ao eixo da proposta em `docs/proposta-brs-bhls/estudos/rede-integrada-2026-11-21`. Contém 23 linhas propostas, 39 traçados de referência, mapa offline, scripts de geração e referências históricas da rede observada.

O [registro de integração](proposta-brs-bhls/INTEGRACAO_REDE_INTEGRADA.md) reúne inventário, diferenças em relação ao conceito inicial e pendências. O estudo complementar não substitui automaticamente a arquitetura inicial, nem demonstra cobertura integral ou viabilidade operacional. Seus dados históricos não substituem uma nova coleta da SEMOB-JP. O mapa já pode ser consultado, enquanto o coletor, a API e o frontend continuam pendentes.

Mover o coletor local existente para:

apps/collector

Depois estabilizar:

- coleta das linhas da SEMOB;
- coleta de horários;
- coleta de itinerários;
- coleta do GeoJSON oficial;
- exportação Excel;
- exportação GeoJSON geral;
- painel local.
