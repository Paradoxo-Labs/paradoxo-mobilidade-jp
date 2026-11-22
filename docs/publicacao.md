# Desenvolvimento e execução local

Repositório: [Paradoxo-Labs/paradoxo-mobilidade-jp](https://github.com/Paradoxo-Labs/paradoxo-mobilidade-jp). A branch de trabalho é `develop`, pública conforme autorização do usuário. A `main` não é atualizada por esta revisão.

As mudanças são entregues por commits e push para `origin/develop`. Não há hospedagem externa ou implantação automática verificada para este atlas; o push não equivale a publicar um site.

O destino de execução verificado é o Docker Desktop com integração WSL, serviço `atlas`, acessível somente pelo host em [http://127.0.0.1:8000](http://127.0.0.1:8000). Após atualizar o checkout, executar:

```sh
python3 -m unittest discover -s apps/planner/tests -v
docker compose up -d --build --wait
docker compose exec -T atlas python3 -m unittest discover -s apps/collector/tests -v
docker compose exec -T atlas python3 -m unittest discover -s apps/planner/tests -v
docker compose ps
```

A pasta `data/` é persistida no host e fica fora do Git. Os resultados curados da proposta são versionados em `docs/proposta-brs-bhls/revisao-atual`. Consultar também [a política de publicação](PUBLICATION_POLICY.md) e [a execução do Docker](../docker/README.md).

## Painel administrativo local

O serviço também atende `/admin`, com cadastro inicial por código de uso único, sessão autenticada e banco persistido em `data/admin/`. O atlas usa a publicação ativa desse banco; salvar rascunho ou versão não publica. Publicar/restaurar no painel atualiza apenas o atlas local, sem executar Git, push ou deploy externo. Código e semente continuam entregues por commits na `develop`.

Primeiro acesso, recuperação de senha, backup e limites: [ADMINISTRACAO.md](ADMINISTRACAO.md).
