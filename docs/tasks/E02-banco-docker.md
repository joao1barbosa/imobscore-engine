# E02 · Banco no Docker

- **Responsável:** E · Executor (OpenCode Go)
- **Prazo:** qua 04/11
- **Fonte:** `docs/PLAN.md`, seção 8.3. Em caso de divergência, vale o plano.

## Objetivo

Subir o PostgreSQL no Docker, com o banco de teste criado na inicialização.

## Arquivos permitidos

`docker-compose.yml` (só o serviço `db` da seção 10 nesta tarefa); `docker/initdb/01-test-db.sql` (`CREATE DATABASE imobscore_test OWNER imobscore;`).

## Dependências

E01

## Especificação

Sem detalhes além do objetivo e dos campos acima.

## Verificação

`docker compose up -d db` fica `healthy`; `docker compose exec db psql -U imobscore -d imobscore_test -c "select 1"` responde.
