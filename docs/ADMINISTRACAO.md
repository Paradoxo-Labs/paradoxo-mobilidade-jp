# Administração local — primeira versão

Painel em [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin). O atlas de consulta permanece em `/`, com rede atual e proposta publicada. O coletor foi movido para a área autenticada.

## Primeiro acesso

Inicie o Docker:

```sh
docker compose up -d --build --wait
docker compose exec atlas python3 apps/admin/manage.py setup-token
```

Copie o código exibido para o formulário de primeiro acesso em `/admin`. Escolha seu usuário e uma senha de 12 a 200 caracteres. O código é de uso único; não existe senha padrão. O painel não foi previamente cadastrado com uma conta de teste.

Para recuperar uma conta existente, use um terminal interativo:

```sh
docker compose exec atlas python3 apps/admin/manage.py reset-password
```

A senha é solicitada sem eco no terminal; todas as sessões anteriores são encerradas. Não passe senhas na linha de comando, em arquivos versionados ou em URLs.

## Fluxo de trabalho

1. **Rede proposta:** abra uma linha existente, duplique-a ou crie em branco. Também é possível criar uma proposta a partir das geometrias coletadas da SEMOB em **Rede atual / coletor**.
2. **Cadastro:** defina código, classe, organização, nome, origem/destino e observações. Um código duplicado não pode ser publicado. Cada linha tem identificador interno independente do código.
3. **Desenho novo:** escolha referências no mapa, arraste os marcadores ou reordene a lista. Calcule o percurso e aplique a prévia. O cálculo utiliza ruas dirigidas da malha local, não retas entre os pontos.
4. **Editar trecho:** selecione A e B na geometria, no sentido da linha; arraste a referência central vermelha ou adicione passagens. O servidor recalcula apenas o intervalo e mantém o restante da geometria. Confira vias, extensão e encaixes antes de aplicar. Uma falha mantém a geometria anterior.
5. **Ida e volta:** são independentes. A função de criar a volta com referências da ida faz novo cálculo dirigido, sem inverter simplesmente a geometria. Sentidos e variantes adicionais podem ter nomes próprios.
6. **Preservação:** a I-131 inicia com os trechos observados da 108/110 bloqueados. Também é possível preservar uma seleção. Ao duplicar uma linha, suas regras viárias de referência são herdadas mesmo com outro código. Para alterá-la, desbloqueie-a explicitamente. O servidor rejeita cálculos que removam um trecho bloqueado.
7. **Comparar:** mapas sincronizados mostram rascunho/prévia e publicação ativa, versões salvas ou uma linha SEMOB, com extensões por sentido. Em uma linha nova, a referência publicada fica vazia.
8. **Salvar:** o rascunho é salvo automaticamente e possui cópia local de recuperação no navegador. **Salvar versão** cria um registro imutável da linha e de seus sentidos, com descrição opcional. Uma versão incompleta pode ser salva, mas não publicada.
9. **Publicar:** revise versão, sentidos, impedimentos e pendências. Confirme que se trata de estudo conceitual. A publicação troca a composição da rede em uma transação, mantendo as demais linhas e o histórico anterior. Rascunhos ou versões salvas não mudam o atlas.
10. **Histórico:** uma versão anterior da linha pode ser recuperada no rascunho. Uma publicação anterior da rede pode ser restaurada como nova publicação, sem apagar o histórico.

Duas abas não sobrescrevem silenciosamente o mesmo rascunho: revisões divergentes retornam conflito e preservam a cópia local. Uma revisão de publicação desatualizada também é rejeitada. A prévia não aplicada é transitória; o conteúdo protegido automaticamente é o rascunho aplicado. Recálculos em andamento são descartados se o editor mudar de contexto.

## Dados e execução

Esta versão aproveita Python e Leaflet existentes e usa SQLite transacional, adequado ao administrador único no Docker local. Não introduz React, FastAPI, Redis ou PostgreSQL nesta etapa. Os módulos administrativos têm API própria, permitindo uma migração posterior sem acoplar a edição aos arquivos importados.

- `data/admin/admin.sqlite3`: conta, sessões, rascunhos, versões, publicações, auditoria e histórico dos trabalhos. Diretório fora do Git; não o apague para atualizar a aplicação.
- `data/admin/setup-token`: código de primeiro acesso, removido após o cadastro.
- `data/raw/` e `data/processed/`: coletas e malha viária, com o fluxo de procedência anterior preservado.
- `docs/proposta-brs-bhls/revisao-atual`: semente inicial do banco. Recriar o container não reimporta nem sobrescreve o banco. Executar o gerador atualiza esses arquivos versionados, não uma publicação já administrada no banco.

O roteador carrega em memória a malha local de `data/raw/cartografia/osm-revisao-rotas.json` e a coleta `data/processed/semob/latest.json`. O primeiro carregamento pode levar alguns instantes; o painel informa seu estado. Os dados já disponíveis neste ambiente são reutilizados. Após substituir a malha OSM no disco, reinicie o serviço para carregá-la novamente. Para preparar outra instalação, obtenha as entradas descritas em [apps/planner/README.md](../apps/planner/README.md) e faça a coleta SEMOB pelo painel. Sem malha/coleta, é possível cadastrar e salvar rascunhos, mas o cálculo de ruas fica indisponível com mensagem explícita.

O contexto viário detalhado do editor também é servido da malha local. Fundos online são opcionais; o fundo local preserva o mapa em falhas de internet. A imagem da aplicação continua somente leitura; o banco e as coletas persistem no volume `./data`.

O coletor percorre o catálogo completo. Execuções iniciadas pelo painel têm progresso e estado persistidos; se o processo reiniciar, um trabalho em andamento fica identificado como interrompido, sem fingir continuidade. Uma coleta não recalcula nem publica a proposta. O controle de ativação de snapshots observados e cancelamento/retomada fina de trabalhos ficam para uma evolução posterior; a rede observada usa o último snapshot processado pelo coletor existente.

## Backup e restauração

Crie um backup consistente do banco, incluindo transações confirmadas no WAL:

```sh
docker compose exec atlas python3 apps/admin/manage.py backup --output /app/data/admin/backups/admin-2026-11-22.sqlite3
```

Escolha um nome novo a cada backup. Não copie apenas `admin.sqlite3` enquanto o serviço estiver rodando. Para restaurar um backup, pare o serviço, preserve o diretório administrativo atual para recuperação, substitua o banco pelo backup e remova apenas os arquivos auxiliares `admin.sqlite3-wal`/`admin.sqlite3-shm` da instância parada antes de iniciá-la novamente. Preserve também os dados de coleta e a malha para reproduzir os cálculos. Backups contêm hashes de senha e sessões: mantenha-os privados e invalide sessões usando `reset-password` após uma recuperação de conta.

## Acesso e limites

Um administrador, sem cadastro público. Senhas com scrypt e sal; cookies HttpOnly/SameSite=Strict, expiração de oito horas, sessões persistidas e revogação no logout; token CSRF, validação de Host/Origin, limite de tentativas e API de escrita autenticada. Endereços administrativos ficam vinculados a `127.0.0.1`/`localhost` na porta publicada. Esta configuração é para Docker local, sem publicação na internet ou configuração de proxy remoto.

A validação bloqueia cadastro incompleto, código duplicado, sentidos obrigatórios ausentes, coordenadas inválidas, saltos superiores a 1 km entre vértices, alterações em trechos preservados e revisões desatualizadas. Não comprova operação de ônibus: relações OSM de conversão, gabarito, sinalização, acessos de terminais, frota e frequência continuam pendentes. Não há edição simultânea colaborativa, múltiplos cenários, desenho de novas vias, dimensionamento automático ou exportação GTFS nesta primeira versão.

Após uma edição, os percentuais antigos de aderência observada são removidos para não apresentar indicadores desatualizados. As vias calculadas da alternativa aparecem na prévia; o itinerário textual da linha pode ser revisado no cadastro. Se a I-332 for alterada, os comparativos históricos congelados deixam de ser apresentados como se representassem o novo traçado.

## Verificações

```sh
docker compose exec -T atlas python3 -m unittest discover -s apps/admin/tests -v
docker compose exec -T atlas python3 -m unittest discover -s apps/collector/tests -v
docker compose exec -T atlas python3 -m unittest discover -s apps/planner/tests -v
```

Testes de publicação e de primeiro acesso devem usar um banco temporário. Não crie contas de QA, publique linhas fictícias ou restaure versões para testar no banco principal do usuário.
