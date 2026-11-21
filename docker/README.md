# Executar o atlas com Docker

Requer Docker Engine/Desktop com Compose. No WSL, habilite a distribuição em **Docker Desktop → Settings → Resources → WSL Integration** ([documentação oficial](https://docs.docker.com/desktop/features/wsl/)).

Na raiz do repositório:

```sh
docker compose up -d --build --wait
```

Abra [http://127.0.0.1:8000](http://127.0.0.1:8000). O serviço `atlas` reúne o servidor Python, o frontend, o coletor SEMOB e o mapa da proposta. Não há necessidade de containers separados para Laravel, Next.js ou banco nesta versão.

## Comandos

```sh
docker compose ps
docker compose logs --tail 100 -f atlas
docker compose exec atlas python3 apps/collector/collector.py --line 0002
docker compose exec atlas python3 -m unittest discover -s apps/collector/tests -v
docker compose down
```

`down` encerra o serviço; as coletas permanecem na pasta `data/` do repositório. Para aplicar alterações no código, execute novamente `docker compose up -d --build --wait`. O código faz parte da imagem, sem montagem de desenvolvimento ou recarga automática.

## Persistência e usuário

O bind mount `./data:/app/data` compartilha as coletas já existentes com o container. Novas respostas e conjuntos processados continuam visíveis em `data/raw/semob` e `data/processed/semob` no host, fora do Git. O arquivo de bloqueio é compartilhado: uma coleta CLI no host e uma coleta no container não devem rodar simultaneamente na mesma pasta.

A imagem e o Compose usam usuário sem privilégios, com UID/GID 1000 por padrão. Para outro usuário Linux/WSL, ajuste `LOCAL_UID` e `LOCAL_GID` com os valores de `id -u` e `id -g` em um arquivo `.env`, usando `.env.example` como referência. O usuário precisa ter permissão de escrita em `./data`; a configuração não altera automaticamente as permissões dos dados existentes.

## Porta e acesso

`APP_PORT` define a porta publicada. Exemplo, se a porta 8000 estiver ocupada:

```sh
APP_PORT=8080 docker compose up -d --build --wait
```

Nesse caso, abra [http://127.0.0.1:8080](http://127.0.0.1:8080). O Compose mantém a porta interna 8000 e informa ao servidor a porta pública para a validação de origem do formulário de coleta.

O servidor escuta em `0.0.0.0` dentro do container, mas a porta é publicada apenas em `127.0.0.1` no host. A imagem tem verificação de saúde via `/api/status`, filesystem de aplicação somente leitura e `/tmp` temporário. Somente a pasta de dados persiste gravações.

O build baixa a imagem Python. A consulta dos mapas locais não requer serviços externos; as coletas dependem de acesso HTTPS à SEMOB a partir do container. Respostas locais, credenciais e ambientes de desenvolvimento são excluídos do contexto de build pelo `.dockerignore`.
