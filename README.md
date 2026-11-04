# ImobScore

Em construção.

App web que recomenda imóveis a partir de escolhas entre pares ("qual você prefere?"). O motor é um neurônio sigmoide bayesiano (modelo de Bradley-Terry), com os pesos amostrados por Metropolis-Hastings escrito à mão em NumPy. O catálogo é simulado, e tudo roda no notebook com Docker Compose, sem internet.

## Escopo do MVP

- **Coleta (`/coleta`):** um colega lê uma tela inicial sobre o experimento, aceita o consentimento, informa a faixa de preço, escolhe uma persona e responde a 25 pares aleatórios de imóveis à venda em Goiânia.
- **Onboarding (`/comecar`) e modo demo (`/demo`):** cidade, compra ou aluguel, faixa de preço e persona (Família, Investidor ou Estudante). No modo demo, um toque na persona preenche o resto.
- **Comparações (`/comparar`):** 3 pares na demo, escolhidos pelo motor.
- **Feed (`/feed`):** o catálogo ordenado por uma nota de afinidade de 0 a 100, com intervalo de incerteza e a alternância Antes e Depois.
- **Painéis (`/modelo` e `/experimento`):** pesos aprendidos, incerteza e diagnósticos do MCMC, e a acurácia de cada método em pares reais.

## Documentação

- [Plano de implementação](docs/PLAN.md)
- [Bases matemáticas e guia de estudo](docs/GUIDE.md)
- [Índice de tarefas](docs/tasks/README.md)
- [Andamento](docs/STATUS.md)
