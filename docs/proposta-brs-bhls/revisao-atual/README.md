# Revisão ativa — rede observada, Cidade Universitária e TIV

Esta é a versão servida por `/api/proposal`. O estudo importado em `../estudos/rede-integrada-2026-11-21` permanece preservado como histórico. Os 23 códigos de serviço e os 39 sentidos/circuitos foram mantidos; todas as geometrias passaram pelo recalculo.

## Integrações e restrições

- **Cidade Universitária:** referência na Estação Cidade Universitária, OSM stop `2533629066`, na Via Expressa Padre Zé / Rua Tabelião Estanislau Eloy. Não é um terminal dentro da universidade. Há referências distintas para Centro/Norte e Bancários/Sul. BRS-300, BRS-800, I-334 e R-343 foram ajustadas, com bloqueio da Via UFPB e das ruas internas do campus.
- **Varadouro:** Terminal Metropolitano no espaço atual do TIV. BRS-100, BRS-200, BRS-300, BRS-500, BRS-501, T-410 e T-610 usam a passagem pela Lagoa e os acessos centrais da linha 0301, preservados literalmente em cada geometria por sentido.
- **Entrada no TIV:** Lagoa / Parque Solon de Lucena → Miguel Couto → Cardoso Vieira → Cândido Pessoa → João Suassuna → Sanhauá → General Lima Mindelo → Desembargador Trindade → TIV.
- **Saída do TIV:** Padre Azevedo → Praça Pedro Américo → Praça Aristides Lobo → Guedes Pereira → Padre Meira → Lagoa, seguindo então o corredor de cada serviço.
- **Oitizeiro:** referência deslocada da feira para a área junto ao viaduto/BR-230, conforme confirmação do usuário sobre a imagem enviada. O ponto é uma referência aproximada na chegada pela Cruz das Armas, não uma planta de plataforma aprovada. Afeta BRS-100, BRS-800 e TRV-721.

## Preferência por padrões observados

A revisão usa a coleta de 85 linhas SEMOB (149 traçados disponíveis) e uma malha viária OSM com 84.209 nós roteáveis e 173.540 segmentos dirigidos. A concentração considera códigos distintos por segmento e por rua. O custo favorece ruas com maior concentração, mantendo as referências territoriais de cada serviço.

O interior do campus é bloqueado com uma margem de contorno de 25 m, para não excluir as próprias ruas públicas de borda. A baia da estação e as vias públicas nomeadas de contorno são exceções explícitas. Ruas privadas, vias não motorizadas e pontas isoladas não são atalhos permitidos.

A correspondência geométrica usa tolerância de 22 m e direção compatível. Calculada da mesma forma antes/depois, a parcela dos traçados em ruas com referência na rede observada passou de **69,6% para 83,0%**, ponderada pela extensão. Houve aumento em **35 dos 39 sentidos**; os quatro restantes não melhoraram nesse indicador. Preservar a passagem pela Lagoa, os acessos do TIV e a cobertura territorial prevalece sobre maximizar um percentual isolado. Não se trata de percentual de demanda atendida ou de validação de frequência.

| Serviço | Extensões revisadas (km) | Ruas observadas por sentido |
| --- | --- | --- |
| BRS-100 | ida: 12,28 / volta: 8,52 | 91,9% / 92,2% |
| BRS-200 | ida: 10,64 / volta: 9,70 | 91,1% / 89,6% |
| BRS-300 | ida: 12,51 / volta: 13,02 | 95,5% / 93,8% |
| BRS-500 | ida: 19,22 / volta: 16,30 | 97,7% / 99,5% |
| BRS-501 | ida: 18,23 / volta: 15,49 | 98,1% / 98,6% |
| BRS-800 | ida: 32,16 / volta: 36,98 | 75,8% / 75,1% |
| T-410 | ida: 18,50 / volta: 17,53 | 86,1% / 82,0% |
| T-610 | ida: 15,56 / volta: 15,34 | 88,5% / 90,2% |
| TRV-321 | ida: 20,78 / volta: 19,55 | 83,4% / 83,9% |
| TRV-322 | circuito: 34,91 | 67,7% |
| TRV-721 | ida: 14,29 / volta: 16,34 | 85,1% / 91,7% |
| I-331 | ida: 8,31 / volta: 9,12 | 90,3% / 89,9% |
| I-332 | ida: 20,97 / volta: 22,09 | 76,2% / 78,8% |
| I-333 | ida: 13,94 / volta: 14,92 | 88,5% / 89,3% |
| I-334 | circuito: 26,44 | 84,0% |
| I-731 | ida: 7,35 / volta: 8,26 | 90,3% / 94,3% |
| R-241 | circuito: 15,04 | 89,3% |
| R-242 | circuito: 13,66 | 77,3% |
| R-343 | circuito: 30,73 | 74,7% |
| L-251 | circuito: 9,32 | 93,1% |
| L-351 | ida: 13,83 / volta: 15,03 | 93,5% / 93,7% |
| L-751 | circuito: 20,10 | 71,3% |
| M-961 | ida: 26,28 / volta: 26,02 | 60,3% / 58,4% |

## Auditoria e limites

`auditoria.json` registra hashes das entradas, consulta OSM, geometria da referência central, referências da estação, ajustes de encaixe, sequência de ruas e formas de acesso. Os encaixes de referências no grafo atingem no máximo 100 m; os dois encaixes entre grafo e geometria central medem 4,4 m e 29,4 m. Eles estão registrados para revisão, sem transformar waypoints em plataformas ou paradas aprovadas.

A referência do HU foi mantida no entorno público, e a ligação Altiplano–Castelo Branco segue vias existentes em vez de impor uma ponte/atalho interno. A linha metropolitana M-961 e alguns setores periféricos têm menor correspondência com o catálogo municipal; a ausência de uma linha municipal no trecho não demonstra ausência de transporte metropolitano.

O roteamento respeita a direção cadastrada nas vias, mas ainda exige verificação de restrições de conversão por relação OSM, raios de giro, gabarito de ônibus, sinalização, paradas e acessos internos dos futuros terminais. Distâncias são aproximadas. Não há alegação de capacidade comprovada ou de rede operacional aprovada.

## Fontes e reprodução

- SEMOB-JP, coleta local completa de 21/11/2026: [serviço de linhas](https://servicos.semobjp.pb.gov.br/linhas-de-onibus/) e [GeoJSON da 0301](https://servicos.semobjp.pb.gov.br/linhas-de-onibus/0301/itinerario/geojson).
- OpenStreetMap: [Estação Cidade Universitária, via 59821461](https://www.openstreetmap.org/way/59821461), [parada 2533629066](https://www.openstreetmap.org/node/2533629066) e malha obtida pelo Overpass. Consulta, data e hashes preservados na auditoria; dados viários © OpenStreetMap contributors, [ODbL](https://www.openstreetmap.org/copyright).
- Prefeitura de João Pessoa: [localização do novo mercado e terminal próximo ao viaduto das Três Lagoas](https://www.joaopessoa.pb.gov.br/noticias/prefeito-autoriza-a-construcao-do-novo-mercado-de-oitizeiro-e-destaca-investimento-de-r-70-milhoes-nos-espacos-publicos-de-comercio-na-capital/). A notícia situa a área; a confirmação do usuário adotou o entorno do viaduto, não o marcador anterior da feira.
- Regras e execução do gerador: [apps/planner/README.md](../../../apps/planner/README.md).

Os arquivos brutos ficam em `data/`, fora do Git. Esta pasta contém os resultados derivados e os metadados necessários para revisar as escolhas, sem substituir os dados observados.
