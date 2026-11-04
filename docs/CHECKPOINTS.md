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

- **Data:** 2026-11-04. **Módulo:** `backend/app/engine/model.py` e `backend/app/engine/pairs.py`. **Guia:** seções 3, 5 e 6.
- **O que σ(wᵀd) significa para um par?** Resposta certa: a chance de o usuário escolher A em vez de B; no exemplo real, 0,74 indica mais chance de A. Claude acrescentou que é probabilidade e não certeza, que depende dos pesos e que inverter o par dá 0,26.
- **Por que o modelo não tem viés?** Resposta certa: com b diferente de 0, dois imóveis idênticos não dariam 0,5. Claude acrescentou que b mediria preferência pela posição na tela, e que o sorteio de lados já evita isso.
- **E se o peso do preço for −3, o que muda na escolha?** João pediu outra explicação e recebeu um exemplo resolvido com peso −2. Depois, calculou certo: a contribuição do preço vira −1,53, wᵀd cai para 0,027 e a chance fica perto de 0,5, com leve vantagem para A. Claude acrescentou que o peso não significa escolher sempre o mais barato: depende do tamanho da diferença de preço.
- **Dúvidas respondidas:** como ler a pergunta 3.
- **Entendido: sim**

## CP3 · Metropolis-Hastings e diagnósticos (A05) · qui 05/11

- **Data:** 2026-11-04. **Módulo:** `backend/app/engine/mcmc.py` e `backend/app/engine/diagnostics.py`. **Guia:** seções 7 a 9.
- **O que a cadeia guarda a cada passo?** Resposta certa: o ponto atual; com a proposta rejeitada, ela fica no mesmo ponto. Claude acrescentou que o ponto repetido conta de novo como amostra, o que faz a frequência acompanhar a posteriori, e que só 1 a cada 8 estados é salvo depois do aquecimento.
- **Por que a razão de Hastings não aparece no código?** João não sabia e pediu a explicação, com exemplo numérico. Depois, respondeu certo: a proposta é simétrica, então a razão vale 1; com uma proposta assimétrica, a linha do `accept` não representaria a posteriori. Claude acrescentou o termo que faltaria nessa linha e a diferença para o corte de P(D).
- **E se o R-hat der 1,30?** João não sabia o que é o R-hat e pediu a explicação, com exemplo numérico. Depois, respondeu certo: as cadeias não concordam, o sistema roda de novo com tudo dobrado e, se falhar, marca `ok = false` sem bloquear. Claude acrescentou que o sistema não conhece a causa da falha e que o `ok = false` vira um alerta no painel do modelo.
- **Dúvidas respondidas:** o que é o R-hat e o que é a razão de Hastings. Para a banca, João deve rever as seções 9.1 e 9.5 do guia, porque as perguntas 2 e 3 precisaram de explicação antes.
- **Entendido: sim**

## CP4 · Afinidade, BALD e baselines (A06) · sex 06/11

## CP5 · Integração motor e API (A-REV2) · sáb 07/11

## CP6 · Experimento real (A08) · dom 08/11

## CP7 · Ensaio de banca (A09) · seg 09/11
