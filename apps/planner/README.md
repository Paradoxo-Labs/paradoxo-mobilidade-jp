# Revisão da proposta por padrões da rede observada

O gerador `revise.py` recalcula os 39 sentidos dos 23 serviços da proposta usando ruas públicas do OSM, preferência por ruas com concentração de linhas SEMOB e regras de integração definidas pelo usuário.

Na raiz do repositório:

```sh
python3 apps/planner/revise.py
python3 -m unittest discover -s apps/planner/tests -v
```

As entradas locais são `data/processed/semob/latest.json` e `data/raw/cartografia/osm-revisao-rotas.json`, mais o estudo importado versionado. A consulta OSM, a data e os hashes das entradas estão em `docs/proposta-brs-bhls/revisao-atual/auditoria.json`. O resultado é gravado em `docs/proposta-brs-bhls/revisao-atual`; os dados brutos não entram no Git.

O atlas serve os resultados versionados, sem recalcular trajetos a cada consulta. Após regenerar, reconstruir o container com `docker compose up -d --build --wait`. O gerador deve ser executado no host; a imagem mantém os arquivos da aplicação somente leitura.

Regras principais:

- Grafo dirigido por vias e nós OSM, respeitando os atributos de mão única e exceções explícitas para ônibus. Exclui acesso privado/proibido e estacionamento interno quando não há permissão de transporte público.
- Bloqueio da `Via UFPB` e do interior do campus, preservando apenas vias públicas de contorno e a baia da Estação Cidade Universitária. Referências próximas são encaixadas no componente viário com entrada e saída disponíveis.

Os giradores de CCHLA e Centro de Tecnologia têm “UFPB” no nome, mas são vias públicas primárias de contorno, fora do interior bloqueado. Eles permanecem disponíveis para evitar impor voltas pela cidade apenas pelo nome da via. A proibição é da circulação interna, não do acesso público ao entorno da universidade.
- Custo por distância com preferência pela concentração de linhas observadas por segmento e por nome de rua; cada código conta uma única vez, sem confundir variantes com linhas adicionais.
- Trechos centrais dos sete serviços radiais copiados da 0301 SEMOB por sentido, para preservar a Lagoa, o espaço atual do TIV e seus percursos de entrada e saída.
- Oitizeiro na área junto ao viaduto/BR-230 indicada pelo usuário, com acessos internos ainda pendentes. Referências por sentido para Cidade Universitária, sem impor a mesma plataforma à ida e à volta.

As geometrias são propostas de estudo. Relações de proibição de conversão OSM, raio de giro, dimensões do ônibus, sinalização e circulação interna de terminais ainda precisam de verificação específica. As estatísticas de ruas observadas não medem demanda, viagens/hora ou capacidade.
