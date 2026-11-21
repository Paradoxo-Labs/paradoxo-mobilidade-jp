# Prompt mestre | Rede integrada de transporte público de João Pessoa

**Base do projeto:** revisão da rede de 21 de novembro de 2026 · 23 linhas de ônibus propostas.  
**Idioma:** português do Brasil.  
**Unidade territorial:** João Pessoa e conexões metropolitanas consideradas no estudo.

---

## 1. Instruções ao Codex

Você vai dar continuidade a um estudo de redesenho do transporte público de João Pessoa. Atue como parceiro de planejamento de transportes, análise geoespacial e desenvolvimento de software. Use este documento como contexto de projeto e consulte os arquivos do pacote quando estiverem disponíveis. A rede está sendo construída incrementalmente por setores e terminais. A versão atual tem 23 serviços de ônibus modelados, além da diretriz de integração com a ferrovia metropolitana existente.

Antes de editar, leia o README, verifique o conteúdo da pasta e rode a geração e os testes do mapa. Se receber apenas este documento, use o inventário, os pontos de referência e as instruções aqui registrados para reconstruir o estado. Quando houver uma nova tarefa, execute-a sobre a revisão vigente. Quando receber apenas o prompt como contexto, incorpore-o e informe os materiais encontrados, o estado verificável e as pendências efetivas.

- Dê precedência à última instrução explícita do usuário. Na sequência, use os itinerários e as decisões documentadas nesta base, o mapa gerado e as rotas armazenadas. Registre e explique divergências relevantes antes de resolvê-las.
- Trate o serviço em operação hoje como referência de cobertura, destinos, itinerários, paradas e conversões. A concepção da nova rede assume, como exercício, que as linhas urbanas anteriores foram substituídas. A referência a um código atual, como 107, 208, 5600 ou I004, indica o trecho ou a função usada como referência.
- Diferencie a decisão do usuário, a solução de traçado escolhida na modelagem, a hipótese operacional e o tema em aberto. Os pontos desenhados em terminais novos são referências geográficas. As rotas calculadas são estimativas de percurso e exigem validação para operação com ônibus.
- Prefira mudanças verificáveis e localizadas. Se uma alteração envolver só uma linha, preserve a geometria das demais, atualize os dois sentidos aplicáveis e faça a verificação automática. Separe alterações de projeto de ajustes técnicos que não mudam a rede.
- Quando identificar uma sobreposição, diga **quais linhas, em qual trecho, em qual sentido e com qual função**. Proximidade entre traços, ruas paralelas, vias marginais, retornos e pistas opostas têm significados diferentes. A existência de um segmento comum permite integração ou compartilhamento de infraestrutura. Uma fusão exige conferir destinos, frequência, caminhada, transbordos e o desvio que passageiros passariam a fazer.
- Use os nomes escolhidos pelo usuário. Em respostas de mudança, entregue o novo itinerário, o mapa quando relevante, os impactos verificáveis e as decisões de modelagem feitas por conta própria. Evite apresentar extensões, frequências, obras, coordenadas de plataforma e integrações tarifárias como aprovadas sem uma decisão correspondente.
- Mantenha separados no modelo os **códigos de linha**, **locais de integração**, **geometria por sentido**, **paradas propostas** e **infraestrutura de circulação**. Uma referência obrigatória para orientar o veículo pode existir apenas como waypoint, sem embarque de passageiros.

## 2. Conceito da rede e decisões sobre modos

A estrutura debatida combina três camadas.

1. **Modernização da linha ferroviária metropolitana existente.** A linha da CBTU liga Santa Rita a Cabedelo atravessando João Pessoa. O cenário de partida dá prioridade à reforma e modernização desse eixo e à integração da Estação João Pessoa no Varadouro. Frequência, frota, sinalização, cruzamentos, confiabilidade, integração de horários e acessos são dimensões de estudo. O mapa de 23 linhas é de ônibus. A ferrovia entra como infraestrutura e serviço integrado em uma camada própria quando for representada.
2. **Ônibus estruturais.** BRS em corredores onde houver prioridade consistente, troncais fora desse padrão e transversais conectando áreas de origem e polos sem obrigar passagem pelo Varadouro. Parte das radiais termina no Terminal Metropolitano. O desenho da prioridade viária está em nível de proposta. A classificação BRS por si só não demonstra largura, capacidade ou implantação de faixa exclusiva em todo o itinerário.
3. **Linhas integracionais, regionais, locais e metropolitanas.** As linhas de bairro aproximam áreas internas de nós de integração. Serviços regionais conectam vários setores próximos ou organizam circulares complementares. A ligação Litoral Sul cumpre função metropolitana. Os deslocamentos entre polos exigem conexões transversais mesmo com uma centralidade forte no Varadouro.

### Rede radial, transversal e circular

- Radial descreve direção funcional entre área periférica e centro. Oitizeiro–Varadouro, Cristo–Varadouro e Mangabeira–Varadouro são exemplos.
- Transversal liga terminais, bairros e polos sem exigir passagem pelo centro tradicional. Mangabeira–Orla–Bessa, Valentina–Oitizeiro e Mangabeira–Cristo são exemplos.
- Troncal descreve função de estruturação e redistribuição. Uma linha troncal pode seguir radialmente e operar com prioridades pontuais ou em tráfego misto em parte do trajeto.
- Circular descreve a forma operacional, com retorno ao ponto de partida. Uma circular pode ser regional, transversal, integracional ou local. Dois sentidos circulares podem ter códigos próprios e itinerários assimétricos, como R-241 e R-242.
- Uma faixa BRS pode servir várias linhas. A unidade de análise de infraestrutura é o corredor com seus segmentos, paradas e interseções. A unidade de serviço ao passageiro é a linha. Uma faixa compartilhada exige avaliar frequência conjunta, capacidade de parada, ultrapassagem, espaço para conversões e regularidade.

### Ferrovia, restrições físicas e hipóteses anteriores

O estudo original perguntou o que limita fisicamente ampliar trilhos em João Pessoa e como outras cidades lidaram com falta de corredor para metrô. A conclusão do projeto nesta etapa é uma **diretriz de avaliação**, sem nova linha de trilhos aprovada. A modernização do eixo metropolitano integrado a ônibus deve ser testada primeiro. Depois, uma eventual nova oferta sobre trilhos deve responder a um volume de viagens, saturação ou ganho de integração que sobreviva a essa comparação.

- Estude faixa de domínio contínua, largura efetiva depois de considerar calçadas, acessos, estações e cruzamentos, nós rodoviários, desníveis, drenagem, pontes, travessias de rios/vales, desapropriações e interferências urbanas. Considere também onde existem polos caminháveis e onde a rodovia, seus acessos e suas alças separam as duas margens.
- O VLT pela BR-230 foi explorado como **hipótese**. Trechos em superfície podem aproveitar espaços existentes quando a geometria, a continuidade e o acesso ao pedestre permitirem. Viadutos, trincheiras e cruzamentos pontuais podem resolver estrangulamentos específicos, com custo e impacto próprios. Compare com prioridade para ônibus e com uso do eixo ferroviário existente. O projeto de ônibus desta revisão não inclui VLT novo nem metrô subterrâneo como premissa.
- O debate sobre Melbourne, tipos de oferta e operação de madrugada serviu de referência conceitual. O projeto de João Pessoa ainda não tem grade 24h, serviço noturno, intervalos, frota, tarifa ou cronograma pactuados. Trate cada dimensão como uma etapa de planejamento quando for solicitada.

## 3. Codificação vigente

Use `PREFIXO-XYZ`. No padrão **XYZ**, **X** é o agrupamento de corredor, terminal ou área de referência do projeto, **Y** é a classe de serviço e **Z** é a sequência de 0 a 9 dentro do agrupamento e da classe. Preserve os identificadores já atribuídos. O grupo de uma linha não implica que ela pertença a todos os terminais por onde passa.

| Y | Prefixo | Classe | Função no projeto |
| --- | --- | --- | --- |
| 0 | BRS | BRS | Serviços estruturais de corredores prioritários |
| 1 | T | Troncal | Eixo estrutural com classificação própria |
| 2 | TRV | Transversal | Ligação entre setores, polos ou terminais |
| 3 | I | Integracional | Conexão a terminal, a outro terminal ou a polo de integração |
| 4 | R | Regional | Articulação de bairros/setores em uma região |
| 5 | L | Local | Cobertura e distribuição de bairro ou conjunto de bairros |
| 6 | M | Metropolitana | Ligação que cruza a fronteira municipal |

Grupos usados na versão atual. **1** Oitizeiro/Cruz das Armas, **2** Cristo/Rangel, **3** Mangabeira e suas conexões, **4** Beira-Rio, **5** eixo Epitácio/Ruy/Bessa, **6** eixo Mandacaru/Ipês, **7** Valentina, **8** eixo Aeroporto/BR-230 e **9** Litoral Sul. Essas referências explicam os códigos já atribuídos. Novos grupos e tipos ficam a cargo da evolução do projeto. O código nunca é exibido como substituto de um nome de destino.

## 4. Terminais, integração e acessos modelados

Coordenadas em **WGS84, longitude antes da latitude**. Alguns marcadores e entradas rodoviárias têm coordenadas diferentes por desenho, especialmente T. Mangabeira. As posições abaixo reproduzem referências do estudo.

| Local | Chave | Referência geográfica | Papel e serviços associados |
| --- | --- | --- | --- |
| Terminal Metropolitano · Varadouro | `metro` | `[-34.890918, -7.116089]` | Nó central intermodal. Integrar Estação João Pessoa da CBTU, Terminal Rodoviário e Terminal de Integração do Varadouro, com conexões de pedestres legíveis. BRS-100, 200, 300, 500, 501 e troncais T-410, T-610. |
| Terminal Mangabeira | `hub` | Antiga sede da Contax, marcador `[-34.821396, -7.161140]`; entrada modelada `[-34.821910, -7.160790]` | Hub da zona sul no eixo da Hilton Souto Maior. BRS-300, T-410, TRV-321, TRV-322, I-331, I-332, I-333, I-334, R-343, L-351 e M-961. |
| Terminal Cristo · Estádio Almeidão | `cristo` | `[-34.874973, -7.166678]` | Hub de Cristo no estádio. BRS-200, BRS-800, TRV-322, I-731, R-241, R-242 e L-251. Preservar o acesso ao estádio e diferenciar marginais, viaduto e alças. |
| Terminal Oitizeiro | `oitizeiro` | Feira de Oitizeiro, `[-34.896326, -7.161357]` | Portal oeste. BRS-100, BRS-800 e TRV-721. O ponto de integração é referencial, com acesso específico por sentido. |
| Terminal Bessa | `bessa` | Entorno da integração existente, `[-34.845409, -7.063077]` | Nó norte. BRS-500, BRS-501, BRS-800, T-610 e TRV-321. É o fim da ligação do aeroporto nesta fase e ponto lógico de conexão em direção a Cabedelo. |
| NTI Valentina | `val` | Entorno da integração usada como referência, `[-34.847347, -7.204896]` | Integração setorial sem BRS na revisão atual. I-331, I-332, I-333, I-731, TRV-721 e L-751. |
| Terminal UFPB | `universidade` / `universidade_public` | Referência no campus `[-34.845526, -7.138236]`; ponto roteado `[-34.845530, -7.138220]` | Ponto comum da I-334 e BRS-800. HU, CT, Via UFPB, Dom Pedro II e Castelo Branco são pontos e acessos distintos. BRS-300 e R-343 atendem a zona universitária segundo seus próprios traçados. |
| Aeroporto Castro Pinto | `aeroporto` | `[-34.949368, -7.144681]` | Origem/destino da BRS-800 no acesso de embarque/desembarque modelado. Não inventar baia, estacionamento ou acesso definitivo. |
| Manaíra Shopping | `shopping` | Acesso pela Av. Vereador Gumercindo Barbosa Dunda, `[-34.844290, -7.095050]` | Polo de parada e conexão de TRV-321, T-610 e BRS-800. O Retão é a Av. Governador Flávio Ribeiro Coutinho. O modelo usa a via pública junto ao shopping, com acessos por sentido. |
| Jacumã | `jacuma` | `[-34.803874, -7.286346]` | Extremidade sul modelada da M-961. |
| Patrícia Tomaz · Três Marias | `patricia` | `[-34.815163, -7.184128]` | Extremidade local da L-351 no recorte Cidade Verde II. |

Use **Terminal de Integração** para a função dos hubs maiores e preserve o letreiro **NTI Valentina** para o nó setorial. A expansão da sigla NTI ficou sem definição explícita. O nome oficial de um equipamento existente e a classificação funcional da rede proposta são campos distintos. O atributo visual `terminal: true` no mapa é também usado para extremidades de linhas, e sozinho não define o porte, o modo ou os serviços de um local. T. Mangabeira recebe BRS e linhas de outros tipos. A integração em Valentina acontece entre serviços de ônibus já listados. Para dimensionamento futuro, avalie embarque e desembarque, travessias, baias, manobra, permanência, informação e acessibilidade.

## 5. Inventário operacional da revisão

A seta **→** descreve uma ordem. A seta **↔** indica ida e volta com geometrias próprias, sujeitas às mãos viárias. Um itinerário circular termina onde começou. Os nomes de bairro indicam área atendida, enquanto as ruas e a geometria armazenada determinam a via. Não adicione horários nem paradas que ainda não foram definidos.

### 5.1 BRS · 6 serviços

| Código e nome | Itinerário e observações |
| --- | --- |
| **BRS-100 · Oitizeiro** | T. Oitizeiro ↔ Av. Cruz das Armas ↔ Jaguaribe ↔ Centro ↔ T. Metropolitano. Usa referência na feira na ponta oeste. Em Jaguaribe, as variantes por sentido passam por referências na João Gama/entorno, conforme o traçado. |
| **BRS-200 · Cristo** | T. Cristo no Almeidão ↔ Rangel pela Av. 2 de Fevereiro ↔ Jaguaribe ↔ Centro ↔ T. Metropolitano. Trechos centrais e de Jaguaribe podem coincidir com a BRS-100. |
| **BRS-300 · Mangabeira–Varadouro** | T. Mangabeira ↔ Hilton Souto Maior/acesso ao Jardim Cidade Universitária ↔ Bancários ↔ UFPB, com referência no CT ↔ Dom Pedro II ↔ Centro ↔ T. Metropolitano. A variante BRS-301 via Três Ruas foi encerrada. |
| **BRS-500 · Epitácio Pessoa–Bessa** | T. Bessa ↔ Aeroclube/Jardim Oceania ↔ Manaíra ↔ Tambaú ↔ Av. Epitácio Pessoa ↔ Centro ↔ T. Metropolitano. Preservar o eixo costeiro/norte comum de referência com a BRS-501. |
| **BRS-501 · Epitácio Pessoa–Bessa via Ruy Carneiro** | T. Bessa ↔ Aeroclube/Jardim Oceania ↔ Manaíra ↔ Tambaú ↔ Av. Senador Ruy Carneiro ↔ conexão em direção ao Centro ↔ T. Metropolitano. A ligação final da Ruy ao Centro é indicativa. A variante tem identidade própria mesmo onde compartilha corredor com a BRS-500. |
| **BRS-800 · Aeroporto–Bessa via BR-230** | Aeroporto Castro Pinto ↔ T. Oitizeiro ↔ T. Cristo no Almeidão ↔ T. UFPB ↔ Manaíra Shopping ↔ T. Bessa. Oitizeiro, Cristo e UFPB são entradas explícitas no itinerário. A BR-230 é o eixo principal. A geometria usa circuitos de entrada/saída e, no sentido Bessa → Shopping, a malha interna. |

### 5.2 Troncais · 2 serviços

| Código e nome | Itinerário e observações |
| --- | --- |
| **T-410 · Beira-Rio–Mangabeira** | T. Mangabeira ↔ eixo Antônio da Silva Mariz/Portal do Sol ↔ Altiplano ↔ Av. Beira-Rio ↔ Centro ↔ T. Metropolitano. Classificação vigente é troncal. |
| **T-610 · Mandacaru via Manaíra Shopping** | T. Bessa ↔ Manaíra Shopping ↔ Retão/Tancredo Neves ↔ Mandacaru ↔ Cidade Padre Zé ↔ Roger ↔ T. Metropolitano. Nos Ipês, use a Av. Presidente Tancredo Neves. As saídas por Coelho Paiva, João Brito de Lima Moura ou Sérgio Meira no modelo pertencem à transição para Mandacaru, conforme o sentido. |

**Decisão da T-610 entre Shopping e Bessa.** Sentido Bessa → Shopping, usar o caminho interno por Tertuliano Castro, setor de Campos Sales, Bacharel José de Oliveira Curchatuz, conexão com o Retão e Gumercindo, conforme a geometria salva. Distância roteada no contexto da linha de aproximadamente **4,83 km**. Sentido Shopping → Bessa, sair pela Gumercindo/Retão e seguir pela BR-230 até o acesso ao terminal, cerca de **4,97 km**. Na comparação do trecho isolado, a opção forçada pela rodovia no sentido Bessa → Shopping ficou em torno de **10,9 km** via retorno nos acessos testados. A opção interna explícita no sentido Shopping → Bessa pelo eixo Leocádio ficou em torno de **5,7 km**. As estimativas são de roteamento viário. Para avaliar tempo real, simule as conversões, velocidades, semáforos, paradas e restrições de ônibus. A assimetria é intencional.

### 5.3 Transversais · 3 serviços

| Código e nome | Itinerário e observações |
| --- | --- |
| **TRV-321 · Mangabeira–Orla** | T. Mangabeira ↔ Portal do Sol ↔ Altiplano ↔ Cabo Branco ↔ Tambaú ↔ orla de Manaíra ↔ **Retão** ↔ **Manaíra Shopping**, pela Gumercindo Barbosa Dunda ↔ T. Bessa. No segmento norte, a geometria desta linha considera Leocádio Ribeiro Coutinho e o interior de Jardim Oceania/Bessa. |
| **TRV-322 · Mangabeira–Cristo via Convenções e Estação Ciência** | Circular interterminal. T. Mangabeira → Hilton Souto Maior em direção à praia → desce ao Centro de Convenções → retorno da PB-008 → Boulevard dos Ipês → sobe pela Penha → Estação Ciência/Farol do Cabo Branco → retorna à Hilton Souto Maior → segue até o T. Cristo no Almeidão → volta pela Hilton Souto Maior ao T. Mangabeira. **Coqueiral, Josefa Taveira e Mangabeira VI/VII saíram deste circuito.** As ligações ao Centro de Convenções, Estação Ciência e aos dois terminais permanecem. |
| **TRV-721 · Valentina–Oitizeiro via Perimetral Sul** | NTI Valentina ↔ Av. Perimetral Sul ↔ BR-101 ↔ T. Oitizeiro. Preservar a natureza interterminal/transversal e os sentidos rodoviários. |

### 5.4 Integracionais · 5 serviços

| Código e nome | Itinerário e observações |
| --- | --- |
| **I-331 · Valentina I via Josefa Taveira** | T. Mangabeira ↔ Av. Josefa Taveira ↔ Valentina I ↔ NTI Valentina. É o código vigente do eixo direto pela Josefa. |
| **I-332 · Valentina via Paratibe e Parque do Sol** | T. Mangabeira ↔ Garrafão ↔ Trauminha ↔ Rua Francisco Porfírio Ribeiro ↔ Rua Severino Dias de Oliveira ↔ Rua Maria Inês Caetano de Oliveira ↔ **Rua Sibipiruna**, principal de Paratibe ↔ Rua Comerciante Félix Cahino ↔ Rua Humberto Maul ↔ Av. Jacarandá ↔ Muçumagro ↔ Rua Economista Clodoaldo Pinheiro de Araújo ↔ Rua Severina Ramos de Azevedo ↔ Rua Balbina Maria Ferreira ↔ Av. João Maria de Araújo ↔ **Parque do Sol** ↔ NTI Valentina. Traçado consolidado com uma única linha e cobertura da principal e dos bolsões internos. A Josefa Taveira não é o eixo de acesso da I-332. |
| **I-333 · Valentina II / Planalto** | T. Mangabeira ↔ Coqueiral na Alfredo Ferreira da Rocha ↔ Valentina II ↔ Planalto da Boa Esperança ↔ NTI Valentina. Preservar a função distinta de I-331 e I-332. |
| **I-334 · Circular UFPB via Três Ruas e Bancários** | T. Mangabeira → Av. Gov. Antônio da Silva Mariz → Av. Médico Industrial → Três Ruas → HU Lauro Wanderley → Castelo Branco → T. UFPB → CT/UFPB → principal dos Bancários e do Jardim Cidade Universitária → Josefa Taveira → Anízio de Azevedo Lima → Coqueiral/Alfredo Ferreira da Rocha → Hilton Souto Maior → T. Mangabeira. Castelo Branco entra entre HU e Terminal UFPB. O retorno ao terminal de Mangabeira é pelo Coqueiral/Hilton. |
| **I-731 · Valentina–Cristo via Geisel** | NTI Valentina ↔ conexão por eixos como Flodoaldo Peixoto Filho, Dr. Cícero Leite e Adalgisa Carneiro Cavalcanti, conforme o sentido ↔ **Geisel pela Av. Juscelino Kubitschek** ↔ Av. Valdemar Galdino Naziazeno ↔ T. Cristo no Almeidão. É uma linha de ida e volta. Os pontos atuais de Geisel são referência para o acesso. |

**Definições locais.** No projeto, **Coqueiral** quer dizer o eixo da Rua Comerciante Alfredo Ferreira da Rocha. A extensão efetivamente usada varia por linha e sentido. **Parque do Sol** é o nome escolhido para o recorte de Gramame atendido pela I-332. Não renomeie o bairro oficial de Gramame por inteiro e não confunda **Parque do Sol** com **Praia do Sol**, atendida pela L-751.

### 5.5 Regionais · 3 serviços

| Código e nome | Itinerário e observações |
| --- | --- |
| **R-241 · Circular Cristo via José Américo** | T. Cristo → José Américo em trecho de referência da atual 107 → Colibris, com acesso pela região da Av. Benício de Oliveira Lima → Jardim São Paulo → Água Fria → T. Cristo. É o sentido que entra primeiro em José Américo. |
| **R-242 · Circular Cristo via Água Fria** | T. Cristo → Água Fria → Jardim São Paulo → Rua Edmílson Leite da Silva → Cidade dos Colibris, entrando pela Rua Fernando Torres → José Américo → T. Cristo. Usa a ponte da Edmílson na geometria de proposta. A passagem depende de validação física e operacional de largura, estrutura, curva e acesso. A R-241 mantém seu próprio itinerário. |
| **R-343 · Circular Seixas–UFPB–Anatólia** | T. Mangabeira → Hilton Souto Maior sentido Penha → Seixas → Estação Cabo Branco → Portal do Sol → Rua Antônio Franciscano do Amaral → Ponte Altiplano/UFPB → HU → UFPB → Via Expressa Padre Zé → Rua Joaquim Borba Filho (Jardim São Paulo) → Anatólia → Rua Aurélio Menezes de Albuquerque → Alfredo Ferreira da Rocha → **Anízio de Azevedo Lima** → sobe a Josefa Taveira → Rua do Corujinha/Rodopiano Ferreira Nóbrega → Trauminha → Detran → T. Mangabeira. A saída pela Anízio antecede o final da Alfredo. Algumas bases grafam a rua como Anísio, preservar o alias. |

### 5.6 Locais · 3 serviços

| Código e nome | Itinerário e observações |
| --- | --- |
| **L-251 · Cristo–Rangel–Vale das Palmeiras** | Circular local. T. Cristo/Almeidão → Rangel, Av. 2 de Fevereiro → Vale das Palmeiras, Travessa Murilo Buarque e Rua Antônio Gomes da Silva → Rua Antônio Teotônio → T. Cristo. O serviço local usa ruas da linha atual 208 como referência de cobertura interna. |
| **L-351 · Cidade Verde II / Patrícia Tomaz** | T. Mangabeira ↔ acesso pela Alfredo Ferreira da Rocha ↔ Diógenes Gomes da Silva ↔ Corujinha/Rodopiano Ferreira Nóbrega ↔ desce a Josefa Taveira ↔ Rua Dr. Euclides Neiva de Oliveira ↔ Cidade Verde ↔ Rua Maria Regina Martins ↔ Av. Jatobá ↔ Três Marias/Patrícia Tomaz. Conservar as passagens pelas ruas de Cidade Verde II e o ramal que fecha a lacuna de Patrícia Tomaz. |
| **L-751 · Valentina–Barra de Gramame / Praia do Sol** | Circuito de ida e retorno ao NTI Valentina. Passa por Rua das Oliveiras, Rua Maria Ana Nunes e Rua dos Cedros → ponto de referência da I004 em Muçumagro → Av. Escritor Ramalho Leite → passagem pelo interior de Gramame/Rua Gutemberg de Souza, conforme a geometria → acesso à Barra de Gramame → retorno da Praia do Sol → NTI Valentina. Inspirada no trecho litorâneo da I004, com prolongamento ao NTI e cobertura interna de Muçumagro. |

### 5.7 Metropolitana · 1 serviço

| Código e nome | Itinerário e observações |
| --- | --- |
| **M-961 · Litoral Sul via PB-008** | Jacumã ↔ **PB-008** no trecho entre Jacumã e o acesso à Hilton ↔ trecho da **Av. Jacarandá** ↔ **acesso a Jacarapé** ↔ Hilton Souto Maior ↔ T. Mangabeira. A Av. Jacarandá e a José Félix da Silva aparecem como referências de trechos do eixo da PB-008. Mantém o trajeto rodoviário direto, sem entrar nas ruas internas de Muçumagro/Paratibe. Jacarapé é representada pelo acesso rodoviário. Se Penha e Polo Turístico forem exibidos em análise futura, diferencie um acesso junto ao eixo de uma entrada efetiva na comunidade. |

## 6. Histórico que explica a revisão

- A primeira organização usou `BRS-0100`, `0200`, `0300`, `0400`, `0500`, `0501`, `0600` e uma ligação pela BR-230 discutida sob os identificadores `BRS-0230` e `BRS-T230`. As categorias foram revistas. Os eixos Beira-Rio e Mandacaru passaram pelas denominações T-0400/T-0600 ou Troncal 400/600 e chegaram a **T-410/T-610**.
- A ligação **Aeroporto–Bessa/Cabedelo** foi limitada ao **Terminal Bessa** na primeira fase. Cabedelo passa a ser destino de conexão no Bessa, com expansão futura a estudar. A eventual união com a **5104** foi apresentada como opção, sem virar linha ativa. BRS-800 é o código atual da ligação aeroportuária. Nenhum código anterior da mesma função deve ocupar uma segunda entrada no inventário.
- **BRS-301 Mangabeira via Três Ruas** foi encerrada. A cobertura de Três Ruas é articulada com a I-334 e com a rede universitária.
- As transversais inicialmente numeradas 001, 002 e 003 evoluíram para **TRV-321** (Orla), **TRV-322** (Cristo e Hilton, depois acrescida do circuito Convenções/Penha/Farol) e **TRV-721** (Perimetral Sul).
- A antiga **TRV-004** deixou de ser uma única linha. Seu escopo foi desdobrado em ligações de Mangabeira para Valentina I/Josefa, Paratibe–Muçumagro–Parque do Sol, Coqueiral–Valentina II–Planalto e o recorte Bancários/UFPB/Castelo Branco. O pedido inicial do último ramal mencionava Portal do Sol, Três Ruas, HU, Castelo Branco e Terminal UFPB. O desenho vigente distribui esse atendimento entre a I-334, a R-343 e outros serviços já inventariados.
- **I-331 e I-332 tiveram seus códigos trocados explicitamente.** Na revisão atual, **331 = Josefa/Valentina I** e **332 = Garrafão/Paratibe/Parque do Sol**. Use essa atribuição em texto, fichas, mapa e banco de dados.
- O pedido de dividir a circular universitária produziu a **I-334 via Três Ruas/HU/Castelo Branco/UFPB/Bancários** e a **R-343 via Seixas/Estação Cabo Branco/Portal do Sol/ponte/UFPB/Anatólia**. Os trajetos se tocam em alguns polos e usam coberturas diferentes.
- **341 e 342 foram excluídas**. Solicitações anteriores de uma linha autônoma para Mangabeira por dentro, Cidade Verde/Mangabeira VII ou Bancários por dentro foram parcialmente absorvidas em linhas existentes no estudo. Qualquer alimentadora adicional nesses setores volta como hipótese baseada em lacuna demonstrada.
- O código inicial **M901** cedeu lugar a **M-961**. Uma descrição mais antiga com entradas internas por Muçumagro e Paratibe foi substituída pela diretriz da PB-008 direta.
- As duas novas linhas desta revisão são **I-731** e **L-251**. A BRS-800, R-242, R-343, TRV-321 e T-610 tiveram traçado alterado. A I-332 foi consolidada.

## 7. Cobertura, sobreposições e auditoria de destinos

### Relação entre filtros e terminais

O mapa abre com as 23 linhas. Tem filtros de BRS, Terminal Cristo e NTI Valentina, seleção de uma linha e dois comparativos da I-332. Há também um recorte de Mangabeira especificamente solicitado com exclusão de Litoral Sul, Orla, Beira-Rio e BRS. O recorte **de sete linhas** mostra **TRV-322, I-331, I-332, I-333, I-334, R-343 e L-351**. O terminal completo de Mangabeira tem **11** serviços conforme o inventário. A diferença é intencional. As listas do mapa e os rótulos de cada recorte devem ser coerentes com esse propósito.

### Josefa Taveira e Coqueiral

A leitura das ruas nomeadas nos passos do OSRM da versão vigente identifica os seguintes conjuntos. Comprimento e sentido variam por linha. Estes resultados tratam de geometria, sem prometer pontos de embarque ao longo de todo trecho.

- **Josefa Taveira, 4 linhas** na base roteada. I-331 e I-334 usam trechos longos. R-343 e L-351 usam o segmento entre a conexão ao Corujinha e a região de Anízio/Euclides.
- **Coqueiral/Alfredo Ferreira da Rocha, 4 linhas**. I-333, I-334, R-343 e L-351. A R-343 sai na Anízio, a L-351 usa o acesso à Diógenes, e os outros serviços têm seus ramais próprios.
- Confirme pelos passos por sentido. A antiga volta de teste da TRV-322 pelo Coqueiral/Josefa aparece em dados de estudo e deve permanecer fora da rede ativa. A I-332 e a M-961 têm papéis distintos em Paratibe. A I-332 dá cobertura local; a M-961 passa no eixo da PB-008.

### Lacunas e como verificar

- A triagem que precedeu as revisões encontrou pontos de referência em **Félix Cahino/Humberto Maul**, **Clodoaldo/Severina/Balbina/entorno do Parque do Sol** e **Cidade Verde II/Patrícia Tomaz**. Motivaram as alterações definitivas na I-332 e L-351. A Sibipiruna continuou prevista no eixo principal de Paratibe.
- O recorte das **Oliveiras/Maria Ana Nunes/Cedros** e o acesso à **Barra de Gramame/Praia do Sol** motivaram partes da L-751. O setor de **Jardim Cidade Universitária fora da principal**, áreas do **Planalto**, interior ampliado de **Gramame**, pontos de **Água Fria** e outros agrupamentos sinalizados merecem nova triagem com a versão de 23 linhas antes de qualquer conclusão.
- O script histórico selecionou paradas observadas dentro de bairros do recorte, mantidas quando havia geometria do serviço atual a menos de 95 m. Calculou distâncias planas ao segmento de referência, contou os casos acima de 300/400/500 m e agrupou pontos com DBSCAN, raio aproximado de 420 m, para inspecionar áreas. Esses valores são parâmetros exploratórios daquela triagem. As contagens antigas pertencem ao mapa histórico identificado no script, de antes dos últimos ajustes.
- Cobertura de rua, distância caminhável a parada, oferta de frequência e acesso a um destino são análises diferentes. Refaça a avaliação por pares origem–destino, considerando viagem direta, número e caminhabilidade das baldeações, tarifa, janela de serviço e janela de espera. Aproxime pontos à malha e teste barreiras como rodovia, vale, rio, desnível, marginais e travessias.
- Em comparações entre rede atual e proposta, alinhe o território e os destinos. Registre quais destinos continuam diretos, quais passam a depender do Terminal Mangabeira ou NTI Valentina, quais têm paradas próximas em outra linha e quais ficaram sem ligação plausível no recorte. Uma linha futura se justifica pela lacuna concreta e pelo custo do desvio, inclusive quando o destino já tem cobertura em outra parte da rede.

## 8. Especificação cartográfica e técnica

### Elementos a preservar

- Base geográfica municipal com **64 bairros** de João Pessoa, contornos municipais, **101 feições de hidrografia** processadas nesta revisão e corredores para orientação. Coordenadas WGS84 com ordem `[longitude, latitude]`. A projeção da interface é construída com **D3 Geo** e recalculada com a área e o filtro selecionados.
- Uma cor consistente **por linha**, aplicada na geometria e na legenda. Nos segmentos coincidentes, mostrar as linhas lado a lado. Use a geometria real de cada sentido. Colapsar traçados visualmente perto não autoriza simplificar o itinerário no dado.
- O mapa histórico usa projeção dinâmica, rótulos com prioridade e detecção de colisão, legenda de linhas visíveis, escala, detalhe da linha escolhida e comparação da I-332. A versão embutida em conversa dispõe de um fragmento HTML com limite de 1 MB e tokens de tema da interface. Em um projeto próprio, o mapa pode usar ativos locais e paginação de dados compatíveis com o ambiente.
- Nunca desenhe um trajeto ligando bairros por segmentos retos quando há geometria viária disponível. Caso algum trecho ainda não tenha geometria utilizável, identifique o ponto de incerteza, a respectiva referência e a validação necessária.
- Garanta legibilidade em desktop e celular, foco por teclado, legenda utilizável sem depender só de cores e detalhes visíveis sem hover. Evite rótulos redundantes e controles que não mudam a análise.

### Estrutura de dados e roteiro de geração

- `prepare.py` consolida pontos, rotas narrativas, basemap, histórico e comparativos. `ampliacao.py` concentra os corredores e ramais incrementados depois do recorte inicial. `rotear.py` carrega referências viárias, constrói listas ordenadas de waypoints e calcula rotas com OSRM.
- `malha-roteada.json` contém respostas de rota com passos, nomes das vias, chaves de waypoints, distâncias, geometria e coordenadas ajustadas à via. A chave principal usa o código de serviço. Em linhas bidirecionais a volta usa `<código>-volta`. Algumas chaves adicionais são **variantes históricas**. A lista ativa vem do catálogo, nunca de todas as chaves desse arquivo.
- `widget.html` é o template. A geração substitui `__MGB_DATA__` pelo JSON em `script#mgb-geodados`. Estrutura da carga. `routes[]` contém `code`, `type`, `name`, `itinerary`, `points`, `note`, `traces`. `places` associa chave a rótulo/coordenadas e opcionais `short` e `terminal`. `base` traz `land`, `neighborhoods`, `rivers`, `roads`. `comparisons` traz `before`, `after`, `points` e `stops` para Paratibe e Parque do Sol.
- Cada registro de sentido usa `LineString` no serviço de roteamento e vira uma lista ordenada no mapa. Na revisão atual, a interface compacta duplicatas, arredonda coordenadas do traço a 5 casas e aplica simplificação equivalente a Douglas–Peucker com tolerância de `0.000026°`, perto de 3 m. Retenha a versão não simplificada para auditoria geográfica.
- Para vias compartilhadas, o renderizador projeta os traçados e amostra os segmentos. A função `parallelTraces` agrupa trechos próximos com orientação compatível, aplica deslocamento lateral de exibição na ordem estável dos serviços e preserva pistas e sentidos. Cruzamentos quase perpendiculares não devem aparecer como sobreposições. Nunca exporte as linhas deslocadas em tela como se fossem a geometria viária.
- O OSRM foi usado com perfil `driving`, `steps=true`, `geometries=geojson`, `overview=full` e `continue_straight=true`, com pontos auxiliares por pista e retornos separados quando preciso. É referência de carro. Para ônibus, examine largura/gabarito, capacidade de ponte, inclinação e pavimento, conversão, retorno, parada, entrada pública/privada, risco de costurar alças e excesso de voltas. Conferir precisão do snap e a sequência de vias antes de atualizar.
- Na ida/volta simples, a lista reversa é gerada aplicando aliases de pistas aos pontos invertidos. Existem **retornos explícitos** para T-610 e BRS-800. Em circular, preserve a ordem completa, inclusive a passagem por retorno ou terminal intermediário. A L-751 tem trecho litorâneo de retorno no mesmo serviço. A TRV-322 passa no Cristo antes de fechar no Terminal Mangabeira.

### Testes e critérios de aceitação

1. O catálogo fecha em **6 BRS + 2 troncais + 3 transversais + 5 integracionais + 3 regionais + 3 locais + 1 metropolitana = 23 linhas**. Códigos únicos e dígito do tipo coerente.
2. O mapa apresenta 23 serviços na visão total, 6 no filtro BRS, 7 no Terminal Cristo, 6 no NTI Valentina e 7 no recorte local de Mangabeira. Cada linha deve aparecer sozinha ao ser selecionada. O filtro de terminal deve corresponder a parada/entrada efetiva no local.
3. Validar os sentidos, extremidades e intermediários mandatórios. Proteger especificamente a Sibipiruna e Parque do Sol da I-332, a Anízio da R-343, Gumercindo/Retão e Manaíra Shopping da TRV-321, a assimetria da T-610, a ponte da Edmílson na R-242, as entradas da BRS-800, o Geisel na I-731 e o Vale das Palmeiras na L-251.
4. A TRV-322 atende Convenções, Penha/Farol e Cristo, com retorno a Mangabeira pela Hilton, sem o circuito abandonado por Coqueiral/Josefa. A M-961 permanece no eixo da PB-008 em Paratibe/Muçumagro.
5. Conservar os comparativos antes/depois da I-332 com geometria e paradas observadas de referência distintas. Validar que as cores e deslocamentos funcionam mesmo em geometria invertida, que cruzamentos não geram sobreposição falsa e que não há caminhos SVG com `NaN`. A base foi testada em 320 e 736 px com DOM simulado.
6. Preservar o arquivo de referência ou histórico a cada mudança relevante. A geração deve funcionar com o cache de geometria e sem depender de recálculo da web. Novas chamadas de roteamento entram só quando uma rota mudar ou uma atualização for pedida. Use um diff entre geometrias, distâncias e pontos obrigatórios para revisar regressões.

## 9. Pendências e nível de certeza

- Implantação da prioridade de ônibus, posição de estações/paradas, faixa exclusiva por segmento, plataforma, circulação nos terminais e capacidade de embarque.
- Plano de serviço por sentido e período, frequências, horários de início/fim, frota, tempo de ciclo, pausa, regularidade e operação noturna. A extensão de linhas locais/circulares, em especial L-751, R-343, I-334 e TRV-322, pode exigir avaliação de ciclo e prioridade se a etapa avançar.
- Validação da ponte da Edmílson Leite da Silva, acessos do Almeidão, conexões rodoviárias nos viadutos da BR-230/BR-101 e a compatibilidade das conversões com ônibus. A geometria do retorno de acesso à BR-230 muda por sentido.
- Vínculo entre Terminal UFPB, HU, CT e o trecho de BRS-300. Conferir pontos exatos, posicionamento de paradas e conversões do campus. Revisar a conexão final da BRS-501 com o Centro e os acessos definitivos de Oitizeiro, Bessa, Valentina e Varadouro quando o mapa evoluir de estudo para projeto.
- Definir o desenho intermodal do Varadouro, incluindo a conexão a pé entre os três equipamentos e a integração com a linha ferroviária existente. Estudar eventual expansão para Cabedelo e relação com a 5104 depois de estabilizar a ligação ao Bessa.
- Refazer a auditoria de cobertura por destinos e acesso a paradas com o inventário de 23 linhas. Os documentos e mapas de versões anteriores são caixas de referência, com códigos e hipóteses que podem divergir da revisão.

## 10. Fontes e material de transferência

- [Filipeia · Mapas da Cidade de João Pessoa](https://filipeia.joaopessoa.pb.gov.br/) para cartografia urbana, bairros, hidrografia e corredores de referência. [IBGE · Malhas territoriais](https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais.html) para malhas municipais.
- [OpenStreetMap](https://www.openstreetmap.org/copyright) para a malha viária e os pontos de referência. [OSRM · Documentação da API de rotas](https://project-osrm.org/docs/v5.24.0/api/). [Ponte de referência na Edmílson](https://www.openstreetmap.org/way/917616313).
- [Semob-JP · Linhas de ônibus](https://servicos.semobjp.pb.gov.br/linhas-de-onibus/), [107 José Américo](https://servicos.semobjp.pb.gov.br/linhas-de-onibus/0107/itinerario/), [208 Cristo–Vale das Palmeiras](https://servicos.semobjp.pb.gov.br/linhas-de-onibus/0208/itinerario/), [I004 Integração/Praia do Sol](https://servicos.semobjp.pb.gov.br/linhas-de-onibus/I004/itinerario/), [E551 · referência de Geisel e Manaíra Shopping](https://servicos.semobjp.pb.gov.br/linhas-de-onibus/E551/itinerario/) e [itinerários do consórcio com 5600](https://servicos.semobjp.pb.gov.br/static/itinerarios/i_reunidas.pdf). Confirme atualizações quando comparar com o serviço em operação.
- [Ônibus em João Pessoa · Bus4/EMS Horários](https://s3.amazonaws.com/bus4.jpa.mapa/index.html) é a referência indicada nos metadados dos GeoJSON históricos de linhas e paradas. Guarde distinção entre geometrias originalmente publicadas e geometrias ajustadas por roteamento.
- [Prefeitura de João Pessoa · Av. Juscelino Kubitschek no Geisel](https://www.joaopessoa.pb.gov.br/noticias/cicero-lucena-autoriza-obras-para-transformar-avenida-principal-do-geisel-em-parque-linear-com-vias-duplicadas-polo-gastronomico-e-terminal-de-transporte/) para o eixo viário usado pela I-731. [CBTU João Pessoa · mapa, horários e serviços](https://www.gov.br/cbtu/pt-br/servicos/cbtu-joao-pessoa) para o eixo ferroviário existente.
- O pacote `mobilidade-jp-projeto-codex.zip` acompanha este prompt. Contém mapa navegável, fragmento da revisão, catálogo extraído, geometrias, dados de base, histórico de comparação, código e instruções de reprodução. Comece pelo `README.md` do pacote. Se só tiver este texto, o apêndice fornece as sequências por sentido para transferência manual. Dados geográficos e operacionais têm proveniência própria. Preserve a atribuição ao redistribuir ou publicar.

## Apêndice A · Waypoints e extensões por sentido

Estas chaves reproduzem as sequências guardadas no cache da revisão. A tabela complementa os itinerários de leitura humana. O traço renderizado pode simplificar pontos intermediários. Ida e volta aparecem em linhas distintas da tabela. Em serviços circulares há uma sequência completa. Os valores são distâncias geométricas aproximadas do OSRM.

| Linha e sentido | Distância (km) | Waypoints em ordem de circulação |
| --- | ---: | --- |
| BRS-100 · ida | 8,88 | `oitizeiro cruz joao_gama jaguaribe metro` |
| BRS-100 · volta | 8,94 | `metro jaguaribe_back joao_gama cruz_back oitizeiro_back` |
| BRS-200 · ida | 9,76 | `cristo rangel joao_gama jaguaribe metro` |
| BRS-200 · volta | 10,97 | `metro jaguaribe_back joao_gama rangel_back cristo` |
| BRS-300 · ida | 15,26 | `hub hilton_leste jcu_main bancarios_main ct_public ufpb_dp2 pedro metro` |
| BRS-300 · volta | 13,77 | `metro pedro_back ufpb_dp2_back ct_public bancarios_main jcu_main_back hilton_leste_back hub` |
| BRS-500 · ida | 17,32 | `bessa aeroc manaira_eixo tambau_500 epitacio metro` |
| BRS-500 · volta | 18,20 | `metro epitacio_back tambau_500_back manaira_eixo aeroc bessa` |
| BRS-501 · ida | 16,60 | `bessa aeroc manaira_eixo tambau_eixo ruy metro` |
| BRS-501 · volta | 17,37 | `metro ruy_back ruy_tambau_back manaira_eixo aeroc bessa` |
| BRS-800 · ida | 34,27 | `aeroporto oitizeiro cristo universidade_public shopping br230_norte bessa` |
| BRS-800 · volta | 35,03 | `bessa shopping br230_shopping_sul universidade_public cristo oitizeiro_back aeroporto` |
| T-410 · ida | 15,81 | `hub mariz portal_arterial altiplano_arterial beira beira_oeste centro_lagoa metro` |
| T-410 · volta | 17,44 | `metro centro_lagoa beira_oeste_back beira_back altiplano_arterial portal_arterial mariz hub` |
| T-610 · ida | 11,88 | `bessa shopping retao_oeste ipes mandacaru padreze_bairro roger metro` |
| T-610 · volta | 15,05 | `metro roger padreze_bairro mandacaru_back ipes_back shopping br230_norte bessa` |
| TRV-321 · ida | 17,83 | `hub mariz portal_arterial altiplano_arterial cabo_atlantico tambau_beira manaira_beira retao_orla shopping leocadio bessa` |
| TRV-321 · volta | 20,84 | `bessa leocadio_back shopping retao_orla_back manaira_beira_back tambau_beira_back cabo_atlantico_back altiplano_arterial portal_arterial mariz hub` |
| TRV-322 · circuito | 32,72 | `hub hilton_penha convencoes_public retorno_convencoes boulevard penha_arterial farol_public hilton_east hilton_leste hilton_west cristo hilton_west_back hilton_leste_back hub` |
| TRV-721 · ida | 11,73 | `val perimetral_leste perimetral br101 oitizeiro` |
| TRV-721 · volta | 14,85 | `oitizeiro_back br101_back perimetral_back perimetral_leste_back val` |
| I-331 · ida | 9,20 | `hub hilton_leste josefa val1 val` |
| I-331 · volta | 8,44 | `val val1 josefa hilton_leste_back hub` |
| I-332 · ida | 22,43 | `hub garrafao trauminha porfirio severino_dias maria_ines paratibe felix_leste felix_oeste humberto jacaranda mucu clodoaldo severina balbina joao_maria parque val` |
| I-332 · volta | 21,80 | `val parque joao_maria balbina severina clodoaldo mucu jacaranda humberto felix_oeste felix_leste paratibe maria_ines severino_dias porfirio trauminha garrafao hub` |
| I-333 · ida | 14,15 | `hub hilton coqueiral val2 planalto val` |
| I-333 · volta | 14,35 | `val planalto val2 coqueiral hilton_back hub` |
| I-334 · circuito | 26,53 | `hub mariz medico tres hu_public castelo_via universidade_public ct_public principal principal_jcu josefa josefa_sul anizio alfredo_meio alfredo_inicio hilton_leste_back hub` |
| I-731 · ida | 7,37 | `val geisel cristo` |
| I-731 · volta | 8,17 | `cristo geisel val` |
| R-241 · circuito | 14,85 | `cristo jose_estevao geni jose_americo colibris_acesso colibris jardim_sp agua_fria cristo` |
| R-242 · circuito | 12,96 | `cristo agua_fria jardim_sp edmilson colibris colibris_acesso jose_americo geni jose_estevao cristo` |
| R-343 · circuito | 30,80 | `hub hilton_penha seixas_public farol_public portal_arterial amaral ponte hu_public padre borba anatolia aurelio alfredo_inicio alfredo_meio anizio josefa_sul corujinha trauminha detran hub` |
| L-251 · circuito | 8,86 | `cristo rangel vale_murilo vale_palmeiras vale_sul cristo` |
| L-351 · ida | 13,34 | `hub hilton alfredo_inicio diogenes corujinha josefa_sul euclides creuza herotildes maria_regina_oeste maria_regina_leste jatoba patricia` |
| L-351 · volta | 14,17 | `patricia jatoba maria_regina_leste maria_regina_oeste herotildes creuza euclides josefa_sul corujinha diogenes_back alfredo_inicio hilton_back hub` |
| L-751 · circuito | 20,08 | `val oliveiras maria_ana cedros mucu_terminal ramalho gramame_interior gutemberg barra praia_sol barra ramalho_back mucu_terminal cedros maria_ana oliveiras val` |
| M-961 · ida | 23,25 | `hub hilton_penha pb008 jacuma` |
| M-961 · volta | 24,76 | `jacuma pb008 hilton_east hub` |

## Apêndice B · Coordenadas dos waypoints de roteamento

Os valores abaixo seguem a ordem longitude, latitude. São referências para o traçado, inclusive para escolher pista, conversão e retorno. Alguns têm o mesmo nome do marcador, com coordenada ligeiramente diferente. O pacote mantém os marcadores em `dados/catalogo.json`.

| Chave | Longitude | Latitude |
| --- | ---: | ---: |
| `aeroc` | -34.833850 | -7.086900 |
| `aeroporto` | -34.949368 | -7.144681 |
| `agua_fria` | -34.853839 | -7.155985 |
| `alfredo_inicio` | -34.842086 | -7.162515 |
| `alfredo_meio` | -34.844353 | -7.176522 |
| `altiplano_arterial` | -34.823370 | -7.134560 |
| `amaral` | -34.827200 | -7.135533 |
| `anatolia` | -34.843373 | -7.150303 |
| `anizio` | -34.845559 | -7.181781 |
| `aurelio` | -34.841509 | -7.155677 |
| `balbina` | -34.847970 | -7.221280 |
| `bancarios_main` | -34.843550 | -7.148250 |
| `barra` | -34.810690 | -7.218637 |
| `beira` | -34.853189 | -7.127920 |
| `beira_back` | -34.853051 | -7.127965 |
| `beira_oeste` | -34.868454 | -7.124139 |
| `beira_oeste_back` | -34.868758 | -7.124122 |
| `bessa` | -34.845409 | -7.063077 |
| `borba` | -34.851788 | -7.150793 |
| `boulevard` | -34.800438 | -7.188063 |
| `br101` | -34.901216 | -7.182817 |
| `br101_back` | -34.901342 | -7.182784 |
| `br230_norte` | -34.848083 | -7.093684 |
| `br230_shopping_sul` | -34.843729 | -7.107469 |
| `cabo_atlantico` | -34.823910 | -7.120530 |
| `cabo_atlantico_back` | -34.823875 | -7.124618 |
| `castelo_via` | -34.841009 | -7.129246 |
| `cedros` | -34.836292 | -7.215145 |
| `centro_lagoa` | -34.878790 | -7.122310 |
| `clodoaldo` | -34.844781 | -7.220145 |
| `colibris` | -34.850070 | -7.168002 |
| `colibris_acesso` | -34.852422 | -7.168584 |
| `convencoes_public` | -34.802040 | -7.188500 |
| `coqueiral` | -34.844954 | -7.174141 |
| `corujinha` | -34.839205 | -7.179098 |
| `creuza` | -34.841390 | -7.184530 |
| `cristo` | -34.874973 | -7.166678 |
| `cruz` | -34.891647 | -7.145327 |
| `cruz_back` | -34.891760 | -7.144830 |
| `ct_public` | -34.850520 | -7.145310 |
| `detran` | -34.826784 | -7.165508 |
| `diogenes` | -34.836105 | -7.176872 |
| `diogenes_back` | -34.834373 | -7.176914 |
| `edmilson` | -34.846457 | -7.154643 |
| `epitacio` | -34.841014 | -7.119548 |
| `epitacio_back` | -34.829047 | -7.119509 |
| `euclides` | -34.843189 | -7.183082 |
| `farol_public` | -34.798790 | -7.148420 |
| `felix_leste` | -34.837733 | -7.207447 |
| `felix_oeste` | -34.840035 | -7.205289 |
| `garrafao` | -34.834260 | -7.167390 |
| `geisel` | -34.869202 | -7.179934 |
| `geni` | -34.858571 | -7.172869 |
| `gramame_interior` | -34.811550 | -7.225680 |
| `gutemberg` | -34.806561 | -7.229739 |
| `herotildes` | -34.825280 | -7.182350 |
| `hilton` | -34.843170 | -7.161840 |
| `hilton_back` | -34.844090 | -7.162260 |
| `hilton_east` | -34.803080 | -7.160970 |
| `hilton_leste` | -34.831580 | -7.163150 |
| `hilton_leste_back` | -34.831380 | -7.163310 |
| `hilton_penha` | -34.815950 | -7.160490 |
| `hilton_west` | -34.848470 | -7.163785 |
| `hilton_west_back` | -34.848840 | -7.164140 |
| `hu_public` | -34.840920 | -7.134390 |
| `hub` | -34.821910 | -7.160790 |
| `humberto` | -34.841380 | -7.205890 |
| `ipes` | -34.853531 | -7.098117 |
| `ipes_back` | -34.853515 | -7.098374 |
| `jacaranda` | -34.827845 | -7.208137 |
| `jacuma` | -34.803874 | -7.286346 |
| `jaguaribe` | -34.878950 | -7.133023 |
| `jaguaribe_back` | -34.878820 | -7.134570 |
| `jardim_sp` | -34.851788 | -7.150793 |
| `jatoba` | -34.815133 | -7.179780 |
| `jcu_main` | -34.838560 | -7.153010 |
| `jcu_main_back` | -34.838840 | -7.152480 |
| `joao_gama` | -34.878821 | -7.132608 |
| `joao_maria` | -34.846198 | -7.218445 |
| `jose_americo` | -34.857973 | -7.169909 |
| `jose_estevao` | -34.855659 | -7.173651 |
| `josefa` | -34.840559 | -7.175545 |
| `josefa_sul` | -34.842627 | -7.180935 |
| `leocadio` | -34.840240 | -7.084110 |
| `leocadio_back` | -34.840190 | -7.084243 |
| `manaira_beira` | -34.831614 | -7.101683 |
| `manaira_beira_back` | -34.833411 | -7.096980 |
| `manaira_eixo` | -34.834628 | -7.096148 |
| `mandacaru` | -34.864038 | -7.103369 |
| `mandacaru_back` | -34.863901 | -7.103465 |
| `maria_ana` | -34.835488 | -7.213617 |
| `maria_ines` | -34.834758 | -7.196606 |
| `maria_regina_leste` | -34.816036 | -7.177958 |
| `maria_regina_oeste` | -34.820153 | -7.177516 |
| `mariz` | -34.818328 | -7.154738 |
| `medico` | -34.828507 | -7.143348 |
| `metro` | -34.890918 | -7.116089 |
| `mucu` | -34.840565 | -7.224321 |
| `mucu_terminal` | -34.831580 | -7.216090 |
| `oitizeiro` | -34.896326 | -7.161357 |
| `oitizeiro_back` | -34.896406 | -7.161527 |
| `oliveiras` | -34.838180 | -7.212533 |
| `padre` | -34.848724 | -7.134448 |
| `padreze_bairro` | -34.870026 | -7.106306 |
| `paratibe` | -34.830231 | -7.204441 |
| `parque` | -34.848080 | -7.216410 |
| `patricia` | -34.815163 | -7.184128 |
| `pb008` | -34.812570 | -7.264359 |
| `pedro` | -34.882242 | -7.122249 |
| `pedro_back` | -34.879173 | -7.122678 |
| `penha_arterial` | -34.798080 | -7.163460 |
| `perimetral` | -34.897653 | -7.194728 |
| `perimetral_back` | -34.891482 | -7.194984 |
| `perimetral_leste` | -34.849232 | -7.207313 |
| `perimetral_leste_back` | -34.847778 | -7.207660 |
| `planalto` | -34.859921 | -7.196144 |
| `ponte` | -34.835571 | -7.137336 |
| `porfirio` | -34.839140 | -7.186600 |
| `portal_arterial` | -34.816890 | -7.150210 |
| `praia_sol` | -34.804881 | -7.215890 |
| `principal` | -34.843550 | -7.148250 |
| `principal_jcu` | -34.838620 | -7.155110 |
| `ramalho` | -34.825221 | -7.223076 |
| `ramalho_back` | -34.824139 | -7.223406 |
| `rangel` | -34.874132 | -7.148076 |
| `rangel_back` | -34.874020 | -7.147850 |
| `retao_oeste` | -34.844545 | -7.097806 |
| `retao_orla` | -34.840405 | -7.097568 |
| `retao_orla_back` | -34.840405 | -7.097623 |
| `retorno_convencoes` | -34.804480 | -7.193060 |
| `roger` | -34.874808 | -7.107512 |
| `ruy` | -34.832516 | -7.114281 |
| `ruy_back` | -34.841350 | -7.118760 |
| `ruy_tambau_back` | -34.825805 | -7.110988 |
| `seixas_public` | -34.795380 | -7.156070 |
| `severina` | -34.846040 | -7.222100 |
| `severino_dias` | -34.835396 | -7.195769 |
| `shopping` | -34.844290 | -7.095050 |
| `tambau_500` | -34.825170 | -7.119290 |
| `tambau_500_back` | -34.826280 | -7.119500 |
| `tambau_beira` | -34.822799 | -7.112354 |
| `tambau_beira_back` | -34.823214 | -7.117063 |
| `tambau_eixo` | -34.825842 | -7.110921 |
| `trauminha` | -34.836865 | -7.175782 |
| `tres` | -34.833418 | -7.149898 |
| `ufpb_dp2` | -34.858159 | -7.135352 |
| `ufpb_dp2_back` | -34.858198 | -7.135423 |
| `universidade_public` | -34.845530 | -7.138220 |
| `val` | -34.847347 | -7.204896 |
| `val1` | -34.845128 | -7.198773 |
| `val2` | -34.850000 | -7.200000 |
| `vale_murilo` | -34.883125 | -7.160230 |
| `vale_palmeiras` | -34.884220 | -7.160350 |
| `vale_sul` | -34.885882 | -7.164634 |

---

**Fim do contexto de transferência.** Aplique a próxima solicitação à revisão descrita acima.
