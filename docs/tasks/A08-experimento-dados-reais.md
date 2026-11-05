# A08 · Experimento com dados reais

- **Responsável:** A · Arquiteto (Claude)
- **Prazo:** dom 08/11, a partir das 12h
- **Fonte:** `docs/PLAN.md`, seção 8.2. Em caso de divergência, vale o plano.

## Objetivo

Rodar o experimento com os dados reais da coleta e escrever docs/results.md.

## Arquivos permitidos

`docs/results.md`; `data/collected/`; `data/results/`; `docs/CHECKPOINTS.md`. *O plano não traz campo "Arquivos" nesta tarefa; lista derivada do texto dela.*

## Dependências

coleta encerrada, A07

## Especificação

- Rodar `make evaluate`. Se houver menos de 5 participantes com pelo menos 20 pares, rodar também `simulate` e `evaluate` e deixar o painel com os dados reais, mais um aviso de quantos são.
- Escrever `docs/results.md` (até 1 página): número de participantes, tabela de acurácia e perda logarítmica por método em n\_train = 3, 5 e 15, se H1 e H2 se confirmaram e as limitações (seção 11 do guia).
- **Checkpoint:** CP6.

## Verificação

`make evaluate`. Se houver menos de 5 participantes com pelo menos 20 pares, rodar também `make simulate` e o `evaluate` sobre os dados simulados.

## Atenção

O guia citado nesta tarefa está em `docs/GUIDE.md`.
