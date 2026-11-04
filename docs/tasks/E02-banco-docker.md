# E02 · Banco no Docker

- **Responsável:** E · Executor (OpenCode Go)
- **Prazo:** qua 04/11
- **Fonte:** este arquivo é autocontido e é o que vale. Consulte `docs/PLAN.md` (seção 8.3) só se faltar algo aqui, lendo apenas a seção necessária.

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

## Regras gerais

- Todo código numérico recebe um `numpy.random.Generator` com semente explícita. Nada usa o estado global de `np.random`.
- Textos da interface em português do Brasil. Nomes de código, tabelas e colunas em inglês.
- Os dados do catálogo são simulados, e a interface diz isso ("catálogo de demonstração").
- Nada depende de internet em execução: sem CDN, sem fontes remotas e sem imagens externas. A única exceção são os mockups em `docs/mockups/`, que não fazem parte do app.
- Claude, ao encontrar uma decisão não prevista, escolhe a opção mais simples compatível com o plano e registra uma linha em `docs/decisions.md`. O executor não decide: pergunta (1.5).
- Ao fim de cada tarefa, o dono atualiza `docs/STATUS.md`.

**Dependências que travam o trabalho.** E05 espera A01 (precisa de `theme.css`). E06 espera A02. E07 espera A03 (`seed_for` e `random_pairs`). E08 espera M1 e M4 aprovados. E10 espera A06 marcada como concluída em `docs/STATUS.md`. E11 a E14 esperam G2. Se uma dependência atrasar, o executor passa para a próxima tarefa sem dependência pendente e registra o atraso em `docs/STATUS.md`.

- Apagar o `.gitkeep` de uma pasta que passou a ter outros arquivos faz parte da tarefa, mesmo sem constar em "Arquivos permitidos".

## Contexto do plano

Trechos copiados de `docs/PLAN.md`. Menções a "seção N" se referem ao plano, e o necessário para esta tarefa está aqui. Se um trecho conflitar com as partes acima deste título, valem as de cima.

### Seção 10 · Docker Compose

```yaml
# docker-compose.yml (referência exata)
services:
  db:
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: imobscore
      POSTGRES_PASSWORD: imobscore
      POSTGRES_DB: imobscore
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./docker/initdb:/docker-entrypoint-initdb.d:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U imobscore"]
      interval: 3s
      retries: 20
    ports: ["5432:5432"]          # usado por make dev e pelos testes
  api:
    build: ./backend
    env_file: .env
    environment:
      DATABASE_URL: postgresql+psycopg://imobscore:imobscore@db:5432/imobscore
    volumes:
      - ./data:/app/data            # pares exportados e resultados ficam no repositório
    depends_on:
      db: { condition: service_healthy }
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"]
      interval: 5s
      retries: 20
  web:
    build: ./frontend
    ports: ["8080:80"]
    depends_on:
      api: { condition: service_healthy }
volumes:
  pgdata:
```

O serviço `db` publica a porta 5432 para `make dev` e para os testes. O `.env` local usa `DATABASE_URL=postgresql+psycopg://imobscore:imobscore@localhost:5432/imobscore` e `TEST_DATABASE_URL=postgresql+psycopg://imobscore:imobscore@localhost:5432/imobscore_test`. Os comandos `make` estão definidos na tarefa E01.
