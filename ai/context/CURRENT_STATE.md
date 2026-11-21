# Estado em 21/11/2026

Primeira versão local implementada. `apps/collector/collector.py` coleta o serviço SEMOB; `server.py` atende em loopback; `apps/web` contém a interface com mapas nativos Leaflet da rede observada e da proposta. Execução: `bash scripts/run-dashboard.sh`.

Não há dependências de runtime externas ao Python 3.10+ e aos arquivos já versionados. Linux/Ubuntu/WSL são os ambientes previstos. A escolha evita depender de Streamlit nesta primeira entrega; Laravel, Next.js e PostGIS permanecem futuros.

Docker disponível: `docker compose up -d --build --wait`. O serviço `atlas` usa Python 3.12, dados compartilhados em `./data`, usuário sem privilégios e porta publicada somente em localhost. `APP_PORT`, `LOCAL_UID` e `LOCAL_GID` são configuráveis; ver `docker/README.md`.

Referência Bus4/EMS: 111 códigos, 296 traçados/variantes, 3.047 paradas; coleta declarada de 02/11/2026. Sem vínculo linha–parada. Estudo proposto: 23 linhas e 39 traçados, revisão de 21/11/2026. Não fundir esses dados com a coleta SEMOB sem conciliação explícita.

Coletas oficiais locais ficam em `data/raw/semob` e `data/processed/semob`, ignoradas pelo Git. As linhas 0002 e 0003 foram coletadas para validação; novas instalações não incluem essas respostas. Ver `apps/collector/README.md` e `ai/tasks/NEXT_STEPS.md`.

Atualização: coleta integral das 85 linhas executada em 21/11/2026, com 149 traçados e seis endpoints GeoJSON vazios (0116, 0120, 0604, 9901, I015, T003). O painel sempre solicita o catálogo completo. A base SEMOB é inicial quando disponível.

Frontend refatorado: identidade do site institucional, assets próprios versionados e fontes OFL locais; mapas nativos Leaflet com ruas OSM, topografia/satélite Esri (referência do Atlas de Distritos) e fallback local. A proposta usa catálogo/GeoJSON, com 23 serviços/39 sentidos, filtros, integrações e comparação histórica da I-332. O HTML original fica apenas em `/proposta-original`. Ver `docs/INTERFACE_E_MAPAS.md`.
