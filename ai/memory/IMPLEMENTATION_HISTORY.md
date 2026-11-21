# Histórico de implementação

## 21/11/2026 — Atlas local e coletor SEMOB

- Implementados parser HTML/GeoJSON, paginação, coleta por linha ou catálogo completo e CLI.
- Preservados respostas originais, procedência e datas por linha; relatórios de falha por campo, gravação atômica e bloqueio contra coletas simultâneas.
- Criado servidor local Python e frontend responsivo com rede observada, mapa original da proposta e coletor na mesma navegação.
- Rede observada com referência histórica offline e fonte SEMOB separada, seleção de linha/sentido, itinerários, horários e exportações JSON/GeoJSON/CSV.
- Coleta real de validação das linhas 0002 e 0003; catálogo consultado com 85 códigos. Respostas ficam fora do Git.
- Scripts de configuração/execução e testes de parsers, preservação de dados, concorrência e rotas HTTP.

## 21/11/2026 — Docker do atlas local

- Adicionados Dockerfile Python 3.12, Docker Compose de serviço único `atlas`, exclusões do contexto de build e parâmetros de porta/UID/GID.
- Dados compartilhados com `./data`, usuário sem privilégios, aplicação somente leitura e healthcheck. Servidor aceita bind interno e porta pública configuráveis, preservando a validação de origem.
- Imagem construída e container saudável em `127.0.0.1:8000`. Passaram 15 testes no container, respostas HTTP do host e coleta real da linha 0002 sem pendências, persistida no host.

## 21/11/2026 — Identidade Paradoxo e mapas nativos

- Interface baseada no site institucional: logotipo oficial, cores, fontes Syne/Space Mono e navegação horizontal.
- Mapas Leaflet locais para rede observada e proposta, sem iframe na proposta. Catálogo/GeoJSON preservados; filtros por classe/linha/sentido, integrações, referências, tela cheia e comparação histórica da I-332.
- Fundos OpenStreetMap e Esri referenciados no Atlas de Distritos da Paraíba, com fallback Filipeia/IBGE e configuração em `apps/web/map-sources.json`.
- Painel coleta sempre todo o catálogo e inicia pela base oficial quando disponível. Executada coleta de 85 linhas, 149 traçados e seis lacunas de geometria publicadas pela fonte.
- Passaram 16 testes de backend e verificação de navegador em 320/390/1440 pixels, incluindo contrato da coleta integral e fallback offline.
