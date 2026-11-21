# Estado em 21/11/2026

Primeira versão local implementada. `apps/collector/collector.py` coleta o serviço SEMOB; `server.py` atende em loopback; `apps/web` contém a interface estática com mapa D3 da rede observada e iframe do mapa original da proposta. Execução: `bash scripts/run-dashboard.sh`.

Não há dependências de runtime externas ao Python 3.10+ e aos arquivos já versionados. Linux/Ubuntu/WSL são os ambientes previstos. A escolha evita depender de Streamlit nesta primeira entrega; Laravel, Next.js, PostGIS e Docker permanecem futuros.

Referência Bus4/EMS: 111 códigos, 296 traçados/variantes, 3.047 paradas; coleta declarada de 02/11/2026. Sem vínculo linha–parada. Estudo proposto: 23 linhas e 39 traçados, revisão de 21/11/2026. Não fundir esses dados com a coleta SEMOB sem conciliação explícita.

Coletas oficiais locais ficam em `data/raw/semob` e `data/processed/semob`, ignoradas pelo Git. As linhas 0002 e 0003 foram coletadas para validação; novas instalações não incluem essas respostas. Ver `apps/collector/README.md` e `ai/tasks/NEXT_STEPS.md`.
