# Rede integrada de João Pessoa

Base de transferência da revisão de 21 de novembro de 2026. O catálogo contém 23 linhas propostas e 39 traçados de referência, contando os dois sentidos das linhas bidirecionais e o traçado completo de cada circular.

## Como começar no Codex

Extraia esta pasta na raiz do projeto e peça ao Codex que leia `mobilidade-jp-prompt-codex.md` e este README. A cartografia, a classificação, os terminais e as decisões estão documentados no prompt. Para navegar agora, abra **`mapa.html`** em um navegador moderno. O mapa inclui o D3 e os dados, funciona sem internet e mantém todos os filtros da revisão.

## Arquivos

| Caminho | Função |
| --- | --- |
| `mobilidade-jp-prompt-codex.md` | Especificação e instruções de continuidade. Traz as 23 linhas, todas as sequências por sentido e coordenadas de roteamento. |
| `mapa.html` | Mapa navegável autônomo. |
| `mapa-rede-joao-pessoa-revisada.html` | Fragmento do mapa original com catálogo e geometria simplificada para exibição. |
| `dados/catalogo.json` | Linhas ativas e marcadores com itinerários, notas e waypoints ordenados por sentido. |
| `dados/linhas-por-sentido.geojson` | 39 geometrias viárias de referência, sem deslocamento gráfico. |
| `dados/waypoints-roteamento.json` | 154 coordenadas usadas pelos 39 traçados. Os marcadores visuais ficam no catálogo. |
| `dados/base-cartografica.json` | Base de referência processada, com bairros, municípios, hidrografia e corredores. |
| `dados/comparativos-i332.json` | Traçados e paradas históricas para os recortes Paratibe e Parque do Sol. |
| `mapa/` | Template, scripts, cache do OSRM, fontes cartográficas locais, D3 e verificação do mapa. |
| `mapa/comparacao-atual/` | Geometrias de referência da rede em operação e triagem histórica. |
| `historico/` | Três versões anteriores do mapa e relatórios de roteamento. |

A vinculação entre arquivos usa o código ativo da linha e, para o sentido contrário, a chave com o sufixo `-volta`. Trate outros registros de `mapa/malha-roteada.json` como testes ou variantes históricas quando estiverem ausentes do catálogo. Os conjuntos extraídos em `dados/` documentam o snapshot que acompanha o prompt. Em uma mudança futura, atualize-os a partir da revisão do catálogo e do cache que o mapa usa.

## Geração local

Com Python 3.10+ na raiz da pasta extraída, use:

```sh
python3 mapa/prepare.py
python3 mapa/abrir.py
```

O primeiro comando recria o fragmento a partir dos arquivos fornecidos. O segundo produz o mapa navegável. A geração mantém a geometria armazenada sem novas chamadas ao roteador. Para verificar o mapa, use Node.js e instale a dependência de simulação do DOM:

```sh
npm ci --prefix mapa
node mapa/check.cjs
```

A verificação cobre a ordem das linhas, os filtros, os comparativos da I-332, as cores e os efeitos de sobreposição em dois tamanhos de tela. Gera SVGs de inspeção na pasta `mapa/`. Para atualizar uma rota, leia `mapa/rotear.py` e confira as listas de pontos em `mapa/ampliacao.py`. O comando `python3 mapa/rotear.py` faz uma atualização completa, depende do serviço OSRM e sobrescreve seu cache local. Para alteração pontual, preserve o cache original e substitua só os sentidos alterados.

A triagem histórica usa NumPy, Matplotlib e scikit-learn. O script fornecido aponta para o mapa histórico que produziu seu resultado. Ajuste essa entrada para a revisão vigente antes de interpretar números como cobertura do projeto atual.

## Dados e atribuição

Cartografia de referência do [Filipeia](https://filipeia.joaopessoa.pb.gov.br/) e do [IBGE](https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais.html), malha viária © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), roteamento [OSRM](https://project-osrm.org/), itinerários históricos referenciados a [Bus4/EMS Horários](https://s3.amazonaws.com/bus4.jpa.mapa/index.html) e tabelas da [Semob-JP](https://servicos.semobjp.pb.gov.br/linhas-de-onibus/). D3 7.9.0 sob [licença ISC](https://github.com/d3/d3/blob/v7.9.0/LICENSE). Preserve as atribuições no mapa e nos dados. Verifique as condições aplicáveis antes de publicar os conjuntos externos.
