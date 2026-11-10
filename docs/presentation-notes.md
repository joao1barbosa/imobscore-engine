# Notas para a apresentação e o artigo

Material de revisão de João para a banca e para o artigo futuro. Cada tema aponta para a decisão registrada, quando houver. Na A09, estas notas alimentam `docs/demo-script.md`.

## Por que o motor não usa fotos

Decisão registrada em `docs/adrs/0001-escopo-atributos-sem-fotos.md`.

### Como falar disso

| Evite | Prefira | Motivo |
| --- | --- | --- |
| "É notório que as fotos são decisivas" | "A evidência sugere que as fotos pesam" | Os estudos medem atenção e mercado, e não a escolha personalizada |
| "Foto é totalmente subjetiva" | "Foto mistura informação concreta e gosto" | Acabamento, conservação e luz são concretos, e já há redes que estimam o nível de luxo a partir de fotos |
| "É muito difícil" ou "é impossível" | "É inviável neste escopo" | A literatura já recomenda com imagens, mas com muitos dados de muitos usuários |
| "Critérios objetivos" | "Atributos estruturados" | Os atributos são objetivos, mas a preferência é subjetiva, e é ela que os pesos aprendem |

### Fala (cerca de 30 segundos)

> As fotos provavelmente pesam muito na escolha de um imóvel, e o ImobScore não tenta aprender isso agora. Com 20 escolhas por pessoa, não há dados para descobrir o que, em uma foto, agrada a cada um. Por isso, os cartões não têm fotos, e o motor aprende só o peso que cada pessoa dá a preço, área, localização e outros atributos. Isso limita o resultado: ele não prevê o comportamento em um portal com fotos. Medir esse efeito é o próximo passo, com anúncios reais.

### Texto para o artigo

> O ImobScore modela a preferência individual sobre 12 atributos estruturados, com utilidade linear e o modelo de Bradley-Terry: P(A ≻ B | w) = σ(wᵀ(z_A − z_B)). Fatores que influenciam a escolha, mas não integram z, como o apelo visual das fotos, passam ao termo de erro da utilidade. Evidências de rastreamento ocular e de mercado sugerem que as fotos têm papel relevante na avaliação de anúncios (Seiler et al., 2012; Benefield et al., 2011), e há modelos que extraem sinais visuais para estimar preços e personalizar recomendações (Poursaeed et al., 2018; He e McAuley, 2016).
>
> Esses métodos, porém, dependem de grandes volumes de dados de muitos usuários. Incorporá-los aqui acrescentaria centenas de dimensões a um modelo treinado com no máximo 10 pares por pessoa, e a posteriori dos pesos visuais permaneceria próxima da priori. Por isso, o estudo se limita a atributos estruturados e apresenta cartões sem fotos, com ilustrações neutras. Os resultados valem, portanto, para escolhas feitas a partir de atributos, e não estimam o desempenho em anúncios com fotos.

### Perguntas prováveis

- **"Então seu modelo ignora o que mais importa?"** Ele ignora de propósito, e isso está declarado. Os cartões não têm fotos justamente para que elas não influenciem as escolhas sem o modelo ver.
- **"E se você tivesse mostrado fotos?"** Elas entrariam no termo de erro. Se o apelo visual acompanhasse preço ou idade, ainda distorceria esses pesos.
- **"Dá para incluir fotos depois?"** Sim, com um modelo global treinado em muitos usuários, alimentando a camada bayesiana individual. Isso se encaixa na fase 4 do plano.

### Cuidados

- **O bairro tem o mesmo problema.** O cartão mostra o nome do bairro, mas o modelo só vê a distância ao centro. A fama que um colega de Goiânia atribui a um bairro também vai para o termo de erro. Vale mencionar antes que perguntem.
- **Não diga que o plano tirou as fotos por esse motivo.** "Sem fotos externas" está no plano junto do requisito de rodar sem internet. O argumento sobre os dados é uma justificativa adicional, e válida.

### Referências a conferir antes de citar

As referências estão completas no ADR. Só o Bradley-Terry vem da lista do guia. Dos outros, a existência foi confirmada e só resumos foram lidos: Benefield et al. (2011), Seiler et al. (2012), Poursaeed et al. (2018) e He e McAuley (2016). McFadden (1974) foi citado de memória e ainda não foi conferido.

## Decisões do experimento que a banca pode cobrar

Decisões de 04/11 a 09/11, registradas em `docs/decisions.md`.

- **20 pares, e não 40:** para reduzir a desistência. Começou com 25 e caiu para 20 em 05/11, depois de as 3 primeiras pessoas acharem longo. Como 10 ficam para teste, a curva de acurácia vai só até `n_train = 10`. P01 a P03 responderam 25 e entram normalmente.
- **Só sessões completas entram na avaliação:** quem abandona antes do 20º par fica de fora (3 sessões).
- **Quem responde rápido demais fica de fora:** mediana abaixo de 1 s por par, regra fixada em 09/11, antes de rodar a avaliação. Saíram P09 e P30, e ficaram 31 participantes.
- **Código gerado pelo servidor:** quem troca de aparelho vira outro participante. Se completar duas vezes, conta como duas pessoas.
- **Catálogo inteiro só em Goiânia e compra:** a coleta e a demo usam a mesma população de imóveis, então o que a demo mostra é o que os dados sustentam. O custo é que os resultados não valem para aluguel nem para outras cidades.
- **Nenhum dado pessoal:** o projeto não guarda nome, e-mail, telefone nem IP. A coleta rodou na Vercel e no Render, que ainda veem o IP em trânsito, como qualquer servidor web.

## Resultados do experimento depois da revisão estatística

Em 09/11, um pesquisador revisou a primeira versão do relatório. O relatório técnico completo, em `docs/relatorio-experimento.pdf`, incorpora as correções. Na banca, use os números e as frases desta seção. As anteriores, como "H2 confirmada", estavam erradas.

### O que mudou

| Antes | Agora | Motivo |
| --- | --- | --- |
| "H1" e "H2" | "Hipóteses de pesquisa HP1 e HP2", cada uma com H₀ e H₁ | Na estatística, H0 e H1 são a nula e a alternativa; usar H1 e H2 para hipóteses de pesquisa confunde |
| Erro padrão, sem valor-p | Wilcoxon pareado (primário), t pareado (conferência), IC 95% pelo t, tamanho de efeito d_z e correção de Holm em 12 testes | O revisor pediu o método do intervalo e os valores-p |
| "H2 confirmada" | Confirmada só para log loss contra a regressão logística | Em acurácia, a vantagem não sobrevive à correção de Holm |
| "H1 confirmada na direção" | H1 não confirmada | Nenhum teste contra a persona fica significativo após a correção |
| "A vantagem diminui com mais pares, como previsto" | Não confirmado | Em acurácia, a queda tem p = 0,07; em log loss, a vantagem aumenta |
| "31 colegas do mesmo curso" | "31 pessoas, da turma e do meu Instagram" | A composição da amostra é desconhecida, porque nenhum dado pessoal foi coletado |

### Os números que valem

- **Log loss contra a regressão logística:** o motor é melhor com 3, 5 e 10 pares (Holm p < 0,001; d_z de 1,1 a 1,2; melhor em 26 a 28 das 31 pessoas). É o resultado mais forte.
- **Acurácia contra a regressão logística:** +4,2, +3,5 e +2,0 pontos. Sem correção, p de 0,007 a 0,02. Com Holm, p de 0,065, 0,065 e 0,117. Não é significativo.
- **Contra a persona:** cerca de +3 pontos de acurácia, sem significância. A mediana das diferenças é de +0,5 ponto: o ganho está concentrado em poucas pessoas com persona muito errada, como P06.
- **Convergência:** 1.860 de 1.860 ajustes do MCMC passaram nos critérios (R-hat < 1,05, ESS > 400, aceitação de 15% a 50%).

### Como falar

- **A frase principal:** "Com 3 a 10 escolhas, o motor bayesiano dá probabilidades muito mais confiáveis que a regressão logística. Em acerto, a vantagem é pequena e não passa na correção para vários testes."
- **Por que a calibração importa:** o produto mostra uma probabilidade ao usuário ("87% de chance de você preferir este"). Se ela estiver errada com confiança, o usuário é enganado. A regressão logística erra com confiança, e o motor não.
- **Não diga** "o motor acerta mais que os outros" sem a ressalva da significância. **Diga** "o motor ficou à frente em todos os tamanhos, mas a diferença de acerto não é estatisticamente significativa nesta amostra".

### Perguntas prováveis sobre a estatística

- **"Por que Wilcoxon e não teste t?"** Nas comparações com a persona, as diferenças não seguem distribuição normal (Shapiro-Wilk p < 0,001). O Wilcoxon não exige normalidade. O teste t está no relatório como conferência e dá conclusões parecidas.
- **"Qual é a unidade de análise?"** A pessoa. Os 20 sorteios de uma pessoa reutilizam os mesmos 20 pares e não são independentes, então tiro a média deles antes de testar. São 31 observações por teste.
- **"Por que Holm?"** São 12 testes. Sem correção, a chance de ao menos um falso positivo passa de 40%. O Holm controla esse erro e é menos conservador que o Bonferroni.
- **"A análise foi pré-registrada?"** As hipóteses, os métodos, as métricas, o protocolo de sorteios e a regra de exclusão foram fixados antes. Os testes estatísticos foram escolhidos depois de ver os resultados descritivos, a pedido de um revisor. O relatório diz isso, e a correção sobre a família inteira de testes compensa parte do risco.
- **"Não ser significativo quer dizer que não há diferença?"** Não. Com 31 pessoas e 10 pares de teste cada, diferenças de 2 a 3 pontos ficam no limite do que dá para detectar. O resultado é inconclusivo para acurácia, não uma prova de igualdade.
