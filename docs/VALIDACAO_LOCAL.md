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
