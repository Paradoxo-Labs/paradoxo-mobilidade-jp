# Revisão da proposta por corredores e rede observada

O gerador `revise.py` prepara os 41 sentidos dos 24 serviços da proposta. `policies.py` explicita as referências territoriais e restrições por serviço. A M-961 preserva exatamente as geometrias originais.

Na raiz:

```sh
python3 apps/planner/revise.py
python3 -m unittest discover -s apps/planner/tests -v
docker compose up -d --build --wait
```

As entradas locais são `data/processed/semob/latest.json`, `data/raw/cartografia/osm-revisao-rotas.json` e o estudo importado versionado. A auditoria identifica consulta OSM, hashes dos dados e das regras. Os resultados são gravados em `docs/proposta-brs-bhls/revisao-atual`, separados do estudo original; dados brutos não entram no Git.

O atlas serve os resultados versionados. O gerador roda no host; o container mantém os arquivos da aplicação somente leitura.

## Regras de circulação

- Grafo dirigido OSM, mãos únicas e exceções explícitas de ônibus. Acesso privado/proibido, estacionamento interno e vias não motorizadas são excluídos.
- Interior do campus e `Via UFPB` bloqueados, preservando ruas públicas de contorno e a baia da Estação Cidade Universitária. Os giradores públicos CCHLA/CT não são ruas internas do campus.
- Distância, vias estruturantes e continuidade dos corredores prevalecem. A concentração SEMOB varia o custo de cada segmento em até 8%; não deve induzir voltas por ruas paralelas. Códigos contam uma única vez, sem confundir variantes com linhas adicionais.
- Referências admitem alternativas próximas na pista correta. Corredores nomeados procuram candidatos na própria avenida. A T-410 permanece na Beira-Rio até a ligação com o Altiplano. T-610/TRV-321 não usam BR-230; BRS-800 usa a rodovia após Cidade Universitária e evita o interior do Castelo Branco.
- Trechos centrais da 0301 preservam os acessos do TIV por sentido. A saída é estendida pela circulação pública da Lagoa até suas plataformas. A referência da Lagoa é o Terminal de Passageiros, não o centro do parque.
- Cristo no terminal atual das 204/208. Oitizeiro no terreno adjacente ao novo mercado: marcador do mercado separado da conexão viária aproximada, com entrada no lote ainda dependente de planta.
- I-332 liga Muçumagro ao terminal sem circular no Parque do Sol; L-751 assume esse atendimento. R-241/242 ampliam José Américo e entram no Colibris. L-251 alcança IFPB/Jaguaribe e amplia cobertura local com referências 204/208/203; a antiga 201 não está nas bases locais.

A auditoria registra ligações entre referências, vias, referências rodoviárias, extensões e ajustes de encaixe. Os testes verificam restrições de corredor, cobertura, terminais, geometrias originais da M-961 e preservação dos 23 serviços/39 sentidos anteriores e inclusão da I-131 em dois sentidos. O custo de concentração não pode escolher uma volta 20% maior em um caso controlado.

Geometrias são propostas de estudo. Relações de proibição de conversão OSM, raios de giro, gabarito, sinalização, paradas e circulação interna dos terminais exigem validação. Estatísticas de ruas observadas não medem demanda, frequência ou capacidade.

## Alimentadora oeste — I-131

`west.py` acrescenta Alto do Mateus ↔ Novais ↔ Jardim Planalto ↔ Cidade dos Funcionários ↔ Terminal Oitizeiro. Preserva literalmente os trechos locais da 108 e da 110 em cada sentido e conecta o setor da 105 por vias públicas. As referências de Cidade dos Funcionários são as da 105, não o polígono agregado de Funcionários da cartografia. A auditoria identifica os trechos, sentidos e índices das fontes, coordenadas preservadas e encaixes de até 35 m. O código I-131 é de estudo; atendimento complementar de Tiradentes, frequências, frota e entrada no terreno do terminal continuam para avaliação.
