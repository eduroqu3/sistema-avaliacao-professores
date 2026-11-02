from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import Teacher, Subject, TeachingAssignment, Evaluation, StudentProfile, StudentEvaluationRecord

User = get_user_model()

class StudentEvaluationFlowTests(TestCase):
    def setUp(self):
        teacher = Teacher.objects.create(name="Docente Teste")
        subject = Subject.objects.create(name="Disciplina Teste")
        self.assignment = TeachingAssignment.objects.create(teacher=teacher, subject=subject, class_name="DEV4", period="2026")
        self.student = User.objects.create_user(username="aluno-teste", password="SenhaForte-123")
        StudentProfile.objects.create(user=self.student, display_name="Aluno Teste")
        self.coordinator = User.objects.create_superuser(username="coord", email="coord@example.com", password="SenhaForte-123")

    def payload(self, **extra):
        data = {"clarity": "4", "knowledge": "4", "engagement": "5", "respect": "5", "organization": "4", "comment": "Sugestão construtiva"}
        data.update(extra)
        return data

    def test_home_loads(self):
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)

    def test_anonymous_cannot_submit_evaluation(self):
        response = self.client.get(reverse("evaluate"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_student_can_submit_once_per_assignment_and_edit_existing(self):
        self.client.login(username="aluno-teste", password="SenhaForte-123")
        url = reverse("student_evaluate", args=[self.assignment.pk])
        response = self.client.post(url, self.payload())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Evaluation.objects.count(), 1)
        self.assertEqual(StudentEvaluationRecord.objects.filter(student=self.student, assignment=self.assignment).count(), 1)
        response = self.client.post(url, self.payload(clarity="2", comment="Texto atualizado"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Evaluation.objects.count(), 1)
        evaluation = Evaluation.objects.get()
        self.assertEqual(evaluation.clarity, 2)
        self.assertEqual(evaluation.comment, "Texto atualizado")

    def test_student_history_is_private(self):
        self.client.login(username="aluno-teste", password="SenhaForte-123")
        self.assertEqual(self.client.get(reverse("student_history")).status_code, 200)

    def test_student_cannot_open_coordinator_dashboard(self):
        self.client.login(username="aluno-teste", password="SenhaForte-123")
        response = self.client.get(reverse("dashboard"))
        self.assertNotEqual(response.status_code, 200)

    def test_coordinator_can_manage_student_accounts(self):
        self.client.login(username="coord", password="SenhaForte-123")
        self.assertEqual(self.client.get(reverse("students")).status_code, 200)


    def test_coordinator_csv_export_is_aggregated(self):
        self.client.login(username="coord", password="SenhaForte-123")
        for _ in range(3):
            Evaluation.objects.create(assignment=self.assignment, clarity=4, knowledge=4, engagement=4, respect=4, organization=4)
        response = self.client.get(reverse("reports_csv"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response["Content-Type"])
        self.assertIn("Professor", response.content.decode("utf-8-sig"))

    def test_evaluation_has_no_direct_student_foreign_key(self):
        evaluation = Evaluation.objects.create(assignment=self.assignment, clarity=4, knowledge=4, engagement=5, respect=5, organization=4)
        self.assertFalse(hasattr(evaluation, "student"))
