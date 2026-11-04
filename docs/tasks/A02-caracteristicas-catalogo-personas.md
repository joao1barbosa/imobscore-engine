# A02 · Características, catálogo simulado e personas

- **Responsável:** A · Arquiteto (Claude)
- **Prazo:** qua 04/11
- **Fonte:** `docs/PLAN.md`, seção 8.2. Em caso de divergência, vale o plano.

## Objetivo

Implementar as 12 características, o catálogo simulado determinístico de 300 imóveis, as personas e os itens de vistoria.

## Arquivos permitidos

`backend/app/engine/features.py`; `backend/app/seed/__init__.py`; `backend/app/seed/catalog.py`; `backend/app/seed/personas.yaml`; `backend/app/seed/inspection_items.yaml`; `backend/tests/engine/test_features.py`; `backend/tests/engine/test_catalog.py`.

## Dependências

E03

## Especificação

- **Especificação:** seções 5.1, 5.3 e 5.10, mais as regras do catálogo a seguir.
- **Catálogo:** `generate_catalog(seed: int) -> list[ListingRow]`, em que `ListingRow` é uma dataclass imutável com os campos da tabela `listings` (seção 4), exceto `id` e `created_at`. São 300 imóveis, todos em Goiânia e à venda (decisão de João em 04/11). Tudo vem de `rng = np.random.default_rng(seed)`, gerados em ordem de índice.
  - `code`: `GYN-V-{0001..0300}`.
  - Bairros, com distância ao centro: Setor Central 1 km, Setor Oeste 2, Setor Universitário 2, Setor Marista 3, Setor Bueno 4, Jardim Goiás 5, Setor Pedro Ludovico 5, Jardim América 6, Parque Amazônia 8. `dist_center_km` = distância do bairro + U(−0,5; 0,5), no mínimo 0,3.
  - `kind`: casa com probabilidade 0,35.
  - `bedrooms`: apartamento sorteado em \[1, 2, 3, 4\] com probabilidades \[0,15; 0,40; 0,35; 0,10\]; casa em \[2, 3, 4, 5\] com \[0,15; 0,40; 0,30; 0,15\].
  - `area_m2` = exp(N(ln(28 + 22 × quartos) + 0,15 se casa; 0,18)), com uma casa decimal.
  - `bathrooms`: inteiro sorteado entre um mínimo e um máximo. O máximo é o menor valor entre os quartos e a área / 25 arredondada para baixo, sendo no mínimo 1. O mínimo é a metade dos quartos arredondada para cima, sem passar do máximo. `parking` = arredondar(área / 45 + N(0; 0,6)), limitado a \[0, 4\]. `age_years`: inteiro de 0 a 40.
  - `leisure_count`: apartamento em \[0, 1, 2, 3\] com \[0,2; 0,3; 0,3; 0,2\]; casa com \[0,6; 0,3; 0,1; 0\].
  - `doorman_24h`: 0,70 em apartamentos e 0,10 em casas. `pet_friendly`: 0,60.
  - Preço de venda: exp(8,5 + 1,0 × ln(área) + 0,08 × vagas − 0,03 × distância − 0,006 × idade + 0,05 × lazer + 0,04 × portaria + N(0; 0,12)), arredondado para R$ 1.000.
  - Claude só pode ajustar o intercepto (8,5), para que pelo menos 95% dos preços fiquem entre R$ 150 mil e R$ 2,5 milhões. Os valores finais vão para `docs/decisions.md`.
  - `title`: "Apartamento de 3 quartos no Setor Bueno" ou "Casa de 1 quarto no ..." (singular com 1). `illustration`: `apartment-1` a `apartment-3` ou `house-1` a `house-3`.
- **`personas.yaml`:** lista com `slug`, `name`, `description` (1 frase), `prior_mean` (as 12 chaves da tabela 5.3), `prior_sd` (12 chaves, todas 1,0) e `demo_defaults` (`city`, `purpose`, `price_min`, `price_max`, com os valores da seção 5.3).
- **`inspection_items.yaml`:** lista com `key`, `label` e `delta`: `noisy_street` Rua barulhenta −10; `humidity` Umidade ou mofo −8; `needs_renovation` Precisa de reforma −7; `low_light` Pouca luz natural −5; `good_light` Boa iluminação +5; `quiet_neighborhood` Vizinhança tranquila +6; `walkable_shops` Comércio a pé +5; `nice_view` Vista bonita +4.
- **Testes:** a mesma semente gera o mesmo catálogo; 300 imóveis, todos em Goiânia e à venda; códigos únicos; faixas de preço (95%); `bathrooms ≤ bedrooms`, no máximo 1 banheiro a cada 25 m² e pelo menos metade dos quartos, salvo quando a área não permite; a mediana vira 0 depois de `standardize`; IQR zero cai para o desvio padrão e depois para 1; `bedrooms_sq` vale 0 para 3 quartos antes da padronização; `raw_matrix` devolve (n, 12).
- **Checkpoint:** CP1.

## Verificação

`cd backend && uv run pytest tests/engine -q && uv run mypy app/engine`.
