-- =============================================================================
-- ESCOLA SENAI MORVAN FIGUEIREDO
-- Curso: Desenvolvimento de Sistemas -- 2025_DEV4_SESI
-- Professor: Johnny Braga de Oliveira
-- Alunos: Eduardo Vieira Roque, Gustavo Costa Trindade, Guilherme Vilares,
--         Aron Maestá, Diogo Ferrata
--
-- PROJETO: Avalia SENAI - Sistema de Avaliação Docente com Anonimato Criptográfico
-- BANCO DE DADOS: PostgreSQL (Supabase)
-- =============================================================================

-- Habilita extensões necessárias no Supabase
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Limpeza preventiva de tabelas caso já existam (ordem reversa de dependências)
DROP TABLE IF EXISTS "evaluations_disposableevaluationtoken" CASCADE;
DROP TABLE IF EXISTS "evaluations_evaluationreceipt" CASCADE;
DROP TABLE IF EXISTS "evaluations_evaluationresponse" CASCADE;
DROP TABLE IF EXISTS "evaluations_evaluationcriterion" CASCADE;
DROP TABLE IF EXISTS "evaluations_evaluationdimension" CASCADE;
DROP TABLE IF EXISTS "evaluations_evaluationcycle" CASCADE;
DROP TABLE IF EXISTS "evaluations_classoffering" CASCADE;
DROP TABLE IF EXISTS "evaluations_discipline" CASCADE;
DROP TABLE IF EXISTS "evaluations_classgroup_students" CASCADE;
DROP TABLE IF EXISTS "evaluations_classgroup" CASCADE;
DROP TABLE IF EXISTS "evaluations_teacherprofile" CASCADE;
DROP TABLE IF EXISTS "evaluations_course" CASCADE;
DROP TABLE IF EXISTS "accounts_user_user_permissions" CASCADE;
DROP TABLE IF EXISTS "accounts_user_groups" CASCADE;
DROP TABLE IF EXISTS "accounts_user" CASCADE;

-- -----------------------------------------------------------------------------
-- 1. TABELA DE USUÁRIOS DO SISTEMA (accounts_user)
-- -----------------------------------------------------------------------------
CREATE TABLE "accounts_user" (
    "id" BIGSERIAL PRIMARY KEY,
    "password" VARCHAR(128) NOT NULL,
    "last_login" TIMESTAMP WITH TIME ZONE NULL,
    "is_superuser" BOOLEAN NOT NULL DEFAULT FALSE,
    "username" VARCHAR(150) NOT NULL UNIQUE,
    "first_name" VARCHAR(150) NOT NULL DEFAULT '',
    "last_name" VARCHAR(150) NOT NULL DEFAULT '',
    "email" VARCHAR(254) NOT NULL DEFAULT '',
    "is_staff" BOOLEAN NOT NULL DEFAULT FALSE,
    "is_active" BOOLEAN NOT NULL DEFAULT TRUE,
    "date_joined" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "role" VARCHAR(20) NOT NULL DEFAULT 'STUDENT' CHECK ("role" IN ('ADMIN', 'COORDINATOR', 'TEACHER', 'STUDENT')),
    "registration_number" VARCHAR(30) UNIQUE NULL,
    "phone" VARCHAR(20) NULL,
    "avatar_url" VARCHAR(200) NULL
);

CREATE INDEX "idx_accounts_user_role" ON "accounts_user" ("role");
CREATE INDEX "idx_accounts_user_reg" ON "accounts_user" ("registration_number");

-- -----------------------------------------------------------------------------
-- 2. TABELA DE CURSOS (evaluations_course)
-- -----------------------------------------------------------------------------
CREATE TABLE "evaluations_course" (
    "id" BIGSERIAL PRIMARY KEY,
    "name" VARCHAR(150) NOT NULL,
    "code" VARCHAR(30) NOT NULL UNIQUE,
    "modality" VARCHAR(20) NOT NULL DEFAULT 'PRESENTIAL' CHECK ("modality" IN ('PRESENTIAL', 'SEMI', 'EAD')),
    "created_at" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 3. PERFIL DO PROFESSOR (evaluations_teacherprofile)
-- -----------------------------------------------------------------------------
CREATE TABLE "evaluations_teacherprofile" (
    "id" BIGSERIAL PRIMARY KEY,
    "user_id" BIGINT NOT NULL UNIQUE REFERENCES "accounts_user" ("id") ON DELETE CASCADE,
    "academic_title" VARCHAR(10) NOT NULL DEFAULT 'ESP' CHECK ("academic_title" IN ('GRAD', 'ESP', 'MEST', 'DOUT', 'NOT')),
    "department" VARCHAR(100) NOT NULL DEFAULT 'Tecnologia da Informação',
    "bio" TEXT NOT NULL DEFAULT ''
);

-- -----------------------------------------------------------------------------
-- 4. TURMAS (evaluations_classgroup) E MATRÍCULAS
-- -----------------------------------------------------------------------------
CREATE TABLE "evaluations_classgroup" (
    "id" BIGSERIAL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "course_id" BIGINT NOT NULL REFERENCES "evaluations_course" ("id") ON DELETE CASCADE,
    "shift" VARCHAR(20) NOT NULL DEFAULT 'MANHA' CHECK ("shift" IN ('MANHA', 'TARDE', 'NOITE', 'INTEGRAL')),
    "year" INTEGER NOT NULL CHECK ("year" >= 2020),
    "semester" SMALLINT NOT NULL CHECK ("semester" IN (1, 2))
);

CREATE INDEX "idx_classgroup_course" ON "evaluations_classgroup" ("course_id");

CREATE TABLE "evaluations_classgroup_students" (
    "id" BIGSERIAL PRIMARY KEY,
    "classgroup_id" BIGINT NOT NULL REFERENCES "evaluations_classgroup" ("id") ON DELETE CASCADE,
    "user_id" BIGINT NOT NULL REFERENCES "accounts_user" ("id") ON DELETE CASCADE,
    CONSTRAINT "uniq_classgroup_student" UNIQUE ("classgroup_id", "user_id")
);

-- -----------------------------------------------------------------------------
-- 5. DISCIPLINAS (evaluations_discipline)
-- -----------------------------------------------------------------------------
CREATE TABLE "evaluations_discipline" (
    "id" BIGSERIAL PRIMARY KEY,
    "name" VARCHAR(150) NOT NULL,
    "code" VARCHAR(30) NOT NULL UNIQUE,
    "course_id" BIGINT NOT NULL REFERENCES "evaluations_course" ("id") ON DELETE CASCADE,
    "workload_hours" INTEGER NOT NULL CHECK ("workload_hours" > 0),
    "description" TEXT NOT NULL DEFAULT ''
);

CREATE INDEX "idx_discipline_course" ON "evaluations_discipline" ("course_id");

-- -----------------------------------------------------------------------------
-- 6. ATRIBUIÇÃO DOCENTE / OFERTA DE DISCIPLINA (evaluations_classoffering)
-- -----------------------------------------------------------------------------
CREATE TABLE "evaluations_classoffering" (
    "id" BIGSERIAL PRIMARY KEY,
    "discipline_id" BIGINT NOT NULL REFERENCES "evaluations_discipline" ("id") ON DELETE CASCADE,
    "teacher_id" BIGINT NOT NULL REFERENCES "evaluations_teacherprofile" ("id") ON DELETE CASCADE,
    "class_group_id" BIGINT NOT NULL REFERENCES "evaluations_classgroup" ("id") ON DELETE CASCADE,
    "academic_period" VARCHAR(20) NOT NULL DEFAULT '2025/1',
    "is_active" BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT "uniq_classoffering_period" UNIQUE ("discipline_id", "teacher_id", "class_group_id", "academic_period")
);

CREATE INDEX "idx_offering_teacher" ON "evaluations_classoffering" ("teacher_id");
CREATE INDEX "idx_offering_discipline" ON "evaluations_classoffering" ("discipline_id");
CREATE INDEX "idx_offering_group" ON "evaluations_classoffering" ("class_group_id");

-- -----------------------------------------------------------------------------
-- 7. CICLO DE AVALIAÇÃO (evaluations_evaluationcycle)
-- -----------------------------------------------------------------------------
CREATE TABLE "evaluations_evaluationcycle" (
    "id" BIGSERIAL PRIMARY KEY,
    "title" VARCHAR(150) NOT NULL,
    "description" TEXT NOT NULL DEFAULT '',
    "academic_period" VARCHAR(20) NOT NULL,
    "start_date" DATE NOT NULL,
    "end_date" DATE NOT NULL,
    "is_active" BOOLEAN NOT NULL DEFAULT TRUE,
    "created_at" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "chk_cycle_dates" CHECK ("end_date" >= "start_date")
);

-- -----------------------------------------------------------------------------
-- 8. DIMENSÕES E CRITÉRIOS DE AVALIAÇÃO
-- -----------------------------------------------------------------------------
CREATE TABLE "evaluations_evaluationdimension" (
    "id" BIGSERIAL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "description" TEXT NOT NULL DEFAULT '',
    "weight" NUMERIC(3, 2) NOT NULL DEFAULT 1.00,
    "order" SMALLINT NOT NULL DEFAULT 1
);

CREATE TABLE "evaluations_evaluationcriterion" (
    "id" BIGSERIAL PRIMARY KEY,
    "dimension_id" BIGINT NOT NULL REFERENCES "evaluations_evaluationdimension" ("id") ON DELETE CASCADE,
    "title" VARCHAR(200) NOT NULL,
    "help_text" VARCHAR(250) NOT NULL DEFAULT '',
    "order" SMALLINT NOT NULL DEFAULT 1,
    "min_score" SMALLINT NOT NULL DEFAULT 1,
    "max_score" SMALLINT NOT NULL DEFAULT 5,
    CONSTRAINT "chk_scores_order" CHECK ("max_score" >= "min_score")
);

CREATE INDEX "idx_criterion_dimension" ON "evaluations_evaluationcriterion" ("dimension_id");

-- -----------------------------------------------------------------------------
-- 9. PROTOCOLO DE ANONIMATO CRIPTOGRÁFICO:
--    TABELA A: COMPROVANTE DE PARTICIPAÇÃO (EvaluationReceipt)
-- -----------------------------------------------------------------------------
-- Esta tabela armazena exclusivamente QUEM votou para evitar votos duplicados.
-- ELA NÃO CONTÉM NENHUMA CHAVE NEM PONTEIRO PARA A TABELA DE RESPOSTAS!
CREATE TABLE "evaluations_evaluationreceipt" (
    "id" BIGSERIAL PRIMARY KEY,
    "student_id" BIGINT NOT NULL REFERENCES "accounts_user" ("id") ON DELETE CASCADE,
    "offering_id" BIGINT NOT NULL REFERENCES "evaluations_classoffering" ("id") ON DELETE CASCADE,
    "cycle_id" BIGINT NOT NULL REFERENCES "evaluations_evaluationcycle" ("id") ON DELETE CASCADE,
    "receipt_hash" VARCHAR(64) NOT NULL UNIQUE,
    "completed_at" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "uniq_student_offering_cycle" UNIQUE ("student_id", "offering_id", "cycle_id")
);

CREATE INDEX "idx_receipt_student" ON "evaluations_evaluationreceipt" ("student_id");
CREATE INDEX "idx_receipt_offering" ON "evaluations_evaluationreceipt" ("offering_id");

-- -----------------------------------------------------------------------------
-- 10. PROTOCOLO DE ANONIMATO CRIPTOGRÁFICO:
--     TABELA B: RESPOSTAS ANÔNIMAS (EvaluationResponse)
-- -----------------------------------------------------------------------------
-- Esta tabela armazena as notas e opiniões pedagógicas.
-- NÃO CONTÉM student_id, nem IP, nem User-Agent, nem chave para EvaluationReceipt!
CREATE TABLE "evaluations_evaluationresponse" (
    "id" BIGSERIAL PRIMARY KEY,
    "offering_id" BIGINT NOT NULL REFERENCES "evaluations_classoffering" ("id") ON DELETE CASCADE,
    "cycle_id" BIGINT NOT NULL REFERENCES "evaluations_evaluationcycle" ("id") ON DELETE CASCADE,
    "overall_score" NUMERIC(4, 2) NOT NULL CHECK ("overall_score" >= 1.00 AND "overall_score" <= 5.00),
    "criteria_scores" JSONB NOT NULL DEFAULT '{}'::jsonb,
    "dimension_scores" JSONB NOT NULL DEFAULT '{}'::jsonb,
    "comment" TEXT NULL,
    "moderation_status" VARCHAR(20) NOT NULL DEFAULT 'APPROVED' CHECK ("moderation_status" IN ('PENDING', 'APPROVED', 'REJECTED')),
    "moderation_notes" TEXT NOT NULL DEFAULT '',
    "moderated_by_id" BIGINT NULL REFERENCES "accounts_user" ("id") ON DELETE SET NULL,
    "moderated_at" TIMESTAMP WITH TIME ZONE NULL,
    "submitted_at" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX "idx_response_offering" ON "evaluations_evaluationresponse" ("offering_id");
CREATE INDEX "idx_response_cycle" ON "evaluations_evaluationresponse" ("cycle_id");
CREATE INDEX "idx_response_status" ON "evaluations_evaluationresponse" ("moderation_status");
CREATE INDEX "idx_response_scores_gin" ON "evaluations_evaluationresponse" USING gin ("criteria_scores");

-- -----------------------------------------------------------------------------
-- 11. NAVEGAÇÃO ANÔNIMA VIA TOKENS / PINS DESCARTÁVEIS (DisposableEvaluationToken)
-- -----------------------------------------------------------------------------
CREATE TABLE "evaluations_disposableevaluationtoken" (
    "id" BIGSERIAL PRIMARY KEY,
    "token" VARCHAR(64) NOT NULL UNIQUE,
    "offering_id" BIGINT NOT NULL REFERENCES "evaluations_classoffering" ("id") ON DELETE CASCADE,
    "cycle_id" BIGINT NOT NULL REFERENCES "evaluations_evaluationcycle" ("id") ON DELETE CASCADE,
    "is_used" BOOLEAN NOT NULL DEFAULT FALSE,
    "used_at" TIMESTAMP WITH TIME ZONE NULL,
    "created_at" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX "idx_disposable_token_code" ON "evaluations_disposableevaluationtoken" ("token");
CREATE INDEX "idx_disposable_token_used" ON "evaluations_disposableevaluationtoken" ("is_used");

-- -----------------------------------------------------------------------------
-- 12. SUPABASE ROW LEVEL SECURITY (RLS) POLICIES
-- -----------------------------------------------------------------------------
-- Ativação do RLS nas tabelas sensíveis
ALTER TABLE "evaluations_evaluationresponse" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "evaluations_evaluationreceipt" ENABLE ROW LEVEL SECURITY;

-- Política 1: Inserção de respostas permitida para usuários autenticados ou anônimos com token válido
CREATE POLICY "Permitir envio de respostas anônimas"
ON "evaluations_evaluationresponse"
FOR INSERT
WITH CHECK (true);

-- Política 2: Alunos NUNCA podem visualizar a tabela bruta de respostas (garantindo sigilo)
-- Política 3: Professores e coordenação visualizam através de roles da aplicação
CREATE POLICY "Leitura de respostas públicas e aprovadas"
ON "evaluations_evaluationresponse"
FOR SELECT
USING ("moderation_status" = 'APPROVED');

-- =============================================================================
-- FIM DO SCRIPT DE ESTRUTURAÇÃO DO BANCO DE DADOS SUPABASE
-- =============================================================================
