# Guia Passo a Passo: Configuração e Implementação do Supabase
## Projeto: Avalia SENAI -- Sistema de Avaliação Docente
### Escola SENAI Morvan Figueiredo -- Curso DEV4 SESI

---

### Identificação da Equipe
- **Alunos:** Eduardo Vieira Roque, Gustavo Costa Trindade, Guilherme Vilares, Aron Maestá, Diogo Ferrata
- **Professor Orientador:** Johnny Braga de Oliveira
- **Curso:** Desenvolvimento de Sistemas (2025_DEV4_SESI)

---

## 1. Visão Geral da Arquitetura de Dados

O sistema **Avalia SENAI** foi projetado com uma arquitetura de banco de dados relacional (PostgreSQL) hospedada no **Supabase**. O sistema possui suporte duplo nativo:
- **Produção / Nuvem:** PostgreSQL 15/16 hospedado no Supabase via pooling de conexões (`DATABASE_URL`).
- **Desenvolvimento Local Offline:** SQLite3 embutido (ativado automaticamente quando nenhuma `DATABASE_URL` for configurada).

O banco de dados implementa um **Protocolo de Anonimato Criptográfico Desacoplado (Zero-Link Anonymity)**, separando fisicamente o comprovante de cumprimento do aluno (`EvaluationReceipt`) da resposta com notas e opiniões (`EvaluationResponse`).

---

## 2. Passo a Passo de Criação e Configuração no Supabase

### Passo 1: Criar uma Conta e Projeto no Supabase
1. Acesse o portal oficial: [https://supabase.com](https://supabase.com).
2. Faça login com sua conta do GitHub ou crie uma conta com seu e-mail institucional.
3. No painel principal (*Dashboard*), clique no botão **New Project** (Novo Projeto).
4. Preencha os campos de configuração:
   - **Name (Nome do Projeto):** `avalia-senai-morvan`
   - **Database Password (Senha do Banco):** Defina uma senha forte e segura (anote esta senha, pois ela será usada na string de conexão).
   - **Region (Região):** Selecione `South America (São Paulo) - sa-east-1` para menor latência de rede.
   - **Pricing Plan:** Selecione o plano gratuito (*Free Tier*).
5. Clique em **Create new project** e aguarde 1 a 2 minutos para que a infraestrutura do PostgreSQL seja provisionada.

---

### Passo 2: Obter a String de Conexão (Connection String)
1. No menu lateral esquerdo do Supabase, clique no ícone de engrenagem **Project Settings** (Configurações do Projeto).
2. Selecione a aba **Database** (Banco de Dados).
3. Role até a seção **Connection parameters** / **Connection string**.
4. Selecione a aba **URI** e o modo **Transaction** (porta 6543) ou **Session** (porta 5432).
5. A string de conexão terá o seguinte formato:
   ```bash
   postgresql://postgres.[SEU-PROJECT-REF]:[SUA-SENHA]@aws-0-sa-east-1.pooler.supabase.com:6543/postgres?sslmode=require
   ```
6. Substitua `[SUA-SENHA]` pela senha que você definiu no momento da criação do projeto.

---

### Passo 3: Configurar o Arquivo `.env` no Projeto Django
1. Na raiz do projeto `Avalia Senai`, crie um arquivo chamado `.env` (ou duplique o arquivo `.env.example`).
2. Cole a URL obtida do Supabase na variável `DATABASE_URL`:

```env
# Configurações do Avalia SENAI
DEBUG=True
SECRET_KEY=senai-morvan-figueiredo-eval-secret-key-2025-production
ALLOWED_HOSTS=localhost,127.0.0.1,*

# Conexão com o Supabase PostgreSQL
DATABASE_URL=postgresql://postgres.sua_ref:sua_senha@aws-0-sa-east-1.pooler.supabase.com:6543/postgres?sslmode=require
```

> **Dica Importante:** Caso sua senha contenha caracteres especiais (como `@`, `#`, `$` ou `%`), certifique-se de codificá-los em formato URL percent-encoding (por exemplo, `@` vira `%40`).

---

### Passo 4: Executar as Migrações do Django ou Importar o Script SQL

Você tem **duas formas** práticas de provisionar a estrutura no Supabase:

#### Opção A (Recomendada via Django CLI):
Com o `.env` configurado com a `DATABASE_URL` do Supabase, abra o terminal na pasta do projeto e execute:
```powershell
.\.venv\Scripts\python manage.py migrate
```
O Django conectará diretamente ao Supabase via driver `psycopg` e criará todas as tabelas, índices e chaves estrangeiras.

#### Opção B (Direto no Painel Web do Supabase via SQL Editor):
Caso prefira criar as tabelas diretamente pela interface gráfica do Supabase:
1. No menu lateral esquerdo do Supabase, clique em **SQL Editor** (Editor SQL).
2. Clique em **+ New query**.
3. Abra o arquivo [supabase_schema.sql](file:///c:/Users/Eduardo%20Vieira%20Roque/Desktop/Avalia%20Senai/supabase_schema.sql) localizado na raiz deste projeto.
4. Copie todo o conteúdo e cole no editor do Supabase.
5. Clique no botão **Run** (ou pressione `Ctrl + Enter`).
6. Todas as 12 tabelas relacionais, restrições e políticas de RLS (*Row Level Security*) serão criadas instantaneamente.

---

### Passo 5: Popular o Banco de Dados com os Dados da Escola SENAI
Para carregar os cursos, docentes (incluindo o Prof. Johnny Braga de Oliveira), a turma `2025_DEV4_SESI`, as dimensões didáticas e as respostas iniciais de demonstração, execute:
```powershell
.\.venv\Scripts\python manage.py seed_data
```

---

## 3. Verificação no Supabase Table Editor

Após a execução, volte ao painel do Supabase e clique em **Table Editor**:
- `accounts_user`: Contém os usuários com suas respectivas roles (`ADMIN`, `COORDINATOR`, `TEACHER`, `STUDENT`).
- `evaluations_teacherprofile`: Contém os perfis dos professores e suas titulações.
- `evaluations_classgroup`: Turma `2025_DEV4_SESI`.
- `evaluations_evaluationcycle`: Ciclo de avaliação ativo.
- `evaluations_evaluationresponse`: Respostas 100% anônimas com notas por critério em formato JSONB.
- `evaluations_evaluationreceipt`: Comprovantes de votação dos alunos, totalmente desacoplados das respostas.
- `evaluations_disposableevaluationtoken`: PINs e tokens descartáveis para aplicação em laboratório.

---

## 4. Resolução de Problemas Frequentes (Troubleshooting)

1. **Erro de Timeout ou recusa de conexão:**
   - Verifique se a sua conexão de internet ou firewall bloqueia a porta `6543`. Se necessário, altere no Supabase para a porta padrão `5432` ou utilize o Pooler IPv4 disponível nas configurações de rede do projeto.
2. **Erro de SSL (`sslmode=require`):**
   - O Supabase exige conexões criptografadas SSL. Mantenha sempre `?sslmode=require` no final da string de conexão.
3. **Ambiente Offline / Sem Internet:**
   - Basta apagar ou comentar a linha `DATABASE_URL` no arquivo `.env`. O sistema comuta automaticamente para o SQLite local (`db.sqlite3`), permitindo desenvolvimento e demonstração 100% offline.
