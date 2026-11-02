import uuid
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Teacher(models.Model):
    name = models.CharField("Nome do professor", max_length=120)
    email = models.EmailField("E-mail institucional", blank=True)
    active = models.BooleanField("Ativo", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["name"]
        verbose_name = "Professor"
        verbose_name_plural = "Professores"
    def __str__(self): return self.name

class Subject(models.Model):
    name = models.CharField("Nome da disciplina", max_length=120)
    code = models.CharField("Código", max_length=20, blank=True)
    active = models.BooleanField("Ativa", default=True)
    class Meta:
        ordering = ["name"]
        verbose_name = "Disciplina"
        verbose_name_plural = "Disciplinas"
    def __str__(self): return self.name

class TeachingAssignment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT, related_name="assignments")
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="assignments")
    class_name = models.CharField("Turma", max_length=60, blank=True)
    period = models.CharField("Período letivo", max_length=40, blank=True)
    active = models.BooleanField("Ativa", default=True)
    class Meta:
        ordering = ["teacher__name", "subject__name"]
        constraints = [models.UniqueConstraint(fields=["teacher", "subject", "class_name", "period"], name="unique_teaching_assignment")]
        verbose_name = "Vínculo docente"
        verbose_name_plural = "Vínculos docentes"
    def __str__(self): return f"{self.teacher} — {self.subject}" 

class Evaluation(models.Model):
    # UUID opaco usado apenas para recuperar a resposta por meio do recibo criptografado.
    # Não há FK para usuário/aluno nem matrícula no registro de resposta.
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    assignment = models.ForeignKey(TeachingAssignment, on_delete=models.PROTECT, related_name="evaluations")
    clarity = models.PositiveSmallIntegerField("Clareza", validators=[MinValueValidator(1), MaxValueValidator(5)])
    knowledge = models.PositiveSmallIntegerField("Domínio do conteúdo", validators=[MinValueValidator(1), MaxValueValidator(5)])
    engagement = models.PositiveSmallIntegerField("Didática e participação", validators=[MinValueValidator(1), MaxValueValidator(5)])
    respect = models.PositiveSmallIntegerField("Respeito e ambiente", validators=[MinValueValidator(1), MaxValueValidator(5)])
    organization = models.PositiveSmallIntegerField("Organização", validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField("Comentário opcional", blank=True, max_length=1200)
    period_label = models.CharField("Período informado", max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Avaliação anônima"
        verbose_name_plural = "Avaliações anônimas"
    @property
    def average(self):
        return round((self.clarity + self.knowledge + self.engagement + self.respect + self.organization) / 5, 2)
    def __str__(self): return f"Avaliação anônima — {self.assignment}"

class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile")
    display_name = models.CharField("Nome de exibição", max_length=120)
    active = models.BooleanField("Conta ativa", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["display_name"]
        verbose_name = "Conta de aluno"
        verbose_name_plural = "Contas de alunos"
    def __str__(self): return self.display_name

class StudentEvaluationRecord(models.Model):
    """Registro de participação separado da resposta, com o identificador da resposta criptografado.

    A coordenação não dispõe de uma relação direta na interface ou no modelo Evaluation.
    O segredo de criptografia precisa permanecer estável e protegido para permitir edição.
    """
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="evaluation_records")
    assignment = models.ForeignKey(TeachingAssignment, on_delete=models.PROTECT, related_name="participation_records")
    encrypted_evaluation_id = models.TextField("Recibo de resposta criptografado")
    class Meta:
        constraints = [models.UniqueConstraint(fields=["student", "assignment"], name="one_student_evaluation_per_assignment")]
        verbose_name = "Controle de participação do aluno"
        verbose_name_plural = "Controles de participação dos alunos"
    def __str__(self): return "Registro de participação protegido"
