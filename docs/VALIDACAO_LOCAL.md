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
