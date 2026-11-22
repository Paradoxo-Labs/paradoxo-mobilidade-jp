# Revisão ativa — corredores, terminais e cobertura local

Esta versão é servida por `/api/proposal`: 24 serviços e 41 sentidos/circuitos. O estudo importado em `../estudos/rede-integrada-2026-11-21` permanece preservado. A M-961 recupera integralmente suas duas geometrias originais; os demais serviços usam a revisão de corredores.

## Terminais e integrações

- **Lagoa:** Terminal de Passageiros da Lagoa, com referência na plataforma 4 cadastrada no OSM (nó 3962688662, fonte SEMOB), em vez de um ponto genérico no parque. O acesso ao TIV mantém o trecho observado da 0301 por sentido. Na saída, o trecho central é estendido pela circulação pública da Lagoa até as plataformas antes de distribuir os serviços por seus corredores. A distribuição operacional entre plataformas ainda deve ser definida.
- **Varadouro:** Terminal Metropolitano no espaço atual do TIV. Os sete serviços radiais mantêm os acessos observados: entrada por Miguel Couto / Cardoso Vieira / Cândido Pessoa / João Suassuna / Sanhauá / General Lima Mindelo / Desembargador Trindade; saída por Padre Azevedo / Pedro Américo / Aristides Lobo / Guedes Pereira / Padre Meira.
- **Cristo:** terminal atual das linhas 204 e 208, aproximadamente -7,16650 / -34,87198. A referência anterior no Almeidão foi substituída.
- **Oitizeiro:** referência do terreno adjacente ao novo mercado, conforme o link enviado pelo usuário (-7,163894 / -34,893325). O marcador identifica a referência do mercado; a conexão viária aproximada fica a 115 m, na BR-230. O limite do lote, a entrada e o percurso interno ainda dependem da planta; não se desenha uma entrada fictícia dentro do terreno.
- **Cidade Universitária:** Estação Cidade Universitária, nó OSM 2533629066 / via 59821461, no entorno público. Vias internas do campus e Via UFPB continuam bloqueadas. Os giradores públicos de CCHLA e CT permanecem disponíveis.

## Ajustes por serviço

| Serviços | Alteração |
| --- | --- |
| BRS-501 | Eixo mais interior de Manaíra, por Sapé, Francisco Brandão e Manoel Morais, distinto da BRS-500. |
| BRS-800 | Depois da estação Cidade Universitária, retorna à BR-230; sem circulação residencial no Castelo Branco. |
| T-410 | Beira-Rio contínua entre o Centro e a ligação com o Altiplano; sem UFPB ou Epitácio Pessoa. |
| T-610 | Bessa / Shopping / Ipês / Mandacaru / Roger, sem BR-230. |
| TRV-321 | Shopping e retorno ao eixo próximo à praia / Jardim Oceania para Bessa; sem BR-230. |
| TRV-721 | Mantém Perimetral Sul / BR-101, retirando o desvio pelo interior do Planalto da Boa Esperança. |
| I-332 | Muçumagro → terminal Valentina, sem o percurso interno do Parque do Sol. |
| R-241 / R-242 | Ambas entram no Colibris por seu setor central e ampliam José Américo com ruas da atual 107. |
| L-251 | Amplia Cristo, Vale das Palmeiras e Rangel, alcança o IFPB pela Primeiro de Maio e retorna. Usa trechos de referência das 204, 208 e 203. A antiga 201 não está disponível nas bases locais e não é apresentada como reproduzida. |
| L-751 | Assume o atendimento interno do **Parque do Sol**, retirado da I-332, preservando Muçumagro, Barra de Gramame e Praia do Sol. |
| M-961 | Restaura exatamente as coordenadas originais, nos dois sentidos. |

## Alimentadora oeste — I-131

Linha única bidirecional: **Terminal Alto do Mateus ↔ Novais ↔ Jardim Planalto ↔ Cidade dos Funcionários ↔ Terminal Oitizeiro**. O código I-131 é provisório, de estudo.

O trecho interno da 108 no Alto do Mateus e as ruas locais da 110 no Jardim Planalto são preservados literalmente em cada sentido, com ligações públicas por Novais e pela área da 105 (São Benedito, Ernani Rabelo, Praça Lauro Wanderley e Desembargador Maurício Furtado). Cidade dos Funcionários corresponde ao setor atendido pela 105; o polígono agregado de Funcionários não define este destino.

Extensões: **ida 10,38 km / volta 11,15 km**. O desenho completo supera a estimativa conceitual de 7–9 km porque preserva a cobertura interna das duas linhas. A auditoria identifica cada trecho observado e os encaixes, limitados a 35 m. O percurso da 110 contém nomes de ruas SEMOB sem correspondência de nome na malha OSM; a geometria publicada é mantida nesses trechos.

A oferta é concentrada em uma alimentadora; Tiradentes permanece como possível complemento a avaliar por cobertura e demanda. Não se atribuem frota, intervalo ou capacidade ainda não dimensionados. A proposta não altera os dados da rede atual nem representa retirada das ligações existentes pelo Acesso Oeste.

## Critério de traçado

A concentração de linhas deixou de dominar o custo. Agora o cálculo prioriza distância e continuidade dos corredores, favorece vias estruturantes e limita o efeito da concentração a 8% do custo de cada segmento. Ruas residenciais recebem custo adicional para evitar atalhos em sucessões de pequenas ruas. As regras territoriais prevalecem sobre esse custo.

Referências intermediárias aceitam alternativas próximas na pista adequada ao sentido. Corredores nomeados usam candidatos na própria avenida, preservando as mãos únicas do OSM. Na T-410, as ligações entre as referências da Beira-Rio permanecem nessa avenida; os antigos desvios por ruas paralelas foram retirados. Isso não implica inverter ilegalmente uma rua de mão única para forçar simetria.

O grafo utiliza 84.209 nós roteáveis e 173.540 segmentos dirigidos. A coleta SEMOB contém 85 linhas e 149 traçados; seis serviços têm GeoJSON vazio. Os percentuais abaixo medem somente correspondência com ruas observadas, com tolerância de 22 m e direção compatível. São indicadores descritivos, não metas de otimização, demanda ou capacidade. A M-961 original tem menor correspondência com a base municipal.

| Serviço | Extensões (km) | Ruas observadas |
| --- | --- | --- |
| BRS-100 | ida: 8,95 / volta: 10,48 | 98,2% / 93,2% |
| BRS-200 | ida: 9,18 / volta: 9,52 | 95,2% / 87,7% |
| BRS-300 | ida: 12,69 / volta: 12,55 | 99,1% / 97,8% |
| BRS-500 | ida: 18,51 / volta: 16,62 | 94,0% / 97,8% |
| BRS-501 | ida: 16,95 / volta: 17,23 | 82,8% / 90,9% |
| BRS-800 | ida: 31,83 / volta: 30,58 | 50,9% / 55,8% |
| T-410 | ida: 16,15 / volta: 14,02 | 77,5% / 74,7% |
| T-610 | ida: 15,02 / volta: 15,12 | 84,8% / 88,4% |
| TRV-321 | ida: 19,75 / volta: 20,79 | 86,5% / 76,7% |
| TRV-322 | circuito: 33,80 | 65,0% |
| TRV-721 | ida: 10,60 / volta: 13,82 | 73,0% / 79,5% |
| I-331 | ida: 7,96 / volta: 8,10 | 92,2% / 86,4% |
| I-332 | ida: 16,49 / volta: 16,44 | 74,4% / 71,0% |
| I-333 | ida: 11,94 / volta: 12,32 | 70,8% / 74,4% |
| I-334 | circuito: 24,62 | 84,4% |
| I-731 | ida: 7,11 / volta: 7,23 | 82,1% / 77,0% |
| R-241 | circuito: 15,06 | 81,2% |
| R-242 | circuito: 13,78 | 66,4% |
| R-343 | circuito: 29,15 | 63,1% |
| L-251 | circuito: 15,26 | 85,8% |
| L-351 | ida: 12,51 / volta: 12,88 | 88,3% / 89,5% |
| L-751 | circuito: 21,20 | 65,1% |
| M-961 | ida: 23,25 / volta: 24,76 | 29,0% / 29,9% |
| I-131 | ida: 10,38 / volta: 11,15 | 87,4% / 86,0% |

## Auditoria e reprodução

`auditoria.json` registra hashes dos dados e das regras, origem OSM, referências dos terminais, trechos centrais, sequência de ruas, referências rodoviárias, ajustes de encaixe e ligações entre cada par de referências. Na M-961, ruas e ligações recalculadas são omitidas para não atribuí-las à geometria original restaurada.

Execute `python3 apps/planner/revise.py` com os dados brutos locais disponíveis; veja [o gerador](../../../apps/planner/README.md). Os dados brutos ficam em `data/`, fora do Git. Após gerar, use `docker compose up -d --build --wait`.

Conversões proibidas por relações OSM, raio de giro, dimensões dos ônibus, sinalização, paradas e circulação interna de terminais ainda exigem validação operacional. A referência do mercado não substitui uma planta do lote do terminal.

## Fontes

- [SEMOB: linhas e itinerários](https://servicos.semobjp.pb.gov.br/linhas-de-onibus/) e [GeoJSON da 0301](https://servicos.semobjp.pb.gov.br/linhas-de-onibus/0301/itinerario/geojson), coleta local completa de 21/11/2026; linhas 107, 203, 204, 208 e corredores atuais como referências.
- [SEMOB: Terminal de Passageiros da Lagoa e plataformas](https://portal.semobjp.pb.gov.br/2024/07/prefeito-entrega-novo-terminal-de-integracao-da-lagoa-e-destaca-avanco-em-obras-de-mobilidade-e-infraestrutura-urbana-na-capital/).
- [OpenStreetMap: plataforma 4 da Lagoa](https://www.openstreetmap.org/node/3962688662), [Estação Cidade Universitária](https://www.openstreetmap.org/way/59821461). Malha e consulta Overpass identificadas na auditoria; dados © OpenStreetMap contributors, [ODbL](https://www.openstreetmap.org/copyright).
- [Prefeitura: novo mercado de Oitizeiro e terminal adjacente](https://www.joaopessoa.pb.gov.br/noticias/prefeito-autoriza-a-construcao-do-novo-mercado-de-oitizeiro-e-destaca-investimento-de-r-70-milhoes-nos-espacos-publicos-de-comercio-na-capital/). O usuário refinou a localização com o ponto do mercado no Google Maps; os limites do terreno e acessos seguem pendentes de planta.
- [SEMOB: Alto do Mateus / 108](https://servicos.semobjp.pb.gov.br/linhas-de-onibus/0108/itinerario/), [Jardim Planalto / 110](https://servicos.semobjp.pb.gov.br/linhas-de-onibus/0110/itinerario/) e [Cidade dos Funcionários / 105](https://servicos.semobjp.pb.gov.br/linhas-de-onibus/0105/itinerario/), referências da nova I-131.
- [IFPB: campus João Pessoa / Primeiro de Maio, 720](https://estudante.ifpb.edu.br/cursos/polo/2/).
