# A-REV2 · Revisão das telas e das personas

- **Responsável:** A · Arquiteto (Claude)
- **Prazo:** sáb 07/11, noite
- **Fonte:** `docs/PLAN.md`, seção 8.2. Em caso de divergência, vale o plano.

## Objetivo

Revisar as telas contra os mockups, cronometrar a demo, ajustar as personas se preciso e abrir tarefas FIX-n.

## Arquivos permitidos

`backend/app/seed/personas.yaml`; `docs/STATUS.md`; `docs/CHECKPOINTS.md`. *O plano não traz campo "Arquivos" nesta tarefa; lista derivada do texto dela.*

## Dependências

E11 a E14

## Especificação

- Abrir cada tela ao lado do seu mockup, em 375 px e 1280 px, e conferir os critérios de aceite visual. Cronometrar o fluxo da demo (meta: 60 s).
- Olhar os 10 primeiros imóveis do feed de cada persona com 0 pares. Se algum resultado for absurdo (ex.: Família com quitinetes no topo), ajustar `personas.yaml` e explicar a João no CP5.
- Problemas viram `FIX-n`, como na A-REV1.

## Verificação

Conferência manual, sem comando no plano: cada tela ao lado do mockup em 375 px e 1280 px, e o fluxo da demo cronometrado (meta: 60 s).
