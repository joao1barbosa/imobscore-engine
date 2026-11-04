# ImobScore — andamento

Ambos os agentes acrescentam linhas; ninguém apaga (seção 1.3 de `docs/PLAN.md`).

## Em andamento

## Concluídas (ID · data · resumo da verificação)

- E01 · 2026-11-03 · `make help` lista os 13 alvos; `docs/PLAN.md` idêntico ao arquivo fornecido (sha256); pastas da seção 3 criadas. PR aguardando a aprovação de João, ver Q1.

## Correções pendentes (FIX-n)

## Perguntas abertas

Formato: ID · pergunta · quem responde.

- Q1 · `CLAUDE.md` deve ser symlink para `AGENTS.md` ou um arquivo próprio? O pedido da E01 pede o symlink, mas também traz um conteúdo diferente para `CLAUDE.md`, e o plano (E01 e seção 3) exige esse conteúdo próprio. Com o symlink, o arquiteto leria as regras do executor, entre elas "Nunca edite: backend/app/engine/". Enquanto não houver resposta, ficam dois arquivos normais; para trocar, basta `ln -sf AGENTS.md CLAUDE.md`, mas o texto do arquiteto precisaria de outro lugar · João · **Respondida em 2026-11-03: dois arquivos separados, como no plano.**
- Q2 · O documento "ImobScore — Bases matemáticas e guia de estudo", citado nos checkpoints (1.4) e nas tarefas A08 e A09, não está no repositório. Claude precisa dele a partir do CP1. Onde ele fica? · João
- Q3 · A exportação do plano perdeu dois diagramas: os trechos `[embedded content: arquitetura ...]` (seção 3) e `[embedded content: cronograma ...]` (seção 8) só têm o marcador. O texto ao redor basta para trabalhar, mas é preciso reexportar? · João
- Q4 · A E05 manda rodar `pnpm create vite frontend`, mas `frontend/` já terá os `.gitkeep` da E01 e, por causa da dependência da A01, `theme.css` e `copy.ts`. Escolher "remover arquivos existentes" apagaria os arquivos do arquiteto. Da mesma forma, `alembic init` na E04 recusa `backend/migrations/` não vazia. Proposta: gerar os dois templates em pasta temporária, copiar para o repositório sem sobrescrever nada e apagar os `.gitkeep` que sobrarem. Isso exige autorizar a mudança, porque o executor não pode decidir · João
- Q5 · A seção 5.4 fala em "4 cadeias avançando juntas", mas a tabela logo abaixo e a seção 5.10 definem 16. O plano assume 16? · João
- Q6 · O `AGENTS.md` e o pedido padrão da seção 1.5 não citam `docs/tasks/`, então o executor não lê esses arquivos nem os avisos da Q4. Como ele deve passar a lê-los, se é que deve? · João

## Bloqueios
