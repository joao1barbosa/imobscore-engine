# E17 · \[C1\] Detalhe do imóvel e vistoria

- **Responsável:** E · Executor (OpenCode Go)
- **Prazo:** seg 09/11, só com autorização de João às 12h e M8 aprovado
- **Fonte:** `docs/PLAN.md`, seção 8.3. Em caso de divergência, vale o plano.

## Objetivo

Implementar o detalhe do imóvel e a vistoria, somente se João reverter o corte C1.

## Arquivos permitidos

`backend/app/api/v1/listings.py`; `backend/app/services/inspection_service.py`; as rotas de vistoria em `sessions.py`; o cálculo de `inspection_delta` em `feed_service.py`; `src/features/listing/*`; testes.

## Dependências

E16

## Especificação

- **Conteúdo:** seções 6 e 7 ("Detalhe e vistoria"). O feed passa a somar a vistoria com `to_score(mean, soma dos delta)`.

## Verificação

`make check`; marcar "Rua barulhenta" baixa o score na hora, e o valor persiste ao recarregar.
