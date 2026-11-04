# ImobScore — instruções para o executor (papel E)
Antes de qualquer tarefa, leia o arquivo da tarefa pedida (docs/tasks/<ID>-*.md) e docs/STATUS.md.
- O arquivo da tarefa é autocontido e é o que vale. Consulte docs/PLAN.md só se faltar algo nele, lendo apenas a seção necessária, nunca o arquivo inteiro.
- Faça somente a tarefa E indicada no pedido. Uma por vez.
- Edite apenas os arquivos listados em "Arquivos permitidos" no arquivo da tarefa.
- Nunca edite: backend/app/engine/, backend/app/seed/, backend/app/analysis/, backend/tests/engine/, docs/mockups/, frontend/src/styles/theme.css, frontend/src/lib/copy.ts, docs/PLAN.md, docs/GUIDE.md, docs/tasks/.
- Importe o motor apenas com "from app.engine import ..." (nomes da seção 5.10 do plano, reproduzida nas tarefas que a usam).
- Textos de tela vêm de frontend/src/lib/copy.ts. Layout e cores vêm do mockup aprovado e de theme.css. Não escreva textos visíveis direto nos componentes.
- Se algo não estiver especificado, não decida: escreva a pergunta em docs/STATUS.md, em "Perguntas abertas", e pare.
- Não adicione dependências nem mude versões. Não apague, pule nem afrouxe testes.
- Termine só com todos os comandos de "Verificação" passando. Registre em docs/STATUS.md e faça um commit "tipo(escopo): ID título".
- Commits e PRs não citam agentes nem ferramentas de IA: sem "Co-Authored-By", sem "Generated with" e sem menção equivalente.
- Se uma verificação falhar duas vezes seguidas, pare e marque a tarefa como "precisa de revisão do arquiteto".
