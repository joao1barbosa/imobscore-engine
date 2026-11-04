# Checkpoints de entendimento

Protocolo na seção 1.4 de `docs/PLAN.md`. Cada registro traz data, módulo, perguntas, resumo das respostas, dúvidas respondidas e a linha "Entendido: sim". Só João pode declarar "entendido". As seções do guia citadas no protocolo estão em `docs/GUIDE.md`.

## CP1 · Características e catálogo (A02) · qua 04/11

- **Data:** 2026-11-04. **Módulo:** `backend/app/engine/features.py` e `backend/app/seed/catalog.py`. **Guia:** seções 2 e 5.4.
- **O que o vetor zero representa?** João respondeu primeiro "o imóvel ideal, de modo geral". Depois de comparar o zero com um imóvel mais barato e com portaria, concluiu que é a mediana de todos os imóveis. Claude acrescentou que é o ponto "típico", calculado por característica, e que pode não existir como imóvel real: a mediana de `bedrooms` é 3, e a de `bedrooms_sq` é 1. João também entendeu que z indica a distância em relação a esse ponto; Claude acrescentou que o sinal é a direção, e não "melhor" ou "pior".
- **Por que padronizar pela mediana e não pela média?** Resposta certa na primeira tentativa: a mediana não é influenciada por valores extremos, ao contrário da média. Claude ajustou para "pouco influenciada" e citou que o IQR segue a mesma lógica.
- **E se um imóvel tiver 5 quartos, como `bedrooms_sq` muda a utilidade?** João pediu outra explicação e recebeu um exemplo resolvido com 3 quartos. Depois, calculou certo: com os pesos da Família, `bedrooms` soma 2,7 × 0,6 = +1,62, e `bedrooms_sq` soma 4,05 × (−0,4) = −1,62, reduzindo a nota. Claude mostrou que a soma é 0 e que o pico da Família fica em 4 quartos.
- **Dúvidas respondidas:** como ler a pergunta 3.
- **Entendido: sim**

## CP2 · Modelo (A03) · qua 04/11

## CP3 · Metropolis-Hastings e diagnósticos (A05) · qui 05/11

## CP4 · Afinidade, BALD e baselines (A06) · sex 06/11

## CP5 · Integração motor e API (A-REV2) · sáb 07/11

## CP6 · Experimento real (A08) · dom 08/11

## CP7 · Ensaio de banca (A09) · seg 09/11
