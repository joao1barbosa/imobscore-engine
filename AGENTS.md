# ImobScore — instruções para o executor (papel E)
Antes de qualquer tarefa, leia docs/PLAN.md (seções 1.3, 1.5, 1.7 e a tarefa pedida) e docs/STATUS.md.
- Faça somente a tarefa E indicada no pedido. Uma por vez.
- Edite apenas os arquivos listados no campo "Arquivos" da tarefa.
- Nunca edite: backend/app/engine/, backend/app/seed/, backend/app/analysis/, backend/tests/engine/, docs/mockups/, frontend/src/styles/theme.css, frontend/src/lib/copy.ts, docs/PLAN.md.
- Importe o motor apenas com "from app.engine import ..." (seção 5.10 do plano).
- Textos de tela vêm de frontend/src/lib/copy.ts. Layout e cores vêm do mockup aprovado e de theme.css. Não escreva textos visíveis direto nos componentes.
- Se algo não estiver especificado, não decida: escreva a pergunta em docs/STATUS.md, em "Perguntas abertas", e pare.
- Não adicione dependências nem mude versões. Não apague, pule nem afrouxe testes.
- Termine só com todos os comandos de "Verificação" passando. Registre em docs/STATUS.md e faça um commit "tipo(escopo): ID título".
- Se uma verificação falhar duas vezes seguidas, pare e marque a tarefa como "precisa de revisão do arquiteto".
