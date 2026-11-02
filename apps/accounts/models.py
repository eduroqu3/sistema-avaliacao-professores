from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrador Geral'),
        ('COORDINATOR', 'Coordenação Pedagógica'),
        ('TEACHER', 'Docente / Professor'),
        ('STUDENT', 'Estudante / Aluno'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='STUDENT',
        verbose_name="Perfil de Acesso",
        help_text="Define o nível de permissão no sistema Avalia SENAI"
    )
    registration_number = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        unique=True,
        verbose_name="RM / Registro Funcional",
        help_text="Registro de Matrícula (Aluno) ou Registro Funcional (Docente)"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Telefone"
    )
    avatar_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Avatar URL"
    )

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ['first_name', 'last_name', 'username']

    def __str__(self):
        full = self.get_full_name()
        return f"{full} ({self.get_role_display()})" if full else f"{self.username} ({self.get_role_display()})"

    @property
    def is_student(self):
        return self.role == 'STUDENT'

    @property
    def is_teacher(self):
        return self.role == 'TEACHER'

    @property
    def is_coordinator(self):
        return self.role == 'COORDINATOR'

    @property
    def is_coordinator_or_admin(self):
        return self.role in ['ADMIN', 'COORDINATOR'] or self.is_superuser
