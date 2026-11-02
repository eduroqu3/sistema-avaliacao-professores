from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.evaluations.models import (
    Course, ClassGroup, TeacherProfile, Discipline, ClassOffering,
    EvaluationCycle, EvaluationDimension, EvaluationCriterion,
    EvaluationReceipt, EvaluationResponse, DisposableEvaluationToken
)

User = get_user_model()

class AnonymityEvaluationTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Usuários
        self.student = User.objects.create_user(
            username="test_student",
            password="password123",
            role="STUDENT",
            registration_number="RM-9999"
        )
        self.teacher_user = User.objects.create_user(
            username="test_teacher",
            password="password123",
            role="TEACHER",
            registration_number="RF-8888",
            first_name="Johnny",
            last_name="Oliveira"
        )
        self.teacher_profile = TeacherProfile.objects.create(
            user=self.teacher_user,
            academic_title="ESP",
            department="Tecnologia da Informação"
        )

        # Estrutura Acadêmica
        self.course = Course.objects.create(name="Desenvolvimento de Sistemas", code="DEV-TEST")
        self.class_group = ClassGroup.objects.create(name="2025_DEV4_SESI", course=self.course, shift="TARDE")
        self.class_group.students.add(self.student)

        self.discipline = Discipline.objects.create(
            name="Programação Web",
            code="WEB-01",
            course=self.course,
            workload_hours=80
        )
        self.offering = ClassOffering.objects.create(
            discipline=self.discipline,
            teacher=self.teacher_profile,
            class_group=self.class_group,
            academic_period="2025/1"
        )

        # Ciclo
        self.cycle = EvaluationCycle.objects.create(
            title="Ciclo Teste 2025/1",
            academic_period="2025/1",
            start_date=timezone.localdate(),
            end_date=timezone.localdate(),
            is_active=True
        )

        # Dimensão e Critérios
        self.dim = EvaluationDimension.objects.create(name="Didática", order=1)
        self.crit1 = EvaluationCriterion.objects.create(dimension=self.dim, title="Clareza", order=1)
        self.crit2 = EvaluationCriterion.objects.create(dimension=self.dim, title="Exemplos", order=2)

    def test_anonymous_evaluation_submission_and_zero_link(self):
        """
        Garante que a avaliação é enviada, o recibo é registrado para o aluno,
        mas a resposta gravada NÃO possui nenhuma referência ao estudante.
        """
        self.client.login(username="test_student", password="password123")

        post_data = {
            f"criterion_{self.crit1.id}": "5",
            f"criterion_{self.crit2.id}": "4",
            "comment": "Excelente disciplina prática de Django!"
        }

        url = reverse('evaluations:evaluate_form', kwargs={'offering_id': self.offering.id})
        response = self.client.post(url, data=post_data, follow=True)

        self.assertEqual(response.status_code, 200)

        # Verifica Recibo
        receipt = EvaluationReceipt.objects.filter(student=self.student, offering=self.offering).first()
        self.assertIsNotNone(receipt)
        self.assertTrue(len(receipt.receipt_hash) > 20)

        # Verifica Resposta Anônima
        resp = EvaluationResponse.objects.filter(offering=self.offering).first()
        self.assertIsNotNone(resp)
        self.assertEqual(resp.overall_score, Decimal("4.50"))
        self.assertEqual(resp.comment, "Excelente disciplina prática de Django!")
        self.assertEqual(resp.moderation_status, "PENDING")

        # Verifica que o modelo EvaluationResponse não possui nenhum campo de student_id
        self.assertFalse(hasattr(resp, 'student'))
        self.assertFalse(hasattr(resp, 'student_id'))

    def test_double_submission_prevented(self):
        """
        Garante que o aluno não consiga votar duas vezes para a mesma disciplina no mesmo ciclo.
        """
        self.client.login(username="test_student", password="password123")

        post_data = {
            f"criterion_{self.crit1.id}": "5",
            f"criterion_{self.crit2.id}": "5",
        }
        url = reverse('evaluations:evaluate_form', kwargs={'offering_id': self.offering.id})
        self.client.post(url, data=post_data)

        # Segunda tentativa
        res2 = self.client.get(url, follow=True)
        # Deve redirecionar para o comprovante
        self.assertContains(res2, "Comprovante de Avaliação Docente")

    def test_disposable_pin_token_evaluation(self):
        """
        Garante a votação 100% anônima sem autenticação prévia via token descartável de laboratório.
        """
        pin_code = "SENAI-TEST-PIN-01"
        token_obj = DisposableEvaluationToken.objects.create(
            token=pin_code,
            offering=self.offering,
            cycle=self.cycle,
            is_used=False
        )

        url = reverse('evaluations:evaluate_by_token', kwargs={'token_code': pin_code})
        post_data = {
            f"criterion_{self.crit1.id}": "5",
            f"criterion_{self.crit2.id}": "4",
            "comment": "Voto anônimo direto no laboratório."
        }

        # Cliente deslogado (anônimo)
        self.client.logout()
        res = self.client.post(url, data=post_data, follow=True)
        self.assertEqual(res.status_code, 200)

        # Token deve ser consumido
        token_obj.refresh_from_db()
        self.assertTrue(token_obj.is_used)
        self.assertIsNotNone(token_obj.used_at)
