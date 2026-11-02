# Plano e escopo implementado — versão de entrega

## Objetivo

Entregar um fluxo operacional coerente de avaliação pedagógica, com contas de alunos administradas pela coordenação, uma avaliação por vínculo, edição pelo histórico e redução da exposição de identidade.

## Escopo implementado

1. **Autenticação por perfil**: coordenação (`is_staff`/`is_superuser`) e aluno (`StudentProfile` ativo).
2. **Gestão de contas**: criação de usuário e senha inicial, ativação/desativação, edição do nome e redefinição de senha pela coordenação.
3. **Participação por vínculo**: restrição única de banco por aluno e vínculo de ensino. Vínculos distintos podem receber avaliações distintas do mesmo aluno.
4. **Histórico e edição**: o aluno vê seus próprios registros e pode editar a resposta já criada. Uma edição atualiza o mesmo registro.
5. **Separação dos dados**: `Evaluation` não tem FK para o aluno. `StudentEvaluationRecord` armazena aluno, vínculo e recibo de avaliação criptografado, sem FK direta para a resposta.
6. **Painel da coordenação**: protegido por perfil; a interface mostra métricas agregadas, não o histórico individual de respostas. Relatórios permitem exportação CSV agregada e impressão em PDF pelo navegador.
7. **Supressão de amostras pequenas**: médias por vínculo/professor são omitidas abaixo do limite `ANONYMITY_MIN_RESPONSES` (padrão 3).
8. **Integridade**: unicidade por aluno/vínculo, validação das notas de 1 a 5, transação ao criar avaliação e recibo.
9. **Operação**: migrações, configuração por ambiente, documentação, exemplo de ambiente e testes automatizados básicos.

## Decisão sobre anonimato

A necessidade de permitir histórico e edição significa que o sistema precisa recuperar a resposta correta de cada aluno. Para reduzir o vínculo direto, o identificador público da avaliação é aleatório e fica criptografado no registro de participação separado. A interface de coordenação não expõe esse registro e não apresenta respostas individuais.

Isso é **separação de acesso e pseudonimização com recibo criptografado**, não anonimato matematicamente absoluto: o operador técnico que controla a aplicação, a chave e o banco pode reconstruir a relação; logs externos ou horários também podem permitir correlação. Por isso, o projeto não promete anonimato absoluto. Para um requisito institucional rigoroso, a arquitetura deve ser avaliada por responsável de segurança/privacidade e os logs de infraestrutura precisam ser revistos.

## Regras de negócio

- Cada conta ativa pode enviar uma avaliação para cada vínculo ativo.
- O mesmo aluno pode avaliar vários vínculos.
- Se já existe avaliação para o vínculo, o formulário abre em modo de edição.
- Editar atualiza a mesma resposta; não aumenta o número de respostas.
- Vínculos inativos não aceitam novas avaliações, mas respostas antigas continuam editáveis pelo histórico.
- Contas desativadas não podem entrar.
- As avaliações antigas anteriores à autenticação continuam anônimas, mas não podem ser associadas a um aluno retroativamente.

## Critérios de aceite

- Coordenação consegue criar aluno e redefinir sua senha.
- Aluno entra e só acessa sua área/histórico.
- Aluno avalia dois vínculos diferentes e tem duas avaliações distintas.
- Enviar novamente no mesmo vínculo atualiza a avaliação existente.
- Restrição única no banco impede duplicidade concorrente por aluno/vínculo.
- Coordenação não tem página de respostas individuais nem acesso ao modelo de recibos no admin.
- Relatórios omitem grupos abaixo do mínimo configurado.
- `python manage.py test` e `python manage.py check` passam no ambiente com dependências instaladas.

## Etapas recomendadas antes do uso institucional

1. Instalar em ambiente de homologação e testar os fluxos completos.
2. Revisar migração de dados de instalações anteriores e validar backup/restauração.
3. Trocar segredo de desenvolvimento por segredo forte e estável via gerenciador seguro.
4. Configurar HTTPS, PostgreSQL, logs mínimos, controle de acesso à infraestrutura e backups.
5. Aprovar política de privacidade, retenção, moderação de comentários e limiar mínimo com a instituição.
6. Fazer avaliação de segurança/LGPD e homologação pelos responsáveis.
