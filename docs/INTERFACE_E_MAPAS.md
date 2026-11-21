# Interface, identidade e cartografia

## Identidade Paradoxo

A interface usa como referência o código do [site institucional](https://paradoxolabs.com.br), disponível no projeto local `site-paradoxo-labs`: preto `#111112`, papel `#f3f0e9`, vermelho `#c71020` / `#ed2633`, títulos Syne e detalhes Space Mono. O logotipo PRDX, as fontes e suas licenças OFL foram copiados para `apps/web/assets`, sem dependência de execução entre repositórios.

A navegação foi reorganizada em cabeçalho horizontal. Os mapas têm painel de busca, filtros e legenda próprios. As linhas da proposta usam cores por classe de serviço, preservando a identidade vermelha para BRS; as demais cores cumprem função cartográfica.

## Proposta nativa

A página da proposta deixou de embutir o HTML antigo em iframe. Ela consome `/api/proposal`, com os dados preservados da revisão de 21/11/2026: `dados/catalogo.json`, `linhas-por-sentido.geojson`, `waypoints-roteamento.json` e `comparativos-i332.json`.

São 23 serviços e 39 geometrias por sentido, com busca por código/trecho, filtro de classe, seleção de sentido, integrações propostas, referências de roteamento e tela cheia. Os comparativos Paratibe/Parque do Sol mostram revisões da I-332, não uma validação da rede observada. Distâncias são referências do roteador e waypoints não equivalem a paradas de embarque.

O mapa de origem continua disponível em `/proposta-original`; `/proposta` leva à nova página integrada. Os arquivos originais do estudo não foram modificados.

## Referência do Atlas de Distritos

Foram consultados o [Paraíba · Atlas de Distritos](https://paraiba-distritos-eleitorais.dev-jailson.chatgpt.site) e seu código local `public/map-six.js`, identificado a partir do chat de origem do site. O atlas já utiliza Leaflet e alternância entre ruas OpenStreetMap, topografia Esri e satélite Esri. Esses provedores foram incorporados à mobilidade com configuração própria em `apps/web/map-sources.json`.

| Fundo | Fonte | Uso |
| --- | --- | --- |
| Ruas | OpenStreetMap, `https://tile.openstreetmap.org/{z}/{x}/{y}.png` | Leitura da malha viária e nomes de ruas; padrão online |
| Topografia | Esri `World_Topo_Map` | Contexto territorial |
| Satélite | Esri `World_Imagery` | Referência visual do território |
| Local | Cartografia Filipeia/IBGE já preservada no estudo | Bairros, municípios e hidrografia; funcionamento sem internet |

O Leaflet 1.9.4 e sua licença são servidos pelo próprio projeto, em `apps/web/vendor/leaflet`. Os fundos online carregam apenas o que é exibido na interação; não há pré-download ou exportação de tiles. Atribuições são exibidas no mapa. A política de Referer permite a identificação da origem conforme a [política de tiles do OpenStreetMap](https://operations.osmfoundation.org/policies/tiles/). Em falha de tiles, o fundo local é ativado e um aviso aparece no mapa.

## Coleta integral

O painel executa sempre a coleta de todo o catálogo SEMOB. A CLI conserva `--line` e `--limit` para manutenção e diagnóstico, mas não são usados pela ação principal da interface.

Em 21/11/2026, todas as 85 linhas do catálogo foram consultadas, com itinerários e horários recebidos e 149 traçados publicados. Os endpoints das linhas **0116, 0120, 0604, 9901, I015 e T003** retornaram coleção GeoJSON vazia. Essas lacunas ficam explícitas; não há reconstrução por ruas nem substituição silenciosa por geometria histórica.

A base oficial coletada é a consulta inicial quando disponível. A referência Bus4/EMS permanece como opção separada, sem equivalência presumida entre códigos.
