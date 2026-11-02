import uuid
import hashlib
from django.db import models
from django.conf import settings
from django.utils import timezone

class Course(models.Model):
    MODALITY_CHOICES = [
        ('PRESENTIAL', 'Presencial'),
        ('SEMI', 'Semipresencial'),
        ('EAD', 'Ensino a Distância'),
    ]

    name = models.CharField(max_length=150, verbose_name="Nome do Curso")
    code = models.CharField(max_length=30, unique=True, verbose_name="Código do Curso")
    modality = models.CharField(max_length=20, choices=MODALITY_CHOICES, default='PRESENTIAL', verbose_name="Modalidade")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class TeacherProfile(models.Model):
    TITLE_CHOICES = [
        ('GRAD', 'Graduado'),
        ('ESP', 'Especialista'),
        ('MEST', 'Mestre'),
        ('DOUT', 'Doutor'),
        ('NOT', 'Notório Saber / Instrutor Especialista'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
        limit_choices_to={'role': 'TEACHER'},
        verbose_name="Conta de Usuário"
    )
    academic_title = models.CharField(max_length=10, choices=TITLE_CHOICES, default='ESP', verbose_name="Titulação")
    department = models.CharField(max_length=100, default='Tecnologia da Informação', verbose_name="Área / Departamento")
    bio = models.TextField(blank=True, verbose_name="Biografia / Especialidades")

    class Meta:
        verbose_name = "Perfil de Docente"
        verbose_name_plural = "Perfis de Docentes"
        ordering = ['user__first_name', 'user__last_name']

    def __str__(self):
        return f"{self.get_academic_title_display()} {self.user.get_full_name() or self.user.username}"


class Discipline(models.Model):
    name = models.CharField(max_length=150, verbose_name="Nome da Disciplina / Unidade Curricular")
    code = models.CharField(max_length=30, unique=True, verbose_name="Código da UC")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='disciplines', verbose_name="Curso")
    workload_hours = models.PositiveIntegerField(default=80, verbose_name="Carga Horária (horas)")
    description = models.TextField(blank=True, verbose_name="Ementa / Descrição")

    class Meta:
        verbose_name = "Disciplina"
        verbose_name_plural = "Disciplinas"
        ordering = ['course', 'name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class ClassGroup(models.Model):
    SHIFT_CHOICES = [
        ('MANHA', 'Manhã'),
        ('TARDE', 'Tarde'),
        ('NOITE', 'Noite'),
        ('INTEGRAL', 'Integral'),
    ]

    name = models.CharField(max_length=100, verbose_name="Nome da Turma (Ex: 2025_DEV4_SESI)")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='class_groups', verbose_name="Curso")
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES, default='MANHA', verbose_name="Turno")
    year = models.PositiveIntegerField(default=2025, verbose_name="Ano")
    semester = models.PositiveSmallIntegerField(default=1, verbose_name="Semestre")
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='enrolled_classes',
        limit_choices_to={'role': 'STUDENT'},
        verbose_name="Alunos Matriculados"
    )

    class Meta:
        verbose_name = "Turma"
        verbose_name_plural = "Turmas"
        ordering = ['-year', 'semester', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_shift_display()})"


class ClassOffering(models.Model):
    """
    Atribuição de uma disciplina a um professor e a uma turma em um período letivo.
    """
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE, related_name='offerings', verbose_name="Disciplina")
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='offerings', verbose_name="Docente")
    class_group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE, related_name='offerings', verbose_name="Turma")
    academic_period = models.CharField(max_length=20, default='2025/1', verbose_name="Período Letivo (ex: 2025/1)")
    is_active = models.BooleanField(default=True, verbose_name="Ativa")

    class Meta:
        verbose_name = "Oferta de Disciplina / Atribuição"
        verbose_name_plural = "Ofertas de Disciplinas"
        unique_together = ('discipline', 'teacher', 'class_group', 'academic_period')
        ordering = ['class_group', 'discipline']

    def __str__(self):
        return f"{self.discipline.name} - {self.teacher.user.get_full_name()} ({self.class_group.name})"


class EvaluationCycle(models.Model):
    title = models.CharField(max_length=150, verbose_name="Título do Ciclo (Ex: Avaliação Docente 2025/1)")
    description = models.TextField(blank=True, verbose_name="Orientações aos Alunos")
    academic_period = models.CharField(max_length=20, default='2025/1', verbose_name="Período de Referência")
    start_date = models.DateField(verbose_name="Data de Início")
    end_date = models.DateField(verbose_name="Data de Término")
    is_active = models.BooleanField(default=True, verbose_name="Ciclo Aberto para Respostas")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ciclo de Avaliação"
        verbose_name_plural = "Ciclos de Avaliação"
        ordering = ['-start_date']

    def __str__(self):
        status = "ATIVO" if self.is_active else "ENCERRADO"
        return f"{self.title} [{status}]"

    def is_currently_open(self):
        today = timezone.localdate()
        return self.is_active and (self.start_date <= today <= self.end_date)


class EvaluationDimension(models.Model):
    """
    Dimensão pedagógica: Didática, Domínio de Conteúdo, Assiduidade, Postura, Feedback.
    """
    name = models.CharField(max_length=100, verbose_name="Nome da Dimensão")
    description = models.TextField(blank=True, verbose_name="Descrição do Foco Avaliativo")
    weight = models.DecimalField(max_digits=3, decimal_places=2, default=1.00, verbose_name="Peso Relativo")
    order = models.PositiveSmallIntegerField(default=1, verbose_name="Ordem de Apresentação")

    class Meta:
        verbose_name = "Dimensão Avaliativa"
        verbose_name_plural = "Dimensões Avaliativas"
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.order}. {self.name}"


class EvaluationCriterion(models.Model):
    """
    Critério ou pergunta específica dentro de uma dimensão.
    """
    dimension = models.ForeignKey(EvaluationDimension, on_delete=models.CASCADE, related_name='criteria', verbose_name="Dimensão")
    title = models.CharField(max_length=200, verbose_name="Enunciado do Critério")
    help_text = models.CharField(max_length=250, blank=True, verbose_name="Explicação / Exemplo para o aluno")
    order = models.PositiveSmallIntegerField(default=1, verbose_name="Ordem")
    min_score = models.PositiveSmallIntegerField(default=1, verbose_name="Nota Mínima")
    max_score = models.PositiveSmallIntegerField(default=5, verbose_name="Nota Máxima")

    class Meta:
        verbose_name = "Critério de Avaliação"
        verbose_name_plural = "Critérios de Avaliação"
        ordering = ['dimension__order', 'order']

    def __str__(self):
        return f"[{self.dimension.name}] {self.title}"


# ==============================================================================
# PROTOCOLO DE ANONIMATO CRIPTOGRÁFICO DESACOPLADO (Zero-Link Anonymity)
# ==============================================================================

class EvaluationReceipt(models.Model):
    """
    TABELA DE COMPROVANTE DE PARTICIPAÇÃO:
    Registra QUE o aluno já votou nesta oferta no ciclo ativo, evitando votos duplicados.
    
    GARANTIA DE ANONIMATO:
    - Esta tabela armazena apenas o id do aluno e a oferta.
    - NÃO POSSUI NENHUMA CHAVE ESTRANGEIRA, ID OU PONTEIRO PARA A TABELA 'EvaluationResponse'.
    - Nem o administrador nem o banco de dados conseguem correlacionar as notas ou comentários ao aluno.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='evaluation_receipts',
        limit_choices_to={'role': 'STUDENT'},
        verbose_name="Estudante"
    )
    offering = models.ForeignKey(ClassOffering, on_delete=models.CASCADE, related_name='receipts', verbose_name="Oferta da Disciplina")
    cycle = models.ForeignKey(EvaluationCycle, on_delete=models.CASCADE, related_name='receipts', verbose_name="Ciclo de Avaliação")
    receipt_hash = models.CharField(max_length=64, unique=True, verbose_name="Hash do Comprovante (Criptográfico)")
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Conclusão")

    class Meta:
        verbose_name = "Comprovante de Participação"
        verbose_name_plural = "Comprovantes de Participação"
        unique_together = ('student', 'offering', 'cycle')
        ordering = ['-completed_at']

    def __str__(self):
        return f"Recibo {self.receipt_hash[:12]}... (Aluno ID: {self.student_id})"

    @staticmethod
    def generate_receipt_token(student_id, offering_id, cycle_id):
        salt = settings.SECRET_KEY
        raw = f"{student_id}:{offering_id}:{cycle_id}:{timezone.now().timestamp()}:{uuid.uuid4()}:{salt}"
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()


class EvaluationResponse(models.Model):
    """
    TABELA DE RESPOSTAS ANÔNIMAS:
    Armazena as notas e opiniões pedagógicas sobre o professor/disciplina.
    
    GARANTIA DE ANONIMATO:
    - NÃO CONTÉM student_id, nem IP, nem User-Agent, nem chave para EvaluationReceipt.
    - O desacoplamento físico e lógico impede qualquer rastreamento reverso de autoria.
    """
    MODERATION_CHOICES = [
        ('PENDING', 'Em Moderação'),
        ('APPROVED', 'Aprovado para Visualização'),
        ('REJECTED', 'Rejeitado por Violação das Diretrizes'),
    ]

    offering = models.ForeignKey(ClassOffering, on_delete=models.CASCADE, related_name='anonymous_responses', verbose_name="Oferta Avaliada")
    cycle = models.ForeignKey(EvaluationCycle, on_delete=models.CASCADE, related_name='anonymous_responses', verbose_name="Ciclo")
    
    # Médias agregadas da resposta
    overall_score = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Média Geral (1.00 a 5.00)")
    
    # Detalhamento de notas por critério em formato JSON estruturado: {"criterion_id": score, ...}
    criteria_scores = models.JSONField(default=dict, verbose_name="Notas por Critério (JSON)")
    
    # Médias consolidadas por dimensão em formato JSON: {"dimension_id": score, ...}
    dimension_scores = models.JSONField(default=dict, verbose_name="Médias por Dimensão (JSON)")
    
    # Comentário qualitativo opcional
    comment = models.TextField(blank=True, null=True, verbose_name="Comentário Opcional / Sugestões")
    
    # Sistema de Moderação Pedagógica
    moderation_status = models.CharField(
        max_length=20,
        choices=MODERATION_CHOICES,
        default='APPROVED',
        verbose_name="Status de Moderação"
    )
    moderation_notes = models.TextField(blank=True, verbose_name="Parecer da Moderação")
    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='moderated_feedbacks',
        verbose_name="Moderador Responsável"
    )
    moderated_at = models.DateTimeField(null=True, blank=True, verbose_name="Data da Moderação")

    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Envio")

    class Meta:
        verbose_name = "Resposta Anônima de Avaliação"
        verbose_name_plural = "Respostas Anônimas de Avaliação"
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Resposta Anônima #{self.id} - Oferta: {self.offering} - Média: {self.overall_score}"


class DisposableEvaluationToken(models.Model):
    """
    MODALIDADE DE NAVEGAÇÃO TOTALMENTE ANÔNIMA VIA TOKEN/PIN DESCARTÁVEL:
    Permite que a coordenação gere bilhetes/PINs únicos para aplicação em laboratório
    sem que o aluno precise sequer efetuar login na máquina.
    """
    token = models.CharField(max_length=64, unique=True, verbose_name="Token de Acesso Único / PIN")
    offering = models.ForeignKey(ClassOffering, on_delete=models.CASCADE, related_name='disposable_tokens', verbose_name="Oferta Alvo")
    cycle = models.ForeignKey(EvaluationCycle, on_delete=models.CASCADE, related_name='disposable_tokens', verbose_name="Ciclo Alvo")
    is_used = models.BooleanField(default=False, verbose_name="Já Utilizado?")
    used_at = models.DateTimeField(null=True, blank=True, verbose_name="Data de Consumo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        verbose_name = "Token Descartável de Avaliação Anônima"
        verbose_name_plural = "Tokens Descartáveis de Avaliação Anônima"
        ordering = ['-created_at']

    def __str__(self):
        status = "UTILIZADO" if self.is_used else "DISPONÍVEL"
        return f"PIN [{self.token}] - {self.offering.discipline.name} ({status})"

    @staticmethod
    def generate_pin(prefix="SENAI"):
        raw_code = uuid.uuid4().hex[:8].upper()
        return f"{prefix}-{raw_code[:4]}-{raw_code[4:]}"
