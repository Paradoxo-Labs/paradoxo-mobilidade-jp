# Administração local — rede, infraestrutura e publicação

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
4. **Editar trecho:** no modo **Arrastar rota**, aproxime o mapa, segure a própria linha e solte sobre outra rua. O marcador encaixa na malha disponível; soltar fora das ruas cancela a ação. O intervalo é escolhido automaticamente em torno da ocorrência arrastada. Confira a prévia e aplique. A seleção manual A/B permanece nas ferramentas avançadas.
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

O contexto viário detalhado do editor também é servido da malha local. O OpenStreetMap é o fundo padrão no painel e no atlas. A base local continua selecionável e é ativada automaticamente se o fundo online falhar. A imagem da aplicação continua somente leitura; o banco e as coletas persistem no volume `./data`.

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

## Estações e terminais

A tela **Estações e terminais** mantém um cadastro compartilhado, com tipos terminal, estação, parada ou referência territorial. Informe nome, observações, posição no terreno, conexão viária e acessos por chave de sentido (`ida`, `volta`, `circuito` ou chave da variante). Clique no mapa ou arraste o marcador correspondente; o terreno e o ponto usado no cálculo podem ocupar locais diferentes. As coordenadas do terreno e da conexão também podem ser digitadas.

**Salvar referência em edição** persiste o cadastro administrativo, mas não altera o atlas. A publicação conjunta inclui o cadastro inteiro em edição. Há controle de revisão para impedir que duas abas sobrescrevam esse cadastro. Arquivar uma referência mantém seu registro; a publicação é bloqueada se a rede final ainda a usar como origem/destino, estação ou referência vinculada.

No editor, **Estações neste sentido** associa estações/terminais ao percurso e permite ordenar os vínculos. Ao vincular, o acesso específico do sentido — ou a conexão viária, quando não houver acesso — vira uma referência permanente. A ordem de atendimento e a lista de referências de cálculo podem ser ajustadas independentemente. Mover o terminal no cadastro não recalcula a rota: confira seus vínculos e recalcule os percursos afetados. A revisão alerta para acessos a mais de 150 m do percurso e referências permanentes a mais de 80 m; esses alertas não substituem uma validação operacional.

## Referências permanentes e seleção

Cada sentido mantém até 100 referências com identificador, nome, posição e vínculo opcional com uma estação. Elas são salvas no rascunho e nas versões. Podem ser renomeadas, arrastadas no mapa e reordenadas pela lista ou pelas setas. Mover uma referência altera sua posição de controle; a geometria só muda depois de calcular e aplicar uma prévia. Arrastar uma referência vinculada a uma estação a transforma em passagem independente, sem mover a estação compartilhada.

- **Guardar A, passagens e B:** acrescenta as referências do intervalo selecionado. Em circuitos, mantenha passagens intermediárias para distinguir o percurso de uma simples origem/destino coincidente.
- **Importar referências do estudo:** substitui a lista de controles pelas referências de roteamento do percurso importado, sem mudar a geometria.
- **Recalcular pelas referências:** recalcula o sentido inteiro na ordem da lista e apresenta prévia; trechos preservados continuam protegidos.
- **Mostrar seleção e ↔:** enquadra no mapa todo o intervalo entre A e B.
- **Reconectar A → B pelas ruas:** calcula o caminho sem passagens intermediárias, útil para remover uma ponta que faz ida e retorno. Não liga pontos por uma reta.
- **Cortar antes de A / depois de B:** apresenta uma prévia de encurtamento do percurso. Bloqueios preservados e extensão mínima são conferidos no servidor antes de aplicar.

Quando a rota passa mais de uma vez pela mesma coordenada, a seleção oferece os índices das passagens. Os campos **Índice A/B** permitem escolher a ocorrência exata; A deve preceder B na ordem do sentido. Os painéis têm rolagem própria para manter o mapa utilizável em percursos com muitas referências.

## Gerenciamento das linhas

**Arquivar / retirar** mantém rascunhos e versões. Para uma linha publicada, prepara a retirada: ela continua no atlas até ser selecionada na publicação conjunta. **Reativar** cancela essa intenção ou torna uma linha arquivada novamente disponível para edição/publicação. Linhas fora da composição atual podem ser abertas a partir da última versão salva.

**Descartar rascunho** exige confirmação e revisão atual, preservando as versões salvas e a publicação. Alterações ainda sem versão salva são perdidas. Depois de restaurar uma publicação antiga, um rascunho pode apontar para uma base desatualizada: salve o conteúdo que deseja preservar em uma versão, descarte o rascunho e abra a linha novamente antes de recuperar a versão desejada no novo rascunho.

## Publicação conjunta

1. Salve uma versão de cada linha que deseja incluir.
2. Abra **Publicação conjunta** e selecione os rascunhos, as retiradas preparadas e, se necessário, o cadastro compartilhado de estações em edição.
3. Revise o mapa da composição final, versões, retiradas, referências alteradas e impedimentos. Novas estações e as linhas que as usam devem entrar no mesmo conjunto.
4. Confirme as pendências e a publicação. Todas as alterações entram em uma única transação, incluindo as estações.

A validação considera a composição final: impede códigos duplicados, referências ausentes/arquivadas, versões incompletas, rascunhos sem a versão atual salva e bases desatualizadas. É possível trocar códigos entre duas linhas na mesma publicação, desde que o resultado final não tenha duplicidade. A revisão perde validade se a publicação ativa, um rascunho selecionado, o estado de uma linha selecionada ou o cadastro de estações incluído mudar.

**Publicações → Restaurar** recupera linhas e referências da publicação selecionada em uma nova publicação. Edições pendentes de estações são mantidas; se o cadastro estava sem alterações pendentes, acompanha a restauração. As tabelas novas são criadas automaticamente ao iniciar o serviço, preservando conta, rascunhos, versões e geometrias existentes. Publicações anteriores à migração recebem as referências da semente que já estava fixada no banco.

## Arraste direto da rota

O editor abre no modo **Arrastar rota**, sem exigir índices, referências ou A/B. Aproxime o mapa até aparecerem as ruas de edição (zoom 14 ou maior), segure um trecho da linha e mova-o para a rua desejada. O marcador é projetado no segmento viário real. Soltar fora das ruas, fora do mapa ou pressionar Escape cancela o gesto sem modificar o rascunho. **Navegar** permite arrastar o mapa normalmente.

Ao soltar em uma rua, o servidor escolhe conexões antes e depois do trecho, respeita o sentido das vias e as regras herdadas da linha e calcula uma prévia. **Aplicar alternativa** salva a alteração no rascunho; publicar continua sendo outra operação. O seletor de alcance controla a vizinhança editada, com ajuste automático para deslocamentos maiores. O arraste limita o destino a 2,5 km da origem do gesto; trechos preservados continuam protegidos.

Em uma rua percorrida mais de uma vez pelo circuito, escolha a passagem indicada pela direção e segure a linha novamente. O cálculo usa a posição dessa passagem na sequência do percurso. Um arraste próximo da emenda fim/início pode envolver os dois lados do circuito, mantendo-o fechado, preservando seu ponto inicial e a ordem do restante do percurso. Não se tenta identificar a passagem apenas pela primeira coordenada coincidente.

**Ferramentas avançadas** reúne a seleção A/B, referências permanentes, cortes e preservação de trechos. **Arrastar rota** retorna à interação direta. As vias para o encaixe vêm do grafo local já filtrado por acesso e regras da linha; o servidor revalida a aresta recebida e a distância da soltura, sem aceitar uma referência livre fora da rua. O encaixe usa projeção no segmento, inclusive em ruas longas sem uma interseção próxima.

## Filtros de consulta das linhas

O catálogo administrativo e a página pública da proposta oferecem **Classe**, **Corredor · eixo viário**, **Família da numeração**, **Terminal** e busca textual. Os critérios são combinados por interseção; limpar os filtros recupera a lista completa. No painel, o mesmo filtro alcança linhas publicadas, novos rascunhos e linhas fora da publicação ativa, mantendo suas ações de gerenciamento.

Corredores seguem os eixos documentados no projeto: Centro/Roger/Jaguaribe, Cruz das Armas, Dois de Fevereiro/Rangel, Dom Pedro II, Beira-Rio, Epitácio/Ruy Carneiro, Mandacaru/Tancredo Neves, Via Oeste e BR-230/orbital. A associação é identificada pelas referências e vias registradas no itinerário; não é calculada pelo código da linha nem representa uma nova análise espacial do traçado. Sem evidência registrada, a linha aparece em **Sem corredor identificado**.

Família é a faixa numérica do código: por exemplo, BRS-100 e I-131 pertencem à família 1xx. Terminal usa os vínculos cadastrados de origem/destino, estações do percurso e referências do itinerário, incluindo as referências legadas da Lagoa por sentido. Proximidade física sem vínculo não é usada para inferir atendimento a um terminal. Os filtros são de consulta e não modificam nem publicam a rede.

Testes das regras compartilhadas, usando Node.js em desenvolvimento:

```sh
node --test apps/web/tests/line-filters.test.cjs
```

### Recuperar um emaranhado de retornos

Se o arraste antigo tiver acumulado várias entradas e saídas na mesma área, reconecte o intervalo inteiro: **Ferramentas avançadas → início A antes da primeira entrada → fim B depois da última saída → Reconectar A → B pelas ruas**. Confira a prévia antes de aplicar. Escolher apenas uma das pequenas voltas pode deixar as outras fora do intervalo e mantê-las no percurso. Os campos de índice ajudam a escolher a ocorrência certa em passagens sobrepostas.

O arraste direto agora planeja os dois lados da conexão evitando cruzar o restante preservado da linha ou acrescentar visitas a pontos já percorridos. Quando a primeira combinação não funciona, tenta planejar pelo outro lado. Se não encontrar ligação sem novas revisitas, recusa a prévia e orienta escolher a outra pista ou reconectar um intervalo maior. Retornos já presentes e o fechamento natural de circuitos não são tratados como repetição nova.

Na demonstração isolada da BRS-800/ida, o intervalo 526–845 da revisão copiada caiu de 9,812 km para 1,068 km pela Rodovia Governador Antônio Mariz. O restante da ida e toda a volta ficaram idênticos. Esses índices pertencem àquela cópia; a edição principal não foi aplicada nem publicada automaticamente.

### Prévia do catálogo administrativo

Em **Rede proposta**, o mapa acima da listagem acompanha a busca e todos os filtros. Cada linha usa seu rascunho mais recente, quando houver; caso contrário, usa a versão publicada ou a última versão salva para linhas fora da publicação. Traço contínuo indica publicação, pontilhado indica rascunho e tracejado indica histórico fora da publicação. Linhas sem geometria continuam na listagem e são contabilizadas abaixo do mapa. Clique no traçado para abrir o editor; **Enquadrar linhas** recupera a visão do resultado. A prévia não salva nem publica alterações.
