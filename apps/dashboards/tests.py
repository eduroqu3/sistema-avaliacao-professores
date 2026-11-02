from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.evaluations.models import (
    Course, ClassGroup, TeacherProfile, Discipline, ClassOffering,
    EvaluationCycle, EvaluationDimension, EvaluationCriterion,
    EvaluationResponse
)

User = get_user_model()

class DashboardsAndReportsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.coordinator = User.objects.create_user(
            username="test_coord",
            password="password123",
            role="COORDINATOR",
            is_staff=True
        )

        self.teacher_user = User.objects.create_user(
            username="test_prof",
            password="password123",
            role="TEACHER",
            first_name="Johnny",
            last_name="Braga"
        )
        self.teacher_profile = TeacherProfile.objects.create(
            user=self.teacher_user,
            academic_title="ESP"
        )

        self.course = Course.objects.create(name="Desenvolvimento de Sistemas", code="DEV-01")
        self.class_group = ClassGroup.objects.create(name="2025_DEV4_SESI", course=self.course)
        self.discipline = Discipline.objects.create(name="Django Web", code="DJ-01", course=self.course)
        self.offering = ClassOffering.objects.create(
            discipline=self.discipline,
            teacher=self.teacher_profile,
            class_group=self.class_group,
            academic_period="2025/1"
        )
        self.cycle = EvaluationCycle.objects.create(
            title="Ciclo 2025/1",
            academic_period="2025/1",
            start_date=timezone.localdate(),
            end_date=timezone.localdate(),
            is_active=True
        )
        self.dim = EvaluationDimension.objects.create(name="Didática", order=1)

        # Resposta com comentário pendente
        self.response_obj = EvaluationResponse.objects.create(
            offering=self.offering,
            cycle=self.cycle,
            overall_score=Decimal("4.80"),
            dimension_scores={str(self.dim.id): 4.8},
            comment="Ótimo professor!",
            moderation_status="PENDING"
        )

    def test_teacher_dashboard_view(self):
        self.client.login(username="test_prof", password="password123")
        res = self.client.get(reverse('dashboards:teacher_dashboard'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Johnny Braga")
        # pt-br localization formats decimals with comma: 4,80
        self.assertContains(res, "4,80")

    def test_coordination_dashboard_view(self):
        self.client.login(username="test_coord", password="password123")
        res = self.client.get(reverse('dashboards:coordination_dashboard'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Painel Geral da Coordenação")

    def test_moderation_action(self):
        self.client.login(username="test_coord", password="password123")
        url = reverse('dashboards:moderation_action', kwargs={'response_id': self.response_obj.id})
        res = self.client.post(url, {'action': 'APPROVE', 'notes': 'Aprovado para exibição'}, follow=True)
        self.assertEqual(res.status_code, 200)

        self.response_obj.refresh_from_db()
        self.assertEqual(self.response_obj.moderation_status, "APPROVED")

    def test_excel_export(self):
        self.client.login(username="test_coord", password="password123")
        url = reverse('reports:export_excel', kwargs={'cycle_id': self.cycle.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
