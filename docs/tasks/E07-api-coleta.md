# E07 · API da coleta

- **Responsável:** E · Executor (OpenCode Go)
- **Prazo:** qui 05/11, manhã
- **Fonte:** `docs/PLAN.md`, seção 8.3. Em caso de divergência, vale o plano.

## Objetivo

Implementar as rotas de metadados, sessões e pares aleatórios usadas pela coleta.

## Arquivos permitidos

`backend/app/schemas/__init__.py`, `meta.py`, `session.py`, `listing.py`, `pair.py`; `backend/app/services/listing_service.py` (`candidate_listings`), `session_service.py`, `pair_service.py`; `backend/app/api/v1/meta.py`, `sessions.py`; `backend/tests/api/test_meta.py`, `test_sessions.py`, `test_pairs_collection.py`.

## Dependências

A03, E06

## Especificação

- **Rotas:** `GET /meta/options`, `GET /meta/personas`, `POST /sessions`, `GET /sessions/{id}`, `GET /sessions/{id}/next-pair`, `POST /sessions/{id}/comparisons/{position}`, com os schemas e as regras da seção 6.
- **`MetaOptions`:** `{ segments: [{ city, purpose, price_floor, price_ceiling }] }`, com o menor e o maior preço de cada segmento.
- **`POST /sessions`:** `target_pairs` vem de `PAIRS_DEMO`, `PAIRS_PRODUCT` ou `PAIRS_COLLECTION`, conforme `mode`. Na coleta, exige `participant_code` e `consent = true`, e grava `consent_at = now()`. O mesmo código pode abrir mais de uma sessão (o colega pode trocar de aparelho).
- **Pares da coleta:** os candidatos são `candidate_listings(session)` (seção 6), ordenados por `code`. A lista dos 40 pares é `random_pairs(len(candidatos), target_pairs, np.random.default_rng(seed_for(session.id, 0)))`, recalculada de forma determinística a cada chamada. O par da posição k é o k-ésimo da lista, gravado em `comparisons` com `selection = 'random'` na primeira vez que for pedido.
- **Modos `demo` e `product`:** `POST /sessions` já funciona, mas `GET /next-pair` devolve `501 not_available` até a E10.
- **Testes:** criação com e sem consentimento; 40 pares sem repetir; recarregar devolve o mesmo par pendente; 409 em resposta repetida e fora de ordem; 204 depois do 40º par e `status = done`; 404 com sessão inexistente; 422 com `price_min >= price_max`.

## Verificação

`cd backend && uv run pytest -q tests/api`.
