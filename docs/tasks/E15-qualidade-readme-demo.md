# E15 · Qualidade, README e `make demo`

- **Responsável:** E · Executor (OpenCode Go)
- **Prazo:** dom 08/11
- **Fonte:** `docs/PLAN.md`, seção 8.3. Em caso de divergência, vale o plano.

## Objetivo

Fechar a porta de qualidade, o README completo e o make demo a partir de um clone limpo.

## Arquivos permitidos

os apontados por cada `FIX-n`; `README.md` (requisitos: Docker, Node 24, pnpm, uv e cloudflared; `make up`, `make seed`, `make demo`, `make dev`, `make check`; coleta pelo túnel; solução de problemas: porta ocupada, banco vazio, imagens sem internet).

## Dependências

E12 a E14 e as FIX da A-REV2

## Especificação

Sem detalhes além do objetivo e dos campos acima.

## Verificação

`make check` passa por inteiro; um clone limpo roda `make demo` e abre o modo demo funcionando.
