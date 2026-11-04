# ImobScore — instruções para o Claude (papel A, arquiteto)
Antes de qualquer tarefa, leia docs/PLAN.md e docs/STATUS.md.
- Faça só as tarefas A e A-REV da seção 8.2, na ordem.
- Siga o protocolo de checkpoints da seção 1.4: ao terminar cada módulo do motor, explique a João, faça as 3 perguntas, espere cada resposta, tire todas as dúvidas e registre em docs/CHECKPOINTS.md. Só João declara "Entendido: sim". Sem isso, não faça commit do módulo seguinte.
- Siga a seção 1.6 para mockups. Nenhuma tela vai para o executor sem "aprovado" em docs/mockups/APPROVAL.md.
- Mantenha a interface da seção 5.10. Se precisar mudá-la, avise João e atualize docs/PLAN.md na mesma alteração.
- Ao mudar uma especificação em docs/PLAN.md, leve a mudança, na mesma alteração, às tarefas E de docs/tasks/ que reproduzem o trecho.
- Decisões não previstas: escolha a opção mais simples compatível com o plano e registre em docs/decisions.md.
- Commits e PRs não citam agentes nem ferramentas de IA: sem "Co-Authored-By", sem "Generated with" e sem menção equivalente.
- Atualize docs/STATUS.md ao fim de cada tarefa.
