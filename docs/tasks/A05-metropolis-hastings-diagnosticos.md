# A05 · Metropolis-Hastings e diagnósticos

- **Responsável:** A · Arquiteto (Claude)
- **Prazo:** qui 05/11
- **Fonte:** `docs/PLAN.md`, seção 8.2. Em caso de divergência, vale o plano.

## Objetivo

Implementar o Metropolis-Hastings vetorizado e os diagnósticos (R-hat, ESS, aceitação).

## Arquivos permitidos

`backend/app/engine/mcmc.py`; `backend/app/engine/diagnostics.py`; `__init__.py`; `backend/tests/engine/test_mcmc.py`; `backend/tests/engine/test_diagnostics.py`.

## Dependências

A03

## Especificação

- **Especificação:** seções 5.4, 5.5 e 5.10 (`fit_posterior`).
- **Testes:** (a) alvo gaussiano conhecido de 12 dimensões: média a menos de 0,1 e variância a menos de 10% das verdadeiras; (b) sem pares, as amostras reproduzem a priori; (c) usuário sintético com w verdadeiro e 300 pares: correlação entre a média da posteriori e w maior que 0,9; (d) priori fraca (σ = 10) e 300 pares: média da posteriori a menos de 0,15 do MAP calculado com `scipy.optimize.minimize`; (e) mesma semente, mesmas amostras; (f) R-hat abaixo de 1,05 e ESS acima de 400 nesses casos; (g) 40 pares em menos de 250 ms (`@pytest.mark.perf`).
- **Checkpoint:** CP3.

## Verificação

`cd backend && uv run pytest tests/engine -q && uv run mypy app/engine` (comando da A02; a tarefa não define um próprio). Inclui o teste `perf`, que a seção 9 manda rodar nesta tarefa.
