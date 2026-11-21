# Próximos passos

## Entrega local disponível em 21/11/2026

Coletor SEMOB, página da rede atual e mapa da proposta estão implementados. Rodar com `bash scripts/run-dashboard.sh`. Ver `apps/collector/README.md`.

## Rede atual

1. Revisar a coleta completa de 85 linhas / 149 traçados e as seis linhas cujo endpoint GeoJSON retornou vazio. Atualizar periodicamente a base oficial.
2. Auditar variantes, dias e observações dos horários contra as páginas originais.
3. Comparar geometrias da SEMOB com a referência Bus4/EMS, sem assumir equivalência de códigos.
4. Incorporar vínculo linha–parada e ordem de atendimento quando houver fonte confiável.
5. Evoluir exportações para Excel e análises de cobertura.

## Proposta BRS/BHLS

1. Conciliar classes e códigos do conceito inicial com o estudo de 23 linhas incorporado.
2. Revisar divergências registradas em `docs/proposta-brs-bhls/INTEGRACAO_REDE_INTEGRADA.md`.
3. Criar matriz linha atual → nova função e refazer auditoria de cobertura.
4. Acrescentar comparação das duas redes ao atlas local.
5. Refinar linhas, paradas, frequências, frota e fases de implantação.

## Plataforma

1. Validar o uso local antes de migrar para API Laravel, PostgreSQL/PostGIS e frontend Next.js.
2. Evoluir o Docker local já disponível e implementar CI/CD e deploy quando essa etapa for iniciada.
