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

## Refinamento: arraste direto da rota

Pedido posterior: segurar e arrastar a própria rota, encaixando apenas em ruas, principalmente em circuitos.

- [x] Seleção automática de trecho por posição na sequência, incluindo a passagem pelo início/fim do circuito.
- [x] Destino projetado em arestas viárias permitidas e validação no servidor.
- [x] Interface simples de arraste, com ferramentas de referências em modo avançado.
- [x] Testes com ruas reais, sobreposições, soltura fora da rua e circuitos no navegador.
- [x] Atualizar Docker, documentação e commit na develop.

Validação do refinamento: 59 testes automatizados e gestos reais no Chromium passaram, incluindo as passagens opostas 0/419 da L-251 junto ao terminal. Fonte protegida é recusada antes do cálculo. Backup anterior à atualização: `data/admin/backups/admin-pre-arraste-2026-11-22.sqlite3`.

Refinamento concluído: serviço principal atualizado e saudável; comparação de hashes confirmou preservação integral de conta, rascunhos, versões, publicações e infraestrutura. A publicação 2 continua com 24 linhas. Recarregar `/admin` para carregar o modo **Arrastar rota**.

## Filtros por eixo, família e terminal

Pedido: filtros por corredor e terminal; usuário confirmou que deseja tanto eixo viário quanto família numérica. Implementados campos independentes no catálogo administrativo e no atlas da proposta, combinados com classe e busca. Regras compartilhadas em `apps/web/line-filters.js`; oito testes de classificação passaram. Validação de navegador concluída na imagem Docker do container `mobilidade-filter-qa`, porta 8003, banco isolado com exemplos de rascunho/arquivamento. Nenhuma publicação de teste foi feita no banco principal.

As combinações, estados vazios, limpeza de filtros, mapa e ações de gerenciamento passaram, incluindo publicadas, novos rascunhos e arquivadas. Telas 1024/390/320 px passaram após ajustar a navegação e os controles do mapa. Entrega concluída: Docker principal atualizado e saudável; commit desta etapa na develop. A conta, versões, publicações e infraestrutura ficaram idênticas ao inventário. Houve criação e edição de um rascunho pelo usuário após o inventário, registradas na auditoria e mantidas; não restaurar o estado anterior. O JSON da proposta publicada permaneceu idêntico.

## Recuperação de emaranhado na BRS-800

Pedido: demonstrar como remover o emaranhado no mapa e preservar a edição atual. Identificado na ida da BRS-800, rascunho `77ea43eb-2304-4b70-b7c7-187e43734357`, revisão 15 no inventário. Cópia isolada em `/tmp/mobilidade-ninho-qa`, com segredo de QA privado. Intervalo 526–845 na cópia: 9,812 km → 1,068 km por reconexão direta; restante da ida e volta devem permanecer intactos. Não aplicar nem publicar essa edição no banco principal automaticamente.

Correção em curso: roteamento do arraste evita nós já usados pelo restante da linha e pelo outro lado da conexão, respeita retornos já existentes e recusa revisitas adicionais. `Network.route` ganhou parâmetro opcional `avoid_nodes`, sem alterar o comportamento padrão. 32 testes administrativos e 12 do roteador passaram. Demonstração no Chromium concluída: 9,812 → 1,068 km; os demais trechos da ida e a volta ficaram idênticos. Capturas reais servidas em `http://127.0.0.1:8004`, pelo container `mobilidade-ninho-demonstracao`, sem acesso ao banco principal. Edição de limpeza aplicada apenas na cópia de QA. Documentação e 32 testes administrativos/12 do roteador conferidos. Entrega: correção do cálculo no Docker principal e commit na develop, sem aplicar nem publicar a limpeza no banco principal. Demonstração verificada em `http://127.0.0.1:8004`; o teste de arraste na malha real retornou alternativa sem novas revisitas e manteve o rascunho da cópia intacto antes de aplicar.
