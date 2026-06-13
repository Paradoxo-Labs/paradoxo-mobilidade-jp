# Política de Publicação

## O que pode ser público agora

Podem ser publicados no GitHub:

- README do projeto;
- visão geral;
- proposta conceitual BRS/BHLS;
- roadmap;
- decisões técnicas;
- estrutura do projeto;
- documentação para agentes de IA;
- scripts genéricos;
- código-fonte do coletor;
- exemplos pequenos e revisados;
- arquivos .gitkeep.

## O que deve ficar fora do Git por padrão

Não devem ser versionados:

- .env;
- .venv;
- caches;
- dados brutos coletados;
- exportações Excel;
- exportações GeoJSON geradas;
- logs locais;
- arquivos temporários;
- arquivos binários de trabalho sem necessidade.

## Como tratar a proposta BRS/BHLS

A proposta pode ser pública, desde que sempre identificada como:

- estudo conceitual;
- documento em refinamento;
- iniciativa independente da Paradoxo Labs;
- proposta técnica sem caráter oficial;
- sugestão inicial sem linhas definitivas.

## Como tratar as linhas propostas

As linhas sugeridas no eixo BRS/BHLS não devem ser apresentadas como versão final.

Elas devem ser tratadas como:

- hipótese inicial;
- rascunho de rede;
- base para refinamento;
- ponto de partida para validação com dados reais;
- sugestão a ser testada em mapa, demanda, frota e operação.

## Como tratar dados reais

Dados reais coletados de fontes públicas podem ser documentados, mas os arquivos gerados localmente devem ficar fora do Git por padrão.

Se for necessário publicar amostras, usar:

data/samples

e manter arquivos pequenos, revisados e claramente identificados como amostra.
