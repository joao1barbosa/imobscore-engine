# A01 · Tema, textos e mockups do gate G1

- **Responsável:** A · Arquiteto (Claude)
- **Prazo:** qua 04/11, até 14h
- **Fonte:** `docs/PLAN.md`, seção 8.2. Em caso de divergência, vale o plano.

## Objetivo

definir a identidade visual e as telas de coleta e de comparação antes de o executor implementá-las.

## Arquivos permitidos

`frontend/src/styles/theme.css`; `frontend/src/lib/copy.ts`; `docs/mockups/m1-coleta.html` e `.md`; `docs/mockups/m4-comparar.html` e `.md`; `docs/mockups/APPROVAL.md`.

## Dependências

nada

## Especificação

- **Passos:**
  1. Primeiro, `theme.css`, para destravar E05: variáveis CSS no formato do shadcn (`--background`, `--foreground`, `--card`, `--card-foreground`, `--primary`, `--primary-foreground`, `--secondary`, `--muted`, `--muted-foreground`, `--accent`, `--border`, `--input`, `--ring`, `--destructive`, `--radius`) para o tema claro (`:root`) e o escuro (`.dark`), mais `--score-low`, `--score-mid`, `--score-high` e `--font-sans: "Geist Variable", sans-serif`. Contraste AA em todos os pares texto e fundo.
  2. `copy.ts`: `export const copy = { common: {...}, collection: {...}, compare: {...} } as const;` com todos os textos das telas M1 e M4, inclusive mensagens de erro e de validação. Textos com variáveis viram funções, por exemplo `progress: (i: number, n: number) => \`Par ${i} de ${n}\`\`.
  3. Mockups no formato da seção 1.6. O cartão de imóvel mostra ilustração, título, bairro, preço, área, quartos, banheiros, vagas, idade e os selos "aceita pet" e "portaria 24 h". M1 inclui o formulário (código, consentimento, cidade, finalidade, faixa de preço, persona), o uso de M4 para os 40 pares e a tela de agradecimento.
  4. Apresentar a João (1.6) e registrar a decisão em `APPROVAL.md`.

## Verificação

O plano não define comando para esta tarefa. Vale o critério de "Pronto quando" abaixo, conferido em `docs/mockups/APPROVAL.md`.

**Pronto quando:** M1 e M4 aparecem como "aprovado" em `APPROVAL.md`.
