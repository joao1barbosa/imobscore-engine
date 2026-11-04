# Índice de tarefas

Tarefas das seções 8.2 e 8.3 de `docs/PLAN.md`, em ordem cronológica, conforme a visão por dia da seção 8.1.
São A01 a A09, as revisões A-REV1 e A-REV2 e E01 a E17.

**Executor (E):** o arquivo da tarefa é autocontido e é o que vale, para que não seja preciso carregar o plano inteiro a cada tarefa. O plano só é consultado se faltar algo, lendo apenas a seção necessária.

**Arquiteto (A):** os arquivos das tarefas A são um atalho para o texto da seção 8.2. O `CLAUDE.md` manda ler o plano inteiro, e em caso de divergência vale o plano.

Os arquivos reproduzem o texto do plano. O objetivo das tarefas e os itens marcados como derivados foram escritos a partir dele, que não os traz em campo próprio.

**Manutenção:** como o executor lê a cópia, toda mudança de especificação em `docs/PLAN.md` precisa ser levada, na mesma alteração, às tarefas E que reproduzem o trecho.

| ID | Título | Responsável | Dependências | Prazo |
| --- | --- | --- | --- | --- |
| E01 | [Repositório e instruções dos agentes](E01-repositorio-instrucoes.md) | E | nada | qua 04/11 |
| A01 | [Tema, textos e mockups do gate G1](A01-tema-mockups-g1.md) | A | nada | qua 04/11, até 14h |
| E02 | [Banco no Docker](E02-banco-docker.md) | E | E01 | qua 04/11 |
| E03 | [Esqueleto do back-end](E03-esqueleto-backend.md) | E | E02 | qua 04/11 |
| E04 | [Modelos do banco e migração](E04-modelos-migracao.md) | E | E03 | qua 04/11 |
| A02 | [Características, catálogo simulado e personas](A02-caracteristicas-catalogo-personas.md) | A | E03 | qua 04/11 |
| E05 | [Esqueleto do front-end](E05-esqueleto-frontend.md) | E | E01, A01 (`theme.css`) | qua 04/11 |
| A03 | [Modelo e pares aleatórios](A03-modelo-pares-aleatorios.md) | A | A02 | qua 04/11 |
| E06 | [Comando seed](E06-comando-seed.md) | E | A02, E04 | qua 04/11, noite |
| E07 | [API da coleta](E07-api-coleta.md) | E | A03, E06 | qui 05/11, manhã |
| A04 | [Mockups do gate G2](A04-mockups-g2.md) | A | A01 | qui 05/11, até 13h |
| A05 | [Metropolis-Hastings e diagnósticos](A05-metropolis-hastings-diagnosticos.md) | A | A03 | qui 05/11 |
| E08 | [Telas da coleta](E08-telas-coleta.md) | E | E05, E07, M1 e M4 aprovados | qui 05/11 |
| E09 | [Docker completo, exportação e túnel](E09-docker-exportacao-tunel.md) | E | E07, E08 | qui 05/11, até 17h |
| A06 | [Afinidade, explicação, BALD, baselines e interface completa](A06-afinidade-bald-baselines.md) | A | A05 | sex 06/11, até 13h |
| E10 | [API do feed, do modelo e do experimento](E10-api-feed-modelo-experimento.md) | E | A06 concluída em `docs/STATUS.md` | sex 06/11 |
| E11 | [Início, onboarding e modo demo](E11-inicio-onboarding-demo.md) | E | G2, E08 | sex 06/11 |
| A07 | [Avaliação, simulação e relatório](A07-avaliacao-simulacao-relatorio.md) | A | A06, E09 | sex 06/11 |
| A-REV1 | [Revisão do back-end](A-REV1-revisao-backend.md) | A | E07 a E10 | sex 06/11, fim do dia |
| E12 | [Comparações da demo e feed com Antes e Depois](E12-comparacoes-feed.md) | E | E10, E11 | sáb 07/11 |
| E13 | [Painel do modelo](E13-painel-modelo.md) | E | E10, G2 | sáb 07/11 |
| E14 | [Painel do experimento](E14-painel-experimento.md) | E | E10, G2 | sáb 07/11 |
| A-REV2 | [Revisão das telas e das personas](A-REV2-revisao-telas-personas.md) | A | E11 a E14 | sáb 07/11, noite |
| A08 | [Experimento com dados reais](A08-experimento-dados-reais.md) | A | coleta encerrada, A07 | dom 08/11, a partir das 12h |
| E15 | [Qualidade, README e `make demo`](E15-qualidade-readme-demo.md) | E | E12 a E14 e as FIX da A-REV2 | dom 08/11 |
| A09 | [Revisão final e roteiro da demo](A09-revisao-final-roteiro-demo.md) | A | E15 | seg 09/11 |
| E16 | [Correções e teste offline](E16-correcoes-teste-offline.md) | E | A09 | seg 09/11, até 18h |
| E17 | [\[C1\] Detalhe do imóvel e vistoria](E17-detalhe-vistoria.md) | E | E16 | seg 09/11, só com autorização de João às 12h e M8 aprovado |

## Regras que valem para todas

- Executor: seção 1.5 do plano e `AGENTS.md`. Arquiteto: seção 1.4 do plano e `CLAUDE.md`.
- Ao fim de cada tarefa, o dono atualiza `docs/STATUS.md` (seção 1.8).
- `make check` é a porta de qualidade única (seção 9).

## Pedido padrão para o executor

João cola no OpenCode, trocando `{ID}`:

```text
Você é o executor (papel E) do projeto ImobScore.
1. Leia AGENTS.md, docs/STATUS.md e o arquivo da tarefa em docs/tasks/{ID}-*.md. Esse arquivo é autocontido e é o que vale; só consulte docs/PLAN.md se faltar algo, lendo apenas a seção necessária.
2. Implemente somente a tarefa {ID}, editando apenas os "Arquivos permitidos".
3. Se algo não estiver especificado, não invente: escreva a pergunta em docs/STATUS.md ("Perguntas abertas") e pare.
4. Ao terminar, rode todos os comandos de "Verificação" da tarefa, cole o resumo da saída em docs/STATUS.md e faça um commit "tipo(escopo): {ID} título".
```
