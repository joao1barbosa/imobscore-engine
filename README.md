# ImobScore

App web que recomenda imóveis a partir de escolhas entre pares ("qual você prefere?"). O motor é um neurônio sigmoide bayesiano (modelo de Bradley-Terry), com os pesos amostrados por Metropolis-Hastings escrito à mão em NumPy. O catálogo é simulado, e tudo roda no notebook com Docker Compose, sem internet.

## Escopo do MVP

- **Coleta (`/coleta`):** um colega lê uma tela inicial sobre o experimento, aceita o consentimento, informa a faixa de preço, escolhe uma persona e responde a 25 pares aleatórios de imóveis à venda em Goiânia.
- **Onboarding (`/comecar`) e modo demo (`/demo`):** faixa de preço e persona (Família, Investidor ou Estudante), sempre para imóveis à venda em Goiânia. No modo demo, um toque na persona preenche o resto.
- **Comparações (`/comparar`):** 3 pares na demo, escolhidos pelo motor.
- **Feed (`/feed`):** o catálogo ordenado por uma nota de afinidade de 0 a 100, com intervalo de incerteza e a alternância Antes e Depois.
- **Painéis (`/modelo` e `/experimento`):** pesos aprendidos, incerteza e diagnósticos do MCMC, e a acurácia de cada método em pares reais.

## Como rodar

O projeto roda com Docker Compose. Num clone novo:

```bash
cp .env.example .env   # o Compose lê o .env; sem ele, "make up" não sobe
make up                # sobe db, api e web
make seed              # recria o catálogo de demonstração (300 imóveis e 3 personas)
```

A interface fica em <http://localhost:8080>, e o nginx repassa `/api` para a API, que também responde em <http://localhost:8080/api/v1/health>.

`make help` lista todos os alvos. Para desenvolver sem Docker, `make dev` sobe só o banco e o terminal mostra os dois comandos locais (`uv run uvicorn` no back-end e `pnpm dev` no front-end).

Os arquivos que a aplicação grava ficam em `data/`, na raiz do repositório: `data/collected/pairs.json` (o export da coleta) e `data/results/results.csv` (os resultados das avaliações).

## Coleta e túnel

Para os colegas responderem à coleta fora da rede local, o túnel do Cloudflare expõe a porta 8080:

```bash
make tunnel
```

O comando imprime um endereço `https://....trycloudflare.com`. Esse é o link da coleta: todos os colegas usam o mesmo endereço.

Se a rede bloquear o QUIC (UDP 7844), o túnel não conecta e o `cloudflared` avisa "Allow outbound QUIC traffic on port 7844". Nesse caso, rode com HTTP/2:

```bash
cloudflared tunnel --url http://localhost:8080 --protocol http2
```

**Rode `make seed` uma última vez antes de enviar o link**, para apagar as sessões de teste que ficaram no banco; sem isso, um teste completo entraria na avaliação como se fosse a participação de alguém. **Depois de enviar o link, nunca mais rode `make seed`**, porque ele apaga as respostas dos colegas.

Durante a coleta, o export só lê o banco:

```bash
make export   # grava data/collected/pairs.json
```

## Documentação

- [Plano de implementação](docs/PLAN.md)
- [Bases matemáticas e guia de estudo](docs/GUIDE.md)
- [Índice de tarefas](docs/tasks/README.md)
- [Andamento](docs/STATUS.md)
