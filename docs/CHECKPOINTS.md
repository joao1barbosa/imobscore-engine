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

- **Data:** 2026-11-04. **Módulo:** `backend/app/engine/affinity.py`, `backend/app/engine/baselines.py` e `next_pair_bald` em `backend/app/engine/pairs.py`. **Guia:** seções 6.4 e 10.
- **O que o score de 87 quer dizer?** Resposta parcial: a probabilidade de o usuário escolher aquele imóvel. Claude completou: 87% de chance de preferir este imóvel a um imóvel típico (z = 0), como média entre os 4.000 gostos plausíveis, o que não é previsão de compra.
- **Por que a média das sigmoides e não a sigmoide da média?** João não sabia e pediu a explicação, com exemplo numérico. Depois, respondeu certo que a outra conta ignora a incerteza, mas errou o caso de amostras quase iguais: disse que as contas dariam resultados diferentes, e elas dão praticamente o mesmo. Claude corrigiu com números e acrescentou que o exagero da sigmoide da média vai para os dois lados, para longe de 50%.
- **E se a regressão logística não tivesse regularização?** Resposta parcial: com 3 pares faltam dados e os pesos saem do controle; a regularização segura isso, mas João disse "regressão linear" e "normaliza". Claude corrigiu os termos e mostrou que os pesos vão para o infinito em dados separáveis, que a penalidade cria um ponto ótimo e que ela equivale ao MAP com priori normal.
- **Dúvidas respondidas:** a média das sigmoides. Para a banca, João deve rever as seções 6.4 e 10 do guia, porque nenhuma resposta saiu completa de primeira. Claude ofereceu refazer as perguntas, e João preferiu fechar o checkpoint.
- **Entendido: sim**

## CP5 · Integração motor e API (A-REV2) · sáb 07/11

## CP6 · Experimento real (A08) · dom 08/11

- **Data:** 2026-11-09. **Módulo:** A08, com 31 participantes reais, `docs/results.md` e `data/results/`. **Guia:** seção 11.
- **O que a curva de acurácia mostra?** Resposta certa: a porcentagem de acertos de cada método conforme o número de pares de treino. Claude completou: são acertos em 10 pares de teste nunca vistos; a forma das linhas é o resultado (a regressão logística se aproxima do motor, que é a H2); e a faixa de ±1 desvio é larga porque cada acerto vale 10 pontos, então a comparação justa é a pareada por pessoa. Na pergunta complementar, sobre por que a persona e os pesos iguais dão linhas retas, João acertou os pesos iguais, trocou "pares de treino" por "pares de teste" e não soube a persona. Claude explicou que nenhum dos dois aprende com as respostas, que os pesos da persona são o ponto de partida do motor, e que a distância entre as duas linhas mostra o quanto as escolhas acrescentam.
- **Por que os pares da coleta são aleatórios?** Resposta parcial: para ver as escolhas e se o motor acerta. Claude completou com o motivo principal, a justiça: se o motor escolhesse os pares, os quatro métodos seriam avaliados num teste montado por um deles. Com pares aleatórios, todos são testados nos mesmos pares neutros. Na demo, o motor escolhe os pares porque ali o objetivo é aprender rápido.
- **E se o MLE ganhar do bayesiano?** João não sabia. Claude explicou: o modelo é o mesmo, e o motor só acrescenta a priori da persona e a média das amostras, por isso a regressão logística é o controle. Se ela ganhasse, o acréscimo estaria atrapalhando, provavelmente por personas longe do gosto real, o que seria uma descoberta sobre as personas e não um defeito do método. Claude ligou isso aos dados: a persona tem log loss de 0,80, o que explica a H1 fraca. João refez a resposta com as próprias palavras, corretamente.
- **Dúvidas respondidas:** por que as linhas da persona e dos pesos iguais são retas. Para a banca, João deve rever a seção 11.5 do guia (resultado negativo e o papel do controle).
- **Entendido: sim**

## CP7 · Ensaio de banca (A09) · seg 09/11
