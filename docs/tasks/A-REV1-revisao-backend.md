# A-REV1 · Revisão do back-end

- **Responsável:** A · Arquiteto (Claude)
- **Prazo:** sex 06/11, fim do dia
- **Fonte:** `docs/PLAN.md`, seção 8.2. Em caso de divergência, vale o plano.

## Objetivo

Revisar o back-end entregue em E07 a E10 contra a especificação e abrir tarefas FIX-n.

## Arquivos permitidos

`docs/STATUS.md` (registro das tarefas `FIX-n`). *O plano não traz campo "Arquivos" nesta tarefa; lista derivada do texto dela.*

## Dependências

E07 a E10

## Especificação

- Ler o diff de E07 a E10 contra as seções 4, 6 e 8.3; rodar `make check`; confirmar que `services/` só importa `app.engine`; medir o tempo de resposta de `POST /comparisons` no modo demo (meta: menos de 300 ms).
- Cada problema vira uma tarefa `FIX-n` em `docs/STATUS.md`, com arquivo, o que está errado e o que a especificação diz. O executor as resolve antes da próxima tarefa.

## Verificação

`make check`; `cd backend && uv run pytest -q -m perf` (seção 9: o teste de desempenho roda na A-REV1). Medir `POST /comparisons` no modo demo: meta de menos de 300 ms.
