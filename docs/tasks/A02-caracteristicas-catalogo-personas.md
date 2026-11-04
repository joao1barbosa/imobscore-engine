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
- **Catálogo:** `generate_catalog(seed: int) -> list[ListingRow]`, em que `ListingRow` é uma dataclass imutável com os campos da tabela `listings` (seção 4), exceto `id` e `created_at`. São 300 imóveis: 3 cidades × 2 finalidades × 50. Tudo vem de `rng = np.random.default_rng(seed)`, nesta ordem fixa de geração: cidade, finalidade, índice.
  - `code`: `{GYN|APG|ANP}-{V|A}-{0001..0050}` (Goiânia, Aparecida de Goiânia, Anápolis; V = venda, A = aluguel).
  - Bairros de Goiânia, com distância ao centro: Setor Central 1 km, Setor Oeste 2, Setor Universitário 2, Setor Marista 3, Setor Bueno 4, Jardim Goiás 5, Setor Pedro Ludovico 5, Jardim América 6, Parque Amazônia 8. Nas outras duas cidades, uma lista fixa de nomes genéricos: Residencial Primavera 3, Jardim das Flores 4, Parque Alvorada 6, Vila Nova 2, Jardim Bela Vista 8, Residencial Ipê 12. `dist_center_km` = distância do bairro + U(−0,5; 0,5), no mínimo 0,3.
  - `kind`: casa com probabilidade 0,35.
  - `bedrooms`: apartamento sorteado em \[1, 2, 3, 4\] com probabilidades \[0,15; 0,40; 0,35; 0,10\]; casa em \[2, 3, 4, 5\] com \[0,15; 0,40; 0,30; 0,15\].
  - `area_m2` = exp(N(ln(28 + 22 × quartos) + 0,15 se casa; 0,18)), com uma casa decimal.
  - `bathrooms`: inteiro de 1 a quartos + 1. `parking` = arredondar(área / 45 + N(0; 0,6)), limitado a \[0, 4\]. `age_years`: inteiro de 0 a 40.
  - `leisure_count`: apartamento em \[0, 1, 2, 3\] com \[0,2; 0,3; 0,3; 0,2\]; casa com \[0,6; 0,3; 0,1; 0\].
  - `doorman_24h`: 0,70 em apartamentos e 0,10 em casas. `pet_friendly`: 0,60.
  - Preço de venda: exp(8,5 + 1,0 × ln(área) + 0,08 × vagas − 0,03 × distância − 0,006 × idade + 0,05 × lazer + 0,04 × portaria + fator da cidade + N(0; 0,12)), arredondado para R$ 1.000. Fator: Goiânia 0; Aparecida −0,12; Anápolis −0,18.
  - Aluguel (`purpose = rent`): preço de venda × 0,0045 × N(1; 0,08), arredondado para R$ 10. `price_brl` guarda o aluguel.
  - Claude só pode ajustar o intercepto (8,5) e os fatores das cidades, para que pelo menos 95% das vendas fiquem entre R$ 150 mil e R$ 2,5 milhões e 95% dos aluguéis entre R$ 700 e R$ 9.000. Os valores finais vão para `docs/decisions.md`.
  - `title`: "Apartamento de 3 quartos no Setor Bueno" ou "Casa de 1 quarto no ..." (singular com 1). `illustration`: `apartment-1` a `apartment-3` ou `house-1` a `house-3`.
- **`personas.yaml`:** lista com `slug`, `name`, `description` (1 frase), `prior_mean` (as 12 chaves da tabela 5.3), `prior_sd` (12 chaves, todas 1,0) e `demo_defaults` (`city`, `purpose`, `price_min`, `price_max`, com os valores da seção 5.3).
- **`inspection_items.yaml`:** lista com `key`, `label` e `delta`: `noisy_street` Rua barulhenta −10; `humidity` Umidade ou mofo −8; `needs_renovation` Precisa de reforma −7; `low_light` Pouca luz natural −5; `good_light` Boa iluminação +5; `quiet_neighborhood` Vizinhança tranquila +6; `walkable_shops` Comércio a pé +5; `nice_view` Vista bonita +4.
- **Testes:** a mesma semente gera o mesmo catálogo; 50 imóveis por segmento; códigos únicos; faixas de preço (95%); `bathrooms ≤ bedrooms + 1`; a mediana vira 0 depois de `standardize`; IQR zero cai para o desvio padrão e depois para 1; `bedrooms_sq` vale 0 para 3 quartos antes da padronização; `raw_matrix` devolve (n, 12).
- **Checkpoint:** CP1.

## Verificação

`cd backend && uv run pytest tests/engine -q && uv run mypy app/engine`.
