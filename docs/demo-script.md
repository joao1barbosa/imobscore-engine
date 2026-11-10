# Roteiro da demo (A09)

Falas para a InovaTech (11/11). Números de `docs/results.md`, da rodada de 09/11 com 31 participantes. Leia em voz alta pelo menos uma vez antes do dia.

## Fala de 60 segundos (visitantes)

Ação na tela entre colchetes. O modo demo usa 3 pares.

> Filtro obriga você a dizer o que quer em números. O ImobScore aprende o seu gosto pelas suas escolhas.
>
> [Toca em Família.] Você escolhe um perfil parecido com o seu, só como ponto de partida.
>
> [Responde aos 3 pares.] Agora, entre dois imóveis, você só diz qual prefere. A cada escolha, o modelo recalcula quanto pesa para você o preço, a área, os quartos, a distância.
>
> [Abre o feed.] Cada imóvel ganha uma nota de 0 a 100, com uma faixa de incerteza e os motivos da nota.
>
> [Alterna Antes e Depois.] Olha a lista se reorganizar: "Antes" é o perfil genérico, e "Depois" já é você, com só 3 escolhas.
>
> Testamos com 31 pessoas: em escolhas que o modelo nunca viu, ele acertou cerca de 65% e, principalmente, deu probabilidades bem mais confiáveis que uma regressão comum.

Se sobrar tempo, abra o painel do modelo e mostre os pesos se afastando do perfil.

## Fala de 3 minutos (professores)

**1. Problema (20 s).** Os portais pedem filtros, mas a preferência por imóvel é uma troca entre atributos: quanto de área vale um quarto a mais, ou quanto de distância compensa um preço menor. O ImobScore aprende essa troca para cada pessoa, a partir de escolhas entre pares.

**2. Modelo (40 s).** Cada imóvel vira um vetor de 12 atributos estruturados padronizados: preço e área em log, quartos e quartos ao quadrado, banheiros, vagas, distância do centro, idade, casa ou apartamento, lazer, pet e portaria. A pessoa tem um peso para cada atributo. A chance de preferir A a B é a sigmoide da diferença das utilidades, σ(wᵀ(z_A − z_B)). É o modelo de Bradley-Terry, ou seja, um neurônio sigmoide sem viés, para que dois imóveis iguais deem 50%.

**3. Parte bayesiana (40 s).** Com 3 escolhas, a regressão logística não tem dados e fica confiante demais. Por isso, os pesos têm uma priori: a persona escolhida dá a média, com desvio 1, e as escolhas formam a verossimilhança. A posteriori não tem fórmula fechada, então eu a amostro com Metropolis-Hastings: 16 cadeias, 4.000 amostras, com R-hat abaixo de 1,05 e ESS acima de 400 como critério de convergência. Leva cerca de 130 ms, então roda a cada resposta.

**4. Do modelo ao produto (20 s).** A nota de 0 a 100 é a probabilidade de a pessoa preferir o imóvel a um imóvel típico, com a média tirada sobre as 4.000 amostras. O intervalo vai do percentil 5 ao 95. Na demo, o próximo par é o que mais reduz a incerteza.

**5. Experimento (50 s).** 31 pessoas, da turma e do meu Instagram, responderam 20 pares aleatórios. Excluí 2 pessoas que responderam em menos de 1 s por par, por uma regra fixada antes da análise. Para cada pessoa, separei 10 pares de teste e treinei com 3, 5 e 10, em 20 sorteios. O motor acertou 64% com 3 pares e 65,5% com 10. A regressão logística acertou 60% e 63%, e a persona sozinha, 61%. No log loss, o motor ficou em 0,64, o único abaixo de chutar 50% (0,69), e essa vantagem sobre a regressão é significativa nos três tamanhos de treino, mesmo com correção para vários testes. As diferenças de acerto, de 2 a 4 pontos, não sobrevivem à correção. Contra a persona, a diferença não é significativa, porque as personas estão longe do gosto de parte dos participantes.

**6. Limites e próximos passos (10 s).** É um estudo exploratório, com amostra de conveniência e catálogo simulado, sem fotos. O próximo passo é calibrar as personas com dados reais e testar com anúncios reais.

## Respostas curtas para as 18 perguntas da banca (seção 12 do guia)

### Sobre ser rede neural

1. **Um neurônio só é rede neural?** É a rede mínima: uma unidade sigmoide, equivalente à regressão logística. A contribuição está em treiná-la de forma bayesiana, com MCMC.
2. **Por que não uma MLP?** Com 3 a 20 pares por pessoa, uma camada oculta teria mais parâmetros que dados e decoraria as respostas. O modelo linear ainda explica a nota atributo por atributo.
3. **Qual a relação com o RankNet?** É a mesma probabilidade σ(f(A) − f(B)) e a mesma perda por pares. Aqui f é linear; no RankNet, f é uma rede.
4. **Por que não tem viés?** Para dois imóveis iguais darem exatamente 50%. Um viés seria preferência pelo lado da tela, e o lado é sorteado.

### Sobre a parte bayesiana

5. **Por que bayesiano e não só gradiente?** Com poucos pares, o MLE fica confiante demais: no experimento, a regressão logística teve log loss pior que chutar. A priori dá um ponto de partida, e a posteriori dá a incerteza que vira o intervalo da nota.
6. **A priori não enviesa o resultado?** Enviesa de propósito quando há poucos dados, e perde peso conforme as escolhas chegam. O risco de uma priori ruim apareceu no experimento, e a comparação com a regressão logística o mede.
7. **De onde vieram os valores das personas?** São hipóteses escritas à mão, com desvio 1 para deixar espaço aos dados. O experimento mostrou que estão longe de parte dos participantes, e calibrá-las com dados reais é o próximo passo.
8. **Qual a diferença entre o seu intervalo e um de confiança?** O meu é de credibilidade: 90% de probabilidade de o valor estar ali, dados o modelo e as escolhas. O de confiança fala de quantas vezes o procedimento acertaria se o experimento fosse repetido.

### Sobre o MCMC

9. **Onde está a cadeia de Markov?** Os estados são vetores de pesos, e o próximo depende só do atual. A regra de aceitação faz a distribuição estacionária ser a posteriori.
10. **Por que a razão de Hastings não aparece?** A proposta gaussiana centrada no ponto atual é simétrica, então a razão vale 1.
11. **Como sabe que convergiu?** Não há prova. Rodo 16 cadeias de pontos espalhados e exijo R-hat abaixo de 1,05, ESS acima de 400 e aceitação entre 15% e 50%.
12. **Por que Metropolis e não HMC?** Com 12 dimensões, o Metropolis basta e dá para implementar e explicar inteiro. O HMC é o próximo passo se o modelo crescer.
13. **A adaptação do passo não quebra a cadeia?** Ela só acontece no aquecimento, que é descartado. Depois, o passo fica fixo.
14. **Quanto tempo leva?** Cerca de 130 ms na mediana no notebook, porque as 16 cadeias avançam juntas no NumPy. Por isso roda depois de cada resposta, sem espera visível.

### Sobre dados, avaliação e produto

15. **Os dados são reais?** O catálogo é simulado, e a tela diz isso. As escolhas da avaliação são reais, de 31 pessoas, com consentimento e sem dado pessoal.
16. **31 pessoas bastam?** Para generalizar, não: é uma amostra de conveniência, da turma e do meu Instagram, e o estudo é exploratório. Por isso comparo os métodos pessoa a pessoa, com testes pareados e correção para vários testes.
17. **E se a pessoa for inconsistente?** Escolhas contraditórias só aproximam as previsões de 50% e alargam o intervalo. O modelo é probabilístico e não quebra.
18. **Como um modelo linear captura "3 quartos é o ideal"?** Pelo atributo (quartos − 3)². Com peso negativo nele, a utilidade dos quartos vira uma parábola com topo, e o modelo continua linear nos pesos.

## Perguntas sobre o resultado

- **Por que o motor ganhou pouco da persona?** Porque as personas estão longe do gosto de parte dos participantes: sozinhas, elas têm log loss pior que chutar. O caso de P06 mostra o motor corrigindo isso: a persona acertava 10% dos pares, e o motor chegou a 64% com 5 pares.
- **E se a regressão logística tivesse ganhado?** Seria sinal de que a priori atrapalha, o que é uma descoberta sobre as personas, e não um defeito do método. A regressão logística é o controle que isola esse efeito.
- **Por que os pares da coleta eram aleatórios?** Para nenhum método escolher o próprio teste. Na demo, o motor escolhe os pares porque ali o objetivo é aprender rápido.
- **Por que excluiu 2 pessoas?** Elas responderam em menos de 1 s por par, sem tempo de ler os dois cartões, e uma alternou A e B nos 20 pares. A regra foi fixada antes de rodar a avaliação.
- **E as fotos?** Ficaram de fora de propósito: com 20 escolhas por pessoa, não há dados para aprender o que agrada numa foto. A fala de 30 segundos está em `docs/presentation-notes.md`.
