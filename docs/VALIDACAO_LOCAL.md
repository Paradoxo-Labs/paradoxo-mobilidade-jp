# Validação da primeira versão local — 21/11/2026

## Verificações automatizadas

Em Python 3.12/Linux, passaram os 14 testes de `python3 -m unittest discover -s apps/collector/tests -v`. Cobrem paginação e códigos alfanuméricos, variantes e ordem das ruas, horários publicados, geometrias, exportações, preservação da coleta anterior em falhas, bloqueio concorrente e rotas HTTP locais.

Também passaram a compilação dos módulos Python, a verificação de sintaxe do JavaScript, `bash -n` dos três scripts, a conferência dos links locais alterados e `git diff --check`.

## Consulta à fonte real

O coletor percorreu a listagem paginada da SEMOB e identificou 85 códigos. Foram baixados itinerários textuais, horários e GeoJSON das linhas 0002 e 0003, sem pendências nessas duas linhas. A coleta da 0002 também foi executada com sucesso pelo formulário do painel, com acompanhamento de progresso e atualização da base consultável.

Essas execuções validam a integração com as páginas consultadas; não equivalem a testar todas as linhas, variantes ou dias do catálogo. As respostas originais e os manifestos ficaram em `data/raw/semob`, e a base consultável em `data/processed/semob/latest.json`, fora do Git.

## Interface no navegador

Verificada em Chromium com larguras de 320, 390 e 1440 pixels:

- Navegação entre rede atual, proposta e coletor, sem transbordamento horizontal das páginas ou links da navegação.
- Carregamento da referência histórica, busca, seleção de linha, visualização opcional das 3.047 paradas e controles de zoom.
- Troca para a fonte SEMOB, seleção de sentido, exibição de ruas e horários e separação das datas da coleta e da fonte.
- Preservação da data de calendário publicada pela fonte: `2024-08-02T00:00:00.000Z` aparece como `02/08/2024`, sem deslocamento para o dia anterior.
- Mapa original da proposta com 23 linhas e filtro individual, incluindo I-332.
- Exportação GeoJSON pelo servidor, coleta real pelo formulário e estados de base ausente, busca sem resultados e hash desconhecido.
- Nenhuma exceção JavaScript durante esses fluxos. As requisições externas do navegador foram bloqueadas para conferir a independência de CDN/tiles; a coleta é feita pelo servidor Python.

Playwright e as bibliotecas de apoio do navegador foram usados somente em diretório temporário para esta validação. Não fazem parte das dependências necessárias para rodar o projeto.

## Limites verificados

O mapa observado é vetorial, sem mapa detalhado de ruas. A referência histórica não tem vínculo sequencial entre linha e parada. Horários ausentes não comprovam ausência de serviço. O catálogo completo da SEMOB ainda precisa de coleta e revisão; a proposta ainda exige conciliação e validação operacional. Não houve publicação externa.

## Docker — 21/11/2026

- Validado `docker compose config --quiet`; imagem construída e serviço iniciado com `docker compose up -d --build --wait` no Docker Desktop com integração WSL.
- Serviço `atlas` saudável e publicado em `127.0.0.1:8000`. Página principal, mapa da proposta, status, bases histórica/SEMOB e exportação GeoJSON responderam HTTP 200 pelo endereço do host.
- Passaram os 15 testes dentro do container, incluindo teste de Host/Origin com porta pública diferente da interna.
- Executada coleta real da linha 0002 dentro do container, sem pendências. O catálogo consultado contém 85 códigos; a linha 0003 previamente coletada foi preservada.
- O conjunto processado atualizado e as respostas brutas apareceram no `data/` do host. A recriação do serviço preservou as coletas anteriores.
- Confirmados UID 1000, pasta de dados gravável e diretório da aplicação não gravável. O container permanece rodando; execução e encerramento estão documentados em [docker/README.md](../docker/README.md).

## Redesign e coleta integral — 21/11/2026

- Coleta de todas as 85 linhas do catálogo executada no Docker: 149 features de traçado, itinerários e horários recebidos. Seis endpoints GeoJSON retornaram vazio: 0116, 0120, 0604, 9901, I015 e T003. Essas pendências são de disponibilidade da geometria; a coleta percorreu todo o catálogo e preservou os demais campos.
- Passaram 16 testes no container, incluindo coleta integral por padrão, API da proposta com 23 serviços/39 geometrias e configuração dos quatro fundos cartográficos.
- Teste no Chromium com larguras de 320, 390 e 1440 pixels: identidade/logo/fontes locais, ausência de iframe, seleção de classes e sentidos, referências do percurso, comparação da I-332, troca de base e fallback local em falhas de tiles.
- Confirmados abertura pela fonte SEMOB, 85 linhas no painel, consulta de horários e aviso de geometria ausente, sem exceções JavaScript. O corpo enviado pelo formulário foi verificado como `{"codes":[]}`, sem iniciar uma segunda coleta integral para esse teste de contrato.
- Na verificação final do fallback, todas as requisições externas foram explicitamente interceptadas pelo teste. Os testes anteriores de troca de fundo chegaram a carregar tiles; não foram usados como comprovação de funcionamento offline.
- Arquivos do estudo original foram preservados. Provedores, identidade e licenças estão registrados em [INTERFACE_E_MAPAS.md](INTERFACE_E_MAPAS.md).

## Traçados por padrões observados — 21/11/2026

- Gerados 39 sentidos/circuitos para os mesmos 23 serviços, por grafo dirigido de vias públicas, preferência de concentração SEMOB e bloqueio de circulação interna da UFPB. A revisão ativa é versionada separadamente do pacote original.
- Testes de dados verificam a posição da Estação Cidade Universitária, a exclusão do interior do campus (com exceções explícitas para vias públicas de contorno), o deslocamento de Oitizeiro e a cópia exata dos trechos da 0301 na Lagoa/TIV em todos os 14 sentidos radiais.
- Passaram 8 testes do planejador, além dos 16 testes da aplicação/coletor, dentro do Docker. Incluem preservação dos serviços/sentidos, extensões, referências, comparativos, sentido dirigido e preferência de ruas observadas.
- No Chromium: API servindo a revisão correta, 39 traçados, marcadores de Cidade Universitária/Lagoa/Oitizeiro, sequência de vias por sentido, opção Circuito, comparação atualizada e telas de 320/390/1440 pixels, sem exceções JavaScript. Tiles externos bloqueados durante essa verificação.
- Auditoria antes/depois pelo mesmo método: 69,6% → 83,0% da extensão em ruas com referência na rede observada, ponderada por extensão. Aumento em 35 sentidos; quatro não melhoraram esse indicador. Isso não mede demanda nem prova viabilidade de operação.
- Entradas e saídas internas dos futuros terminais, restrições de conversão e gabarito de ônibus continuam pendentes. As referências de Oitizeiro adotam a área junto ao viaduto indicada pelo usuário, sem tratar o ponto aproximado como plataforma aprovada.
- Fontes, método, tabela por serviço e encaixes de referência estão em [revisao-atual/README.md](proposta-brs-bhls/revisao-atual/README.md).

## Revisão de corredores e cobertura — 21/11/2026

Esta revisão substitui os traçados e indicadores da etapa anterior na proposta ativa.

- Preservados 23 serviços e 39 geometrias. M-961 restaurada integralmente a partir do estudo original; I-332 sem o percurso interno do Parque do Sol, assumido pela L-751.
- Lagoa referenciada no Terminal de Passageiros; Cristo no terminal atual das 204/208; Oitizeiro no ponto do mercado enviado pelo usuário, distinguindo-o da conexão viária aproximada. A entrada no lote adjacente ainda depende da planta.
- T-410 contínua pela Beira-Rio entre as referências do corredor; T-610/TRV-321 sem BR-230; BRS-800 com BR-230 após Cidade Universitária e sem ruas residenciais do Castelo Branco. R-241/242 com Colibris e José Américo; L-251 ampliada até IFPB/Jaguaribe, com referências das 203/204/208. A antiga 201 está ausente das bases locais.
- Passaram **11 testes do planejador e 16 testes do coletor/API dentro do Docker**. Incluem geometria exata da M-961, terminais, preservação dos serviços, continuidade da Beira-Rio, exclusão de rodovia nas linhas indicadas, cobertura local e sentido dirigido. Os hashes dos dados e das regras conferem com a auditoria.
- Chromium: 12 serviços alterados selecionados e cada sentido/circuito exibido individualmente; comparação do Parque do Sol identificada como transferência à L-751; marcadores dos terminais; navegação com a rede SEMOB de 85 linhas e coletor integral. Telas de 320, 390 e 1440 px sem overflow e sem exceções JavaScript. Requisições externas de tiles explicitamente bloqueadas; fallback cartográfico local confirmado.
- `docker compose up -d --build --wait` concluiu com o serviço `atlas` saudável em `127.0.0.1:8000`. Capturas de conferência local: `/tmp/mobilidade-jp-beira-rio.png` e `/tmp/mobilidade-jp-parque-do-sol.png` (temporárias, fora do Git).
- O estudo original permaneceu intocado. A revisão é conceitual; os testes não substituem validação de conversões, gabarito, plataformas e operação. Não houve publicação em hospedagem externa.

## Alimentadora oeste I-131 — conclusão em 22/11/2026

- Adicionada a I-131, em dois sentidos: Terminal Alto do Mateus ↔ Novais ↔ Jardim Planalto ↔ Cidade dos Funcionários ↔ Terminal Oitizeiro. A proposta ativa passa a 24 serviços e 41 traçados; os 39 traçados anteriores foram comparados com o commit de origem e permanecem iguais.
- Preservados literalmente os trechos locais da 108 e da 110, com índices, sentidos e coordenadas registrados na auditoria. Conexões pelo setor da 105 em vias públicas; encaixes entre geometria observada e grafo limitados a 35 m. As extensões completas são 10,38 km na ida e 11,15 km na volta, superiores à estimativa conceitual inicial por manterem a cobertura interna dos bairros.
- Passaram os 12 testes do planejador no host e os 16 testes do coletor/API no Docker. A nova verificação confere a ordem territorial nos dois sentidos, a preservação das geometrias observadas, os encaixes, referências e extensões. Hashes dos dados e dos três módulos de geração conferidos.
- Chromium: totais dinâmicos 24/41, busca por Novais, Jardim Planalto e Cidade dos Funcionários, seleção da I-131, seus dois sentidos, marcador de Alto do Mateus, referências do percurso e itinerário da 110. Larguras 320/390/1440 px sem overflow e sem exceções JavaScript. Tiles externos bloqueados; fundo cartográfico local confirmado. Captura temporária em `/tmp/mobilidade-jp-i131.png`, fora do Git.
- Navegação para a rede SEMOB continua com 85 linhas; coletor continua com a ação de coleta integral. Docker atualizado e saudável em `127.0.0.1:8000`. O estudo importado e os dados observados não foram alterados.
- I-131 é código de estudo. Complementação de Tiradentes, frequência, frota, conversões e acesso interno ao terreno de Oitizeiro permanecem para avaliação; não há operação aprovada ou implantação externa declarada.

## Administração local autenticada — 22/11/2026

- Implementado painel `/admin` com identidade Paradoxo: primeiro acesso por código de uso único, login/logout, coletor autenticado, listagem, criação em branco, duplicação e importação da SEMOB, sentidos/variantes, editor Leaflet, comparação, versões, revisão de publicação e restauração.
- O editor calcula pelas ruas da malha local. O arraste gera uma prévia; aplicar altera somente o rascunho. Intervalos fora da seleção e trechos bloqueados são preservados. A volta pode ser recalculada com referências da ida, sem inverter simplesmente sua geometria. Há proteção de cópia local, salvamento automático, desfazer/refazer e conflitos entre revisões.
- SQLite persistido em `data/admin/`, fora do Git. Senhas com scrypt, sessões HttpOnly/SameSite=Strict com expiração, CSRF, Host/Origin, limite de tentativas e publicação transacional. Referências da semente ficam fixadas no banco; recriar o container não sobrescreve o trabalho administrativo.
- Passaram **40 testes no Docker**: 11 de administração, 17 do coletor/API e 12 do planejador. Cobrem autenticação/CSRF, persistência/reinício, conflito entre abas, bloqueio de geometria inválida ou incompleta, preservação de trechos, direção de ruas, publicação/rollback, revisão desatualizada, duplicação com regras herdadas e referências globais fixadas.
- Chromium em uma instância temporária na porta 8001, com banco separado e coletas/malha somente leitura: primeiro cadastro e login, criação em branco, cálculo real dos dois sentidos, arraste de referência e prévia sem mutação antecipada, aplicação, salvamento e reabertura, comparação com publicação e SEMOB, versão, confirmação das pendências, publicação e restauração. A rede mudou de 24 para 25 serviços apenas no banco de QA e voltou a 24 após restauração. A instância temporária foi removida ao terminar.
- Testada navegação em 1440/1024/390/320 px, incluindo editor, comparação, salvamento, revisão, cadastro e histórico. Requisições externas bloqueadas durante os testes; mapa e contexto viário locais utilizados. Sem exceções JavaScript na rodada final. Corrigida resposta assíncrona de comparação que podia reabrir uma tela após o usuário sair dela.
- Instância principal saudável no Docker. Conferência somente de leitura: 24 serviços/41 traçados e geometrias originais preservados, versão da publicação identificada no atlas, coletor retirado da navegação pública e primeiro acesso disponível. Não foi cadastrada conta de QA no banco principal. Dados brutos, estudo original e semente versionada permanecem intocados.
- Capturas temporárias: `/tmp/mobilidade-admin-editor.png`, `/tmp/mobilidade-admin-publicacao.png` e `/tmp/mobilidade-admin-primeiro-acesso.png`, fora do Git. Operação, primeiro acesso e backup em [ADMINISTRACAO.md](ADMINISTRACAO.md).
- Escopo local de administrador único. Publicação pelo painel atualiza o atlas local; não executa Git ou implantação externa. Validação operacional, dimensionamento de frota/frequência, edição colaborativa, múltiplos cenários e ativação manual de snapshots observados continuam fora desta primeira versão.

## Administração: estações, editor e publicação conjunta — 22/11/2026

- Imagem Docker com cadastro de estações/terminais, terreno e conexão viária separados, acessos por sentido e arquivamento de referências. O cadastro em edição permanece separado do atlas até a publicação.
- Referências permanentes com nome e ordem persistidos por sentido; importação das referências do estudo; arraste, seleção por ocorrência/índice, enquadramento de A/B, reconexão direta pelas ruas e corte de extremidades com prévia. Listas longas têm rolagem própria, sem esticar o mapa.
- Arquivamento prepara a retirada de linhas publicadas, preservando versões; reativação e descarte confirmado de rascunhos. Publicação conjunta verifica a composição final e aplica linhas, retiradas e referências em uma única transação. Restauração inclui as referências da publicação.
- No Docker isolado: 22 testes administrativos, 17 do coletor/HTTP e 12 do roteador passaram. Há testes de migração sem reescrever versões/rascunhos, revisão concorrente de estações e publicações, troca de códigos entre linhas, impedimento de códigos duplicados, referências arquivadas em uso, retirada/reativação e cortes protegidos por bloqueios.
- Chromium no container de QA da porta 8003, com banco separado e entradas SEMOB/OSM somente leitura: cadastro com dois acessos, recarga com referências preservadas, reconexão do desvio da L-251, corte com prévia/desfazer, arraste de referência sem mutação da geometria, arquivamento e publicação de duas linhas + uma retirada + uma estação; restauração da composição anterior. Nenhuma dessas publicações foi feita no banco principal.
- Conferidos editor/comparação e telas novas em 1024, 390 e 320 px, incluindo alternância de telas durante redimensionamento sem exceções JavaScript. Um teste com salvamento atrasado confirmou a preservação de novas alterações no formulário e a atualização do mesmo identificador ao salvar novamente. Uma estação publicada no banco de QA apareceu no atlas.
- Antes de atualizar a instância principal, criado backup consistente em `data/admin/backups/admin-pre-infra-2026-11-22.sqlite3`, privado e fora do Git. O registro de continuidade está em `docs/PROGRESSO_ADMIN.md`.
- Serviço principal atualizado e saudável. Comparação de hashes antes/depois confirmou preservação integral da conta existente, dos dois rascunhos, das 25 versões e das duas publicações. `PRAGMA integrity_check` retornou `ok`; apenas as tabelas novas de infraestrutura/gerenciamento foram inicializadas.
- Conferência anônima no navegador após a atualização: publicação 2 com 24 linhas, Estação Cidade Universitária identificada como estação e com rótulo no mapa, login previamente configurado e módulos novos presentes, sem dados de QA. Container temporário e segredo de QA removidos.

## Arraste direto sobre ruas — 22/11/2026

- Interação principal substituída por arraste da própria linha, com captura do ponteiro, marcador projetado nas ruas permitidas e escolha automática do intervalo. A seleção manual e as referências continuam nas ferramentas avançadas.
- 30 testes administrativos, 17 do coletor/HTTP e 12 do roteador passaram. Os novos testes cobrem projeção no meio de ruas longas, mão única, rejeição de terreno vazio/aresta inexistente/via proibida, posição da ocorrência na sequência, emenda de circuito, preservação do ponto inicial, geometria externa ao intervalo e trechos bloqueados.
- Chromium com mouse em container isolado: arraste real da L-251 para uma rua disponível, prévia sem mutação antecipada, aplicação, desfazer e cancelamento ao soltar fora da malha. Conferidos os modos simples/avançado e larguras 1024/390/320 px, sem exceções JavaScript.
- Na rua compartilhada junto ao início/fim da L-251, o navegador ofereceu as passagens 0 e 419. A passagem inicial foi escolhida e arrastada por mouse; o resultado envolveu a emenda do circuito, mantendo o início e o fechamento. Um segundo arraste iniciado em trecho preservado foi recusado sem alterar a geometria.
- Antes da atualização principal, criado backup privado `data/admin/backups/admin-pre-arraste-2026-11-22.sqlite3`, fora do Git. Os testes de edição ocorreram apenas no banco de QA da porta 8003.
- Docker principal atualizado e saudável. Comparação de hashes confirmou preservação integral de conta, rascunhos, versões, publicações e infraestrutura; o JSON público permaneceu idêntico (publicação 2, 24 linhas). Novo módulo de arraste servido pelo painel.

## Filtros por corredor, família numérica e terminal — 22/11/2026

- Regras compartilhadas entre a proposta pública e o catálogo administrativo. Eixo viário é independente da família numérica; terminais usam vínculos cadastrados e referências legadas da Lagoa, sem inferir atendimento por proximidade.
- Oito testes Node.js passaram: independência eixo/família, nomes com acentos, nomes semelhantes que não são eixos, vínculos de terminais, interseção dos critérios, ausência de classificação e consulta sem mutação do cadastro.
- Chromium na imagem Docker isolada, porta 8003: combinações de corredor/família/terminal, linha selecionada liberada ao mudar filtros, reconhecimento da Lagoa, lista e mapa vazios para combinação sem resultados e limpeza de todos os critérios. Verificada família 9xx com Mangabeira retornando apenas M-961 na publicação de referência.
- No painel, conferidos os mesmos filtros em publicadas, novos rascunhos e linhas fora da publicação ativa. Botões de gerenciamento continuam presentes após filtrar; grupos vazios são ocultados e a busca combina com os demais campos. Os exemplos de rascunho/arquivamento foram criados apenas no banco de QA.
- Proposta e administração conferidas em 1024, 390 e 320 px sem rolagem horizontal ou exceções JavaScript. Navegação e opções do mapa se acomodam em linhas adicionais nas telas menores.
- Docker principal atualizado e saudável. Conta, versões, publicações e infraestrutura iguais ao inventário; o JSON público também permaneceu idêntico. A auditoria registrou criação/edição de rascunho pelo usuário após o inventário, preservadas durante a entrega. Nenhuma versão anterior foi restaurada para desfazer essas alterações.
- Conferência anônima da instância principal passou: combinação Cruz das Armas + família 1xx + Oitizeiro mostra BRS-100, limpeza recupera a lista completa e o módulo compartilhado carrega no painel. Container e segredo temporário de QA removidos.

## Recuperação do emaranhado na BRS-800 — 22/11/2026

- Caso identificado na ida da BRS-800: cópia da revisão 15 do rascunho, com 1.055 coordenadas. Na área da captura enviada pelo usuário, o cadastro inicial tinha 1,56 km e nenhum vértice repetido; a edição tinha 8,92 km e 132 repetições. Essa medida da área é diferente da extensão do intervalo completo escolhido para reparo.
- Em cópia isolada no Docker, selecionado o intervalo 526–845 e acionada a reconexão direta: 9,812 km → 1,068 km pela Rodovia Governador Antônio Mariz. Chromium confirmou prefixo/sufixo da ida e geometria completa da volta idênticos, ausência de mutação antes de aplicar e publicação de QA intacta. Nenhuma edição de rota foi aplicada no banco principal.
- Capturas reais antes/seleção/prévia/depois disponíveis na demonstração local da porta 8004, servida por container separado e sem banco administrativo montado. O painel principal permanece na porta 8000.
- Corrigido o cálculo dos dois lados do arraste para evitar nós do restante preservado e da outra conexão, tentar a ordem alternativa e recusar novas revisitas. O parâmetro `avoid_nodes` é opcional: testes conferem a alternativa ao evitar um nó e que uma chamada posterior sem restrição mantém o comportamento original.
- 32 testes administrativos e 12 do roteador passaram, incluindo alternativa sem repetir pontos, rejeição de retorno adicional sem mutação, manutenção dos retornos existentes e exclusão das duplicatas de junção/fechamento da contagem.
- Verificação adicional no Chromium: a página de demonstração alterna as imagens reais; uma chamada real de arraste na malha devolveu alternativa sem revisitas adicionais e sem alterar o rascunho.

## Prévia da listagem administrativa — 22/11/2026

- Chromium com cópia do catálogo e respostas administrativas simuladas, sem login ou escrita no banco principal: mapa e listagem iguais após busca, corredor, família, terminal, resultado vazio e limpeza. Conferido rascunho pontilhado e ausência de erros JavaScript.
- Layouts 1024, 390 e 320 px sem rolagem horizontal. OpenStreetMap permanece padrão, com fundo local quando a fonte online falha.
- 32 testes administrativos passaram. A alteração acrescenta geometrias à resposta autenticada do catálogo, sem modificar a publicação pública.
- Docker principal atualizado e saudável; hashes de conta, rascunhos, versões, publicações, infraestrutura e JSON público permaneceram iguais após a atualização.
