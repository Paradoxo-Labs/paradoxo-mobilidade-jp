# Integração do estudo complementar de rede integrada

## Origem e escopo

Em 21/11/2026, o pacote fornecido pelo usuário `mobilidade-jp-projeto-codex.zip` foi incorporado à parte da proposta BRS/BHLS. A revisão declarada no pacote é de **21 de novembro de 2026**.

Os 50 arquivos originais foram preservados, sem alteração de conteúdo, em [estudos/rede-integrada-2026-11-21](estudos/rede-integrada-2026-11-21/README.md). Apenas a pasta externa `joao-pessoa-mobilidade` foi substituída pelo caminho do estudo no repositório. O conjunto tem 39.972.643 bytes descompactados.

SHA-256 do ZIP recebido: `38eda8264b3e160043312dfc000b5f422a43280a0de52963e8bdae150e1aaa09`.

O pacote é um estudo complementar, não uma rede oficial, um projeto executivo ou uma substituição automática do [conceito inicial](CONTEXTO_COMPLETO.md). A classificação de uma linha como BRS não comprova prioridade viária implantável em todo o percurso. Distâncias e geometrias roteadas são referências de modelagem e exigem validação para ônibus.

O arquivo `mobilidade-jp-prompt-codex.md` foi preservado como documentação de origem. Suas instruções e decisões pertencem ao contexto do projeto paralelo; não constituem instruções globais para agentes nem decisões automaticamente aprovadas para o Paradoxo Mobilidade JP.

## Material disponível

| Material | Conteúdo e uso |
| --- | --- |
| [Mapa offline](estudos/rede-integrada-2026-11-21/mapa.html) | HTML autônomo com D3 e dados embutidos; abrir em navegador moderno |
| [Catálogo](estudos/rede-integrada-2026-11-21/dados/catalogo.json) | 23 linhas, locais de referência, itinerários, notas e sentidos |
| [GeoJSON](estudos/rede-integrada-2026-11-21/dados/linhas-por-sentido.geojson) | 39 geometrias viárias de referência, sem deslocamento gráfico |
| [Waypoints](estudos/rede-integrada-2026-11-21/dados/waypoints-roteamento.json) | Pontos usados para orientar os percursos; não equivalem a paradas |
| [Base cartográfica](estudos/rede-integrada-2026-11-21/dados/base-cartografica.json) | Municípios, bairros, hidrografia e corredores de referência |
| [Comparativos I-332](estudos/rede-integrada-2026-11-21/dados/comparativos-i332.json) | Comparações históricas dos recortes Paratibe e Parque do Sol |
| [Geração e testes](estudos/rede-integrada-2026-11-21/README.md) | Scripts Python, template do mapa e verificação em Node.js |
| Histórico e comparação com rede observada | Versões anteriores, triagem e referências externas preservadas nas pastas `historico/` e `mapa/comparacao-atual/` |

Os 39 traçados contam ida/volta das linhas bidirecionais e um percurso completo para cada circular. Não são 39 linhas. Registros do cache `mapa/malha-roteada.json` ausentes do catálogo são testes ou variantes históricas, não serviços ativos do estudo.

## Inventário do estudo importado

Distribuição: 6 BRS, 2 troncais, 3 transversais, 5 integracionais, 3 regionais, 3 locais e 1 metropolitana.

| Código | Classe | Itinerário de referência |
| --- | --- | --- |
| BRS-100 | brs | T. Oitizeiro → Cruz das Armas → Jaguaribe → Centro → Terminal Metropolitano |
| BRS-200 | brs | T. Cristo (Almeidão) → Rangel → Jaguaribe → Centro → Terminal Metropolitano |
| BRS-300 | brs | T. Mangabeira → Jardim Cidade Universitária / Bancários → UFPB → Dom Pedro II → Centro → T. Metropolitano |
| BRS-500 | brs | T. Bessa → Aeroclube / Jardim Oceania → Manaíra → Tambaú → Epitácio Pessoa → Centro → Terminal Metropolitano |
| BRS-501 | brs | T. Bessa → Aeroclube / Jardim Oceania → Manaíra → Tambaú → Ruy Carneiro → Centro → Terminal Metropolitano |
| BRS-800 | brs | Aeroporto Castro Pinto → T. Oitizeiro → T. Cristo (Almeidão) → T. UFPB → Manaíra Shopping → T. Bessa |
| T-410 | troncal | T. Mangabeira → Portal do Sol → Altiplano → Beira-Rio → Centro → T. Metropolitano |
| T-610 | troncal | T. Bessa → Manaíra Shopping → Av. Tancredo Neves (Ipês) → Mandacaru → Cidade Padre Zé → Roger → Terminal Metropolitano |
| TRV-321 | transversal | T. Mangabeira → Portal do Sol → Altiplano → Cabo Branco → Tambaú → Manaíra → Retão → Manaíra Shopping → T. Bessa |
| TRV-322 | transversal | T. Mangabeira → Hilton Souto Maior, sentido praia → Centro de Convenções → retorno → Boulevard dos Ipês → Penha → Estação Ciência / Farol → Hilton Souto Maior → T. Cristo (Estádio Almeidão) → Hilton Souto Maior → T. Mangabeira |
| TRV-721 | transversal | NTI Valentina → Perimetral Sul → BR-101 → T. Oitizeiro |
| I-331 | integracional | T. Mangabeira → Josefa Taveira → Valentina I → NTI Valentina |
| I-332 | integracional | T. Mangabeira → Garrafão → Trauminha → Francisco Porfírio Ribeiro → Severino Dias de Oliveira → Maria Inês Caetano de Oliveira → Sibipiruna → Félix Cahino → Humberto Maul → Av. Jacarandá → Muçumagro → Clodoaldo Pinheiro → Severina Ramos → Balbina Ferreira → João Maria de Araújo → Parque do Sol → NTI Valentina |
| I-333 | integracional | T. Mangabeira → Coqueiral → Valentina II → Planalto da Boa Esperança → NTI Valentina |
| I-334 | integracional | T. Mangabeira → Av. Gov. Antônio da Silva Mariz → Av. Médico Industrial → Três Ruas → HU → Castelo Branco → T. UFPB → CT/UFPB → Principal dos Bancários / Jd. Cidade Universitária → Josefa Taveira → R. Anízio de Azevedo Lima → Alfredo F. da Rocha (Coqueiral) → Hilton Souto Maior → T. Mangabeira |
| I-731 | integracional | NTI Valentina ↔ Geisel (Av. Juscelino Kubitschek) ↔ T. Cristo (Almeidão) |
| R-241 | regional | T. Cristo (Almeidão) → José Américo (trecho da 107) → Colibris → Jardim São Paulo → Água Fria → T. Cristo |
| R-242 | regional | T. Cristo (Almeidão) → Água Fria → Jardim São Paulo → R. Edmílson Leite da Silva → Colibris (R. Fernando Torres) → José Américo → T. Cristo |
| R-343 | regional | T. Mangabeira → Hilton Souto Maior, sentido Penha → Seixas → Estação Cabo Branco → Portal do Sol → R. Antônio Franciscano do Amaral → Ponte Altiplano–UFPB → HU → UFPB → Via Expressa Padre Zé → R. Joaquim Borba Filho (Jardim São Paulo) → Anatólia → Aurélio Menezes de Albuquerque → Alfredo F. da Rocha → R. Anízio de Azevedo Lima → Josefa Taveira → R. do Corujinha → Trauminha → Detran → T. Mangabeira |
| L-251 | local | T. Cristo (Almeidão) → Rangel (Av. 2 de Fevereiro) → Vale das Palmeiras (Tv. Murilo Buarque / R. Antônio Gomes da Silva) → T. Cristo |
| L-351 | local | T. Mangabeira → acesso pela Alfredo F. da Rocha → Diógenes Gomes da Silva → R. do Corujinha → Josefa Taveira → Dr. Euclides Neiva de Oliveira → Cidade Verde → R. Maria Regina Martins → Av. Jatobá → Três Marias / Patrícia Tomaz |
| L-751 | local | NTI Valentina → Oliveiras / Maria Ana Nunes / Cedros → antigo ponto da I004 em Muçumagro → Av. Escritor Ramalho Leite → acesso à Barra de Gramame → Praia do Sol → NTI Valentina |
| M-961 | metropolitana | Jacumã → PB-008 → trecho da Av. Jacarandá → acesso a Jacarapé → Hilton Souto Maior → T. Mangabeira |

## Relação com o conceito inicial

As aproximações abaixo são funcionais. Não constituem conversão definitiva de códigos nem equivalência de itinerários.

| Tema | Conceito inicial | Estudo complementar | Encaminhamento |
| --- | --- | --- | --- |
| Classes e códigos | E/P/A/I/X/M; I significa interterminal | BRS/T/TRV/I/R/L/M; I significa integracional | Criar matriz de correspondência por função e trecho; preservar identificadores de cada estudo |
| Expresso e parador | Serviços E e P por corredor | Catálogo sem pares E/P por corredor | Definir padrões de parada antes de assumir equivalência operacional |
| Corredores Cruz das Armas, Cristo e Pedro II | Corredores 1, 2 e 3 | BRS-100, BRS-200 e BRS-300 | Comparar os traçados por sentido e acessos aos terminais |
| Eixo Epitácio | Corredor 5 | BRS-500 e BRS-501, esta com Ruy Carneiro | Avaliar funções e sobreposição das duas variantes |
| Beira-Rio e Mandacaru | Corredores 4 e 6 com E/P | T-410 e T-610, classificados como troncais | Conciliar classificação e prioridade viária por segmento |
| Centro e Via Oeste | Corredores 0 e 7 | Sem serviços estruturais próprios correspondentes no catálogo de 23 linhas | Manter como temas pendentes; ausência não significa descarte aprovado |
| Valentina | Terminal Valentina | NTI Valentina, sem BRS nesta revisão | Definir papel, infraestrutura e acessos |
| Terminal UFPB | UFPB como estação/polo de integração | Terminal de referência compartilhado por BRS-800 e I-334 | Conferir acesso ao campus, HU, CT, conversões e paradas |
| Aeroporto / BR-230 | X-01 até Intermares/Cabedelo | BRS-800 termina no Bessa | Extensão a Cabedelo permanece hipótese a estudar |
| Ligação litorânea | I-10 Mangabeira–Bessa | TRV-321 Mangabeira–Orla–Bessa | Comparar percursos, destinos e integração |
| Interterminais | I-01 a I-07 | Ligações distribuídas entre TRV e I, algumas circulares | Comparar funções; não renomear por semelhança numérica |
| Metropolitana sul | M-06 Jacumã–Mangabeira e outras metropolitanas | M-961 Jacumã–Mangabeira; demais metropolitanas fora do catálogo | Avaliar cobertura e articulação regional sem supor rede completa |
| Ferrovia | Integração com CBTU a estudar | Diretriz de modernização do eixo existente e integração no Varadouro | Manter como camada de estudo; não há novo VLT ou metrô aprovado |

O estudo complementar detalha referências de localização como Mangabeira na antiga Contax, Cristo no Almeidão e Oitizeiro na feira. São referências geográficas de modelagem, não terrenos, plataformas ou obras aprovados.

## Como consultar e reproduzir

Abra o [mapa.html](estudos/rede-integrada-2026-11-21/mapa.html) diretamente no navegador. A consulta ao mapa fornecido não requer instalação nem acesso à internet.

Para reproduzir, execute os comandos a partir da raiz deste repositório:

```sh
python3 docs/proposta-brs-bhls/estudos/rede-integrada-2026-11-21/mapa/prepare.py
python3 docs/proposta-brs-bhls/estudos/rede-integrada-2026-11-21/mapa/abrir.py
npm ci --ignore-scripts --prefix docs/proposta-brs-bhls/estudos/rede-integrada-2026-11-21/mapa
node docs/proposta-brs-bhls/estudos/rede-integrada-2026-11-21/mapa/check.cjs
```

A geração Python utiliza os dados locais. A instalação das dependências dos testes requer acesso ao npm quando não houver cache. O script `mapa/rotear.py` é uma operação separada: consulta OSRM e sobrescreve o cache de rotas; não faz parte da simples reprodução offline.

## Validação da incorporação

- Conferidos os 50 arquivos contra o ZIP, byte a byte.
- Todos os arquivos JSON/GeoJSON foram analisados sem erro.
- Conferidas 23 linhas e 39 geometrias, com correspondência das chaves de sentido entre catálogo e GeoJSON e coordenadas dentro dos limites geográficos.
- Executados `prepare.py` e `abrir.py` em cópia temporária. Ambos os HTMLs reproduzidos são idênticos aos recebidos; a geração informa 64 bairros e 101 elementos de hidrografia.
- Executado `mapa/check.cjs` com Node.js 22 e dependências do lockfile, em cópia temporária: passaram as verificações das 23 linhas, filtros, seleções, cores, sobreposições e comparativos de Paratibe/Parque do Sol nas larguras de 320 e 736 pixels.
- Conferidos os links locais da documentação de integração e a formatação do diff com `git diff --check`.

Essas verificações comprovam integridade e reprodução técnica. Não validam demanda, cobertura, legalidade de conversões ou viabilidade de operação.

## Próximos passos de consolidação

1. Elaborar matriz entre códigos, funções e trechos dos dois estudos.
2. Validar referências da rede observada com coleta atualizada da SEMOB-JP. A triagem histórica do pacote não deve ser apresentada como auditoria das 23 linhas vigentes do estudo.
3. Refazer análise de cobertura por destinos, acesso a paradas e sentidos; verificar sobreposições pelo trecho e função atendida.
4. Validar acessos aos terminais e campus, ponte da Edmílson, conversões e ligações nos viadutos da BR-230/BR-101 para circulação de ônibus.
5. Definir paradas, frequências, frota, ciclos, integração tarifária e fases de implantação.
6. Consolidar uma versão única da proposta após resolver as diferenças documentadas.

## Fontes e publicação

As fontes declaradas no pacote incluem Filipeia, IBGE, OpenStreetMap, OSRM, Bus4/EMS Horários e SEMOB-JP. As atribuições originais permanecem no README, no prompt e nos mapas importados. A incorporação não revalida a atualidade das referências externas.

O conjunto documental congelado é uma exceção delimitada à política padrão sobre caches e dados brutos, registrada em [PUBLICATION_POLICY.md](../PUBLICATION_POLICY.md). Novas coletas e artefatos de execução continuam sujeitos à política normal. As condições das fontes externas precisam ser verificadas antes de publicação; a integração local não publica os arquivos em nenhum serviço.
