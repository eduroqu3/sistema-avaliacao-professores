# ESCOLA SENAI MORVAN FIGUEIREDO

**Curso:** Desenvolvimento de Sistemas -- 2025_DEV4_SESI\
**Professor:** Johnny Braga de Oliveira

# TEMA -- 7

## Projeto Final -- Sistema de Avaliação de Professores

### Contexto

A escola precisa de uma forma estruturada e anônima para que os alunos
possam avaliar o desempenho dos professores, permitindo que a
coordenação identifique pontos fortes, oportunidades de melhoria e
ofereça suporte pedagógico adequado.

### Problemática

O desafio dos alunos será criar um sistema seguro e confiável,
garantindo anonimato, métricas, dashboards e relatórios comparativos.

## Arquitetura do Projeto

### Back-end (Django)

-   Django (framework principal)
-   Django REST Framework (opcional, para dashboards ou apps mobile)
-   Django Guardian (controle avançado de permissões por usuário)

### Banco de Dados

-   PostgreSQL (armazenamento de professores, disciplinas, avaliações e
    métricas)

### Front-end

-   HTML, CSS, JavaScript
-   Bootstrap ou Tailwind CSS para responsividade
-   Visualização de gráficos com django-chartjs

## Módulos Principais

### 1. Gestão de Usuários

-   Perfis: aluno, professor, administrador
-   Permissões avançadas com django-guardian

### 2. Questionários de Avaliação

-   Avaliações por disciplina
-   Garantia de anonimato com django-anonymizer
-   Sistema de comentários opcional, moderado

### 3. Dashboards

-   Visualização de métricas de desempenho por professor
-   Gráficos comparativos de turmas, disciplinas e períodos
    (django-chartjs)

### 4. Relatórios

-   Comparativos de avaliações
-   Exportação em PDF ou Excel (opcional via reportlab ou openpyxl)

### 5. API REST (opcional)

-   Endpoints para envio de avaliações e consumo de dashboards

## Bibliotecas Necessárias

  -----------------------------------------------------------------------------------
  Biblioteca              Instalação                          Função
  ----------------------- ----------------------------------- -----------------------
  django                  `pip install django`                Framework principal

  django-chartjs          `pip install django-chartjs`        Criação de gráficos e
                                                              visualizações das
                                                              métricas

  django-anonymizer       `pip install django-anonymizer`     Garantir anonimato das
                                                              respostas dos alunos

  django-guardian         `pip install django-guardian`       Controle avançado de
                                                              permissões de acesso

  djangorestframework     `pip install djangorestframework`   API para dashboards ou
  (opcional)                                                  integração com apps

  psycopg2                `pip install psycopg2`              Conexão com PostgreSQL
  -----------------------------------------------------------------------------------

## Entregáveis

### 1. Prototipação UI/UX (Figma ou similar)

-   Fluxo de avaliação anônima
-   Dashboard do professor e coordenação
-   Visualização de gráficos e métricas

### 2. Documentação Técnica e Funcional

-   Requisitos funcionais e não funcionais
-   Diagrama de entidades (DER)
-   Casos de uso (responder avaliação, gerar relatório, visualizar
    métricas)
-   Manual de instalação/configuração
-   Guia do usuário final

### 3. Projeto Django Funcional

-   CRUD completo de professores, disciplinas e avaliações
-   Garantia de anonimato nas respostas
-   Dashboards com gráficos (django-chartjs)
-   Relatórios comparativos gerados

### 4. Apresentação Final (dezembro/2025)

-   Demonstração do sistema de avaliação
-   Apresentação de dashboards e métricas
-   Protótipo navegável
-   Explicação das bibliotecas utilizadas e das soluções implementadas
-   Discussão das dificuldades e como foram resolvidas

------------------------------------------------------------------------

## Identificação dos alunos

Aluno(a): \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
Data: \_\_\_\_/\_\_\_\_/\_\_\_\_\_\_\_\_

Aluno(a): \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
Data: \_\_\_\_/\_\_\_\_/\_\_\_\_\_\_\_\_

Aluno(a): \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
Data: \_\_\_\_/\_\_\_\_/\_\_\_\_\_\_\_\_

Aluno(a): \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
Data: \_\_\_\_/\_\_\_\_/\_\_\_\_\_\_\_\_

Aluno(a): \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
Data: \_\_\_\_/\_\_\_\_/\_\_\_\_\_\_\_\_
