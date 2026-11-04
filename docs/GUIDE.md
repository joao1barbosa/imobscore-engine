# ImobScore — Bases matemáticas e guia de estudo

Oct 28, 2026 · @João

## 1. Como usar este guia

Este guia começa do zero e termina explicando cada linha do motor do ImobScore. A ideia é que, em 11/11, você consiga defender o projeto diante de professores experientes. As seções seguem a ordem em que um conceito depende do outro, e nenhuma pressupõe algo que ainda não foi explicado. A Parte I (seções 2 a 12) é o que você precisa para 11/11. A Parte II (seções 13 a 19) é a matemática das fases seguintes do produto: redes com camadas ocultas, ranking, recomendação colaborativa, exploração, inferência bayesiana avançada, testes A/B e deduplicação de anúncios. As seções 20 e 21 trazem o roteiro de estudo e as referências das duas partes.

A frase que resume o projeto, e que você vai entender por completo até a seção 10:

> O ImobScore modela a preferência de cada pessoa com um neurônio sigmoide (modelo de Bradley-Terry). Em vez de achar um único conjunto de pesos, ele usa Metropolis-Hastings, um método de Monte Carlo baseado em cadeias de Markov, para sortear milhares de conjuntos de pesos compatíveis com as escolhas da pessoa e com a persona dela. A média das previsões desses pesos vira o score, e a dispersão entre elas mostra a incerteza.

**Como estudar cada seção**

1. Leia a ideia em palavras.
2. Refaça o exemplo numérico à mão ou na calculadora. Todos os números do guia foram conferidos em Python.
3. Responda ao "Teste-se" sem olhar. As respostas estão logo abaixo.
4. Leia em voz alta o bloco "Na banca", que é a forma curta de explicar aquele ponto.

**Notação usada no guia**

| Símbolo | Lê-se | Significa no ImobScore |
| --- | --- | --- |
| x | "xis" | Atributos brutos de um imóvel (preço, área, quartos…) |
| z | "z" | Os mesmos atributos padronizados, 12 números |
| w | "dablio" | Pesos da pessoa: quanto cada característica importa para ela |
| d | "d" | Diferença entre o imóvel escolhido e o rejeitado (z\_vencedor − z\_perdedor) |
| wᵀz | "w transposto z" | Produto escalar: soma de peso × característica |
| σ(u) | "sigma de u" | Função sigmoide, que transforma qualquer número em uma probabilidade |
| P(A \| B) | "probabilidade de A dado B" | Probabilidade condicional |
| μ, σ | "mi", "sigma" | Média e desvio padrão (cuidado: esse σ não é a sigmoide) |
| D | "D" | Os dados: todas as escolhas da pessoa |
| S | "S" | Número de amostras do MCMC (4.000) |
| Σ | "somatório" | Soma de uma lista de termos |

O mapa dos conceitos está no fim desta seção. Volte a ele sempre que perder o fio.

&#91;embedded content: mapa dos conceitos · seções 2 a 11\]

As setas mostram de onde vem cada peça. O Metropolis-Hastings (seção 9) reúne as duas trilhas: o modelo e o Bayes de cima, o Monte Carlo de baixo.

## 2. Vetores, características e produto escalar

Um vetor é só uma lista ordenada de números. No ImobScore, cada imóvel vira um vetor de 12 números e cada pessoa vira outro vetor de 12 pesos. O produto escalar entre os dois diz o quanto aquele imóvel agrada aquela pessoa.

### 2.1 Imóvel como vetor

Para simplificar, use só 3 características: preço, área e quartos. Um apartamento de R$ 450 mil, 90 m² e 3 quartos vira x = (450.000; 90; 3). A posição importa: o primeiro número é sempre o preço, o segundo a área e o terceiro os quartos.

### 2.2 Por que padronizar

Os números brutos têm escalas muito diferentes. O preço está na casa das centenas de milhares e os quartos vão de 1 a 5. Se fossem usados assim, o preço dominaria qualquer soma. Padronizar é reescrever cada característica como "quantas unidades típicas acima ou abaixo do típico":

```latex
z_j = \frac{t_j(x) - c_j}{s_j}
```

- **t\_j(x)** é a característica depois de uma transformação. Preço e área passam por logaritmo (seção 3), porque uma diferença de R$ 100 mil pesa muito em um imóvel de R$ 200 mil e quase nada em um de R$ 2 milhões. O logaritmo transforma diferenças relativas em diferenças absolutas.
- **c\_j** é a **mediana**: o valor do meio quando todos os imóveis são ordenados. A mediana não é puxada por uma mansão muito cara, ao contrário da média.
- **s\_j** é a escala: o **intervalo interquartil** (IQR, a distância entre o valor que deixa 25% abaixo e o que deixa 75% abaixo) dividido por 1,349. Em dados com distribuição normal, IQR / 1,349 é igual ao desvio padrão. Por isso é chamado de desvio padrão robusto: tem o mesmo significado, mas não se deixa levar por valores extremos.

**Consequência importante:** depois de padronizar, o imóvel mediano, com todas as características no valor do meio, vira o vetor zero (0; 0; …; 0). É esse o "imóvel típico" que aparece no selo do score.

### 2.3 Produto escalar

O produto escalar de w e z multiplica posição por posição e soma tudo:

```latex
w^\top z = w_1 z_1 + w_2 z_2 + \dots + w_{12} z_{12} = \sum_{j=1}^{12} w_j z_j
```

**Exemplo.** A pessoa tem pesos w = (−1,0; 0,8; 0,6) para (preço, área, quartos). O peso negativo no preço quer dizer que mais caro é pior. O imóvel A, já padronizado, é z\_A = (0,5; 1,2; 1,0): um pouco mais caro, bem mais espaçoso e com um quarto a mais que o típico.

```latex
w^\top z_A = (-1{,}0)(0{,}5) + (0{,}8)(1{,}2) + (0{,}6)(1{,}0) = -0{,}50 + 0{,}96 + 0{,}60 = 1{,}06
```

O resultado 1,06 é a **utilidade** do imóvel A para essa pessoa: quanto maior, mais ela gosta. Ainda não é uma probabilidade. A seção 3 mostra como transformá-lo em uma.

### 2.4 Vetor diferença

Para comparar dois imóveis, subtraia um vetor do outro, posição por posição. Com z\_B = (−0,3; 0,0; 0,0):

```latex
d = z_A - z_B = (0{,}5 - (-0{,}3);\; 1{,}2 - 0;\; 1{,}0 - 0) = (0{,}8;\; 1{,}2;\; 1{,}0)
```

```latex
w^\top d = (-1{,}0)(0{,}8) + (0{,}8)(1{,}2) + (0{,}6)(1{,}0) = 0{,}76
```

Repare que wᵀd = wᵀz\_A − wᵀz\_B = 1,06 − 0,30 = 0,76. A diferença das utilidades é igual à utilidade da diferença. Essa propriedade, chamada linearidade, é o que permite ao modelo trabalhar só com d.

**Teste-se**

1. Com w = (−1,0; 0,8; 0,6), qual a utilidade do imóvel típico?
2. Se w\_preço fosse −3,0 em vez de −1,0, A continuaria melhor que B?

*Respostas:* (1) Zero, porque o imóvel típico é o vetor zero. (2) wᵀd = (−3,0)(0,8) + 0,96 + 0,60 = −0,84. Seria negativo, então B passaria a ser o preferido.

**Na banca:** "Cada imóvel vira um vetor de 12 características padronizadas pela mediana e pelo desvio robusto. O imóvel típico fica na origem, e a utilidade é o produto escalar com os pesos da pessoa."

## 3. Funções, exponencial, logaritmo, derivada e a sigmoide

A sigmoide é a peça que transforma uma utilidade (qualquer número real) em uma probabilidade (entre 0 e 1). Para entendê-la, são precisas três ideias: exponencial, logaritmo e derivada.

### 3.1 Função

Uma função é uma regra que recebe um número e devolve outro. f(u) = 2u + 1 recebe 3 e devolve 7. A sigmoide é uma função: recebe a utilidade e devolve uma probabilidade.

### 3.2 Exponencial

O número e ≈ 2,718 é uma constante, como o π. A exponencial e^u (também escrita exp(u)) é "e elevado a u". Três propriedades bastam:

- e^0 = 1, e^u é sempre positiva e cresce muito rápido: e^1 ≈ 2,72; e^2 ≈ 7,39; e^5 ≈ 148.
- e^(−u) = 1 / e^u. Então e^(−5) ≈ 0,0067, muito perto de zero.
- e^(a+b) = e^a · e^b. Somar no expoente equivale a multiplicar.

### 3.3 Logaritmo natural

O logaritmo natural ln (ou log) é o inverso da exponencial: ln(e^u) = u. Ele responde "a que potência elevo e para obter este número?". ln(1) = 0, ln(e) = 1, e o logaritmo só existe para números positivos.

A propriedade que o projeto usa o tempo todo é **log de um produto = soma dos logs**:

```latex
\ln(a \cdot b \cdot c) = \ln a + \ln b + \ln c
```

Isso importa por dois motivos. Primeiro, a probabilidade de várias escolhas acontecerem juntas é um produto de muitos números menores que 1, que fica tão pequeno que o computador arredonda para zero. A soma dos logs não tem esse problema. Segundo, somas são mais fáceis de derivar que produtos.

O logaritmo também explica a padronização do preço: ln(400.000) − ln(200.000) = ln(2) ≈ 0,69, e ln(2.000.000) − ln(1.000.000) = ln(2) ≈ 0,69. Dobrar o preço pesa igual em qualquer faixa.

### 3.4 Derivada

A derivada de uma função em um ponto é a inclinação da curva naquele ponto: quanto a saída muda quando a entrada aumenta um pouquinho. Derivada positiva quer dizer que a função sobe ali, negativa quer dizer que desce, e zero quer dizer que está num topo ou num vale. Com várias entradas (12 pesos), o vetor das derivadas em relação a cada uma se chama **gradiente**, e aponta para onde a função sobe mais rápido. É isso que o treino por gradiente usa (seção 6). Duas regras bastam aqui: a derivada de e^u é e^u, e a derivada de ln(u) é 1/u.

### 3.5 A sigmoide

```latex
\sigma(u) = \frac{1}{1 + e^{-u}}
```

- Se u é muito positivo, e^(−u) ≈ 0 e σ(u) ≈ 1.
- Se u é muito negativo, e^(−u) é enorme e σ(u) ≈ 0.
- Se u = 0, σ(0) = 1 / (1 + 1) = 0,5.

| u | −4 | −2 | −1 | 0 | 1 | 2 | 4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| σ(u) | 0,018 | 0,119 | 0,269 | 0,500 | 0,731 | 0,881 | 0,982 |
| σ'(u) = σ(u)(1 − σ(u)) | 0,018 | 0,105 | 0,197 | 0,250 | 0,197 | 0,105 | 0,018 |

No exemplo da seção 2, wᵀd = 0,76 e σ(0,76) ≈ 0,68. A pessoa prefere A a B com 68% de probabilidade.

**Três propriedades que a banca pode pedir:**

1. **Simetria:** σ(−u) = 1 − σ(u). Por isso P(B ≻ A) = 1 − P(A ≻ B) sai de graça. Veja na tabela: σ(−2) = 0,119 = 1 − 0,881.
2. **Derivada:** σ'(u) = σ(u)(1 − σ(u)). O máximo é 0,25, em u = 0: a probabilidade é mais sensível aos pesos quando o modelo está em dúvida.
3. **Log da chance (logit):** se p = σ(u), então u = ln(p / (1 − p)). A utilidade é o logaritmo da chance (*log-odds*). Um peso w\_j = 0,8 quer dizer: aumentar z\_j em 1 soma 0,8 ao log da chance, ou seja, multiplica a chance por e^0,8 ≈ 2,2.

**Detalhe de implementação:** para u = −1000, e^1000 estoura a memória do computador (vira infinito). O código calcula log(1 + e^(−u)) com `np.logaddexp(0, -u)`, que dá o mesmo resultado sem estourar.

**Teste-se**

1. Quanto vale σ(−0,76)?
2. Se P(A ≻ B) = 0,9, qual a utilidade da diferença?

*Respostas:* (1) 1 − 0,68 = 0,32. (2) u = ln(0,9 / 0,1) = ln(9) ≈ 2,20.

**Na banca:** "A sigmoide transforma a diferença de utilidade em probabilidade, com σ(−u) = 1 − σ(u). Isso garante que P(A ≻ B) + P(B ≻ A) = 1. Os pesos têm leitura direta como log da chance."

## 4. Probabilidade do zero

Probabilidade é um número entre 0 e 1 que mede o quanto algo é esperado: 0 é impossível e 1 é certo. O ImobScore usa probabilidade em dois sentidos: a chance de uma escolha acontecer e o grau de crença sobre quais são os pesos de uma pessoa.

### 4.1 Eventos e regras básicas

- Um **evento** é algo que pode ou não acontecer, como "a pessoa escolhe A".
- **Complemento:** P(não A) = 1 − P(A).
- **Independência e regra do produto:** se dois eventos não influenciam um ao outro, P(A e B) = P(A) · P(B). Dois lançamentos de moeda dão duas caras com 0,5 × 0,5 = 0,25.

O modelo assume que, **conhecidos os pesos w**, cada escolha é independente das outras. Por isso a probabilidade de um conjunto de escolhas é o produto das probabilidades de cada uma (seção 6).

### 4.2 Probabilidade condicional

P(A | B) é a probabilidade de A **sabendo que** B aconteceu:

```latex
P(A \mid B) = \frac{P(A \text{ e } B)}{P(B)}
```

**Exemplo.** Em uma turma de 40 pessoas, 10 procuram aluguel e, dessas, 6 têm pet. P(tem pet | procura aluguel) = 6/10 = 0,6. A condição restringe o universo às 10 pessoas que procuram aluguel. No ImobScore, P(A ≻ B | w) é a probabilidade de escolher A **se** os pesos da pessoa forem w.

### 4.3 Variável aleatória, média e variância

Uma variável aleatória é um número cujo valor depende do acaso, como o resultado de um dado. A **média** (ou esperança, E\[X\]) é o valor médio no longo prazo. Para o dado, (1 + 2 + 3 + 4 + 5 + 6) / 6 = 3,5. A **variância** é a média do quadrado da distância até a média e mede o espalhamento. O **desvio padrão** é a raiz quadrada da variância e volta à unidade original.

### 4.4 Distribuição normal

A distribuição normal N(μ, σ²) é a curva em forma de sino, centrada em μ e com largura σ. A densidade dela é:

```latex
f(w) = \frac{1}{\sigma\sqrt{2\pi}} \exp\left(-\frac{(w - \mu)^2}{2\sigma^2}\right)
```

Você não precisa decorar a fórmula toda. Basta notar que o logaritmo dela é uma parábola:

```latex
\ln f(w) = -\frac{(w - \mu)^2}{2\sigma^2} + \text{constante}
```

É exatamente o termo de log-priori do motor. Valores perto de μ são prováveis, e a probabilidade cai rápido com a distância. Regra prática: cerca de 68% dos valores ficam a menos de 1σ da média, 95% a menos de 2σ e 99,7% a menos de 3σ.

**No ImobScore:** a priori da persona Família diz que o peso do preço é N(−1,0; 1,0²). Antes de qualquer escolha, o motor acredita que o peso está entre −3,0 e +1,0 com 95% de chance, com o valor mais provável em −1,0. Isso deixa espaço até para alguém da persona Família que não liga para preço.

### 4.5 Percentis

O percentil 5 é o valor que deixa 5% dos dados abaixo. O intervalo do percentil 5 ao 95 contém 90% dos valores. É o intervalo que o feed mostra ("entre 71 e 95").

### 4.6 Lei dos grandes números

A média de muitas amostras independentes se aproxima da média verdadeira. Lançando um dado 10 vezes, a média pode dar 4,1. Lançando 10.000 vezes, ela fica muito perto de 3,5. O erro típico cai como 1/√S, em que S é o número de amostras: 100 vezes mais amostras reduzem o erro 10 vezes. Essa lei é a base do Monte Carlo (seção 8).

**Teste-se**

1. Se w \~ N(0,4; 0,5²), entre quais valores estão cerca de 95% dos pesos?
2. Por que a independência das escolhas é "dado w" e não absoluta?

*Respostas:* (1) Entre 0,4 − 1,0 = −0,6 e 0,4 + 1,0 = 1,4. (2) Sem conhecer w, uma escolha dá pistas sobre a próxima, porque ambas revelam o mesmo gosto. Conhecido o gosto, o que sobra é ruído independente.

**Na banca:** "A priori é uma normal por peso, centrada na persona. As escolhas são condicionalmente independentes dado w, o que torna a verossimilhança um produto."

## 5. O neurônio sigmoide e o modelo de Bradley-Terry

O motor do ImobScore é um único neurônio artificial. Ele recebe a diferença entre dois imóveis e devolve a probabilidade de a pessoa preferir o primeiro. Esse neurônio é matematicamente idêntico a um modelo estatístico de 1952 para comparações entre pares, o modelo de Bradley-Terry.

### 5.1 O neurônio artificial

Um neurônio artificial faz duas coisas: (1) uma soma ponderada das entradas e (2) aplica uma função de ativação ao resultado.

```latex
\text{saída} = \text{ativação}\left(\sum_j w_j \, \text{entrada}_j + b\right)
```

- **Entradas:** os 12 números de d = z\_A − z\_B.
- **Pesos:** os 12 números de w, o gosto da pessoa.
- **Viés b:** não existe neste modelo (ver 5.3).
- **Ativação:** sigmoide, então a saída é uma probabilidade.

Uma rede neural é feita de muitos neurônios em camadas. Com uma camada só e um neurônio só, de ativação sigmoide, a rede é exatamente uma **regressão logística**. É o caso mais simples de rede neural, e o ponto de partida de qualquer curso da área.

### 5.2 O modelo de Bradley-Terry

Bradley e Terry (1952) propuseram que cada item i tem uma "força" s\_i e que a chance de i vencer j é:

```latex
P(i \succ j) = \frac{e^{s_i}}{e^{s_i} + e^{s_j}}
```

Dividindo em cima e embaixo por e^(s\_i):

```latex
P(i \succ j) = \frac{1}{1 + e^{s_j - s_i}} = \frac{1}{1 + e^{-(s_i - s_j)}} = \sigma(s_i - s_j)
```

O ImobScore não dá uma força solta para cada imóvel. A força de um imóvel **para aquela pessoa** é a utilidade s = wᵀz. Substituindo:

```latex
P(A \succ B \mid w) = \sigma(w^\top z_A - w^\top z_B) = \sigma\left(w^\top (z_A - z_B)\right) = \sigma(w^\top d)
```

Essa é a fórmula central do projeto. Ela faz o neurônio da 5.1 e o modelo de Bradley-Terry coincidirem.

**Por que isso importa para o produto:** como a força vem das características, e não de um número por imóvel, 3 escolhas já dizem algo sobre todos os 300 imóveis. Uma cadeia de Markov com cada imóvel como estado só aprenderia algo sobre os 6 imóveis mostrados. Foi por isso que essa alternativa foi descartada.

### 5.3 Por que não há viés (intercepto)

Com um viés b, P(A ≻ B) = σ(wᵀd + b). Se A e B forem o mesmo imóvel, d = 0 e a probabilidade seria σ(b), que só vale 0,5 quando b = 0. Um b diferente de zero quer dizer "prefere quem está na posição A": um viés de posição, que não tem nada a ver com gosto. O modelo fica sem b, e o app sorteia o lado em que cada imóvel aparece, para que um viés de posição real da pessoa vire só ruído.

### 5.4 Como ler os pesos

- **Sinal:** w\_preço < 0 quer dizer que, mantido o resto, mais caro é menos preferido.
- **Tamanho:** como as características estão padronizadas, os pesos são comparáveis entre si. |w\_área| = 0,8 contra |w\_vagas| = 0,2 quer dizer que a área pesa 4 vezes mais.
- **Chance:** um aumento de 1 em z\_j multiplica a chance de preferência por e^(w\_j) (seção 3.5).
- **Preferência com pico:** com w\_quartos > 0 e w\_quartos² < 0, a utilidade dos quartos é uma parábola com topo. É assim que o modelo aprende "3 quartos é ideal, 5 é demais", mesmo sendo linear nas características.

### 5.5 Ligado ao RankNet

O RankNet (Burges et al., 2005; Burges, 2010, MSR-TR-2010-82) usa exatamente a mesma probabilidade, σ(f(A) − f(B)), e a mesma perda por pares. A diferença é que f é uma rede com camadas ocultas. O ImobScore é um RankNet em que f(z) = wᵀz, sem camada oculta. A evolução natural, na fase 4, é trocar f por uma MLP quando houver escolhas de muitos usuários, e depois passar ao LambdaMART.

### 5.6 Ruído e inconsistência

A saída é uma probabilidade, não uma certeza. Uma pessoa que escolhe A em um par e, depois, um imóvel parecido com B em outro não quebra o modelo. Ela só indica que, para ela, os dois estão perto de 50%. O modelo também não exige transitividade perfeita: não é um sistema de regras.

**Teste-se**

1. Se z\_A = z\_B, quanto vale P(A ≻ B)?
2. Qual a diferença entre o ImobScore e o RankNet?

*Respostas:* (1) d = 0, então σ(0) = 0,5. (2) A função de pontuação f: no ImobScore ela é linear (um neurônio); no RankNet, é uma rede com camadas ocultas.

**Na banca:** "O motor é um neurônio com sigmoide e sem viés, aplicado à diferença entre dois imóveis. Isso é o modelo de Bradley-Terry com forças lineares nas características, e também o RankNet sem camada oculta."

## 6. Verossimilhança e máxima verossimilhança por gradiente

A verossimilhança mede o quanto um conjunto de pesos w explica as escolhas que a pessoa fez. O jeito clássico de treinar um neurônio é procurar o w que maximiza essa medida. Esse é o baseline `mle` do projeto, e entendê-lo mostra por que o motor bayesiano existe.

### 6.1 Verossimilhança

Com os pares orientados do vencedor para o perdedor (d\_i = z\_vencedor − z\_perdedor), cada escolha tem probabilidade σ(wᵀd\_i). Como as escolhas são independentes dado w (seção 4.1), a probabilidade de todas juntas é o produto:

```latex
L(w) = P(D \mid w) = \prod_{i=1}^{m} \sigma(w^\top d_i)
\qquad
\ell(w) = \ln L(w) = \sum_{i=1}^{m} \ln \sigma(w^\top d_i) = -\sum_{i=1}^{m} \ln\left(1 + e^{-w^\top d_i}\right)
```

A verossimilhança é uma função de w, com os dados fixos. Ela não é a probabilidade de w, e essa distinção costuma ser cobrada.

### 6.2 Exemplo com uma característica

Três escolhas, só com a característica área: d = (1,0; 0,5; −0,4). Nas duas primeiras a pessoa escolheu o imóvel maior. Na terceira, escolheu o menor.

| w | σ(w·1,0) | σ(w·0,5) | σ(w·(−0,4)) | L(w) | ℓ(w) | Derivada ℓ'(w) |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 0,500 | 0,500 | 0,500 | 0,125 | −2,079 | +0,550 |
| 1 | 0,731 | 0,622 | 0,401 | 0,183 | −1,700 | +0,218 |
| 2 | 0,881 | 0,731 | 0,310 | 0,200 | −1,611 | −0,022 |
| 3 | 0,953 | 0,818 | 0,231 | 0,180 | −1,713 | −0,169 |

A verossimilhança é máxima perto de w = 1,88, onde a derivada cruza o zero. Esse é o **estimador de máxima verossimilhança** (MLE). Pesos maiores explicam melhor as duas primeiras escolhas e pior a terceira, e o MLE é o melhor equilíbrio.

### 6.3 Gradiente e o treino por gradiente

Usando a regra da cadeia e a derivada da sigmoide (seção 3.5), a derivada de ln σ(u) é 1 − σ(u). Então:

```latex
\nabla_w \ell(w) = \sum_{i=1}^{m} \left(1 - \sigma(w^\top d_i)\right) d_i
```

Leitura: cada par empurra w na direção de d\_i, com força proporcional ao erro do modelo (1 − σ). Um par que o modelo já acerta com confiança quase não empurra.

O **gradiente ascendente** repete w ← w + η ∇ℓ(w), em que η é a taxa de aprendizado. No exemplo, com η = 1 e começando em w = 0: 0 → 0,55 → 0,91 → 1,16 → 1,33 → … até chegar a 1,88. Em redes neurais, o mesmo processo aparece como "minimizar a perda de entropia cruzada", que é −ℓ(w).

### 6.4 O problema com poucos pares

Com **um único par** (d = 1,0), ℓ(w) = −ln(1 + e^(−w)) só aumenta com w: vale −0,313 em w = 1, −0,007 em w = 5 e −0,00005 em w = 10. Não existe máximo, e o MLE vai para o infinito. Isso acontece sempre que um hiperplano separa perfeitamente os pares (dados separáveis), o que é quase garantido com 3 pares e 12 características.

A correção usual é a **regularização L2**: maximizar ℓ(w) − ‖w‖² / (2C). O scikit-learn faz isso com `C=1.0` por padrão. No exemplo da 6.2, o ótimo cai de 1,88 para 0,41. A seção 7 mostra que essa penalidade é uma priori normal centrada em zero disfarçada. Então o baseline `mle` é, a rigor, um MAP com priori N(0, 1), e o relatório deve dizer isso.

### 6.5 O que falta ao MLE

O MLE devolve **um** w. Ele não diz o quanto o modelo tem certeza desse valor. Depois de 3 pares e depois de 300, a saída tem o mesmo formato, mas a confiança deveria ser muito diferente. A abordagem bayesiana guarda essa informação.

**Teste-se**

1. Por que o gradiente usa (1 − σ) e não σ?
2. Por que o MLE diverge com 1 par?

*Respostas:* (1) Porque o rótulo é sempre 1 (o vencedor), e 1 − σ é o erro da previsão. Acerto total dá erro zero. (2) Porque aumentar w sempre explica melhor aquele único par. Não há nenhum outro dado puxando no sentido contrário.

**Na banca:** "O MLE treina o neurônio por gradiente, mas com 3 pares os dados são separáveis e os pesos divergem. A regularização L2 resolve, mas equivale a uma priori em zero e ainda devolve um ponto só, sem incerteza."

## 7. Teorema de Bayes: priori, verossimilhança e posteriori

O teorema de Bayes diz como atualizar uma crença quando chega um dado novo. No ImobScore, a crença inicial vem da persona (a priori). Cada escolha atualiza essa crença, e o resultado é uma distribuição inteira sobre os pesos (a posteriori), e não um ponto só.

### 7.1 O teorema

```latex
\underbrace{p(w \mid D)}_{\text{posteriori}} = \frac{\overbrace{P(D \mid w)}^{\text{verossimilhança}} \;\cdot\; \overbrace{p(w)}^{\text{priori}}}{\underbrace{P(D)}_{\text{evidência}}}
```

- **Priori p(w):** o que se acredita sobre os pesos antes de ver as escolhas. Aqui é a normal da persona.
- **Verossimilhança P(D | w):** o quanto cada w explica as escolhas (seção 6).
- **Posteriori p(w | D):** a crença atualizada.
- **Evidência P(D):** a probabilidade das escolhas considerando todos os w possíveis. Ela só serve para a posteriori somar 1.

Forma curta, que é a que o código usa: **posteriori ∝ verossimilhança × priori** (∝ lê-se "proporcional a"). Em logaritmo: log-posteriori = log-verossimilhança + log-priori + constante. É a fórmula do `log_posterior` no plano de implementação.

### 7.2 Exemplo discreto: três hipóteses

Antes do caso contínuo, suponha que só existam 3 tipos de pessoa, cada um com pesos fixos para (preço, área, quartos), e que a priori dê 1/3 para cada:

- **Econômico:** w = (−2,0; 0,2; 0,0)
- **Espaço:** w = (−0,3; 1,5; 0,5)
- **Indiferente:** w = (0; 0; 0)

A pessoa escolhe A em vez de B, com d = (0,8; 1,2; 1,0) (seção 2.4: A é mais caro e maior).

| Hipótese | Priori | Verossimilhança σ(wᵀd) | Priori × verossimilhança | Posteriori |
| --- | --- | --- | --- | --- |
| Econômico | 0,333 | σ(−1,36) = 0,204 | 0,068 | 0,128 |
| Espaço | 0,333 | σ(2,06) = 0,887 | 0,296 | 0,557 |
| Indiferente | 0,333 | σ(0) = 0,500 | 0,167 | 0,314 |
| Soma (evidência) |  |  | 0,530 | 1,000 |

Uma escolha só já fez a hipótese Espaço subir de 33% para 56%, mas não eliminou as outras. A posteriori dessa escolha vira a priori da próxima. É assim que o aprendizado acumula.

### 7.3 O caso contínuo e por que é difícil

No motor real, w pode ser qualquer ponto de um espaço de 12 dimensões, e não 3 hipóteses. A evidência vira uma integral:

```latex
P(D) = \int_{\mathbb{R}^{12}} P(D \mid w)\, p(w)\, dw
```

Essa integral não tem fórmula fechada para a sigmoide. Fazer uma grade com 100 valores por peso exigiria 100¹² = 10²⁴ avaliações, o que é impossível. A solução é não calcular P(D): o Metropolis-Hastings (seção 9) só usa razões entre posterioris, em que P(D) se cancela.

### 7.4 Exemplo contínuo com um peso

Com uma característica só, dá para calcular a posteriori em uma grade e ver o efeito da priori. Usando os 3 pares da seção 6.2 e, depois, 60 pares simulados de uma pessoa com peso verdadeiro 1,2:

| Priori | Pares | Média da posteriori | Intervalo de 90% |
| --- | --- | --- | --- |
| N(−1; 1) | 3 | −0,34 | −1,79 a 1,09 |
| N(0; 1) | 3 | 0,42 | −1,01 a 1,87 |
| N(1,5; 1) | 3 | 1,60 | 0,13 a 3,10 |
| N(−1; 1) | 60 | 1,22 | 0,61 a 1,89 |
| N(0; 1) | 60 | 1,38 | 0,74 a 2,08 |
| N(1,5; 1) | 60 | 1,66 | 0,96 a 2,42 |

Duas lições, que são as hipóteses H1 e H2 do relatório:

1. **Com poucos pares, a priori decide muito.** As médias variam de −0,34 a 1,60 conforme a priori. Uma priori boa (perto do gosto real) ajuda; uma ruim atrapalha. É por isso que a persona importa.
2. **Com muitos pares, os dados dominam.** Com 60 pares, as três posterioris ficam entre 1,22 e 1,66, perto do valor verdadeiro 1,2, e os intervalos ficam com cerca de metade da largura.

### 7.5 MAP, regularização e o elo com a seção 6

O ponto mais alto da posteriori se chama **MAP** (máximo a posteriori). Com priori N(0, C):

```latex
\ln p(w \mid D) = \ell(w) - \frac{\|w\|^2}{2C} + \text{const}
```

É exatamente o objetivo do scikit-learn com regularização L2. No exemplo, o MAP com N(0; 1) é 0,41, o mesmo valor da seção 6.4. Então regularização L2 = priori normal em zero. O motor bayesiano vai além em dois pontos: centra a priori na persona, e não em zero, e guarda a distribuição inteira, e não só o topo.

### 7.6 Intervalo de credibilidade contra intervalo de confiança

O intervalo bayesiano de 90% (credibilidade) quer dizer: "dado o modelo e os dados, há 90% de probabilidade de o peso estar aqui". O intervalo de confiança frequentista quer dizer outra coisa: "se o experimento fosse repetido muitas vezes, 90% dos intervalos construídos assim conteriam o valor verdadeiro". É uma pergunta frequente de banca.

**Teste-se**

1. Na tabela da 7.2, por que a hipótese Econômico não foi a zero?
2. Por que o MCMC não precisa calcular P(D)?

*Respostas:* (1) Porque, pelo modelo, mesmo um econômico escolhe o imóvel mais caro 20% das vezes. Uma escolha só não é prova definitiva. (2) Porque ele compara p(w' | D) com p(w | D), e na razão o P(D) aparece em cima e embaixo.

**Na banca:** "A persona é a priori e as escolhas entram pela verossimilhança. A posteriori não tem forma fechada em 12 dimensões, então eu a amostro. Com poucos pares a priori pesa, com muitos os dados dominam, e o experimento mede justamente isso."

## 8. Monte Carlo e cadeias de Markov

MCMC quer dizer *Markov Chain Monte Carlo*. São duas ideias juntas: **Monte Carlo** (calcular médias sorteando amostras) e **cadeia de Markov** (um jeito de produzir essas amostras quando não dá para sorteá-las diretamente).

### 8.1 Monte Carlo: trocar uma integral por uma média

Tudo o que o feed precisa da posteriori é alguma média: a média dos pesos, a probabilidade média de preferir um imóvel, os percentis. Em matemática, essas médias são integrais. Monte Carlo troca a integral pela média de amostras:

```latex
\mathbb{E}[g(w) \mid D] = \int g(w)\, p(w \mid D)\, dw \;\approx\; \frac{1}{S}\sum_{s=1}^{S} g(w_s), \qquad w_s \sim p(w \mid D)
```

Pela lei dos grandes números (seção 4.6), a aproximação melhora com S, e o erro cai como 1/√S. O ImobScore usa S = 4.000 amostras.

Com as amostras em mãos, tudo vira conta simples:

- Média de um peso = média da coluna dele nas 4.000 amostras.
- Intervalo de 90% = percentis 5 e 95 dessa coluna.
- Afinidade de um imóvel = média de σ(w\_sᵀz) (seção 10).

O problema que sobra é **como sortear** amostras de uma distribuição que só conhecemos a menos de uma constante (P(D) é desconhecido). É aí que entra a cadeia de Markov.

### 8.2 Cadeia de Markov

Uma cadeia de Markov é uma sequência de estados em que o próximo estado depende **só do estado atual**, e não do caminho até ele. Essa é a "propriedade de Markov".

**Exemplo do tempo.** Dois estados, Sol e Chuva. Se hoje faz sol, amanhã faz sol com 0,8 e chove com 0,2. Se hoje chove, amanhã faz sol com 0,4 e chove com 0,6.

```latex
T = \begin{pmatrix} 0{,}8 & 0{,}2 \\ 0{,}4 & 0{,}6 \end{pmatrix} \qquad \text{(linha = hoje, coluna = amanhã; ordem: Sol, Chuva)}
```

Começando num dia de chuva, a probabilidade de sol nos dias seguintes é p\_(t+1) = 0,8 p\_t + 0,4 (1 − p\_t):

| Dia | 0 | 1 | 2 | 3 | 4 | 5 | … |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P(Sol), começando com chuva | 0 | 0,400 | 0,560 | 0,624 | 0,650 | 0,660 | → 0,667 |
| P(Sol), começando com sol | 1 | 0,800 | 0,720 | 0,688 | 0,675 | 0,670 | → 0,667 |

Os dois pontos de partida convergem para o mesmo valor, 2/3. Essa é a **distribuição estacionária** π = (2/3, 1/3): depois de muitos passos, a cadeia esquece de onde começou e passa 2/3 do tempo no sol.

Três fatos que valem para o MCMC:

1. Uma cadeia "bem-comportada" (que alcança qualquer estado e não fica presa em ciclos) tem uma única distribuição estacionária e converge para ela de qualquer ponto de partida.
2. Os primeiros passos ainda dependem do ponto de partida. Por isso o motor descarta o início (aquecimento, ou *burn-in*).
3. Passos vizinhos são parecidos entre si (autocorrelação). 4.000 amostras de uma cadeia valem menos que 4.000 amostras independentes, e o ESS (seção 9.5) mede quanto valem.

### 8.3 A ideia do MCMC

No exemplo do tempo, a matriz T foi dada e a distribuição estacionária saiu dela. O MCMC faz o caminho inverso: **constrói uma regra de transição cuja distribuição estacionária é a posteriori desejada**. Depois é só deixar a cadeia andar e anotar onde ela passa. Os estados visitados são as amostras.

A condição que garante isso se chama **balanço detalhado**: o fluxo de w para w' tem de ser igual ao fluxo de w' para w.

```latex
p(w \mid D)\, T(w \to w') = p(w' \mid D)\, T(w' \to w)
```

O Metropolis-Hastings é uma receita que satisfaz essa condição usando só razões p(w' | D) / p(w | D).

**Atenção à diferença de vocabulário, que a banca pode explorar:** no MCMC, os **estados** da cadeia são vetores de pesos w, e não imóveis. A cadeia passeia pelo espaço de gostos possíveis da pessoa. A versão descartada do projeto usava imóveis como estados, que é outra coisa.

**Teste-se**

1. No exemplo do tempo, quantos dias de sol você espera em 300 dias?
2. Por que as primeiras iterações do MCMC são descartadas?

*Respostas:* (1) Cerca de 200 (2/3 de 300). (2) Porque ainda refletem o ponto de partida, e não a distribuição estacionária.

**Na banca:** "Eu preciso de médias sobre a posteriori, e Monte Carlo as estima com amostras. Como não dá para sortear a posteriori diretamente, construí uma cadeia de Markov sobre os pesos cuja distribuição estacionária é a posteriori. Os estados da cadeia são vetores de pesos."

## 9. Metropolis-Hastings passo a passo e diagnósticos

O Metropolis-Hastings (MH) anda pelo espaço de pesos dando passos aleatórios. Ele aceita sempre um passo para uma região mais provável e às vezes aceita um passo para uma menos provável. Essa regra simples faz a cadeia passar em cada região um tempo proporcional à posteriori.

### 9.1 O algoritmo

1. Comece em algum w₀.
2. **Proponha** um vizinho: w' = w + h · σ\_priori ⊙ ε, com ε sorteado de N(0, 1) em cada uma das 12 posições (⊙ é multiplicação posição a posição). O passo h controla o tamanho do pulo.
3. **Calcule a razão** de aceitação:

```latex
\alpha = \min\left(1,\; \frac{p(w' \mid D)}{p(w \mid D)}\right) = \min\left(1,\; \frac{P(D \mid w')\, p(w')}{P(D \mid w)\, p(w)}\right)
```

4. **Sorteie** u uniforme entre 0 e 1. Se u < α, aceite (w ← w'). Senão, fique onde está e conte w de novo como amostra.
5. Volte ao passo 2.

Repare que P(D) sumiu da razão: ele aparece em cima e embaixo. É isso que torna o MH viável (seção 7.3).

**Por que não aparece a correção de Hastings.** Na forma geral, a razão inclui q(w | w') / q(w' | w), em que q é a distribuição da proposta. Como a proposta é uma normal centrada no ponto atual, ir de w para w' é tão provável quanto voltar, então esse fator vale 1. Esse caso simétrico é o algoritmo original de Metropolis (1953). Hastings (1970) generalizou para propostas assimétricas.

**Por que funciona (esboço).** Com proposta simétrica, o fluxo de w para w' é p(w) · q · min(1, p(w')/p(w)) = q · min(p(w), p(w')). Essa expressão é simétrica em w e w', então o fluxo de volta é igual. Isso é o balanço detalhado da seção 8.3, e garante que a posteriori seja a distribuição estacionária.

### 9.2 Em logaritmo

O código trabalha com log, porque as probabilidades são minúsculas. A regra "u < α" vira:

```latex
\ln u < \ln p(w' \mid D) - \ln p(w \mid D)
```

O "min(1, …)" some sozinho: se a diferença for positiva, ln u (que é sempre negativo) é menor que ela e o passo é aceito.

### 9.3 Exemplo à mão

Um peso, priori N(0; 1) e um par com d = 1,0. Então ln p(w | D) = −ln(1 + e^(−w)) − w²/2 + constante.

| Ponto | −ln(1 + e^(−w)) | −w²/2 | ln p (sem a constante) |
| --- | --- | --- | --- |
| w = 0 | −0,693 | 0 | −0,693 |
| w' = 0,8 | −0,371 | −0,320 | −0,691 |
| w'' = 2,5 | −0,079 | −3,125 | −3,204 |

- **De 0 para 0,8:** diferença = −0,691 − (−0,693) = +0,002 > 0. Aceita sempre. A verossimilhança subiu um pouco mais do que a priori caiu.
- **De 0,8 para 2,5:** diferença = −3,204 − (−0,691) = −2,513. A probabilidade de aceitar é e^(−2,513) ≈ 0,08. Em 8% das vezes a cadeia vai para 2,5, e em 92% fica em 0,8. A priori não acredita em pesos tão grandes, e um par só não basta para convencê-la.

### 9.4 O passo h e a taxa de aceitação

- **h pequeno demais:** quase tudo é aceito, mas a cadeia anda devagar e as amostras ficam muito parecidas.
- **h grande demais:** quase tudo é rejeitado e a cadeia fica parada.
- **Meio-termo:** para passeios aleatórios em muitas dimensões, a teoria (Roberts, Gelman e Gilks, 1997) indica uma taxa ótima perto de 0,234. O motor mira 0,30, que é razoável para 12 dimensões, e começa com h = 2,38/√12 ≈ 0,69, que vem da mesma teoria.
- **Adaptação:** no aquecimento, a cada 50 iterações, h ← h · e^(taxa − 0,30). Acima da meta, o passo cresce; abaixo, diminui. Depois do aquecimento, h fica fixo. Se h continuasse mudando conforme o histórico, a transição deixaria de depender só do estado atual, a cadeia deixaria de ser de Markov e a garantia da 9.1 se perderia.
- **Escala por peso:** a proposta multiplica por σ\_priori. Pesos com mais incerteza na priori recebem passos maiores.

### 9.5 Diagnósticos: como saber se convergiu

Nenhum diagnóstico prova a convergência. Eles só detectam sinais de que ela não aconteceu. Por isso o motor roda **16 cadeias** começando de pontos espalhados.

- **Gráfico de traço:** o valor de um peso ao longo das iterações, uma linha por cadeia. Se convergiu, as linhas se misturam numa faixa sem tendência (o aspecto de "lagarta peluda"). Se cada uma fica numa altura, não convergiu. Ele aparece no painel do modelo.
- **R-hat (Gelman-Rubin):** compara a variação **entre** as cadeias com a variação **dentro** de cada uma. Se todas exploram a mesma região, as duas são parecidas e R-hat ≈ 1. O motor exige R-hat < 1,05. A versão "dividida" corta cada cadeia ao meio, para pegar também uma cadeia que ainda está se deslocando.

```latex
\hat{R} = \sqrt{\frac{\frac{n-1}{n} W + \frac{1}{n} B}{W}}, \quad W = \text{média das variâncias dentro}, \quad B = n \times \text{variância das médias entre cadeias}
```

- **ESS (tamanho efetivo da amostra):** quantas amostras independentes as 4.000 amostras correlacionadas valem. Um passeio aleatório em 12 dimensões rende só cerca de 2% de amostras efetivas por iteração. Por isso o motor roda 16 cadeias × 2.000 iterações (32.000 estados) e guarda 1 a cada 8, chegando a 4.000 amostras com ESS acima de 400. Guardar 1 a cada 8 (desbaste) economiza memória quase sem perder informação, porque estados vizinhos são muito parecidos. ESS = S / (1 + 2 Σ ρ\_t), em que ρ\_t é a autocorrelação com defasagem t. O motor exige ESS > 400 em todos os pesos.
- **Taxa de aceitação:** entre 0,15 e 0,50.

### 9.6 O código em uma tela

Esta é a essência do `mcmc.py`. Vale ler até conseguir explicar cada linha:

```python
def metropolis(log_post, mu, sd, rng, chains=16, warmup=1000, draws=2000, thin=8):
    d = mu.size                                    # 12 pesos
    W = mu + sd * rng.standard_normal((chains, d)) # início espalhado
    lp = log_post(W)                               # (chains,)
    h = 2.38 / np.sqrt(d)                          # passo inicial
    out = np.empty((chains, draws // thin, d))
    acc_window = 0
    for t in range(1, warmup + draws + 1):
        W_new = W + h * sd * rng.standard_normal((chains, d))  # proposta simétrica
        lp_new = log_post(W_new)
        accept = np.log(rng.random(chains)) < lp_new - lp       # regra de MH em log
        W[accept], lp[accept] = W_new[accept], lp_new[accept]
        acc_window += accept.mean()
        if t <= warmup and t % 50 == 0:                         # adapta só no aquecimento
            h = float(np.clip(h * np.exp(acc_window / 50 - 0.30), 0.01, 5.0))
            acc_window = 0
        if t > warmup and (t - warmup) % thin == 0:        # desbaste: 1 a cada 8
            out[:, (t - warmup) // thin - 1] = W
    return out, h
```

### 9.7 Alternativas ao MH, para responder "por que este método?"

| Método | O que faz | Por que não foi o escolhido |
| --- | --- | --- |
| Gibbs | Sorteia um peso por vez da distribuição condicional exata | Com a sigmoide, a condicional não tem forma conhecida. Exigiria um truque de aumento de dados (Pólya-Gamma) |
| HMC e NUTS (usados no Stan e no PyMC) | Usam o gradiente para dar passos longos e bem aceitos | Mais eficientes em alta dimensão, mas com 12 pesos o MH basta, e o HMC é bem mais difícil de implementar à mão e de explicar |
| Aproximação de Laplace | Aproxima a posteriori por uma normal em torno do MAP | Rápida, mas supõe uma posteriori simétrica, o que falha com poucos pares |
| Inferência variacional | Ajusta uma distribuição simples por otimização | Tende a subestimar a incerteza, que é justamente o que o produto quer medir |

**Teste-se**

1. Uma proposta pior é sempre rejeitada?
2. O que significa um R-hat de 1,30?

*Respostas:* (1) Não. Ela é aceita com probabilidade igual à razão das posterioris. É isso que deixa a cadeia explorar, em vez de só subir até um pico. (2) Que as cadeias ainda não concordam entre si. As amostras não devem ser usadas, e é preciso rodar mais iterações ou ajustar o passo.

**Na banca:** "É um Metropolis de passeio aleatório gaussiano, com proposta simétrica, então a razão de Hastings vale 1. São 16 cadeias vetorizadas de 3.000 iterações, com 1.000 de aquecimento, em que o passo é adaptado para cerca de 30% de aceitação. Depois disso ele fica fixo. A convergência é checada com R-hat dividido abaixo de 1,05 e ESS acima de 400."

## 10. Da posteriori ao score de afinidade e à incerteza

Com 4.000 vetores de pesos sorteados, o motor calcula para cada imóvel a probabilidade média de ele ser preferido ao imóvel típico. Esse número, vezes 100, é o score. A dispersão entre as 4.000 previsões é o intervalo que aparece no cartão.

### 10.1 Afinidade

Como o imóvel típico é o vetor zero (seção 2.2), comparar o imóvel x com ele dá d = z(x) − 0 = z(x). Então:

```latex
\text{afinidade}(x) = \frac{1}{S}\sum_{s=1}^{S} \sigma\left(w_s^\top z(x)\right) \approx P(x \succ \text{típico} \mid D)
```

Essa média sobre as amostras é a **distribuição preditiva a posteriori**: a probabilidade de preferência levando em conta todos os gostos compatíveis com as escolhas, cada um com o peso que a posteriori dá a ele.

### 10.2 Exemplo com 5 amostras

Uma característica, z(x) = 1,0 e 5 amostras do peso: (0,2; 1,0; 1,8; 2,6; −0,6).

| Amostra w\_s | 0,2 | 1,0 | 1,8 | 2,6 | −0,6 |
| --- | --- | --- | --- | --- | --- |
| σ(w\_s · 1,0) | 0,550 | 0,731 | 0,858 | 0,931 | 0,354 |

- **Afinidade** = média = 0,685, então o score é 68 (sem vistoria).
- **Erro comum:** tirar a média dos pesos primeiro dá w̄ = 1,0 e σ(1,0) = 0,731. O resultado é mais confiante do que deveria. A média das sigmoides incorpora a dúvida: a amostra −0,6 puxa para baixo. Matematicamente, a média de uma função curva não é a função da média (desigualdade de Jensen). Com pouca informação, a versão bayesiana fica mais perto de 50%, o que é o comportamento honesto.
- **Intervalo:** com 4.000 amostras, os percentis 5 e 95 das sigmoides formam o "entre 71 e 95" do cartão. Intervalo largo quer dizer que o modelo ainda não sabe se a pessoa vai gostar. Intervalo estreito quer dizer o contrário.

### 10.3 Score final e vistoria

```latex
\text{score}(x) = \operatorname{clip}\left(\operatorname{round}(100 \cdot \text{afinidade}(x)) + \sum \Delta_{\text{vistoria}},\; 0,\; 100\right)
```

No exemplo, marcar "rua barulhenta (−10)" leva o score de 68 para 58. A vistoria é um ajuste manual por cima do modelo: não muda os pesos nem a posteriori. É importante dizer isso na banca, porque a vistoria não é aprendizado.

### 10.4 "Por que este imóvel"

A utilidade é uma soma, então dá para dividi-la por característica: c\_j = w̄\_j · z\_j(x). Com w̄ = (−1,0; 0,8; 0,6) e z = (0,5; 1,2; 1,0), da seção 2:

| Característica | w̄\_j | z\_j | Contribuição c\_j | Texto mostrado |
| --- | --- | --- | --- | --- |
| Área | 0,8 | 1,2 | +0,96 | mais espaçoso |
| Quartos | 0,6 | 1,0 | +0,60 | mais quartos |
| Preço | −1,0 | 0,5 | −0,50 | mais caro que o típico |

Essa explicação é exata para um modelo linear. Em uma rede com camadas ocultas, ela precisaria de métodos de aproximação. É mais uma vantagem de começar com um neurônio só.

### 10.5 Qual par mostrar em seguida (BALD)

Nos modos demo e produto, o motor escolhe o par que mais ensina. A medida usada é o BALD (*Bayesian Active Learning by Disagreement*, Houlsby et al., 2011), que se apoia na entropia. A entropia H(p) = −p ln p − (1 − p) ln(1 − p) mede a incerteza de um sim ou não: é máxima (0,693) em p = 0,5 e zero em p = 0 ou 1.

```latex
\text{BALD} = \underbrace{H(\bar p)}_{\text{incerteza total}} - \underbrace{\frac{1}{S}\sum_s H(p_s)}_{\text{incerteza que sobraria mesmo sabendo } w}
```

| Par | p\_s em 4 amostras | p̄ | H(p̄) | Média de H(p\_s) | BALD |
| --- | --- | --- | --- | --- | --- |
| Par 1 | 0,50; 0,50; 0,50; 0,50 | 0,50 | 0,693 | 0,693 | 0,000 |
| Par 2 | 0,95; 0,05; 0,95; 0,05 | 0,50 | 0,693 | 0,199 | 0,495 |

Nos dois pares o modelo está em 50%, mas por motivos diferentes. No par 1, todas as amostras concordam que é cara ou coroa: os imóveis são equivalentes para a pessoa, e perguntar não ensina nada. No par 2, as amostras discordam com convicção: metade dos gostos possíveis prefere A e metade prefere B. A resposta elimina metade das hipóteses. O BALD escolhe o par 2.

**Teste-se**

1. Por que a afinidade do imóvel típico é sempre 50?
2. Por que a coleta com colegas não usa o BALD?

*Respostas:* (1) Porque z = 0 dá σ(0) = 0,5 para qualquer amostra. (2) Porque a avaliação precisa de pares que não dependam de nenhum dos modelos comparados. Pares escolhidos pelo motor bayesiano favoreceriam esse motor.

**Na banca:** "O score é a probabilidade preditiva a posteriori de preferir o imóvel ao típico, ou seja, a média das sigmoides sobre as amostras, e não a sigmoide da média. O intervalo vem dos percentis. O próximo par é o de maior BALD, aquele em que os gostos plausíveis mais discordam."

## 11. Avaliação: métricas e baselines

O experimento responde a uma pergunta: com poucas escolhas, qual método acerta mais as preferências reais de uma pessoa em pares que ela respondeu, mas que o modelo nunca viu? Cada colega responde 40 pares aleatórios. Parte deles treina o modelo e outra parte, separada, testa.

### 11.1 Treino e teste

Avaliar um modelo nos mesmos pares usados para treiná-lo mede memória, e não generalização. Por isso, para cada colega:

1. Sorteie 10 pares para teste e deixe-os de lado.
2. Dos 30 restantes, use os n\_train primeiros para treinar, com n\_train ∈ {3, 5, 10, 15, 25}.
3. Meça nos 10 de teste.
4. Repita com 20 sorteios diferentes (`split_seed` de 0 a 19) e tire a média e o desvio padrão. Com só 10 pares de teste, um sorteio isolado varia muito.

Os pares da coleta são aleatórios, e não escolhidos pelo BALD. Se o motor bayesiano escolhesse os pares, a avaliação ficaria a favor dele.

### 11.2 Os quatro métodos

| Método | O que é | Pergunta que responde |
| --- | --- | --- |
| Pesos iguais | Todo peso vale +1 ou −1, conforme a direção óbvia | Personalizar vale a pena? (piso) |
| Média ponderada da persona | Pesos = média da priori, sem aprender nada | A persona sozinha basta? (o produto original) |
| Regressão logística (MLE com L2) | Mesmo neurônio, um ponto só, priori em zero | O ganho vem do neurônio ou da parte bayesiana? |
| Neurônio bayesiano (MCMC) | Priori da persona + escolhas + média sobre amostras | O motor do produto |

A comparação entre a regressão logística e o motor bayesiano isola o efeito da priori da persona e da média sobre amostras, porque o neurônio é o mesmo. É o tipo de controle que uma banca experiente procura.

### 11.3 Acurácia

Proporção de pares de teste em que o método dá mais de 50% ao imóvel que a pessoa escolheu. Exatamente 50% conta como meio acerto. É fácil de explicar ("acertou 7 de 10"), mas ignora a confiança: acertar com 51% vale o mesmo que acertar com 99%.

### 11.4 Perda logarítmica (log loss)

```latex
\text{log loss} = -\frac{1}{n}\sum_{i=1}^{n} \ln p_i, \qquad p_i = \text{probabilidade que o método deu à escolha real}
```

| p dada à escolha real | 0,90 | 0,60 | 0,50 | 0,10 | 0,01 |
| --- | --- | --- | --- | --- | --- |
| −ln p | 0,105 | 0,511 | 0,693 | 2,303 | 4,605 |

Quanto menor, melhor. Um método que sempre diz 50% tem log loss de 0,693, então qualquer valor acima disso é pior que chutar. A métrica pune muito a confiança errada: errar com 99% custa 4,6, contra 0,69 de errar dizendo 50%. É nela que a vantagem bayesiana deve aparecer com poucos pares, porque o MLE tende a ficar confiante demais.

### 11.5 Hipóteses e como ler o resultado

- **H1:** o motor bayesiano supera a média ponderada da persona já com 3 a 5 pares.
- **H2:** o motor bayesiano supera a regressão logística com poucos pares, e a vantagem diminui conforme os pares aumentam.
- **O gráfico principal** é acurácia (ou log loss) contra n\_train, com uma linha por método e uma faixa de ±1 desvio. Se H2 estiver certa, as linhas da regressão logística e do motor bayesiano se aproximam da esquerda para a direita.
- **Limites assumidos:** até 10 colegas de um mesmo curso formam um estudo exploratório. Os resultados saem por pessoa, sem alegar que valem para a população. Personas sintéticas só servem de ponto de partida, e o teste usa apenas escolhas humanas reais.
- **Resultado negativo** também é resultado. Se a regressão logística empatar ou ganhar, a explicação provável é que a priori da persona está longe do gosto real dos colegas. Isso é uma descoberta sobre as personas, e não uma falha do método. A seção 7.4 mostra exatamente esse efeito.

### 11.6 Teste de sanidade com dados simulados

Antes dos dados reais, o comando `simulate` cria pessoas com pesos verdadeiros conhecidos. Nesse caso dá para checar duas coisas que nunca se sabe com dados reais: se a posteriori cobre o peso verdadeiro (o intervalo de 90% deve conter o valor real em cerca de 90% das vezes) e se, com muitos pares e priori fraca, a média do MCMC coincide com o MAP. Isso valida o código, não o produto.

**Teste-se**

1. Um método tem acurácia de 0,70 e log loss de 0,90. O que isso indica?
2. Por que repetir com 20 sorteios?

*Respostas:* (1) Ele acerta a direção 7 em 10 vezes, mas, quando erra, erra com muita confiança. O log loss ficou pior que o de chutar 50% (0,693). (2) Porque com 10 pares de teste cada acerto muda a acurácia em 10 pontos. A média de 20 divisões reduz essa variação e mostra o quanto o resultado oscila.

**Na banca:** "Avaliei em pares de teste separados, com 20 divisões por pessoa, usando acurácia e log loss. A regressão logística é o controle que isola a contribuição da priori e do MCMC, e os pares da coleta são aleatórios para não favorecer nenhum método."

## 12. Perguntas prováveis da banca e respostas

São 18 perguntas, agrupadas por tema, com respostas de 2 a 4 frases. Treine em voz alta até responder sem ler. Quando não souber algo, diga "isso está fora do que eu testei" e explique o que faria para testar. Isso vale mais do que improvisar.

### Sobre ser rede neural

1. **"Um neurônio só é rede neural?"** É a rede neural mais simples: uma camada, uma unidade, ativação sigmoide, o que equivale à regressão logística. A contribuição do projeto está em treiná-la de forma bayesiana, com MCMC, o que é uma rede neural bayesiana na forma mínima. A MLP com RankNet está no roadmap para quando houver dados de muitos usuários.
2. **"Por que não usou uma MLP?"** Com 3 a 25 pares por pessoa, uma camada oculta teria muito mais parâmetros do que dados e decoraria as respostas. Além disso, o modelo linear dá explicações exatas por característica.
3. **"Qual a relação com o RankNet?"** Mesma probabilidade σ(f(A) − f(B)) e mesma perda por pares. No ImobScore, f é linear. No RankNet, f é uma rede com camadas ocultas.
4. **"Por que não tem viés?"** Para que dois imóveis iguais deem exatamente 50%. Um viés seria preferência pelo lado da tela, e o lado é sorteado.

### Sobre a parte bayesiana

5. **"Por que bayesiano e não só gradiente?"** Com poucos pares, o MLE diverge ou fica confiante demais. A priori da persona dá um ponto de partida sensato, e a posteriori dá a incerteza, que o produto usa no intervalo do cartão e na escolha do próximo par.
6. **"A priori não enviesa o resultado?"** Enviesa de propósito quando há poucos dados, e perde peso conforme os pares chegam (seção 7.4). Uma priori ruim é um risco real. O experimento mede isso ao comparar com a regressão logística, que não usa a persona.
7. **"De onde vieram os valores das personas?"** São hipóteses de partida escritas à mão, com desvio 1,0 para deixar espaço aos dados. Não foram estimadas de dados reais. Calibrá-las com dados de muitos usuários é trabalho futuro.
8. **"Qual a diferença entre o seu intervalo e um intervalo de confiança?"** O meu é de credibilidade: 90% de probabilidade de o valor estar ali, dado o modelo e os dados. O de confiança fala da frequência com que o procedimento acertaria em repetições do experimento.

### Sobre o MCMC

9. **"Isso é uma cadeia de Markov? Onde está a cadeia?"** Os estados são vetores de pesos. O próximo estado depende só do atual (proposta mais aceitação), e a regra de aceitação faz a distribuição estacionária ser a posteriori.
10. **"Por que a razão de Hastings não aparece?"** Porque a proposta gaussiana centrada no ponto atual é simétrica, então q(w | w') / q(w' | w) = 1.
11. **"Como você sabe que convergiu?"** Não há prova. Rodo 16 cadeias de pontos espalhados e exijo R-hat dividido abaixo de 1,05, ESS acima de 400 e aceitação entre 15% e 50%. Também testo o código em um alvo gaussiano conhecido e comparo com o MAP quando há muitos dados.
12. **"Por que Metropolis e não HMC ou NUTS?"** Com 12 dimensões, o Metropolis é suficiente e dá para implementar e explicar inteiro. O HMC seria mais eficiente em dimensão alta e é o próximo passo natural se o modelo crescer.
13. **"A adaptação do passo não quebra a cadeia?"** Ela só acontece no aquecimento, que é descartado. Depois, o passo fica fixo e a cadeia é de Markov.
14. **"Quanto tempo leva?"** Cerca de 200 ms com 40 pares no notebook, porque as 16 cadeias avançam vetorizadas no NumPy. Por isso o motor roda depois de cada resposta, sem espera visível.

### Sobre dados, avaliação e produto

15. **"Os dados são reais?"** O catálogo é simulado, com regras de preço plausíveis, e isso aparece na tela. As escolhas usadas na avaliação são reais, de colegas, com consentimento.
16. **"Dez pessoas bastam?"** Para generalizar, não. O estudo é exploratório e os resultados saem por pessoa, com 20 divisões de treino e teste para mostrar a variação.
17. **"E se a pessoa for inconsistente?"** O modelo é probabilístico: escolhas contraditórias só aproximam as previsões de 50% e alargam o intervalo. Não quebram nada.
18. **"Por que características lineares capturam '3 quartos é ideal'?"** Por causa da característica (quartos − 3)². Com peso negativo nela, a utilidade dos quartos vira uma parábola com topo, e o modelo continua linear nos pesos.

# Parte II · A matemática das próximas fases

Esta parte não é necessária para 11/11. Ela prepara você para as fases 2 a 5 do roadmap e para perguntas do tipo "e depois?". Cada seção diz em que fase o assunto entra e parte do que você já sabe da Parte I.

## 13. Redes com camadas ocultas e retropropagação

**Fase 4 (motor híbrido).** Um neurônio só soma efeitos independentes: área vale o mesmo com ou sem vaga. Uma camada oculta permite interações, como "aceitar pet só importa se for casa" ou "perto do centro só compensa abaixo de certo preço". Com escolhas de muitos usuários, uma MLP aprende essas interações, e o RankNet é a forma de treiná-la com pares.

### 13.1 A MLP (perceptron multicamadas)

```latex
h = \operatorname{ReLU}(W_1 z + b_1), \qquad f(z) = v^\top h + c, \qquad \operatorname{ReLU}(u) = \max(0, u)
```

- **W₁** é uma matriz: cada linha é um neurônio oculto, com os próprios 12 pesos. Com 32 neurônios ocultos, W₁ tem 32 × 12 = 384 pesos.
- **ReLU** zera o que é negativo. Sem uma função não linear entre as camadas, duas camadas lineares se reduzem a uma só.
- **f(z)** é a utilidade, como wᵀz no MVP, só que agora não linear.

**Exemplo.** z = (1,0; 0,5), W₁ = \[\[0,5; −1,0\]; \[1,0; 1,0\]\], b₁ = 0 e v = (0,8; 0,6). Então W₁z = (0,5 − 0,5; 1,0 + 0,5) = (0; 1,5), h = ReLU(0; 1,5) = (0; 1,5) e f = 0,8 · 0 + 0,6 · 1,5 = 0,9. O primeiro neurônio oculto ficou "desligado" para esse imóvel.

### 13.2 Perda do RankNet

A probabilidade é a mesma da Parte I, trocando wᵀz por f(z):

```latex
P(A \succ B) = \sigma\big(f(z_A) - f(z_B)\big), \qquad \mathcal{L} = -\sum_{\text{pares}} \ln \sigma\big(f(z_{\text{venc}}) - f(z_{\text{perd}})\big)
```

Com Δ = f(z\_venc) − f(z\_perd), a derivada da perda em relação às duas saídas é:

```latex
\frac{\partial \mathcal{L}}{\partial f(z_{\text{venc}})} = -\big(1 - \sigma(\Delta)\big), \qquad \frac{\partial \mathcal{L}}{\partial f(z_{\text{perd}})} = +\big(1 - \sigma(\Delta)\big)
```

O vencedor é empurrado para cima e o perdedor para baixo, com força igual ao erro. É o mesmo (1 − σ) da seção 6.3. Burges chamou essa força de "lambda", e é dela que vem o nome LambdaRank (seção 14).

### 13.3 Retropropagação (backpropagation)

Para treinar, é preciso a derivada da perda em relação a cada peso de W₁ e v. A retropropagação é a regra da cadeia aplicada de trás para frente:

```latex
\frac{\partial \mathcal{L}}{\partial v} = \frac{\partial \mathcal{L}}{\partial f}\, h, \qquad \frac{\partial \mathcal{L}}{\partial W_1} = \left(\frac{\partial \mathcal{L}}{\partial f}\, v \odot \mathbb{1}[W_1 z + b_1 > 0]\right) z^\top
```

O termo 1\[… > 0\] é a derivada da ReLU: 1 onde o neurônio estava ligado e 0 onde estava desligado. Na prática, bibliotecas como o PyTorch calculam isso sozinhas (diferenciação automática). Mas a banca de uma fase futura vai esperar que você saiba de onde vem.

### 13.4 Otimização e generalização

- **SGD com mini-lotes:** atualiza os pesos com o gradiente de um punhado de pares por vez, em vez de todos. É mais rápido e o ruído ajuda a sair de regiões ruins.
- **Adam:** o otimizador padrão. Ajusta a taxa de aprendizado de cada peso usando médias móveis do gradiente e do quadrado dele.
- **Sobreajuste:** com mais pesos que dados, a rede decora. Os remédios são separar treino, validação e teste; usar *weight decay* (a mesma L2 da seção 6.4); *dropout* (desligar neurônios ao acaso no treino); e parar cedo quando a perda de validação volta a subir.
- **Embeddings:** variáveis com muitas categorias, como bairro, viram vetores aprendidos de poucos números. Bairros parecidos para os usuários ficam com vetores próximos.

### 13.5 Como isso se junta ao MVP

No motor híbrido, a MLP global aprende uma representação rica dos imóveis com dados de todos os usuários. O neurônio bayesiano do MVP continua por cima, com pesos pessoais sobre essa representação. A rede dá a visão geral, e o MCMC personaliza com poucos pares. Para levar incerteza à rede inteira, as opções comuns são *deep ensembles* (treinar várias redes com sementes diferentes) e *MC dropout* (manter o dropout ligado na previsão).

**Teste-se.** Por que duas camadas lineares sem ReLU equivalem a uma? *Resposta:* W₂(W₁z) = (W₂W₁)z, e o produto de duas matrizes é outra matriz.

## 14. Aprender a ranquear: NDCG, LambdaRank e LambdaMART

**Fase 4.** O RankNet acerta pares, mas o usuário só olha o topo do feed. Errar a ordem entre o 1º e o 2º é muito pior que errar entre o 41º e o 42º. O LambdaRank e o LambdaMART corrigem isso pesando cada par pelo quanto ele muda uma métrica de topo, o NDCG.

### 14.1 NDCG

Cada imóvel mostrado tem uma relevância rel (ex.: 0 = ignorado, 1 = clicado, 2 = favoritado, 3 = visita marcada). O ganho acumulado com desconto (DCG) pesa mais as primeiras posições:

```latex
\text{DCG@k} = \sum_{i=1}^{k} \frac{2^{\text{rel}_i} - 1}{\log_2(i + 1)}, \qquad \text{NDCG@k} = \frac{\text{DCG@k}}{\text{DCG@k da ordem ideal}}
```

| Ordem mostrada (relevâncias) | DCG@4 | NDCG@4 |
| --- | --- | --- |
| 3, 2, 1, 0 (ideal) | 7 + 1,893 + 0,5 + 0 = 9,393 | 1,000 |
| 3, 2, 0, 1 (troca no fim) | 7 + 1,893 + 0 + 0,431 = 9,324 | 0,993 |
| 0, 2, 3, 1 (o melhor em 3º) | 0 + 1,893 + 3,5 + 0,431 = 5,824 | 0,620 |

Trocar os dois últimos custa menos de 1%. Tirar o melhor do topo custa 38%.

### 14.2 LambdaRank

O NDCG muda aos saltos quando a ordem muda, então não tem derivada útil. O truque de Burges foi não derivar o NDCG, e sim multiplicar a força do RankNet pelo quanto o NDCG mudaria se o par trocasse de lugar:

```latex
\lambda_{ij} = \big(1 - \sigma(f_i - f_j)\big) \cdot \left|\Delta \text{NDCG}_{ij}\right|
```

Pares que mexem no topo empurram forte. Pares lá de baixo quase não empurram.

### 14.3 Árvores com gradient boosting e LambdaMART

- **Árvore de decisão:** uma sequência de perguntas ("área > 80 m²?", "bairro = Setor Bueno?") que termina em um valor. Captura interações e limiares naturalmente.
- **Gradient boosting:** soma de muitas árvores pequenas, F(z) = Σ η · árvoreₘ(z). Cada árvore nova é treinada para prever o gradiente da perda das anteriores, ou seja, para corrigir o erro que sobrou. η (taxa de aprendizado, ex.: 0,05) faz cada correção ser pequena. É gradiente descendente no espaço de funções.
- **LambdaMART** = gradient boosting em que o "gradiente" de cada imóvel é a soma dos λ dos pares em que ele aparece. Na prática, é o objetivo `lambdarank` do LightGBM ou o `rank:ndcg` do XGBoost.
- **Por que árvores:** em dados tabulares (preço, área, bairro), modelos de árvores ainda costumam vencer redes neurais (Grinsztajn et al., 2022). Por isso o roadmap prevê testar os dois.

### 14.4 Cliques não são escolhas limpas

No produto, os dados deixam de ser pares explícitos e passam a ser cliques e favoritos. Dois cuidados matemáticos aparecem:

- **Viés de posição:** o 1º do feed recebe mais cliques só por estar em cima. A correção usual é pesar cada clique pelo inverso da probabilidade de aquela posição ser vista (*inverse propensity weighting*).
- **Pares implícitos:** "clicou no 3º e pulou o 1º e o 2º" vira os pares 3 ≻ 1 e 3 ≻ 2. É assim que o Bradley-Terry do MVP continua útil com dados de uso.

**Teste-se.** Por que o LambdaRank não deriva o NDCG diretamente? *Resposta:* Porque o NDCG só muda quando dois itens trocam de posição. Entre uma troca e outra ele é constante, então a derivada é zero em quase todo lugar.

## 15. Recomendação colaborativa e modelo hierárquico

**Fases 2 e 4.** O MVP aprende cada pessoa isoladamente, partindo de uma persona escrita à mão. Com muitos usuários, dá para aprender as personas a partir dos dados e aproveitar o que pessoas parecidas escolheram. Duas famílias de métodos fazem isso: a filtragem colaborativa e os modelos bayesianos hierárquicos.

### 15.1 Similaridade de cosseno

O jeito mais simples de achar "imóveis parecidos com os que você curtiu" é comparar vetores pelo ângulo entre eles:

```latex
\cos(a, b) = \frac{a^\top b}{\|a\|\,\|b\|}, \qquad \|a\| = \sqrt{a^\top a}
```

Vale 1 para vetores na mesma direção, 0 para perpendiculares e −1 para opostos. É o produto escalar da seção 2, normalizado pelo tamanho dos vetores.

### 15.2 Fatoração de matrizes

Monte uma matriz R com uma linha por usuário e uma coluna por imóvel, preenchida com 1 onde houve interação. A fatoração procura vetores curtos p\_u (usuário) e q\_i (imóvel) tais que:

```latex
r_{ui} \approx p_u^\top q_i, \qquad \min_{p, q} \sum_{(u,i)\ \text{observados}} \left(r_{ui} - p_u^\top q_i\right)^2 + \lambda\left(\|p_u\|^2 + \|q_i\|^2\right)
```

Os vetores q\_i viram características aprendidas, que capturam o que as 12 características manuais não capturam (ex.: "prédio com boa fama"). O ponto fraco é o **cold start**: imóvel novo não tem interações e, portanto, não tem q\_i. O modelo por características do MVP não sofre disso, e por isso os dois se complementam em um modelo híbrido.

### 15.3 Modelo hierárquico: personas aprendidas

Hoje a priori de cada pessoa é N(μ\_persona, σ²), com μ escrito à mão. No modelo hierárquico, μ também vira um parâmetro aprendido com os dados de todos:

```latex
\mu_{\text{persona}} \sim \mathcal{N}(0, \tau^2), \qquad w_u \sim \mathcal{N}(\mu_{\text{persona}(u)}, \sigma^2 I), \qquad \text{escolhas}_u \sim \text{Bradley-Terry}(w_u)
```

Isso produz o **agrupamento parcial** (*partial pooling*): quem tem poucos pares fica perto da média do grupo, e quem tem muitos se afasta dela. No caso mais simples, com uma média de grupo μ, n observações com média x̄ e variâncias conhecidas, a estimativa é uma média ponderada:

```latex
\hat{w}_u = \frac{\frac{n}{s^2}\,\bar{x}_u + \frac{1}{\sigma^2}\,\mu}{\frac{n}{s^2} + \frac{1}{\sigma^2}}
```

Com n = 0, a estimativa é μ. Quando n cresce, ela vai para x̄\_u. É a mesma lógica da seção 7.4, agora com μ aprendido. Na banca de uma fase futura, isso responde à pergunta "de onde vieram as personas?" com dados, e não com palpite.

### 15.4 Descobrir personas

Com as médias das posterioris de muitos usuários, um algoritmo de agrupamento (k-means ou uma mistura de normais) encontra grupos de gosto parecido. Esses grupos substituem as três personas manuais e podem revelar perfis que ninguém imaginou.

**Teste-se.** Por que o modelo por características resolve o cold start de imóveis novos, e a fatoração não? *Resposta:* Porque ele avalia qualquer imóvel pelas características que ele já tem ao ser cadastrado. A fatoração depende do histórico de interações do imóvel.

## 16. Explorar ou aproveitar: bandits e amostragem de Thompson

**Fase 4.** Um feed que só mostra o que o modelo já acha bom nunca descobre se a pessoa gostaria de outra coisa. Mostrar algo incerto custa um pouco agora e ensina para depois. Esse dilema se chama **exploração contra aproveitamento**, e a teoria dos *multi-armed bandits* estuda como equilibrá-lo.

### 16.1 O problema

Há várias opções ("braços", como em máquinas caça-níqueis), cada uma com uma taxa de sucesso desconhecida. A cada rodada você escolhe uma, vê o resultado e aprende. O objetivo é minimizar o **arrependimento** (*regret*): a diferença entre o que você ganhou e o que ganharia escolhendo sempre a melhor opção.

| Estratégia | Como escolhe | Problema |
| --- | --- | --- |
| Gulosa | Sempre a de maior média estimada | Pode ficar presa na primeira que pareceu boa |
| ε-gulosa | A melhor, exceto em ε% das vezes, ao acaso | Explora até o que já sabe que é ruim |
| UCB | A de maior média + bônus de incerteza | Precisa de uma fórmula de bônus para cada modelo |
| Thompson | Sorteia uma hipótese da posteriori e age como se ela fosse verdade | Precisa da posteriori, e o ImobScore já tem |

### 16.2 Amostragem de Thompson

A regra é escolher cada opção com a probabilidade de ela ser a melhor. Na prática, basta sortear uma amostra da posteriori e escolher a melhor opção segundo aquela amostra.

**Exemplo com cliques.** Dois anúncios: A teve 3 cliques em 10 exibições e B, 1 clique em 2. Com priori uniforme, as posterioris das taxas de clique são distribuições Beta: A \~ Beta(4, 8), com média 0,33, e B \~ Beta(2, 2), com média 0,50 e muito mais incerta. Sorteando uma taxa de cada e mostrando a maior, B é escolhido cerca de 73% das vezes. Ele ganha espaço por ser promissor e pouco conhecido, e o espaço encolhe sozinho se os novos dados forem ruins.

### 16.3 No ImobScore

O motor já tem 4.000 amostras de w. Para Thompson, em vez de ordenar o feed pela afinidade média, sorteie uma amostra w\_s e ordene por σ(w\_sᵀz). Cada vez que o feed é montado, a ordem varia um pouco, mais onde o modelo está incerto. Uma versão mais conservadora mantém os primeiros itens pela média e reserva algumas posições para Thompson. O BALD da seção 10.5 tem o mesmo espírito, mas otimiza só o aprendizado. Thompson equilibra aprender e agradar.

**Teste-se.** Por que a amostragem de Thompson explora menos com o tempo? *Resposta:* Porque a posteriori se estreita com os dados. As amostras passam a concordar, e a opção escolhida quase sempre é a melhor.

## 17. Inferência bayesiana avançada

**Fase 4 em diante.** Quando o modelo crescer (pesos pessoais sobre uma representação com dezenas ou centenas de dimensões, ou um modelo hierárquico com milhares de usuários), o passeio aleatório do Metropolis fica lento demais. Estas são as ferramentas seguintes.

### 17.1 Conjugação: quando a posteriori tem fórmula

Algumas combinações de priori e verossimilhança dão uma posteriori da mesma família da priori. Com priori Beta(a, b) para uma taxa de clique e k cliques em n exibições, a posteriori é Beta(a + k, b + n − k), sem nenhuma amostragem (seção 16.2). Normal com normal também dá normal (seção 15.3). A sigmoide não tem par conjugado, e é por isso que o MVP precisa de MCMC.

### 17.2 Hamiltonian Monte Carlo (HMC) e NUTS

O HMC trata a log-posteriori como um terreno e o vetor w como uma bolinha que rola nele. A bolinha recebe um empurrão aleatório (o momento p) e segue as leis da física por um tempo, usando o gradiente para saber para onde o terreno desce:

```latex
H(w, p) = \underbrace{-\ln p(w \mid D)}_{\text{energia potencial}} + \underbrace{\tfrac{1}{2} p^\top p}_{\text{energia cinética}}
```

A trajetória é simulada com o integrador *leapfrog* (passos alternados de posição e momento) e termina com uma aceitação no estilo Metropolis. O resultado são saltos longos e com alta aceitação, mesmo em centenas de dimensões. O **NUTS** (*No-U-Turn Sampler*) escolhe sozinho o comprimento da trajetória, parando quando ela começa a voltar. É o padrão do Stan, do PyMC e do NumPyro. Pré-requisito: o gradiente da log-posteriori, que você já sabe calcular (seção 6.3).

### 17.3 Aproximação de Laplace

Ache o MAP e aproxime a posteriori por uma normal centrada nele, com a curvatura dada pela matriz de segundas derivadas (Hessiana) H:

```latex
p(w \mid D) \approx \mathcal{N}\left(w_{\text{MAP}},\; H^{-1}\right), \qquad H = -\nabla^2 \ln p(w \mid D)\,\big|_{w_{\text{MAP}}}
```

É muito rápida e funciona bem com muitos dados. Com poucos pares, a posteriori fica assimétrica e a aproximação piora. Vale comparar com o MCMC do MVP: é um bom experimento para um relatório futuro.

### 17.4 Inferência variacional

Escolha uma família simples q(w), como uma normal com média e desvio por peso, e ajuste-a para ficar o mais perto possível da posteriori. "Perto" é medido pela divergência de Kullback-Leibler, e o ajuste maximiza o ELBO:

```latex
\text{ELBO}(q) = \mathbb{E}_{q}\left[\ln P(D \mid w)\right] - \mathrm{KL}\left(q(w) \,\|\, p(w)\right)
```

Vira um problema de otimização, que escala para milhões de parâmetros (é assim que se treinam redes neurais bayesianas grandes). O preço é que ela costuma subestimar a incerteza.

### 17.5 Gibbs com Pólya-Gamma

Polson, Scott e Windle (2013) mostraram que, introduzindo uma variável auxiliar com distribuição Pólya-Gamma por par, a regressão logística passa a ter condicionais normais. Aí dá para usar Gibbs, que não precisa de passo nem de taxa de aceitação. É um caminho elegante para um MCMC mais eficiente no mesmo modelo do MVP.

### 17.6 O fluxo de trabalho bayesiano

Gelman et al. (2020) descrevem o processo completo, que vale para qualquer versão futura do motor:

1. **Checagem preditiva da priori:** sorteie pesos só da priori e veja se os feeds gerados fazem sentido. Uma persona Família que prefere quitinetes indica uma priori errada.
2. **Ajuste e diagnósticos:** R-hat e ESS, de preferência nas versões com normalização por postos (Vehtari et al., 2021), mais robustas que a da seção 9.5.
3. **Checagem preditiva da posteriori:** simule escolhas com as amostras e compare com as escolhas reais.
4. **Comparação de modelos:** validação cruzada, como no experimento da seção 11.

**Teste-se.** Por que o HMC precisa do gradiente e o Metropolis não? *Resposta:* O Metropolis só compara valores da posteriori em dois pontos. O HMC simula uma trajetória, e a força que move a bolinha é o gradiente da log-posteriori.

## 18. Experimentos online: teste A/B e métricas de negócio

**Fases 2 e 5.** O portão da fase 2 pergunta se as pessoas preferem o feed aos filtros. A forma confiável de responder é um teste A/B: sortear usuários para cada versão e comparar uma métrica definida antes. A matemática aqui é a estatística inferencial clássica, que complementa o lado bayesiano da Parte I.

### 18.1 Teste de hipótese

- **Hipótese nula H₀:** não há diferença entre feed e filtros na métrica (ex.: % de usuários que salvam um imóvel).
- **p-valor:** a probabilidade de ver uma diferença pelo menos tão grande quanto a observada **se H₀ fosse verdadeira**. Não é a probabilidade de H₀ ser verdadeira. Essa confusão é o erro mais comum.
- **Nível de significância α = 0,05:** rejeita-se H₀ se p < 0,05. Em 5% dos testes sem diferença real, haverá um falso positivo.
- **Poder (1 − β), geralmente 80%:** a chance de detectar uma diferença que realmente existe.

### 18.2 Quantos usuários são necessários

Para comparar duas proporções com α = 0,05 e poder de 80%, uma regra prática para o tamanho por grupo é:

```latex
n \approx \frac{16\, p(1-p)}{\delta^2}
```

em que p é a taxa atual e δ é a menor diferença que importa. Com 10% dos usuários salvando um imóvel e δ = 2 pontos percentuais: n ≈ 16 × 0,09 / 0,0004 = 3.600 por grupo. Diferenças pequenas exigem muitos usuários: δ = 1 ponto quadruplica o n. Saber disso evita lançar um teste que nunca teria poder para responder.

### 18.3 Armadilhas

- **Espiar o resultado** todo dia e parar quando p < 0,05 infla muito os falsos positivos. Defina o tamanho antes, ou use métodos sequenciais.
- **Muitas métricas:** com 20 métricas, uma deve dar "significativa" por acaso. Escolha uma métrica principal antes.
- **Efeito novidade:** a versão nova atrai curiosidade nos primeiros dias.
- **Desbalanceamento da amostra:** se o sorteio era 50/50 e os grupos ficaram 52/48, algo está quebrado na atribuição.

### 18.4 Versão bayesiana do A/B

Com priori Beta para a taxa de cada grupo (seção 17.1), a posteriori sai direto. Por Monte Carlo, calcula-se P(taxa\_feed > taxa\_filtros | dados). A pergunta respondida ("qual a chance de o feed ser melhor?") é mais intuitiva que o p-valor. As duas abordagens devem concordar quando há muitos dados.

### 18.5 Métricas de negócio (fase 5)

| Métrica | Fórmula | Para quê |
| --- | --- | --- |
| Taxa de clique (CTR) | cliques / exibições | Relevância do feed |
| Conversão | contatos qualificados / visitantes | Valor para a imobiliária |
| Receita por exibição | CTR × preço por clique | Comparar posições e anúncios |
| Retenção em 7 dias | usuários que voltam / usuários novos | Portão da fase 4 |

Um cuidado específico: se anúncios pagos subirem no ranking só por pagarem, a relevância cai e o produto perde a razão de existir. Comparadores de preço costumam combinar relevância e lance, ordenando pela receita esperada (probabilidade de clique × lance), e a probabilidade de clique vem justamente do motor.

**Teste-se.** p = 0,03 quer dizer que há 97% de chance de o feed ser melhor? *Resposta:* Não. Quer dizer que, se não houvesse diferença, uma diferença assim apareceria em 3% dos experimentos. A chance de o feed ser melhor é uma pergunta bayesiana (18.4).

## 19. Matemática do agregador: similaridade e deduplicação

**Fase 3.** O mesmo apartamento aparece em vários portais, com títulos, fotos e preços um pouco diferentes. Decidir que dois anúncios são o mesmo imóvel (resolução de entidades) é o problema técnico central do agregador. Ele combina medidas de similaridade, truques para não comparar tudo com tudo e uma regra probabilística de decisão.

### 19.1 Similaridade de texto

- **Jaccard:** quebre cada descrição em pedaços de k palavras seguidas (*shingles*) e compare os conjuntos: J(A, B) = |A ∩ B| / |A ∪ B|. Vale 1 para textos iguais e 0 para textos sem nada em comum.
- **Distância de edição (Levenshtein):** o número mínimo de inserções, remoções e trocas de letras para transformar um texto no outro. "Rua T-55" e "R. T 55" ficam próximos. A biblioteca `rapidfuzz` calcula versões normalizadas de 0 a 100.

### 19.2 MinHash e LSH: não comparar todos com todos

Com 100 mil anúncios, comparar todos os pares dá cerca de 5 bilhões de comparações. O **MinHash** resume cada conjunto de shingles em uma assinatura curta com uma propriedade notável: a probabilidade de duas assinaturas coincidirem em uma posição é exatamente a similaridade de Jaccard. O **LSH** (*locality-sensitive hashing*) divide a assinatura em b faixas de r valores e só compara anúncios que coincidem em pelo menos uma faixa inteira:

```latex
P(\text{virar candidato}) = 1 - \left(1 - s^{r}\right)^{b}
```

| Similaridade de Jaccard s | 0,3 | 0,5 | 0,8 | 0,9 |
| --- | --- | --- | --- | --- |
| P(candidato), com b = 20 e r = 5 | 0,05 | 0,47 | 0,9996 | ≈ 1 |

A curva em S separa bem: pares muito parecidos quase sempre viram candidatos, e pares pouco parecidos quase nunca. Só os candidatos passam pela comparação completa.

### 19.3 Fotos e localização

- **Hash perceptual:** reduz uma foto a 64 bits que mudam pouco quando a foto é recortada, comprimida ou tem a cor ajustada. Duas fotos são parecidas quando a **distância de Hamming** (bits diferentes) é pequena, por exemplo ≤ 10 de 64. A biblioteca `imagehash` faz isso.
- **Distância na esfera (Haversine):** a distância entre dois pontos por latitude φ e longitude λ, com R ≈ 6.371 km:

```latex
d = 2R \arcsin\sqrt{\sin^2\!\left(\frac{\varphi_2 - \varphi_1}{2}\right) + \cos\varphi_1 \cos\varphi_2 \sin^2\!\left(\frac{\lambda_2 - \lambda_1}{2}\right)}
```

Na prática, o PostGIS calcula isso no banco. A mesma fórmula substitui a `dist_center_km` simulada quando houver endereços reais.

### 19.4 Decidir: o modelo de Fellegi-Sunter

Para cada campo (preço, área, endereço, fotos), estime m = P(campo concorda | é o mesmo imóvel) e u = P(campo concorda | são imóveis diferentes). Cada campo soma um peso ao placar do par:

```latex
\text{peso}_{\text{concorda}} = \log_2 \frac{m}{u}, \qquad \text{peso}_{\text{discorda}} = \log_2 \frac{1 - m}{1 - u}
```

Se as fotos concordam em 95% dos pares verdadeiros e em 1% dos falsos, concordar soma log₂(0,95/0,01) ≈ +6,6 e discordar soma log₂(0,05/0,99) ≈ −4,3. Acima de um limiar, o par é fundido. Abaixo de outro, é separado. No meio, vai para revisão manual. Repare que é o mesmo raciocínio de log da chance das seções 3.5 e 7: cada evidência soma um termo, como em um classificador bayesiano ingênuo.

**Teste-se.** Por que o MinHash permite estimar a similaridade de Jaccard sem comparar os conjuntos? *Resposta:* Porque a fração de posições iguais nas assinaturas é uma estimativa de Monte Carlo da probabilidade de coincidência, e essa probabilidade é exatamente o Jaccard.

## 20. Roteiro de estudo

O roteiro tem duas trilhas: uma curta, até a apresentação, com a Parte I, e uma longa, depois dela, com a Parte II, seguindo a ordem das fases do produto.

### 20.1 Até 11/11: Parte I

São cerca de 1 hora por dia de 29/10 a 10/11, acompanhando o que o agente estiver implementando. Assim cada conceito é estudado no dia em que o código correspondente aparece, e você pode ler o código real como exercício.

| Dia | Estudar | Junto com a tarefa do plano | Pronto quando você consegue |
| --- | --- | --- | --- |
| 29/10 | Seções 1 e 2 | T06 (características) | Calcular wᵀz e wᵀd à mão e explicar a padronização pela mediana |
| 30/10 | Seção 3 | T07 (catálogo) | Esboçar a sigmoide e provar que σ(−u) = 1 − σ(u) |
| 31/10 | Seção 4 | T08 a T10 (coleta) | Explicar independência condicional e a regra 68–95–99,7 |
| 01/11 | Seção 5 | T11 (modelo) | Deduzir P(A ≻ B) = σ(wᵀd) a partir de Bradley-Terry |
| 02/11 | Seção 6 | T15 (baselines) | Refazer a tabela da seção 6.2 e explicar por que o MLE diverge com 1 par |
| 03/11 | Seção 7 | T12 (MCMC) | Refazer a tabela das 3 hipóteses e explicar por que P(D) se cancela |
| 04/11 | Seção 8 | T12 (MCMC) | Calcular a distribuição estacionária do exemplo do tempo |
| 05/11 | Seção 9 | T12 e T21 (painel do modelo) | Explicar cada linha do `mcmc.py` real e ler um gráfico de traço |
| 06/11 | Seção 10 | T13, T14 e T20 (feed) | Explicar a diferença entre média das sigmoides e sigmoide da média, e o BALD |
| 07/11 | Seção 11 | T26 (resultados reais) | Ler o gráfico do experimento e dizer se H1 e H2 se confirmaram |
| 08/11 | Seção 12, perguntas 1 a 9 | Congelamento | Responder em voz alta sem ler |
| 09/11 | Seção 12, perguntas 10 a 18 | Ensaio da demo | Responder em voz alta sem ler |
| 10/11 | Simulação de banca | Checklist da véspera | Explicar o motor inteiro em 3 minutos, no quadro, sem anotações |

**Exercício final (10/11).** Em uma folha em branco, escreva de memória, nesta ordem: (1) a padronização; (2) P(A ≻ B | w) = σ(wᵀd); (3) a log-posteriori; (4) os 4 passos do Metropolis; (5) a fórmula da afinidade; (6) o BALD. Explique cada uma com uma frase. Se conseguir, você está pronto para a banca.

### 20.2 Depois de 11/11: trilha por fase

Cada bloco só precisa estar pronto quando a fase correspondente começar. O exercício de cada bloco é implementar algo pequeno no próprio ImobScore, porque é o jeito mais rápido de a teoria virar competência.

| Bloco | Quando | Estudar | Recursos principais (seção 21) | Exercício no ImobScore |
| --- | --- | --- | --- | --- |
| 1 · Fundamentos sólidos | Nov a dez/2026 | Álgebra linear (matrizes, autovalores), cálculo de várias variáveis, probabilidade | 3Blue1Brown, MIT 18.06, Mathematics for Machine Learning, Seeing Theory | Reescrever à mão o gradiente e a Hessiana da log-posteriori |
| 2 · Bayes de verdade | Dez/2026 a jan/2027 | Modelos bayesianos, priori, checagens preditivas, modelos hierárquicos (seções 15.3, 17.1, 17.6) | Statistical Rethinking, Think Bayes, Student's Guide to Bayesian Statistics | Checagem preditiva da priori das três personas |
| 3 · Experimentos (fase 2) | Antes do teste feed contra filtros | Testes de hipótese, poder, tamanho de amostra, A/B bayesiano (seção 18) | Trustworthy Online Controlled Experiments, ISL cap. 13 | Calcular o tamanho de amostra do teste da fase 2 |
| 4 · Agregador (fase 3) | Antes de importar anúncios reais | Jaccard, MinHash, LSH, distâncias, Fellegi-Sunter (seção 19) | Mining of Massive Datasets, cap. 3 | Implementar MinHash + LSH em NumPy e testar com anúncios duplicados simulados |
| 5 · Redes e ranking (fase 4) | Quando houver escolhas de muitos usuários | MLP, retropropagação, RankNet, NDCG, LambdaMART, fatoração (seções 13 a 15) | Nielsen, Karpathy, Dive into Deep Learning, Burges (2010), LightGBM | Treinar um RankNet em PyTorch e um LambdaMART no LightGBM com usuários simulados e comparar o NDCG@10 |
| 6 · Inferência avançada e exploração (fase 4) | Junto com o bloco 5 | HMC, NUTS, Laplace, variacional, Thompson (seções 16 e 17) | Betancourt (2017), Tutorial on Thompson Sampling, MCMC Interactive Gallery | Implementar HMC para o mesmo modelo do MVP e comparar ESS por segundo com o Metropolis |
| 7 · Referência contínua | Sempre | Aprofundamento de qualquer tópico | Bayesian Data Analysis, Murphy, Bishop | — |

Uma ordem alternativa, se a fase 3 vier antes da 2: os blocos 3 e 4 trocam de lugar. Os blocos 1 e 2 servem para todas as fases e não devem ser pulados.

## 21. Referências

São 46 referências, organizadas por tema e marcadas por nível (B = básico, I = intermediário, A = avançado) e pela seção do guia que cada uma aprofunda. Os links foram localizados por busca em 28/10/2026. Itens sem link são clássicos fáceis de achar pelo nome. Quase tudo é gratuito e em inglês, e os recursos em português aparecem primeiro.

### 21.1 Para começar do zero

| Recurso | Formato | Nível | Seções |
| --- | --- | --- | --- |
| Khan Academy em português: cursos de Estatística e probabilidade e de Álgebra linear | Site com vídeos e exercícios, em português | B | 2 a 4 |
| Bussab e Morettin, *Estatística Básica* | Livro didático brasileiro | B | 4, 18 |
| 3Blue1Brown: séries *Essence of linear algebra* e *Essence of calculus* | YouTube, com legendas em português em muitos vídeos | B | 2, 3, 6 |
| 3Blue1Brown: *Bayes theorem, the geometry of changing beliefs* | YouTube | B | 7 |
| [Seeing Theory](https://seeing-theory.brown.edu/) (Brown University) | Site interativo | B | 4, 7 |
| StatQuest (Josh Starmer): vídeos sobre distribuição normal, máxima verossimilhança, regressão logística e gradiente descendente | YouTube | B | 4, 5, 6 |
| [MIT 18.06, Álgebra Linear](https://www.mit.edu/~18.06/) (Gilbert Strang) | Curso com aulas gravadas | I | 2, 13, 17 |
| [Mathematics for Machine Learning](https://mml-book.com) (Deisenroth, Faisal e Ong) | Livro gratuito | I | 2, 3, 6, 13 |

### 21.2 Probabilidade, Bayes e MCMC

| Recurso | Formato | Nível | Seções |
| --- | --- | --- | --- |
| [Think Bayes 2](https://allendowney.github.io/ThinkBayes2) (Allen Downey) | Livro gratuito, com código em Python | B | 7, 8 |
| [Probabilistic Programming and Bayesian Methods for Hackers](https://freecomputerbooks.com/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers.html) (Davidson-Pilon) | Livro gratuito em notebooks Python | B | 7 a 9 |
| [Statistical Rethinking, curso 2025](https://github.com/rmcelreath/stat_rethinking_2025) (McElreath) | Aulas no YouTube + livro | I | 7 a 9, 15, 17 |
| [A Student's Guide to Bayesian Statistics](https://study.sagepub.com/lambert/student-resources/random-walk-metropolis/author-videos) (Ben Lambert) | Livro + vídeos curtos do autor | I | 7 a 9 |
| [The Markov-chain Monte Carlo Interactive Gallery](https://chi-feng.github.io/mcmc-demo) (Chi Feng) | Animações interativas de MH, HMC e NUTS | B | 9, 17 |
| [Why Metropolis–Hastings Works](https://www.gregorygundersen.com/blog/2019/11/02/metropolis-hastings/) (Gregory Gundersen) | Artigo de blog com a prova | I | 8, 9 |
| [Bayesian Data Analysis, 3ª ed.](https://sites.stat.columbia.edu/gelman/book) (Gelman et al.) | Livro (PDF gratuito no site) | A | 7 a 9, 15, 17 |
| [A Conceptual Introduction to Hamiltonian Monte Carlo](https://arxiv.org/abs/1701.02434) (Betancourt, 2017) | Artigo | A | 17 |
| [Rank-normalization, folding, and localization: an improved R-hat](https://arxiv.org/abs/1903.08008) (Vehtari et al., 2021) | Artigo | A | 9, 17 |
| [Bayesian Workflow](https://arxiv.org/abs/2011.01808) (Gelman et al., 2020) | Artigo | A | 17 |
| [Bayesian inference for logistic models using Pólya-Gamma latent variables](https://ideas.repec.org/a/taf/jnlasa/v108y2013i504p1339-1349.html) (Polson, Scott e Windle, 2013) | Artigo | A | 17 |

### 21.3 Redes neurais

| Recurso | Formato | Nível | Seções |
| --- | --- | --- | --- |
| 3Blue1Brown: série *Neural networks* (capítulos 1 a 4, incluindo retropropagação) | YouTube | B | 5, 13 |
| [Neural Networks and Deep Learning](https://neuralnetworksanddeeplearning.com/) (Michael Nielsen) | Livro online gratuito | B | 5, 6, 13 |
| [Neural Networks: Zero to Hero](https://karpathy.ai/zero-to-hero.html) (Andrej Karpathy) | Aulas no YouTube, programando do zero | I | 13 |
| *Dive into Deep Learning* (Zhang, Lipton, Li e Smola) | Livro interativo gratuito, com código | I | 13 |
| *Deep Learning* (Goodfellow, Bengio e Courville) | Livro, gratuito no site oficial | A | 13 |
| [Pattern Recognition and Machine Learning](https://www.microsoft.com/en-us/research/publication/pattern-recognition-machine-learning/) (Bishop) | Livro, PDF gratuito da Microsoft | A | 5, 6, 13, 17 |
| [Probabilistic Machine Learning](https://github.com/probml/pml-book) (Kevin Murphy), volumes 1 e [2](https://probml.github.io/pml-book/book2) | Livros gratuitos | A | Todas |
| [An Introduction to Statistical Learning, edição em Python](https://statlearning.com) (James et al.) | Livro gratuito | I | 6, 11, 14, 18 |

### 21.4 Ranking e recomendação

| Recurso | Formato | Nível | Seções |
| --- | --- | --- | --- |
| Bradley e Terry (1952), *Rank analysis of incomplete block designs* | Artigo clássico | I | 5 |
| Burges et al. (2005), *Learning to rank using gradient descent* (RankNet) | Artigo | I | 5, 13 |
| [From RankNet to LambdaRank to LambdaMART: An Overview](https://www.microsoft.com/en-us/research/?p=159784) (Burges, 2010) | Relatório técnico | I | 13, 14 |
| [RankNet: A ranking retrospective](https://microsoft.com/en-us/research/?p=4852) (Microsoft Research) | Artigo de blog | B | 13 |
| [Learning to Rank for Information Retrieval](https://doi.org/10.1561/1500000016) (Tie-Yan Liu, 2009) | Monografia | A | 14 |
| [XGBoost: A Scalable Tree Boosting System](https://arxiv.org/abs/1603.02754) (Chen e Guestrin, 2016) | Artigo | A | 14 |
| [LightGBM: A Highly Efficient Gradient Boosting Decision Tree](https://proceedings.neurips.cc/paper/2017/file/6449f44a102fde848669bdd9eb6b76fa-Paper.pdf) (Ke et al., 2017) | Artigo | A | 14 |
| [Why do tree-based models still outperform deep learning on tabular data?](https://arxiv.org/abs/2207.08815) (Grinsztajn et al., 2022) | Artigo | I | 14 |
| [Matrix Factorization Techniques for Recommender Systems](https://www.cs.columbia.edu/%7Eblei/fogm/2023F/readings/KorenBellVolinsky2009.pdf) (Koren, Bell e Volinsky, 2009) | Artigo | I | 15 |
| [Applying Deep Learning To Airbnb Search](https://arxiv.org/abs/1810.09591) (Haldar et al., 2018) | Artigo de indústria | I | 13, 14 |
| [Bayesian Active Learning for Classification and Preference Learning](https://arxiv.org/pdf/1112.5745) (Houlsby et al., 2011) | Artigo (BALD) | A | 10 |
| [A Tutorial on Thompson Sampling](https://arxiv.org/pdf/1707.02038) (Russo et al., 2018) | Tutorial | I | 16 |

### 21.5 Experimentos e dados do agregador

| Recurso | Formato | Nível | Seções |
| --- | --- | --- | --- |
| [Trustworthy Online Controlled Experiments](https://www.cambridge.org/core/books/trustworthy-online-controlled-experiments/D97B26382EB0EB2DC2019A7A7B518F59) (Kohavi, Tang e Xu) | Livro | I | 18 |
| [Mining of Massive Datasets, cap. 3: Finding Similar Items](https://www.cambridge.org/core/books/mining-of-massive-datasets/finding-similar-items/E95DF3F67E190463300FEF1EC0AFF9E4) (Leskovec, Rajaraman e Ullman) | Livro (PDF gratuito no site dos autores, em Stanford) | I | 19 |
| Fellegi e Sunter (1969), *A Theory for Record Linkage* | Artigo clássico | A | 19 |

### 21.6 Artigos originais dos métodos do MVP

| Referência | O que introduziu | Seções |
| --- | --- | --- |
| Metropolis et al. (1953), *Equation of state calculations by fast computing machines* | O algoritmo de Metropolis | 9 |
| Hastings (1970), *Monte Carlo sampling methods using Markov chains and their applications* | A generalização para propostas assimétricas | 9 |
| Gelman e Rubin (1992), *Inference from iterative simulation using multiple sequences* | O R-hat | 9 |
| Roberts, Gelman e Gilks (1997), *Weak convergence and optimal scaling of random walk Metropolis algorithms* | A taxa de 0,234 e o fator 2,38/√d | 9 |

Antes de citar no relatório, confira ano, autores e título de cada referência na página original.
