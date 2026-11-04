# A03 · Modelo e pares aleatórios

- **Responsável:** A · Arquiteto (Claude)
- **Prazo:** qua 04/11
- **Fonte:** `docs/PLAN.md`, seção 8.2. Em caso de divergência, vale o plano.

## Objetivo

Implementar sigmoide, log-posteriori e a geração de pares aleatórios da coleta, liberando a E07.

## Arquivos permitidos

`backend/app/engine/model.py`; `backend/app/engine/pairs.py` (só `seed_for` e `random_pairs` nesta tarefa); `backend/app/engine/__init__.py` (só com os nomes já implementados); `backend/tests/engine/test_model.py`; `backend/tests/engine/test_pairs.py`.

## Dependências

A02

## Especificação

- **Especificação:** seções 5.2, 5.7 (modo coleta) e 5.10.
- **Testes:** `sigmoid` sem `nan` nem aviso com u = ±1000; `log_likelihood` igual a `-sklearn.metrics.log_loss(np.ones(m), p, labels=[0, 1]) * m` em dados aleatórios; com m = 0, `log_posterior` igual a `log_prior`; `random_pairs(50, 40, rng)` sem par repetido e com cada índice no máximo 3 vezes; mesma semente, mesma lista; em 2.000 pares, o lado esquerdo fica com o índice menor entre 45% e 55% das vezes.

## Verificação

`cd backend && uv run pytest tests/engine -q && uv run mypy app/engine` (o plano manda usar a verificação da A02).

**Pronto quando:** verificação da A02 passa, CP2 concluído e A03 registrada em `docs/STATUS.md` (isso libera E07).
