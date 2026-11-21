# Aplicação local e coletor SEMOB

Requer Python 3.10+ em Linux/Ubuntu/WSL. Não é necessário instalar bibliotecas Python ou Node.js para executar a aplicação. O bloqueio de coletas concorrentes usa `fcntl` do sistema operacional.

Na raiz do repositório:

```sh
bash scripts/setup.sh
bash scripts/run-dashboard.sh
```

Abra [http://127.0.0.1:8000](http://127.0.0.1:8000). Para outra porta: `bash scripts/run-dashboard.sh --port 8080`. O servidor atende apenas em loopback. Encerre com Ctrl+C. Uma coleta em andamento é interrompida ao encerrar o processo; seu último conjunto publicado permanece preservado.

## Páginas

- **Rede atual:** busca por código, nome e ruas coletadas; mapa vetorial offline com zoom, seleção de linha e sentido, paradas históricas opcionais, itinerários e horários disponíveis.
- **Rede proposta:** mapa original de 23 linhas e 39 traçados incorporado na navegação. Preserva filtros e comparativos do estudo.
- **Coletor SEMOB:** coleta em segundo plano, progresso, erros e downloads JSON, GeoJSON e catálogo CSV.

A primeira abertura usa os 296 itinerários/variantes e 3.047 paradas da referência Bus4/EMS de 02/11/2026. Isso permite consultar o mapa sem rede. Não há vínculo sequencial linha–parada nessa base. Para consultar a SEMOB, faça uma coleta e escolha **Coleta local · SEMOB-JP**. As bases não são misturadas automaticamente.

## Coleta pela linha de comando

```sh
# Uma linha, preservando as demais já coletadas
bash scripts/collect-all.sh --line 0002

# Várias linhas ou um lote pequeno para validação
bash scripts/collect-all.sh --line 0002 --line 0101
bash scripts/collect-all.sh --limit 3

# Catálogo completo (pode levar vários minutos)
bash scripts/collect-all.sh
```

O coletor percorre a paginação do catálogo, extrai ruas por sentido/variante, quadros de horários e o endpoint GeoJSON usado pelo mapa oficial. Preserva códigos alfanuméricos e zeros à esquerda. Código numérico curto é preenchido somente quando a versão com quatro dígitos existe no catálogo.

As requisições são sequenciais, com intervalo mínimo de 300 ms, timeout de 25 s e até duas novas tentativas para falhas transitórias. O CLI retorna `0` ao concluir sem pendências, `2` se houve falhas em campos e `1` se não conseguiu concluir a coleta. A interface mostra pendências por linha, sem esconder campos ausentes.

## Armazenamento e integridade

- `data/raw/semob/<execucao>/`: respostas HTML/JSON recebidas e `manifest.json` com URLs, datas e erros.
- `data/processed/semob/latest.json`: conjunto publicado para consulta local, gravado por substituição atômica.
- Cada linha tem `retrieved_at` e `source_updated_at`, separados: publicação pela fonte e consulta local não são a mesma data.
- Coletas parciais atualizam apenas as linhas solicitadas. Linhas totalmente falhas e linhas não solicitadas mantêm os dados anteriores. Campos que falham em uma linha parcialmente atualizada ficam vazios e identificados, sem misturar silenciosamente versões.
- Linhas antigas ausentes do catálogo recém-consultado continuam na base e são sinalizadas na interface.
- Um bloqueio de arquivo impede a coleta simultânea pelo painel e por outro processo CLI na mesma pasta.
- Dados de execução ficam fora do Git. O estudo importado é preservado em seu diretório documental.

É possível isolar dados com `--data-dir /tmp/minha-coleta`, tanto no servidor quanto no coletor.

## Limites desta versão

O mapa da rede observada usa D3 e a cartografia vetorial já disponível no repositório, sem depender de tiles ou CDN. Não é um mapa de ruas detalhado. Leaflet é a tecnologia do mapa da SEMOB, mas não é requisito para consumir seu GeoJSON.

Não há atualização automática, comparação unificada entre redes, dados ao vivo dos veículos, sequência oficial de paradas, frota, demanda ou auditoria operacional. Ausência de horários para um dia não implica ausência de serviço. A atualização declarada no GeoJSON pode ser antiga. A proposta continua conceitual e independente.

## Verificação

```sh
python3 -m unittest discover -s apps/collector/tests -v
```

Os testes usam páginas sintéticas com as estruturas da SEMOB para conferir paginação, variantes, horários, geometrias, preservação dos dados e rotas HTTP sem depender de acesso à internet.

A validação desta entrega incluiu consulta real à SEMOB e testes no navegador. Ver [registro de validação](../../docs/VALIDACAO_LOCAL.md).
