# Decisões técnicas

## 21/11/2026 — Primeira versão local

- Servidor HTTP e coletor em Python 3.10+ com biblioteca padrão; frontend HTML/CSS/JavaScript. O plano Python/Streamlit foi simplificado para eliminar instalação de dependências nesta entrega local. Laravel, Next.js e PostGIS continuam previstos para outra etapa.
- Mapa observado em D3 com cartografia vetorial já fornecida pelo estudo. Funciona sem tiles ou CDN. Leaflet é usado pelo site da SEMOB, mas seu GeoJSON pode ser consumido independentemente dessa biblioteca.
- Mapa da proposta original preservado e servido em iframe na mesma navegação. Alterações no estudo importado exigem atualização própria dos seus dados e testes.
- Base histórica e coleta oficial separadas. Preservar procedência por linha, data de coleta e atualização declarada pela fonte. Não interpretar horários ausentes como ausência de serviço.
- Respostas brutas por execução, publicação atômica do conjunto processado e bloqueio de coleta concorrente na mesma pasta. Dados de execução fora do Git.
- Servidor restrito a loopback, rotas de arquivos explícitas e início de coleta por JSON na mesma origem. Não é serviço preparado para exposição pública.
