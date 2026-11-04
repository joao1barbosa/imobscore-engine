# E06 · Comando seed

- **Responsável:** E · Executor (OpenCode Go)
- **Prazo:** qua 04/11, noite
- **Fonte:** `docs/PLAN.md`, seção 8.3. Em caso de divergência, vale o plano.

## Objetivo

Implementar o comando seed, que popula catálogo, personas e estatísticas de padronização.

## Arquivos permitidos

`backend/app/cli.py` (app Typer, rodado com `python -m app.cli`; deixar as funções `simulate` e `evaluate` para a A07); `o arquivo termina com if __name__ == "__main__": app()`; `backend/app/services/__init__.py`; `backend/app/services/seed_service.py`; `backend/tests/services/test_seed.py`.

## Dependências

A02, E04

## Especificação

- **`seed [--force] [--if-empty] [--with-results]`:**
  1. Se existir alguma linha em `sessions` e não houver `--force`, parar com a mensagem "Existem sessões; use --force para apagar tudo".
  2. Com `--if-empty` e `listings` não vazia, não fazer nada além do passo 6.
  3. Em uma transação: `TRUNCATE` de todas as tabelas, com `CASCADE`.
  4. Inserir `generate_catalog(settings.CATALOG_SEED)` em `listings` e as personas de `app/seed/personas.yaml` em `personas`.
  5. Para cada (cidade, finalidade): `T = raw_matrix(listings do segmento)`, `center, scale = fit_stats(T)` e uma linha em `feature_stats` por chave de `FEATURE_KEYS`.
  6. Com `--with-results` e `data/results/results.csv` existente: carregar esse CSV como em `load-results` (E10).

## Verificação

`pytest tests/services/test_seed.py` confere 300 imóveis, 3 personas e 72 linhas de `feature_stats`; rodar duas vezes gera os mesmos códigos e preços.
