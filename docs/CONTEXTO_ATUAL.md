# Contexto Atual

O Paradoxo Mobilidade JP possui uma primeira versão local funcional, implementada em 21/11/2026.

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

- coletor SEMOB e servidor Python com biblioteca padrão em apps/collector;
- futura API Laravel em apps/api;
- frontend local HTML/CSS/JavaScript com Leaflet em apps/web; Next.js permanece previsto para evolução;
- documentação técnica em docs;
- contextos para IA em ai;
- dados locais em data;
- exportações em exports.

## Próxima etapa técnica

### Estudo complementar incorporado em 21/11/2026

O pacote `mobilidade-jp-projeto-codex.zip` foi incorporado ao eixo da proposta em `docs/proposta-brs-bhls/estudos/rede-integrada-2026-11-21`. Contém 23 linhas propostas, 39 traçados de referência, mapa offline, scripts de geração e referências históricas da rede observada.

O [registro de integração](proposta-brs-bhls/INTEGRACAO_REDE_INTEGRADA.md) reúne inventário, diferenças em relação ao conceito inicial e pendências. O estudo complementar não substitui automaticamente a arquitetura inicial, nem demonstra cobertura integral ou viabilidade operacional. Seus dados históricos não substituem uma nova coleta da SEMOB-JP.

O coletor e o painel estão implementados. Executar `bash scripts/run-dashboard.sh` e abrir `http://127.0.0.1:8000`. Há navegação entre rede atual, proposta e coleta. A rede atual inicia com a referência histórica offline; a coleta oficial fica em base separada e acrescenta itinerários textuais, horários e geometrias da SEMOB.

O coletor percorre a listagem paginada, registra respostas originais, datas e pendências por campo. As exportações disponíveis são JSON completo, GeoJSON e catálogo CSV. Foram coletadas localmente as linhas 0002 e 0003 para validação; esses dados de execução não são versionados e não significam que o catálogo completo tenha sido coletado.

O atlas também possui execução com Docker Compose: `docker compose up -d --build --wait`, com serviço único, verificação de saúde, publicação em localhost e dados persistidos em `./data`. Ver [Docker](../docker/README.md).

Próxima etapa: revisar variantes/pendências da coleta completa e criar a comparação de cobertura entre as duas redes. Exportação Excel, API Laravel, PostGIS e migração do frontend para Next.js continuam pendentes. Detalhes em [apps/collector/README.md](../apps/collector/README.md).

## Atualização da interface e coleta integral

A coleta completa foi executada em 21/11/2026: 85 linhas consultadas, 149 traçados recebidos e seis linhas sem geometria publicada no endpoint. A próxima etapa de dados passa a ser revisar essas lacunas e manter as coletas atualizadas.

A interface agora segue a identidade do site Paradoxo, com logotipo oficial, Syne, Space Mono e cores institucionais. Os dois mapas são nativos em Leaflet; a proposta não usa mais iframe. Fontes de ruas, topografia e satélite foram referenciadas no Atlas de Distritos da Paraíba, preservando fallback vetorial local. Ver [interface e mapas](INTERFACE_E_MAPAS.md).
