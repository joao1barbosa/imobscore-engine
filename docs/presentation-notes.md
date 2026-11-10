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

## Bootstrap e tamanho de amostra (revisão de 10/11)

O mesmo pesquisador sugeriu "extrapolar" as 31 respostas com técnicas de amostragem: o sampling do OpenTelemetry, um notebook do Kaggle e um vídeo sobre `df.sample(replace=True)`. A resposta curta é que **reamostrar não cria dados**. O relatório (seções 3.10, 4.5 e 4.6) ganhou o uso correto dessas ideias.

### O que cada fonte é

| Fonte | O que é | Serve para nós? |
| --- | --- | --- |
| OpenTelemetry, sampling | Escolher quais registros de monitoramento de servidores guardar, para economizar armazenamento | Não. Não trata de pessoas nem de inferência |
| Vídeo, `df.sample(n=10000, replace=True)` | Gerar mais linhas repetindo as existentes | Não para aumentar n: seria pseudorreplicação |
| Vídeo, `stratify=y` | Manter a proporção das classes ao dividir treino e teste | Não muda o n. Estratificar por persona exigiria nova coleta |
| Notebook do Kaggle, capítulo 4 | Bootstrap: reamostrar a amostra do mesmo tamanho para medir a incerteza da média e montar um IC | Sim. É o que foi acrescentado |

O próprio notebook alerta, no capítulo 1.2, que uma amostra de conveniência não permite generalizar. É o nosso caso, e o relatório diz isso.

### Por que duplicar pessoas é errado

Se as 31 pessoas virassem 1.000 linhas copiadas, o teste acharia que há 1.000 pessoas independentes. O erro padrão cairia cerca de 5,7 vezes (√(1000/31)), e quase tudo ficaria "significativo" sem nenhuma informação nova. Esse erro se chama **pseudorreplicação**, e um revisor reconhece na hora. Pelo mesmo motivo, os 20 sorteios por pessoa entram como média, e não como 620 observações.

### O que o bootstrap mostrou

- **Como funciona:** cada réplica sorteia 31 pessoas com reposição entre as 31 e recalcula a diferença média. São 10.000 réplicas. O IC 95% vai do quantil 2,5% ao 97,5%. O n continua 31: o bootstrap mede a incerteza sem supor distribuição normal.
- **Resultado:** em 10 dos 12 testes, o IC do bootstrap e o IC do teste t concordam. Nenhuma decisão muda.
- **A exceção é T7 e T8 (log loss contra a persona).** O IC t inclui o zero (−0,01 a 0,33), mas o bootstrap não (0,04 a 0,35). A causa é P06, cujo ganho é de 2,6, enquanto ninguém perde mais que 0,21. Esse valor extremo infla o desvio padrão. Sem P06, os dois intervalos ficam acima de zero, com efeito de +0,08. Leitura: o motor dá probabilidades um pouco melhores que a persona sozinha, de forma consistente, mas o efeito é pequeno e não sobrevive à correção de Holm.

### Quantas pessoas seriam necessárias (80% de poder, supondo o efeito observado)

| Comparação | d_z | Um teste pré-registrado (α = 0,05) | Família de 12 testes (α = 0,05/12) |
| --- | --- | --- | --- |
| Acurácia contra a regressão, 3 pares (T3) | 0,49 | 35 | 61 |
| Acurácia contra a regressão, 5 pares (T4) | 0,54 | 30 | 52 |
| Acurácia contra a regressão, 10 pares (T5) | 0,44 | 42 | 75 |
| Log loss contra a persona, 3 pares (T7) | 0,34 | 71 | 125 |
| Acurácia contra a persona, 3 pares (T1) | 0,22 | 159 | 279 (mais de 400 pela simulação do Wilcoxon) |
| Log loss contra a regressão (T9 a T11) | 1,1 | 8 a 9 | 14 a 16 |

Esses números são otimistas. O efeito medido em 31 pessoas é impreciso e tende a ser superestimado quando ficou perto da significância.

### Como falar

- **A frase principal:** "Reamostragem não aumenta a amostra, só mede a incerteza. Fiz o bootstrap por pessoa, e ele confirmou as mesmas conclusões. Para confirmar a vantagem em acerto sobre a regressão, eu precisaria de cerca de 60 pessoas."
- **Se perguntarem do próximo passo:** "Pré-registrar um único teste principal. Sem a correção para 12 testes, bastariam cerca de 35 pessoas pelo efeito observado. Eu planejaria 60, com folga, porque o efeito observado tende a estar superestimado."
- **Não diga** "o bootstrap aumentou a confiança" ou "o bootstrap mostrou que é significativo". **Diga** "o bootstrap mostrou que a conclusão não depende da suposição de normalidade".

### Perguntas prováveis

- **"Por que não usou bootstrap para ter mais dados?"** Porque o bootstrap não gera dados. Ele reamostra as mesmas 31 pessoas para ver quanto a média oscilaria. Copiar pessoas para inflar o n tornaria os valores-p artificialmente pequenos.
- **"O bootstrap mudou alguma conclusão?"** Não. Ele só revelou que, na log loss contra a persona, o intervalo do teste t estava largo demais por causa de uma pessoa (P06). Mesmo assim, esse teste não passa na correção de Holm.
- **"Qual o poder do seu estudo?"** Não reporto "poder observado", porque ele é só outra forma de escrever o valor-p. Reporto quantas pessoas um próximo estudo precisaria: cerca de 60 para a acurácia contra a regressão.
- **"Por que 31 pessoas bastaram para a log loss, mas não para a acurácia?"** O efeito na log loss é grande (d_z ≈ 1,1): o motor ganha em 26 a 28 das 31 pessoas. Na acurácia, o efeito é médio (d_z ≈ 0,5), e cada pessoa só tem 10 pares de teste, então cada acerto vale 10 pontos e o ruído é grande.
