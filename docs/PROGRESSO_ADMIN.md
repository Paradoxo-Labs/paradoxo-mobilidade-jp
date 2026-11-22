# Continuação do painel administrativo

Pedido: implementar, nesta ordem, estações e terminais; referências permanentes e melhorias do editor; gerenciamento das linhas; publicação conjunta. Finalizar com commit na develop.

## Progresso

- [x] Cadastro compartilhado de estações/terminais, localização e acessos por sentido; rascunho separado da publicação.
- [x] Referências permanentes por percurso; seleção de sobreposições, recálculo sem desvio e corte de extremidades.
- [x] Arquivamento/restauração de linhas e retirada da publicação por revisão.
- [x] Revisão e publicação atômica de várias linhas, retiradas e estações.
- [x] Testes de migração, conflitos, publicação e navegador em banco isolado.
- [x] Atualizar documentação e reconstruir o Docker.
- [x] Fazer commit na develop.

## Continuidade

O banco de uso real está em `data/admin/admin.sqlite3` e não deve receber contas, linhas ou publicações de teste. Usar banco temporário para testes. Não apagar os dados existentes. A aplicação principal usa a porta 8000.

Se houver interrupção, consultar este arquivo, `git status`, o diff e os testes antes de retomar. O registro de progresso permite continuar a execução, mas não agenda uma retomada automática nem depende de crédito disponível.

## Verificações concluídas

- Imagem Docker construída com o código final.
- 22 testes administrativos, 17 do coletor/HTTP e 12 do roteador passaram no container isolado.
- Chromium: estação com acessos por sentido; referências preservadas após recarregar; reconexão direta do desvio da L-251; corte com prévia e desfazer; arraste de controle sem alterar a geometria; arquivamento; duas linhas + retirada + estação publicadas atomicamente; restauração das estações; telas em 1024/390/320 px.
- Backup transacional da instância principal: `data/admin/backups/admin-pre-infra-2026-11-22.sqlite3` (privado, fora do Git).
- Layout final passou, incluindo navegação/redimensionamento sem exceções JavaScript e preservação de alterações digitadas durante salvamento.
- Docker principal atualizado e saudável. A migração preservou integralmente 1 conta, 2 rascunhos, 25 versões e 2 publicações; integridade SQLite ok.
- Conferência anônima da instância principal passou: publicação 2, 24 linhas, Estação Cidade Universitária no mapa e módulos administrativos carregados, sem dados de QA.
- Implementação concluída. O commit desta entrega contém este registro; consulte `git log -1` para identificar a revisão. Não há implementação pendente deste pedido.

## Como retomar após uma interrupção futura

Abra o projeto e peça: “Continue pelo registro em docs/PROGRESSO_ADMIN.md”. Conferir primeiro a branch, `git status` e os últimos commits, sem sobrescrever mudanças do usuário. Se este pedido já estiver concluído, apresentar o estado atual antes de iniciar uma etapa nova. Este arquivo é um ponto de continuidade, não um agendamento ou uma garantia de execução quando não houver crédito disponível.
