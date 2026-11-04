# A06 · Afinidade, explicação, BALD, baselines e interface completa

- **Responsável:** A · Arquiteto (Claude)
- **Prazo:** sex 06/11, até 13h
- **Fonte:** `docs/PLAN.md`, seção 8.2. Em caso de divergência, vale o plano.

## Objetivo

Implementar afinidade, explicação, BALD e baselines, completando a interface 5.10 e liberando a E10.

## Arquivos permitidos

`backend/app/engine/affinity.py`; `backend/app/engine/pairs.py` (`next_pair_bald`); `backend/app/engine/baselines.py`; `__init__.py` (todos os nomes da 5.10, exceto os de `evaluation`); testes correspondentes.

## Dependências

A05

## Especificação

- **Especificação:** seções 5.6 a 5.8 e 5.10.
- **Testes:** afinidade sempre em \[0, 1\]; `to_score` sempre em \[0, 100\], inclusive com delta de −80 e +80; o imóvel típico (z = 0) tem afinidade 0,5; `explain` devolve no máximo 4 motivos e ignora |c| < 0,1; BALD ≥ 0 em todos os candidatos e nunca repete um par de `shown`; com amostras quase iguais, BALD perto de 0 em todos os pares; `fit_mle` treina com 1 par; os quatro métodos de `predict_proba` devolvem valores em (0, 1).

## Verificação

`cd backend && uv run pytest tests/engine -q && uv run mypy app/engine` (comando da A02; a tarefa não define um próprio).

**Pronto quando:** testes passam, CP4 concluído e "A06 concluída: interface 5.10 completa" registrada em `docs/STATUS.md` (libera E10).
