# Guia do banco de dados — Avalia SENAI

## Modelo lógico

```text
Teacher 1 ─── N TeachingAssignment N ─── 1 Subject
                         │
                         ├── 1 ─── N Evaluation
                         │            (sem FK para aluno)
                         │
                         └── 1 ─── N StudentEvaluationRecord N ─── 1 User
                                      (participação + recibo cifrado)

User 1 ─── 1 StudentProfile
```

`StudentEvaluationRecord` e `Evaluation` são relacionados por um identificador UUID criptografado no registro de participação, e não por uma chave estrangeira direta. A restrição única `(student_id, assignment_id)` garante no banco uma participação por aluno/vínculo. As respostas não guardam matrícula, username ou FK de aluno.

## Tabelas

### `avaliacoes_teacher`
- `id`, `name`, `email`, `active`, `created_at`

### `avaliacoes_subject`
- `id`, `name`, `code`, `active`

### `avaliacoes_teachingassignment`
- `id`, `teacher_id`, `subject_id`, `class_name`, `period`, `active`
- Restrição única: professor + disciplina + turma + período.

### `avaliacoes_evaluation`
- `id`, `public_id` (UUID aleatório), `assignment_id`, cinco notas de 1 a 5, `comment`, `period_label`, `created_at`, `updated_at`
- Sem campo de aluno/usuário.

### `avaliacoes_studentprofile`
- `id`, `user_id`, `display_name`, `active`, `created_at`

### `avaliacoes_studentevaluationrecord`
- `id`, `student_id`, `assignment_id`, `encrypted_evaluation_id`
- Restrição única: `student_id + assignment_id`.
- Sem timestamps de participação, para reduzir metadados que poderiam ser correlacionados com o horário da resposta.

## Notas de privacidade

- A coordenação administra contas, mas a interface não expõe a tabela de participação nem respostas individuais.
- O recibo cifrado permite ao aluno recuperar e editar sua própria resposta.
- A chave é derivada de `DJANGO_SECRET_KEY`; mantenha a chave estável e protegida.
- Um administrador técnico com acesso ao banco e à chave ainda pode reconstruir a relação. Não existe garantia de anonimato absoluto quando o sistema precisa permitir edição individual.
- Comentários podem conter dados identificáveis. Evite exibi-los em relatórios, modere-os antes de divulgação e considere desativar comentários livres se o risco for alto.
- Resultados por grupo abaixo do limite `ANONYMITY_MIN_RESPONSES` são ocultados (padrão 3).

## Migração e backup

1. Faça backup do banco e teste a restauração.
2. Execute `python manage.py migrate` em homologação.
3. Para PostgreSQL, configure `DB_ENGINE=postgresql` e as variáveis `DB_*`; instale `psycopg[binary]`.
4. Não altere a chave de criptografia sem um procedimento de recriptografia dos recibos existentes.
