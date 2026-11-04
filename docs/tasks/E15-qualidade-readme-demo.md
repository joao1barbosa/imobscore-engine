# E15 · Qualidade, README e `make demo`

- **Responsável:** E · Executor (OpenCode Go)
- **Prazo:** dom 08/11
- **Fonte:** este arquivo é autocontido e é o que vale. Consulte `docs/PLAN.md` (seção 8.3) só se faltar algo aqui, lendo apenas a seção necessária.

## Objetivo

Fechar a porta de qualidade, o README completo e o make demo a partir de um clone limpo.

## Arquivos permitidos

os apontados por cada `FIX-n`; `README.md` (requisitos: Docker, Node 24, pnpm, uv e cloudflared; `make up`, `make seed`, `make demo`, `make dev`, `make check`; coleta pelo túnel; solução de problemas: porta ocupada, banco vazio, imagens sem internet).

## Dependências

E12 a E14 e as FIX da A-REV2

## Especificação

Sem detalhes além do objetivo e dos campos acima.

## Verificação

`make check` passa por inteiro; um clone limpo roda `make demo` e abre o modo demo funcionando.

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

### Seção 9 · Testes, verificação e critérios de aceite

Cada tarefa traz seus próprios comandos de verificação (seção 8). Esta seção reúne o que vale para todas e o roteiro manual que substitui o teste automatizado de ponta a ponta.

**`make check`** é a porta de qualidade única. Roda no notebook antes de cada commit de fim de tarefa e no fim de cada dia:

```bash
cd backend && uv run ruff check . && uv run ruff format --check . \
  && uv run mypy app/engine && uv run pytest -q -m "not perf"
cd frontend && pnpm lint && pnpm format:check && pnpm typecheck && pnpm test:run
```

| Camada | Dono | Ferramenta | O que cobrir |
| --- | --- | --- | --- |
| Motor (`app/engine`) | A | pytest | Todos os testes de A02, A03, A05, A06 e A07; cobertura de pelo menos 90% (`pytest --cov=app/engine`) |
| Serviços e API | E | pytest, `TestClient` e banco `imobscore_test` | Os testes listados em E06, E07, E09 e E10; cada rota com um caso de sucesso e um de erro |
| Telas | E | Vitest, Testing Library e MSW | Os testes listados em E08 e E11 a E14 |
| Ponta a ponta | J com A | Roteiro manual abaixo | Os 10 passos, offline |

**Convenções**

- Todo teste numérico usa semente fixa e tolerância explícita (`np.testing.assert_allclose(..., atol=...)`).
- O teste de desempenho do MCMC recebe `@pytest.mark.perf` e fica fora do `make check`. Claude o roda na A05 e na A-REV1.
- Nenhum teste depende de internet nem do horário.
- Nenhum agente apaga, pula ou afrouxa um teste para fazê-lo passar.

#### Roteiro manual offline (A09 com João em 09/11; João repete em 10/11)

- [ ] 1\. Desligar o Wi-Fi. Rodar `make demo`. O modo demo abre em até 2 minutos.
- [ ] 2\. Tocar em Família. O primeiro par aparece em até 1 segundo.
- [ ] 3\. Responder 3 pares em menos de 20 segundos, sem espera visível entre eles.
- [ ] 4\. O feed aparece com 30 imóveis, selo, intervalo e motivos \[C2\]. Todo score fica entre 0 e 100.
- [ ] 5\. Alternar Antes e Depois: a lista reordena com animação.
- [ ] 6\. Painel do modelo: 12 pesos, R-hat abaixo de 1,05 e diagnóstico sem alerta.
- [ ] 7\. Painel do experimento: dados reais, ou o aviso "Dados simulados".
- [ ] 8\. Recarregar a página no meio dos pares: volta ao mesmo par, sem pular.
- [ ] 9\. Em 375 px (DevTools), a coleta e a demo funcionam sem rolagem horizontal.
- [ ] 10\. Na aba Network do navegador, nenhuma requisição sai de `localhost`.

#### Critérios de aceite do MVP (09/11, 22h)

- [ ] `make check` passa por inteiro.
- [ ] Os 10 passos do roteiro manual passam.
- [ ] `docs/CHECKPOINTS.md` tem CP1 a CP7 com "Entendido: sim".
- [ ] `docs/mockups/APPROVAL.md` tem M1 a M7 aprovados, e as telas implementadas batem com eles.
- [ ] `docs/results.md` e `data/results/` existem, com dados reais ou simulados declarados.
- [ ] `docs/STATUS.md` sem `FIX-n` aberto e sem pergunta aberta.
- [ ] Tag `v1.0.0` criada.

### Seção 10 · Docker Compose, seed e demo offline

No dia, o notebook roda `make demo` sem internet e abre o navegador em `http://localhost:8080/demo`. Todas as imagens e dependências são baixadas antes, em casa.

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

**Checklist da véspera (10/11)**

- [ ] Com internet: `docker compose pull` e `make up`, para deixar todas as imagens no cache do notebook.
- [ ] Desligar o Wi-Fi e repetir o roteiro manual da seção 9 a partir de `make reset` e `make demo`.
- [ ] Conferir que `data/collected/pairs.json` e `data/results/` estão no repositório. O `make demo` recarrega os resultados a partir deles, mesmo com o banco recriado.
- [ ] Desativar a suspensão de tela e as atualizações automáticas do sistema.
- [ ] Deixar um segundo navegador aberto no painel do experimento, ao lado da demo.
- [ ] Plano B: gravar um vídeo de 60 segundos da demo.
- [ ] Ler `docs/demo-script.md` em voz alta uma vez.

### Seção 2 · Infra e ferramentas gerais

| Ferramenta | Para quê |
| --- | --- |
| Docker + Docker Compose | Serviços `db`, `api` e `web` rodando localmente e offline |
| Nginx (imagem `nginx:alpine`) | Serve o build do front-end e faz proxy de `/api` para a API |
| Makefile | Atalhos: `make up`, `make seed`, `make test`, `make demo`, `make evaluate` |
| pre-commit | \[corte\] Substituído pelo comando make check (seção 9) |
| GitHub Actions | \[corte\] Substituído pelo comando make check (seção 9) |
| Cloudflare Tunnel (`cloudflared`, opcional) | Expor a página de coleta aos colegas a partir do notebook, sem deploy (ver seção 12) |

### Seção 1.7 · Escopo no prazo curto

**Essencial (não corta):** o motor completo (seções 5.1 a 5.9) com testes; a coleta e a avaliação com dados reais, ou simulados e declarados como tal; o fluxo da demo (persona, 3 pares, feed com Antes e Depois); os painéis do modelo e do experimento; e a execução offline.

**Já cortado (não implementar):**

| Item | Onde aparecia | O que fica no lugar |
| --- | --- | --- |
| Rolagem infinita do feed | 7 | Uma consulta só, com `limit=30` |
| Aba Lado a lado | 7 | A alternância Antes e Depois |
| Recompensa com feed ao fim da coleta | 7 | Tela de agradecimento |
| GitHub Actions e pre-commit | 2 | `make check` rodado no notebook (seção 9) |
| Playwright | 2, 9 | Roteiro manual offline (seção 9) |
| `dev:mock` no navegador | 2 | MSW só nos testes |
| Cobertura mínima no front-end | 2 | Testes dos fluxos críticos listados em cada tarefa |

**Cortes condicionais**, nesta ordem, decididos por João em 09/11 às 12h:

| Corte | O que sai | O que fica |
| --- | --- | --- |
| C1 · já aplicado, reversível | Detalhe do imóvel e vistoria (M8, tarefa E17) | Cartão do feed sem link |
| C2 | Motivos "por que este imóvel" no cartão | Score e intervalo |
| C3 | Escolha adaptativa de pares (BALD) | Pares aleatórios também na demo |
| C4 | Gráfico de traço das cadeias no painel do modelo | Quadro de diagnósticos |
