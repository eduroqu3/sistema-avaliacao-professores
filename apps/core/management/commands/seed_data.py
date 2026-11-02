import random
import uuid
from decimal import Decimal
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.evaluations.models import (
    Course, TeacherProfile, Discipline, ClassGroup, ClassOffering,
    EvaluationCycle, EvaluationDimension, EvaluationCriterion,
    EvaluationReceipt, EvaluationResponse, DisposableEvaluationToken
)

User = get_user_model()

class Command(BaseCommand):
    help = "Popula o banco de dados com dados iniciais realistas do SENAI Morvan Figueiredo."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Iniciando carga de dados institucionais (SENAI Morvan Figueiredo)..."))

        # 1. Usuários Administrativos e Coordenação
        admin_user, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "first_name": "Administrador",
                "last_name": "Geral",
                "email": "admin@sp.senai.br",
                "role": "ADMIN",
                "is_staff": True,
                "is_superuser": True,
                "registration_number": "ADM-001"
            }
        )
        admin_user.set_password("senai123")
        admin_user.save()

        coord_user, _ = User.objects.get_or_create(
            username="coordenacao",
            defaults={
                "first_name": "Profa. Valéria",
                "last_name": "Mendes",
                "email": "coordenacao.ti@sp.senai.br",
                "role": "COORDINATOR",
                "is_staff": True,
                "registration_number": "COORD-101"
            }
        )
        coord_user.set_password("senai123")
        coord_user.save()

        # 2. Professores (Destaque para Prof. Johnny Braga de Oliveira conforme TEMA-7)
        teachers_data = [
            {
                "username": "johnny",
                "first_name": "Johnny",
                "last_name": "Braga de Oliveira",
                "email": "johnny.oliveira@sp.senai.br",
                "title": "ESP",
                "department": "Desenvolvimento de Sistemas & Arquitetura Web",
                "bio": "Especialista em Desenvolvimento Web FullStack, Django, Python e Arquitetura de Software.",
                "rf": "RF-2025-07"
            },
            {
                "username": "mariana",
                "first_name": "Mariana",
                "last_name": "Alencar",
                "email": "mariana.alencar@sp.senai.br",
                "title": "MEST",
                "department": "Banco de Dados & Inteligência Artificial",
                "bio": "Mestre em Ciência da Computação, especialista em PostgreSQL, Supabase e Modelagem Relacional.",
                "rf": "RF-2024-12"
            },
            {
                "username": "carlos",
                "first_name": "Carlos",
                "last_name": "Eduardo Souza",
                "email": "carlos.souza@sp.senai.br",
                "title": "ESP",
                "department": "Infraestrutura & DevOps",
                "bio": "Especialista em Nuvem, Microsserviços e Engenharia de Software Moderna.",
                "rf": "RF-2023-33"
            }
        ]

        teacher_profiles = []
        for t in teachers_data:
            user, _ = User.objects.get_or_create(
                username=t["username"],
                defaults={
                    "first_name": t["first_name"],
                    "last_name": t["last_name"],
                    "email": t["email"],
                    "role": "TEACHER",
                    "registration_number": t["rf"]
                }
            )
            user.set_password("senai123")
            user.save()

            profile, _ = TeacherProfile.objects.get_or_create(
                user=user,
                defaults={
                    "academic_title": t["title"],
                    "department": t["department"],
                    "bio": t["bio"]
                }
            )
            teacher_profiles.append(profile)

        # 3. Alunos do Grupo (Identificação dos alunos conforme solicitação do usuário)
        students_team_data = [
            ("eduardo", "Eduardo", "Vieira Roque", "RM-20250101"),
            ("gustavo", "Gustavo", "Costa Trindade", "RM-20250102"),
            ("guilherme", "Guilherme", "Vilares", "RM-20250103"),
            ("aron", "Aron", "Maestá", "RM-20250104"),
            ("diogo", "Diogo", "Ferrata", "RM-20250105"),
        ]

        student_users = []
        for uname, fname, lname, rm in students_team_data:
            st, _ = User.objects.get_or_create(
                username=uname,
                defaults={
                    "first_name": fname,
                    "last_name": lname,
                    "email": f"{uname}@aluno.senai.br",
                    "role": "STUDENT",
                    "registration_number": rm
                }
            )
            st.set_password("senai123")
            st.save()
            student_users.append(st)

        # 4. Curso e Turma (Conforme TEMA-7: 2025_DEV4_SESI)
        course, _ = Course.objects.get_or_create(
            code="DEV-SESI",
            defaults={
                "name": "Técnico em Desenvolvimento de Sistemas",
                "modality": "PRESENTIAL"
            }
        )

        class_group, _ = ClassGroup.objects.get_or_create(
            name="2025_DEV4_SESI",
            course=course,
            defaults={
                "shift": "TARDE",
                "year": 2025,
                "semester": 1
            }
        )
        for st in student_users:
            class_group.students.add(st)
        class_group.save()

        # 5. Disciplinas e Ofertas
        disciplines_data = [
            ("Desenvolvimento de Aplicações Web (Django/Python)", "DEV-PY-01", 100, teacher_profiles[0]),
            ("Banco de Dados Relacionais e Nuvem (PostgreSQL/Supabase)", "BD-SQL-02", 80, teacher_profiles[1]),
            ("Engenharia de Software e Metodologias Ágeis", "ENG-SOFT-03", 60, teacher_profiles[2]),
        ]

        offerings = []
        for dname, dcode, dwork, tprof in disciplines_data:
            disc, _ = Discipline.objects.get_or_create(
                code=dcode,
                defaults={
                    "name": dname,
                    "course": course,
                    "workload_hours": dwork,
                    "description": f"Formação técnica e prática de {dname} no SENAI Morvan Figueiredo."
                }
            )
            offering, _ = ClassOffering.objects.get_or_create(
                discipline=disc,
                teacher=tprof,
                class_group=class_group,
                academic_period="2025/1",
                defaults={"is_active": True}
            )
            offerings.append(offering)

        # 6. Ciclo de Avaliação Ativo
        today = timezone.localdate()
        cycle, _ = EvaluationCycle.objects.get_or_create(
            academic_period="2025/1",
            title="Avaliação Docente Institucional - 2025/1",
            defaults={
                "description": (
                    "Prezados alunos da turma 2025_DEV4_SESI, sua participação sincera e anônima é essencial "
                    "para o aprimoramento contínuo das práticas pedagógicas da Escola SENAI Morvan Figueiredo. "
                    "Seus dados de resposta são 100% desvinculados do seu perfil de usuário."
                ),
                "start_date": today - timedelta(days=10),
                "end_date": today + timedelta(days=20),
                "is_active": True
            }
        )

        # 7. Dimensões Pedagógicas e Critérios Estruturados
        dimensions_data = [
            {
                "order": 1,
                "name": "Didática e Metodologia de Ensino",
                "desc": "Clareza expositiva, ritmo de aula, contextualização prática e estímulo à aprendizagem.",
                "criteria": [
                    ("Clareza na explicação dos conceitos teóricos e resolução de dúvidas.", "Explica de forma acessível e objetiva."),
                    ("Utilização de exemplos práticos do mercado de trabalho e estudos de caso.", "Traz projetos e situações reais para a sala de aula."),
                    ("Estímulo à participação ativa, perguntas e colaboração em equipe.", "Incentiva os alunos a exporem dúvidas e debaterem."),
                ]
            },
            {
                "order": 2,
                "name": "Domínio Tecnológico e Conhecimento Prático",
                "desc": "Profundidade técnica, segurança nas ferramentas e atualização com as tendências do mercado.",
                "criteria": [
                    ("Domínio aprofundado das tecnologias e frameworks abordados (Django, SQL, etc.).", "Demonstra segurança ao programar e debugar."),
                    ("Capacidade de orientar a resolução de problemas e erros de código em laboratório.", "Auxilia os alunos com eficiência durante a prática."),
                ]
            },
            {
                "order": 3,
                "name": "Pontualidade, Assiduidade e Organização",
                "desc": "Cumprimento de horários, cronograma de aulas e disponibilidade pedagógica.",
                "criteria": [
                    ("Pontualidade no início e término das aulas e intervalos.", "Respeita o cronograma escolar do SENAI."),
                    ("Cumprimento do plano de ensino e ementa da Unidade Curricular.", "Apresenta o conteúdo programado de forma estruturada."),
                ]
            },
            {
                "order": 4,
                "name": "Relacionamento Interpessoal e Postura Profissional",
                "desc": "Respeito, ética, empatia, escuta ativa e tratamento equitativo com os estudantes.",
                "criteria": [
                    ("Tratamento respeitoso, ético e cordial com todos os alunos.", "Mantém ambiente acolhedor e profissional."),
                    ("Disponibilidade para atendimento extraclasse e orientação pedagógica.", "Acessível nos canais institucionais quando necessário."),
                ]
            },
            {
                "order": 5,
                "name": "Critérios de Avaliação e Feedback",
                "desc": "Transparência nas notas, correção justa e retorno construtivo para evolução do aluno.",
                "criteria": [
                    ("Clareza e justiça nos critérios de avaliação e prazos de entrega.", "Rubricas claras e avisadas com antecedência."),
                    ("Devolutiva e feedback detalhado sobre entregas e atividades práticas.", "Aponta pontos fortes e oportunidades de melhoria."),
                ]
            }
        ]

        all_criteria = []
        for dim_data in dimensions_data:
            dimension, _ = EvaluationDimension.objects.get_or_create(
                name=dim_data["name"],
                defaults={
                    "order": dim_data["order"],
                    "description": dim_data["desc"],
                    "weight": Decimal("1.00")
                }
            )
            for idx, (crit_title, crit_help) in enumerate(dim_data["criteria"], start=1):
                crit, _ = EvaluationCriterion.objects.get_or_create(
                    dimension=dimension,
                    title=crit_title,
                    defaults={
                        "help_text": crit_help,
                        "order": idx,
                        "min_score": 1,
                        "max_score": 5
                    }
                )
                all_criteria.append(crit)

        # 8. Criação de Respostas Anônimas de Exemplo para Johnny, Mariana e Carlos
        # Geramos distribuições realistas para alimentar os gráficos do Chart.js
        sample_comments_johnny = [
            ("Excelente metodologia! A abordagem prática com projetos reais em Django nos dá total confiança para o mercado.", "APPROVED"),
            ("O professor domina profundamente arquitetura web e sempre tem paciência para explicar dúvidas em sala.", "APPROVED"),
            ("Aulas muito dinâmicas e material de apoio impecável. Melhor matéria do semestre!", "APPROVED"),
            ("Poderia reservar mais 15 minutos ao final da aula para tira-dúvidas de código mais avançado.", "APPROVED"),
            ("Texto ofensivo de teste para demonstrar a fila de moderação pedagógica.", "PENDING"),
        ]

        sample_comments_mariana = [
            ("Didática perfeita para banco de dados. A modelagem no Supabase e PostgreSQL ficou muito clara.", "APPROVED"),
            ("Muito atenciosa e traz exercícios que realmente desafiam nosso raciocínio analítico.", "APPROVED"),
            ("Explicações claras e bons laboratórios de SQL prático.", "APPROVED"),
        ]

        sample_comments_carlos = [
            ("Excelente conhecimento em metodologias ágeis e arquitetura em nuvem.", "APPROVED"),
            ("Gostaria de mais aulas práticas no laboratório com Docker e CI/CD.", "APPROVED"),
        ]

        # Respostas para Prof. Johnny Braga de Oliveira
        offering_johnny = offerings[0]
        if EvaluationResponse.objects.filter(offering=offering_johnny).count() == 0:
            for i in range(12):
                crit_scores = {}
                dim_totals = {}
                dim_counts = {}

                for c in all_criteria:
                    # Johnny tem média alta (4 ou 5)
                    score = random.choices([4, 5], weights=[25, 75])[0]
                    crit_scores[str(c.id)] = score
                    
                    dim_id = str(c.dimension.id)
                    dim_totals[dim_id] = dim_totals.get(dim_id, 0) + score
                    dim_counts[dim_id] = dim_counts.get(dim_id, 0) + 1

                dim_scores = {dim_id: round(dim_totals[dim_id] / dim_counts[dim_id], 2) for dim_id in dim_totals}
                overall = round(sum(crit_scores.values()) / len(crit_scores), 2)

                comm_text, status = ("", "APPROVED")
                if i < len(sample_comments_johnny):
                    comm_text, status = sample_comments_johnny[i]

                EvaluationResponse.objects.create(
                    offering=offering_johnny,
                    cycle=cycle,
                    overall_score=Decimal(str(overall)),
                    criteria_scores=crit_scores,
                    dimension_scores=dim_scores,
                    comment=comm_text if comm_text else None,
                    moderation_status=status
                )

        # Respostas para Profa. Mariana
        offering_mariana = offerings[1]
        if EvaluationResponse.objects.filter(offering=offering_mariana).count() == 0:
            for i in range(10):
                crit_scores = {}
                dim_totals = {}
                dim_counts = {}

                for c in all_criteria:
                    score = random.choices([4, 5, 3], weights=[45, 50, 5])[0]
                    crit_scores[str(c.id)] = score
                    dim_id = str(c.dimension.id)
                    dim_totals[dim_id] = dim_totals.get(dim_id, 0) + score
                    dim_counts[dim_id] = dim_counts.get(dim_id, 0) + 1

                dim_scores = {dim_id: round(dim_totals[dim_id] / dim_counts[dim_id], 2) for dim_id in dim_totals}
                overall = round(sum(crit_scores.values()) / len(crit_scores), 2)

                comm_text, status = ("", "APPROVED")
                if i < len(sample_comments_mariana):
                    comm_text, status = sample_comments_mariana[i]

                EvaluationResponse.objects.create(
                    offering=offering_mariana,
                    cycle=cycle,
                    overall_score=Decimal(str(overall)),
                    criteria_scores=crit_scores,
                    dimension_scores=dim_scores,
                    comment=comm_text if comm_text else None,
                    moderation_status=status
                )

        # Respostas para Prof. Carlos
        offering_carlos = offerings[2]
        if EvaluationResponse.objects.filter(offering=offering_carlos).count() == 0:
            for i in range(8):
                crit_scores = {}
                dim_totals = {}
                dim_counts = {}

                for c in all_criteria:
                    score = random.choices([3, 4, 5], weights=[20, 50, 30])[0]
                    crit_scores[str(c.id)] = score
                    dim_id = str(c.dimension.id)
                    dim_totals[dim_id] = dim_totals.get(dim_id, 0) + score
                    dim_counts[dim_id] = dim_counts.get(dim_id, 0) + 1

                dim_scores = {dim_id: round(dim_totals[dim_id] / dim_counts[dim_id], 2) for dim_id in dim_totals}
                overall = round(sum(crit_scores.values()) / len(crit_scores), 2)

                comm_text, status = ("", "APPROVED")
                if i < len(sample_comments_carlos):
                    comm_text, status = sample_comments_carlos[i]

                EvaluationResponse.objects.create(
                    offering=offering_carlos,
                    cycle=cycle,
                    overall_score=Decimal(str(overall)),
                    criteria_scores=crit_scores,
                    dimension_scores=dim_scores,
                    comment=comm_text if comm_text else None,
                    moderation_status=status
                )

        # 9. Gerar recibos de participação para alguns alunos da turma (garantindo que 2 já votaram e 3 ainda têm pendência)
        # Observação: os recibos NÃO possuem link com as respostas criadas acima!
        for st in student_users[:2]:
            token_hash = EvaluationReceipt.generate_receipt_token(st.id, offering_johnny.id, cycle.id)
            EvaluationReceipt.objects.get_or_create(
                student=st,
                offering=offering_johnny,
                cycle=cycle,
                defaults={"receipt_hash": token_hash}
            )

        # 10. Tokens Descartáveis para Navegação e Votação 100% Anônima (Modo PIN Laboratório)
        pins_demo = ["SENAI-2025-DEV4-LAB1", "SENAI-2025-DEV4-LAB2", "SENAI-2025-DEV4-LAB3"]
        for p in pins_demo:
            DisposableEvaluationToken.objects.get_or_create(
                token=p,
                offering=offering_johnny,
                cycle=cycle,
                defaults={"is_used": False}
            )

        self.stdout.write(self.style.SUCCESS("[OK] Banco de dados populado com sucesso com dados da Escola SENAI Morvan Figueiredo!"))
        self.stdout.write(self.style.SUCCESS("[OK] Usuarios criados: admin/senai123, coordenacao/senai123, johnny/senai123, eduardo/senai123, etc."))
