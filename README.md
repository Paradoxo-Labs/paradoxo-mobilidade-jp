# Paradoxo Mobilidade JP

Uma iniciativa da Paradoxo Labs, desenvolvida por Jailson Silva, para inteligência, dados e visualização da mobilidade urbana de João Pessoa/PB.

## Visão

O Paradoxo Mobilidade JP nasce como uma iniciativa técnica e cívica para transformar dados públicos de mobilidade urbana em informação estruturada, mapas, análises e propostas.

O projeto possui dois eixos complementares:

1. Rede atual observada

Coleta, organização e visualização dos dados reais disponíveis publicamente sobre linhas, horários, itinerários e geometrias do transporte coletivo de João Pessoa.

Este eixo mantém o projeto sincronizado com a realidade operacional atual.

2. Proposta de rede BRS/BHLS

Estudo conceitual inicial de reorganização da rede de transporte coletivo de João Pessoa com base em corredores BRS/BHLS, terminais, estações, miniestações, alimentadoras, linhas interterminais, metropolitanas e especiais.

Este eixo ainda não possui linhas definitivas. Os códigos, traçados e agrupamentos propostos são hipóteses iniciais de trabalho e precisam ser refinados a partir dos dados reais, validação territorial, análise de demanda, estimativa de frota, frequências, mapas e fases de implantação.

## Objetivo

Construir uma base técnica para:

- entender a rede atual;
- coletar dados públicos de forma reprodutível;
- visualizar itinerários e horários;
- comparar a rede atual com propostas futuras;
- apoiar diagnósticos urbanos;
- desenvolver uma proposta BRS/BHLS para João Pessoa;
- evoluir futuramente para plataforma web com API, banco geográfico e dashboards.

## Status

Primeira versão local implementada: rede atual observada, mapa da proposta e coletor da SEMOB na mesma navegação.

A proposta conta também com um [estudo complementar de rede integrada, revisão de 21/11/2026](docs/proposta-brs-bhls/INTEGRACAO_REDE_INTEGRADA.md), com 23 linhas propostas, 39 traçados de referência e mapa interativo offline. O estudo amplia o material disponível para análise; a codificação e os traçados ainda precisam ser conciliados com o conceito inicial.

A aplicação atual utiliza Python 3.10+ com biblioteca padrão no servidor/coletor e HTML/CSS/JavaScript com D3 no frontend. Não exige instalação de pacotes para rodar em Linux/Ubuntu/WSL.

## Rodar localmente

Com Docker:

```sh
docker compose up -d --build --wait
```

Abra [http://127.0.0.1:8000](http://127.0.0.1:8000). As coletas persistem na pasta `data/`. Consulte [Docker, portas e persistência](docker/README.md).

Ou diretamente com Python:

```sh
bash scripts/setup.sh
bash scripts/run-dashboard.sh
```

Abra [http://127.0.0.1:8000](http://127.0.0.1:8000).

- **Rede atual:** referência histórica offline de 111 códigos de linha, 296 traçados/variantes e 3.047 paradas; seleção de linha/sentido e consulta dos dados disponíveis.
- **Rede proposta:** mapa interativo do estudo complementar, com 23 linhas e 39 traçados.
- **Coletor SEMOB:** coleta de linhas, ruas por sentido, horários e GeoJSON, progresso e downloads. A base SEMOB é consultada separadamente da referência histórica.

Para iniciar uma coleta pequena pela CLI:

```sh
bash scripts/collect-all.sh --line 0002
```

Sem `--line`, o coletor percorre todo o catálogo. As respostas e o conjunto processado ficam em `data/`, fora do Git. Uma nova instalação abre com a referência histórica; a coleta oficial depende de acesso à internet. Consulte [execução, armazenamento e limites](apps/collector/README.md).

## Evolução prevista

A estrutura mantém espaço para:

- evolução do coletor local Python;
- futura API Laravel;
- futuro frontend Next.js;
- evolução da infraestrutura Docker já disponível para o atlas local;
- dados geográficos;
- documentação para humanos e agentes de IA;
- proposta conceitual BRS/BHLS.

## Aviso importante

Este projeto é uma iniciativa independente da Paradoxo Labs.

A proposta BRS/BHLS aqui documentada é um estudo conceitual em refinamento. Ela não representa decisão oficial da SEMOB-JP, Prefeitura Municipal de João Pessoa ou qualquer órgão público.

As linhas propostas ainda não devem ser interpretadas como desenho final de rede. São sugestões iniciais para orientar estudos posteriores.

## Estrutura

apps/collector  - Coletor SEMOB e servidor local Python
apps/api        - Futuro backend Laravel
apps/web        - Frontend local HTML/CSS/JavaScript; Next.js previsto para evolução
docker/         - Infraestrutura Docker
data/           - Dados locais coletados/processados
exports/        - Arquivos exportados
docs/           - Documentação técnica e conceitual
ai/             - Contextos, agentes e prompts para IA/LLMs
scripts/        - Scripts auxiliares

## Repositórios

GitHub público:
https://github.com/Paradoxo-Labs/paradoxo-mobilidade-jp

GitLab técnico:
https://gitlab.com/paradoxo-labs/products/paradoxo-mobilidade-jp
