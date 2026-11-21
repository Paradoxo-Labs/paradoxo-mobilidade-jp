# Histórico de implementação

## 21/11/2026 — Atlas local e coletor SEMOB

- Implementados parser HTML/GeoJSON, paginação, coleta por linha ou catálogo completo e CLI.
- Preservados respostas originais, procedência e datas por linha; relatórios de falha por campo, gravação atômica e bloqueio contra coletas simultâneas.
- Criado servidor local Python e frontend responsivo com rede observada, mapa original da proposta e coletor na mesma navegação.
- Rede observada com referência histórica offline e fonte SEMOB separada, seleção de linha/sentido, itinerários, horários e exportações JSON/GeoJSON/CSV.
- Coleta real de validação das linhas 0002 e 0003; catálogo consultado com 85 códigos. Respostas ficam fora do Git.
- Scripts de configuração/execução e testes de parsers, preservação de dados, concorrência e rotas HTTP.
