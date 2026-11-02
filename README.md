<<<<<<< HEAD
# Avalia SENAI -- Sistema de Avaliação de Professores

**Escola SENAI Morvan Figueiredo**  
**Curso:** Desenvolvimento de Sistemas -- `2025_DEV4_SESI`  
**Professor Orientador:** Johnny Braga de Oliveira  
**Tema:** TEMA-7 -- Sistema de Avaliação de Professores  

---

### Identificação dos Alunos:
- **Eduardo Vieira Roque**
- **Gustavo Costa Trindade**
- **Guilherme Vilares**
- **Aron Maestá**
- **Diogo Ferrata**

---

## 🌟 Visão Geral

O **Avalia SENAI** é um sistema web completo desenvolvido em Python e Django, com design inspirado nas diretrizes do `DESIGN.md` (tipografia Manrope, cores off-black, cards minimalistas e ausência de emojis clichês), concebido para assegurar o **anonimato criptográfico absoluto** dos estudantes ao avaliarem seus professores.

### Principais Funcionalidades:
1. **Protocolo Zero-Link de Anonimato:** Separação física e relacional entre o comprovante do aluno (`EvaluationReceipt`) e a resposta anônima (`EvaluationResponse`).
2. **Modo PIN Descartável:** Votação direta em computadores de laboratório sem necessidade de login.
3. **Dashboards Dinâmicos com Chart.js:** Radar de competências pedagógicas e histogramas de notas por dimensão.
4. **Fila de Moderação Pedagógica:** Controle ético dos comentários de texto livre pela coordenação.
5. **Relatórios Oficiais e Exportação:** Impressão de parecer oficial em formato A4 e download de planilhas Excel `.xlsx`.
6. **Suporte a Supabase (PostgreSQL 15/16) e SQLite Local:** Troca automática via variável `DATABASE_URL` no `.env`.

---

## 🚀 Como Executar o Projeto

### 1. Pré-requisitos
- Python 3.10+ (desenvolvido e testado em Python 3.14)
- Git (opcional)

### 2. Instalação e Execução
```powershell
# Ativar o ambiente virtual existente
.\.venv\Scripts\Activate.ps1

# Ou criar novo ambiente virtual e instalar dependências
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt

# Executar as migrações do banco de dados
.\.venv\Scripts\python manage.py migrate

# Carregar os dados institucionais do SENAI Morvan Figueiredo
.\.venv\Scripts\python manage.py seed_data

# Executar os testes automatizados
.\.venv\Scripts\python manage.py test apps.evaluations.tests apps.dashboards.tests

# Iniciar o servidor de desenvolvimento
.\.venv\Scripts\python manage.py runserver
```

Acesse no navegador: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🔑 Perfis de Acesso Pré-configurados (Atalho de 1 Clique no Topo)

| Perfil | Usuário | Senha | Função no Sistema |
|---|---|---|---|
| **Administrador** | `admin` | `senai123` | Acesso completo e gestão de usuários |
| **Coordenação** | `coordenacao` | `senai123` | Painel geral da escola, moderação e relatórios |
| **Docente** | `johnny` | `senai123` | Dashboard pessoal do Prof. Johnny Braga de Oliveira |
| **Estudante** | `eduardo` | `senai123` | Aluno Eduardo Vieira Roque (Turma 2025_DEV4_SESI) |
| **PIN Anônimo** | `SENAI-2025-DEV4-LAB1` | *(sem senha)* | Votação direta em bancada de laboratório |

---

## 📚 Documentação Anexa

- [DOCUMENTACAO_TECNICA.md](file:///c:/Users/Eduardo%20Vieira%20Roque/Desktop/Avalia%20Senai/DOCUMENTACAO_TECNICA.md): Requisitos funcionais, não-funcionais, DER em Mermaid, casos de uso detalhados e guia do usuário.
- [supabase_setup_guide.md](file:///c:/Users/Eduardo%20Vieira%20Roque/Desktop/Avalia%20Senai/supabase_setup_guide.md): Passo a passo para criação do projeto no Supabase e conexão com o Django.
- [supabase_schema.sql](file:///c:/Users/Eduardo%20Vieira%20Roque/Desktop/Avalia%20Senai/supabase_schema.sql): Script DDL completo em SQL nativo do PostgreSQL com políticas de Row Level Security (RLS).
- [design.md](file:///c:/Users/Eduardo%20Vieira%20Roque/Desktop/Avalia%20Senai/design.md): Guia de estilo visual (Tipografia Manrope e padrões de interface).
- [TEMA-7.md](file:///c:/Users/Eduardo%20Vieira%20Roque/Desktop/Avalia%20Senai/TEMA-7.md): Guia original do projeto da Escola SENAI Morvan Figueiredo.
=======
# Avalia SENAI — versão de entrega

Sistema Django para avaliação pedagógica da Escola SENAI Morvan Figueiredo. Inclui gestão de professores, disciplinas, vínculos, contas de alunos, avaliações por vínculo, histórico privado do aluno e relatórios agregados.

## Funcionalidades desta versão

- Autenticação separada por perfil: coordenação e aluno.
- Coordenação pode criar/editar/desativar contas de alunos e redefinir senhas.
- Cada aluno pode registrar **uma avaliação por vínculo professor-disciplina/turma/período**.
- O aluno consulta seu histórico e edita uma avaliação existente; editar não cria uma segunda resposta.
- Registros de participação ficam em tabela separada das respostas. O identificador opaco da resposta é armazenado como recibo criptografado, sem FK de aluno na avaliação.
- A interface da coordenação não expõe a tabela de participação nem mostra comentários/respostas individuais.
- Médias por grupo com menos de `ANONYMITY_MIN_RESPONSES` respostas são omitidas (padrão: 3).
- CRUD de professores, disciplinas e vínculos; dashboard, relatórios agregados, exportação CSV e impressão/salvamento em PDF pelo navegador.
- Migrações versionadas, testes automatizados básicos e configuração por variáveis de ambiente.

## Instalação local (Windows)

Requer Python 3.10 ou superior.

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/`. Entre em `/entrar/` com o superusuário para abrir a coordenação. Crie contas de alunos no menu **Alunos**; o aluno usa o mesmo endereço de login e é redirecionado para sua área.

## Instalação local (macOS/Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Dados de demonstração (opcional)

```bash
python manage.py seed_demo
```

O comando cria vínculos de exemplo, sem apagar registros existentes. Use somente dados fictícios em demonstrações.

## Variáveis de ambiente

Copie `.env.example` para `.env` e carregue as variáveis no ambiente antes de executar. O Django não carrega `.env` automaticamente; em Windows, defina-as na sessão do terminal ou use um gerenciador de ambiente apropriado.

- `DJANGO_SECRET_KEY`: segredo forte, aleatório e estável.
- `DJANGO_DEBUG`: `1` para desenvolvimento; `0` para produção.
- `DJANGO_ALLOWED_HOSTS`: lista de hosts separados por vírgula.
- `ANONYMITY_MIN_RESPONSES`: limite mínimo de respostas para publicar médias por grupo (padrão 3).
- Para PostgreSQL, `DB_ENGINE=postgresql`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` e instale `psycopg[binary]`.

**Não altere `DJANGO_SECRET_KEY` depois de começar a registrar avaliações.** A chave deriva a criptografia dos recibos que permitem ao aluno recuperar e editar suas próprias respostas. Perder/trocar essa chave torna os recibos antigos ilegíveis, embora as respostas agregadas continuem no banco.

## Banco existente de versões anteriores

1. Faça uma cópia de segurança do `db.sqlite3` e de toda a pasta do projeto.
2. Preserve a pasta `avaliacoes/migrations` já aplicada, se ela existir no projeto antigo. Esta entrega inclui migrações `0001_initial` e `0002_student_accounts_anonymous_receipts`; em instalações que já aplicaram uma `0001_initial` equivalente, aplique a nova `0002` com `python manage.py migrate`.
3. Se o projeto antigo foi executado sem migrações versionadas ou a migração inicial divergir, **não apague nem substitua o banco original**. Faça uma cópia e valide a migração em ambiente de teste; os esquemas devem ser alinhados antes de aplicar a atualização.
4. As avaliações anônimas antigas não podem ser atribuídas retroativamente a contas de alunos e não aparecem no histórico de nenhum aluno. Elas permanecem no agregado histórico.

## Testes

```bash
python manage.py test
python manage.py check
```

Teste também manualmente: criação de conta de aluno, avaliação de dois vínculos diferentes, edição de uma avaliação no histórico, bloqueio de acesso de aluno ao painel da coordenação, desativação de conta e backup/restauração.

## Privacidade: limites importantes

O desenho evita uma FK direta entre `Evaluation` e a conta do aluno. A relação de participação guarda o identificador da resposta criptografado com chave derivada de `DJANGO_SECRET_KEY`; a coordenação não tem tela para consultar ou decifrar essa relação. Isso reduz a associação casual e o acesso por usuários da coordenação, mas **não garante anonimato absoluto perante administradores técnicos que controlem o servidor, a chave e o banco**. Horários de acesso, logs externos e conteúdo identificável em comentários também podem permitir correlação. Para uso real, minimize logs, restrinja acesso à infraestrutura, mantenha HTTPS e faça avaliação de privacidade/LGPD.

## Produção

SQLite é adequado para desenvolvimento e testes pequenos. Para uso institucional, prefira PostgreSQL, HTTPS, `DJANGO_DEBUG=0`, segredo via ambiente/secret manager, domínio autorizado, backups automáticos com restauração testada, atualização de dependências, monitoramento e processo de resposta a incidentes. Esta entrega é uma base de aplicação; a implantação em produção deve ser homologada no ambiente real da instituição.
>>>>>>> df73181025d511b4cfebb61908aad9e5724a56ef
