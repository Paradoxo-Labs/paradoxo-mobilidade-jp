# Dados locais

`raw/semob/<execucao>/` recebe as respostas originais da SEMOB e o manifesto de coleta. `processed/semob/latest.json` contém a base consultada pelo atlas local. Essas pastas de execução são ignoradas pelo Git.

Use `bash scripts/collect-all.sh --line 0002` para iniciar uma coleta, ou a página Coletor SEMOB do painel. Sem `--line`, o coletor consulta todo o catálogo. Linhas não solicitadas mantêm seus dados anteriores.

A referência histórica e o mapa da proposta permanecem no conjunto documental versionado em `docs/proposta-brs-bhls/estudos/rede-integrada-2026-11-21`. As duas fontes são identificadas separadamente na interface.
