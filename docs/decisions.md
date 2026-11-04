# Decisões não previstas no plano

Uma decisão por linha, no formato: data · tarefa · decisão · motivo. Ninguém apaga linhas (seção 1.3 de `docs/PLAN.md`). Decisões maiores, que precisem de contexto e alternativas, vão para `docs/adrs/`.

- 2026-11-03 · E01 · `README.md` traz o resumo do escopo do MVP, além do título e de "em construção" · pedido de João, mais amplo que o texto da E01.
- 2026-11-03 · E01 · Criados `docs/adrs/` e `docs/tasks/`, que não constam da árvore da seção 3 · pedido de João.
- 2026-11-03 · E01 · `docs/tasks/` também cobre A-REV1 e A-REV2, além de A01 a A09 e E01 a E17 · o pedido quer um arquivo por tarefa listada nas seções 8.2 e 8.3, e as duas revisões estão lá.
- 2026-11-03 · E01 · O título `## Perguntas abertas` de `docs/STATUS.md` fica sem o sufixo do plano, e o formato "ID · pergunta · quem responde" vai na linha abaixo · pedido de João, sem perder o formato do plano.
- 2026-11-03 · E01 · `APPROVAL.md` tem 9 linhas, porque M3b é uma tela própria na tabela da seção 1.6 · sem a linha própria, M3b não teria onde receber o "aprovado" que libera a E11.
- 2026-11-03 · E01 · `.editorconfig` usa tabulação no `Makefile` · a regra "2 espaços nos demais" quebraria as receitas do make.
- 2026-11-03 · E01 · `.env.example` inclui `TEST_DATABASE_URL`, e `DATABASE_URL` aponta para `localhost` · valores da seção 10; o Compose sobrescreve `DATABASE_URL` no serviço `api`.
- 2026-11-03 · E01 · `frontend/src/features/collection`, `home` e `demo` não foram criadas · não constam da árvore da seção 3; as tarefas E08 e E11 as criam (a seção 8 prevalece).
- 2026-11-03 · E01 · `docker-compose.yml`, `docs/results.md`, `docs/demo-script.md` e os arquivos de código da seção 3 não foram criados · a E01 cria só as pastas; esses arquivos pertencem a E02, A08, A09 e às demais tarefas.
- 2026-11-03 · E01 · O remoto estava vazio, então `main` recebeu um commit raiz vazio antes da branch da E01 · um PR precisa de uma branch de destino com histórico comum.
- 2026-11-03 · E01 · `CLAUDE.md` e `AGENTS.md` ficam como dois arquivos separados, sem symlink · decisão de João (Q1), seguindo o plano.
- 2026-11-03 · E01 · O guia de estudo foi copiado para `docs/GUIDE.md` e entra na lista "Nunca edite" do executor, junto com `docs/tasks/` · decisão de João (Q2); o arquivo de tarefa virou a fonte do executor, que não deve alterá-lo.
- 2026-11-03 · E01 · `docs/PLAN.md` difere do arquivo fornecido em uma palavra: "4 cadeias" virou "16 cadeias" na seção 5.4 · decisão de João (Q5).
- 2026-11-03 · E01 · `AGENTS.md` deixa de ser o texto exato da E01: o arquivo da tarefa é lido primeiro e é o que vale · decisão de João (Q6), para não carregar o plano inteiro a cada tarefa.
- 2026-11-03 · E01 · As tarefas E reproduzem os trechos do plano de que precisam; as tarefas A não, porque o `CLAUDE.md` manda ler o plano inteiro · o pedido de João (Q6) trata do executor.
- 2026-11-03 · E01 · Além da palavra da Q5, `docs/PLAN.md` mudou na seção 1.5 e nos blocos de `AGENTS.md` e `CLAUDE.md` da E01; o `CLAUDE.md` ganhou a regra de levar às tarefas E as mudanças de especificação · decisão de João (Q7).
- 2026-11-03 · E01 · `AGENTS.md` e `CLAUDE.md` proíbem citar agentes em commits e PRs, e os commits do PR #1 foram reescritos sem essas menções · pedido de João.
- 2026-11-03 · E01 · Os blocos da E01 em `docs/PLAN.md` receberam a regra de não citar agentes em commits e PRs · pedido de João.
