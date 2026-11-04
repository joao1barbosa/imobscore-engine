# E04 · Modelos do banco e migração

- **Responsável:** E · Executor (OpenCode Go)
- **Prazo:** qua 04/11
- **Fonte:** `docs/PLAN.md`, seção 8.3. Em caso de divergência, vale o plano.

## Objetivo

Criar os modelos SQLAlchemy das 8 tabelas e a migração inicial única do Alembic.

## Arquivos permitidos

`backend/app/models/__init__.py`, `base.py`, `listing.py`, `feature_stats.py`, `persona.py`, `session.py`, `comparison.py`, `posterior.py`, `inspection.py`, `experiment_result.py`; `backend/alembic.ini`; `backend/migrations/` (`env.py` e uma única revisão `0001_initial.py`); `backend/tests/test_migrations.py`.

## Dependências

E03

## Especificação

- **Especificação:** o DDL da seção 4, exatamente, com SQLAlchemy 2.0 (`Mapped[...]`). Convenção de nomes no `MetaData`: `ix_%(column_0_label)s`, `uq_%(table_name)s_%(column_0_name)s`, `ck_%(table_name)s_%(constraint_name)s`, `fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s`, `pk_%(table_name)s`. Depois do `--autogenerate`, conferir à mão os `CHECK` e o `gen_random_uuid()`.

## Verificação

um teste roda `upgrade head`, `downgrade base` e `upgrade head` no banco de teste sem erro; `\dt` mostra as 8 tabelas.

## Atenção

`backend/migrations/` já existe com um `.gitkeep` da E01, e `alembic init` recusa pasta não vazia. Ver a pergunta Q4 em `docs/STATUS.md`.
