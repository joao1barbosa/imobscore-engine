# Resultados do experimento (A08)

Rodada `a6310bac-f944-4a05-8979-d6c84bc75116`, de 09/11/2026, com as escolhas reais da coleta (`data/collected/pairs.json`). Os arquivos estão em `data/results/`.

## Participantes

A coleta durou de 05/11 a 07/11 e foi encerrada em 09/11. Foram 36 sessões: 33 completas e 3 incompletas, que ficaram de fora. Também saíram 2 pessoas pela regra de exclusão fixada antes da avaliação (`docs/decisions.md`, 09/11): P09 e P30, com mediana abaixo de 1 s por par. P30 alternou A e B nos 20 pares.

**Ficam 31 participantes.** 28 responderam 20 pares e 3 responderam 25. Personas escolhidas: Família (17), Estudante (10) e Investidor (4).

Para cada pessoa e cada tamanho de treino, foram feitos 20 sorteios: 10 pares para teste e 3, 5 ou 10 pares para treino, tirados dos que sobraram.

## Acurácia e perda logarítmica (média de 31 pessoas × 20 sorteios)

| Método | Acurácia com 3 | com 5 | com 10 | Log loss com 3 | com 5 | com 10 |
| --- | --- | --- | --- | --- | --- | --- |
| Motor bayesiano | **64,0%** | **64,3%** | **65,5%** | **0,644** | **0,645** | **0,642** |
| Regressão logística | 59,9% | 60,8% | 63,4% | 0,805 | 0,840 | 0,851 |
| Média da persona | 61,4% | 61,4% | 61,4% | 0,803 | 0,803 | 0,803 |
| Pesos iguais | 54,2% | 54,2% | 54,2% | 1,629 | 1,629 | 1,629 |

Referência: chutar 50% em todo par dá acurácia de 50% e log loss de 0,693.

O desvio entre pessoas e sorteios é grande, de 19 a 20 pontos de acurácia, porque cada acerto em 10 pares de teste vale 10 pontos. Por isso, a tabela abaixo compara os métodos **na mesma pessoa**: diferença do motor para o outro método, média das 31 pessoas, ± erro padrão.

| Motor bayesiano contra | Treino | Acurácia (pontos) | Melhor / pior em | Log loss | Melhor / pior em |
| --- | --- | --- | --- | --- | --- |
| Média da persona | 3 | +2,6 ± 2,1 | 17 / 13 | −0,16 ± 0,09 | 21 / 10 |
| Média da persona | 5 | +2,9 ± 2,5 | 17 / 13 | −0,16 ± 0,09 | 20 / 11 |
| Regressão logística | 3 | +4,2 ± 1,5 | 23 / 8 | −0,16 ± 0,03 | 27 / 4 |
| Regressão logística | 5 | +3,5 ± 1,2 | 21 / 8 | −0,20 ± 0,03 | 26 / 5 |
| Regressão logística | 10 | +2,0 ± 0,8 | 21 / 9 | −0,21 ± 0,03 | 28 / 3 |

## Hipóteses

Testes pareados por pessoa: Wilcoxon de postos sinalizados, bilateral, com correção de Holm nos 12 testes e α = 0,05. O método completo está em `docs/relatorio-experimento.pdf`.

- **H1, o motor supera a média da persona já com 3 a 5 pares: não confirmada.** O motor ganha na média, com cerca de 3 pontos de acurácia e log loss 0,16 menor, mas nenhuma diferença é significativa após a correção. Na acurácia, ele ganha em 17 pessoas e perde em 13. O caso mais claro de ganho é P06: a persona escolhida acerta 10% dos pares dela, e o motor sobe para 64% com 5 pares.
- **H2, o motor supera a regressão logística com poucos pares, e a vantagem diminui: confirmada só na primeira parte e só na log loss.**
  - **Log loss:** a vantagem é grande e significativa com 3, 5 e 10 pares (Holm p < 0,001; d<sub>z</sub> ≈ 1,1). A regressão logística fica pior que chutar 50% (0,80 a 0,85), porque erra com muita confiança, como prevê a seção 11.4 do guia. O motor fica abaixo de 0,693 em todos os tamanhos de treino.
  - **Acurácia:** a vantagem de 2 a 4 pontos tem p não corrigido entre 0,007 e 0,02, mas não sobrevive à correção (Holm p de 0,07 a 0,12).
  - **A vantagem diminuir:** não se confirmou. Em acurácia, ela cai 2,2 pontos de 3 para 10 pares (p = 0,07). Em log loss, ela aumenta.

## Limitações

- **Amostra:** 31 pessoas recrutadas por conveniência no grupo da turma e no Instagram do autor. A composição é desconhecida, porque nenhum dado pessoal foi coletado. O estudo é exploratório e não vale para a população.
- **Catálogo:** é simulado. Só as escolhas são reais.
- **Teste:** 10 pares por pessoa, então cada resultado individual oscila muito. A faixa de ±1 desvio na figura mistura pessoas e sorteios, e a comparação justa é a da tabela pareada.
- **Estatística:** as razões entre a diferença e o erro padrão (cerca de 1,2 para H1 e de 2,5 a 3,0 para H2, na acurácia) são indicações. Não houve teste formal com correção para várias comparações.
- **Personas:** com log loss 0,80, pior que chutar 50%, e 6 pessoas abaixo de 50% de acurácia, as personas escritas à mão estão longe do gosto de parte dos participantes. Isso explica por que H1 não se confirmou: o motor parte de uma priori ruim e, com 10 pares, ainda não a corrige por completo. Ele sobe só de 64,0% para 65,5%.
- **Exclusões:** 2 pessoas saíram pela regra de tempo, fixada antes de rodar a avaliação. P01 a P03 responderam 25 pares, antes da mudança para 20.
