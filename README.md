# ImobScore

App web que recomenda imóveis a partir de escolhas entre pares ("qual você prefere?"). O motor é um neurônio sigmoide bayesiano (modelo de Bradley-Terry), com os pesos amostrados por Metropolis-Hastings escrito à mão em NumPy. O catálogo é simulado, e tudo roda no notebook com Docker Compose, sem internet.

## Escopo do MVP

- **Coleta (`/coleta`):** um colega lê uma tela inicial sobre o experimento, aceita o consentimento, informa a faixa de preço, escolhe uma persona e responde a 20 pares aleatórios de imóveis à venda em Goiânia.
- **Onboarding (`/comecar`) e modo demo (`/demo`):** faixa de preço e persona (Família, Investidor ou Estudante), sempre para imóveis à venda em Goiânia. No modo demo, um toque na persona preenche o resto.
- **Comparações (`/comparar`):** 3 pares na demo, escolhidos pelo motor.
- **Feed (`/feed`):** o catálogo ordenado por uma nota de afinidade de 0 a 100, com intervalo de incerteza e a alternância Antes e Depois.
- **Painéis (`/modelo` e `/experimento`):** pesos aprendidos, incerteza e diagnósticos do MCMC, e a acurácia de cada método em pares reais.

## Requisitos

- **Docker** com Compose v2 (`docker compose`) e **make**. Para o modo demo, só isso é necessário.
- **Node 24** ou mais novo e **pnpm**, para o `make check` e para o front-end local (`make dev`). Na primeira vez, rode `cd frontend && pnpm install` com internet.
- **uv**, para o back-end local e o `make check`. O uv baixa o Python 3.12 sozinho.
- **cloudflared**, só para `make tunnel` (ver abaixo).

## Como rodar

Num clone novo, com um comando:

```bash
cp .env.example .env   # o Compose lê o .env; sem ele, nenhum alvo sobe
make demo              # sobe db, api e web, e abre o modo demo
```

`make demo` abre <http://localhost:8080/demo>. Ele semeia o catálogo só se o banco estiver vazio, e carrega `data/results/results.csv` sem repetir um `run_id` que já exista. Não apaga nada: se o banco tiver dados da coleta, eles ficam.

Sem o modo demo, o caminho é:

```bash
make up                # sobe db, api e web
make seed              # recria o catálogo de demonstração (300 imóveis e 3 personas) e apaga as sessões
```

A interface fica em <http://localhost:8080>, e o nginx repassa `/api` para a API, que também responde em <http://localhost:8080/api/v1/health>.

Principais alvos (`make help` lista todos):

| Alvo | O que faz |
| --- | --- |
| `make up` | Sobe db, api e web, com build |
| `make demo` | `make up`, semeia se o banco estiver vazio, carrega os resultados e abre `/demo` |
| `make seed` | Recria o catálogo e as personas, e apaga todas as sessões |
| `make dev` | Sobe só o banco e mostra como rodar a API e o front-end localmente |
| `make check` | Porta de qualidade: lint, formato, tipos e testes do back-end e do front-end |
| `make test` | Só os testes |
| `make export` | Grava os pares da coleta em `data/collected/pairs.json` |
| `make evaluate` | Exporta, avalia e carrega os resultados no banco |
| `make down` | Para os contêineres, sem apagar o banco |
| `make reset` | Apaga o banco (pede confirmação) |

`make check` precisa do banco no ar (`make up` ou `make dev`), porque os testes de API usam o banco `imobscore_test` em `localhost:5432`.

Os arquivos que a aplicação grava ficam em `data/`, na raiz do repositório: `data/collected/pairs.json` (o export da coleta) e `data/results/results.csv` (os resultados das avaliações). Os dois estão versionados, então um clone novo já tem os resultados.

## Coleta e túnel

Para os colegas responderem à coleta fora da rede local, o túnel do Cloudflare expõe a porta 8080:

```bash
make tunnel
```

O comando imprime um endereço `https://....trycloudflare.com`. Esse é o link da coleta: todos os colegas usam o mesmo endereço.

O alvo usa HTTP/2, porque algumas redes bloqueiam o QUIC (UDP 7844) e o túnel não conectaria. O endereço só existe enquanto o comando estiver rodando: durante a coleta, o notebook precisa ficar ligado, sem suspender, com o Docker e o túnel no ar. Se o túnel cair, o comando gera outro endereço, e o link enviado aos colegas para de funcionar.

**Rode `make seed` uma última vez antes de enviar o link**, para apagar as sessões de teste que ficaram no banco; sem isso, um teste completo entraria na avaliação como se fosse a participação de alguém. **Depois de enviar o link, nunca mais rode `make seed`**, porque ele apaga as respostas dos colegas.

Durante a coleta, o export só lê o banco:

```bash
make export   # grava data/collected/pairs.json
```

## Solução de problemas

- **Porta ocupada (5432 ou 8080).** `make up` ou `make demo` falha com "port is already allocated" ou "address already in use". Veja quem usa a porta com `ss -ltnp | grep -E ':(5432|8080)\b'`, e pare esse processo ou o outro projeto do Compose (com `make down` dentro dele). Para mudar a porta da interface, troque `8080:80` no `docker-compose.yml`.
- **Banco vazio: a interface não mostra imóveis nem personas.** `make demo` semeia sozinho quando o banco está vazio. Para semear sem apagar nada, use `docker compose exec api python -m app.cli seed --if-empty`. `make seed` recria o catálogo, mas apaga todas as sessões, inclusive as da coleta.
- **Painel do experimento vazio.** Rode `make demo` de novo: ele carrega `data/results/results.csv` no banco, sem repetir uma rodada que já esteja lá.
- **Imagens ou pacotes sem internet.** `make up` e `make demo` precisam das imagens base e das dependências do Python e do Node no cache do Docker. Com internet, rode `docker compose pull` e `make up` uma vez: depois disso, `make demo` funciona offline.
- **`make check` falha antes dos testes do front-end.** Falta instalar as dependências: rode `cd frontend && pnpm install` e tente de novo.
- **A API não responde.** Veja os logs com `docker compose logs api`. A API só responde depois que o banco está saudável e as migrações rodaram.

## Documentação

- [Plano de implementação](docs/PLAN.md)
- [Bases matemáticas e guia de estudo](docs/GUIDE.md)
- [Resultados do experimento](docs/results.md)
- [Roteiro da demo](docs/demo-script.md)
- [Índice de tarefas](docs/tasks/README.md)
- [Andamento](docs/STATUS.md)
