# Contexto Atual

O Paradoxo Mobilidade JP possui uma primeira versão local funcional, implementada em 21/11/2026.

O projeto começou a partir da necessidade de construir uma ferramenta local para trabalhar com dados reais das linhas de ônibus de João Pessoa, coletados a partir de fontes públicas da SEMOB-JP.

Durante a evolução do trabalho, o projeto passou a incorporar também uma proposta conceitual maior: uma reorganização da rede de transporte coletivo baseada em corredores BRS/BHLS.

## Dois eixos do projeto

### 1. Rede atual observada

Este eixo responde à pergunta:

Como a rede funciona hoje?

Inclui:

- coleta de linhas atuais;
- coleta de horários;
- coleta de itinerários textuais;
- coleta de GeoJSON oficial;
- exportação para CSV, Excel e GeoJSON;
- visualização em painel local;
- análise da rede existente.

Este eixo é essencial porque impede que a proposta fique desconectada da realidade.

### 2. Proposta de rede BRS/BHLS

Este eixo responde à pergunta:

Como a rede poderia ser reorganizada?

Inclui:

- corredores estruturais BRS/BHLS;
- terminais;
- estações;
- miniestações;
- linhas expressas;
- linhas paradoras;
- linhas alimentadoras;
- linhas interterminais;
- linhas metropolitanas;
- linhas especiais;
- fases de implantação;
- comparação futura com a rede atual.

Importante: as linhas da proposta ainda não estão definidas de forma final. Elas representam uma sugestão inicial de arquitetura da rede e precisam de refinamento.

## Estado atual do repositório

O repositório possui estrutura preparada para:

- coletor SEMOB e servidor Python com biblioteca padrão em apps/collector;
- futura API Laravel em apps/api;
- frontend local HTML/CSS/JavaScript com Leaflet em apps/web; Next.js permanece previsto para evolução;
- documentação técnica em docs;
- contextos para IA em ai;
- dados locais em data;
- exportações em exports.

## Próxima etapa técnica

### Estudo complementar incorporado em 21/11/2026

O pacote `mobilidade-jp-projeto-codex.zip` foi incorporado ao eixo da proposta em `docs/proposta-brs-bhls/estudos/rede-integrada-2026-11-21`. Contém 23 linhas propostas, 39 traçados de referência, mapa offline, scripts de geração e referências históricas da rede observada.

O [registro de integração](proposta-brs-bhls/INTEGRACAO_REDE_INTEGRADA.md) reúne inventário, diferenças em relação ao conceito inicial e pendências. O estudo complementar não substitui automaticamente a arquitetura inicial, nem demonstra cobertura integral ou viabilidade operacional. Seus dados históricos não substituem uma nova coleta da SEMOB-JP.

O coletor e o painel estão implementados. Executar `bash scripts/run-dashboard.sh` e abrir `http://127.0.0.1:8000`. Há navegação entre rede atual, proposta e coleta. A rede atual inicia com a referência histórica offline; a coleta oficial fica em base separada e acrescenta itinerários textuais, horários e geometrias da SEMOB.

O coletor percorre a listagem paginada, registra respostas originais, datas e pendências por campo. As exportações disponíveis são JSON completo, GeoJSON e catálogo CSV. Foram coletadas localmente as linhas 0002 e 0003 para validação; esses dados de execução não são versionados e não significam que o catálogo completo tenha sido coletado.

O atlas também possui execução com Docker Compose: `docker compose up -d --build --wait`, com serviço único, verificação de saúde, publicação em localhost e dados persistidos em `./data`. Ver [Docker](../docker/README.md).

Próxima etapa: revisar variantes/pendências da coleta completa e criar a comparação de cobertura entre as duas redes. Exportação Excel, API Laravel, PostGIS e migração do frontend para Next.js continuam pendentes. Detalhes em [apps/collector/README.md](../apps/collector/README.md).

## Atualização da interface e coleta integral

A coleta completa foi executada em 21/11/2026: 85 linhas consultadas, 149 traçados recebidos e seis linhas sem geometria publicada no endpoint. A próxima etapa de dados passa a ser revisar essas lacunas e manter as coletas atualizadas.

A interface agora segue a identidade do site Paradoxo, com logotipo oficial, Syne, Space Mono e cores institucionais. Os dois mapas são nativos em Leaflet; a proposta não usa mais iframe. Fontes de ruas, topografia e satélite foram referenciadas no Atlas de Distritos da Paraíba, preservando fallback vetorial local. Ver [interface e mapas](INTERFACE_E_MAPAS.md).

## Revisão dos traçados propostos

A proposta ativa passa a ser `docs/proposta-brs-bhls/revisao-atual`, com todos os 39 sentidos recalculados por ruas públicas e preferência por concentração de linhas observadas. A integração da UFPB foi corrigida para a Estação Cidade Universitária, sem Via UFPB/atalhos internos. O Terminal Metropolitano utiliza o espaço atual do TIV, com trechos centrais da 0301 e passagem pela Lagoa. Oitizeiro usa a referência do terreno ao lado do novo mercado enviada pelo usuário; Cristo usa o terminal atual e Lagoa usa o Terminal de Passageiros. A circulação interna dos novos terminais e restrições de conversão/gabarito continuam pendentes de validação. Ver [revisão ativa e auditoria](proposta-brs-bhls/revisao-atual/README.md).

### Refinamento de corredores e cobertura

A revisão ativa passou a priorizar continuidade dos corredores, com menor peso da concentração e alternativas de pista por sentido. T-410 mantém a Beira-Rio, T-610/TRV-321 evitam BR-230 e BRS-800 retorna à rodovia após Cidade Universitária. R-241/242 ampliam José Américo e entram no centro do Colibris; L-251 amplia a cobertura local e passa pelo IFPB. Parque do Sol fica com L-751, retirado da I-332; M-961 recupera os traçados originais. A referência de Oitizeiro foi refinada pelo ponto do novo mercado enviado pelo usuário; circulação interna do terreno segue pendente de planta. Lagoa e Cristo usam os terminais existentes. Ver [regras e resultados ativos](proposta-brs-bhls/revisao-atual/README.md).

### Alimentadora oeste — I-131

A proposta ativa passa a 24 serviços e 41 traçados, incluindo a I-131: Alto do Mateus ↔ Novais ↔ Jardim Planalto ↔ Cidade dos Funcionários ↔ Terminal Oitizeiro. Preserva trechos locais da 108/110 e conecta a área da 105. Ida de 10,38 km e volta de 11,15 km; complementação de Tiradentes, frota, frequência e acesso interno a Oitizeiro ainda não dimensionados. Os 39 traçados anteriores permanecem preservados.

### Painel administrativo local — 22/11/2026

O atlas passa a ter `/admin`, com login de administrador único e SQLite persistido em `data/admin/`. Reúne o coletor autenticado, criação/duplicação/importação de linhas, sentidos independentes, edição de trechos com arraste e roteamento local, preservação de segmentos, rascunhos automáticos, comparação, versões, publicação e restauração. O atlas consulta a publicação ativa do banco, inicialmente importada das 24 linhas/41 traçados versionados; rascunhos não alteram a rede de consulta. Não existe senha padrão: o primeiro cadastro exige o código local obtido por `docker compose exec atlas python3 apps/admin/manage.py setup-token`. [Operação, limites e backup](ADMINISTRACAO.md).
