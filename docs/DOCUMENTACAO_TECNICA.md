# Documentação técnica — Avalia SENAI

## Stack

- Python e Django 5.x
- SQLite para desenvolvimento; PostgreSQL opcional para produção
- Templates Django, HTML e CSS responsivo
- `cryptography` (Fernet) para criptografar o recibo de resposta usado pelo histórico do aluno

## Aplicações e rotas

- `/`: página inicial
- `/entrar/` e `/sair/`: autenticação e saída
- `/aluno/`: vínculos ativos e estado da participação
- `/aluno/avaliar/<id>/`: criar/editar avaliação do vínculo
- `/aluno/historico/`: histórico do próprio aluno
- `/painel/`: indicadores agregados da coordenação
- `/professores/`, `/disciplinas/`, `/vinculos/`: cadastros da coordenação
- `/coordenacao/alunos/`: contas de alunos
- `/relatorios/`: resultados agregados
- `/admin/`: administração Django para usuários autorizados

## Modelos

- `Teacher`: professor.
- `Subject`: disciplina.
- `TeachingAssignment`: professor + disciplina + turma + período; combinação única.
- `Evaluation`: resposta pedagógica, com UUID opaco, notas, comentário opcional e timestamps. Não possui campo nem FK para aluno/usuário.
- `StudentProfile`: perfil de aluno ligado ao usuário de autenticação Django.
- `StudentEvaluationRecord`: controle de participação por aluno e vínculo; restrição única `(student, assignment)` e recibo criptografado da avaliação. Não há FK direta para `Evaluation`.

## Fluxo de avaliação

1. Aluno autenticado abre a área de avaliações.
2. Para um vínculo ativo sem participação, envia o formulário.
3. A aplicação grava `Evaluation` e, na mesma transação, grava `StudentEvaluationRecord` com o UUID da resposta criptografado.
4. Uma restrição única impede criar outro controle de participação para o mesmo aluno/vínculo.
5. Ao voltar ao vínculo, a aplicação decifra o recibo, localiza a resposta e abre o mesmo registro em edição.
6. A edição atualiza a avaliação existente, mantendo uma resposta por vínculo.

## Autorização

- Coordenação: usuários Django com `is_staff` ou `is_superuser`.
- Aluno: usuário autenticado com `StudentProfile.active=True` e `User.is_active=True`.
- Views de cadastros, painel e relatórios exigem perfil de coordenação.
- Views de avaliação e histórico exigem perfil de aluno.
- `Evaluation` e `StudentEvaluationRecord` não são registrados no Django Admin para reduzir exposição de respostas individuais e recibos.

## Criptografia dos recibos

`avaliacoes/privacy.py` deriva uma chave Fernet a partir de SHA-256 de `DJANGO_SECRET_KEY`. Essa chave precisa ser estável. Uma rotação sem recriptografia torna os recibos existentes impossíveis de decifrar. Em produção, use segredo aleatório protegido e mantenha cópia de recuperação em cofre de segredos.

A criptografia não elimina a capacidade técnica do operador que controla o segredo e o banco de recuperar o mapeamento. O sistema reduz o acesso por telas de coordenação, mas não deve ser descrito como anonimato absoluto. Horários de acesso e conteúdo de comentário também podem identificar alguém.

## Migrações

- `0001_initial.py`: estrutura original de professores, disciplinas, vínculos e avaliações.
- `0002_student_accounts_anonymous_receipts.py`: UUID da avaliação, timestamp de edição, perfis e controles de participação.

Execute `python manage.py migrate`. Se houver instalação antiga com migrações diferentes ou tabelas criadas manualmente, faça backup e valide o caminho de atualização em cópia antes de aplicar.

## Verificação

```bash
python manage.py check
python manage.py test
```

## Produção

Defina `DJANGO_DEBUG=0`, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, HTTPS, banco de produção e política de backups. Use PostgreSQL em escala institucional e revise permissões, logs, monitoramento, retenção de dados e requisitos LGPD. A homologação deve incluir teste de restauração e validação de privacidade.
