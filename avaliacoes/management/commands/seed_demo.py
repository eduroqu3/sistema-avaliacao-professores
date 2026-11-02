from django.core.management.base import BaseCommand
from avaliacoes.models import Teacher, Subject, TeachingAssignment

class Command(BaseCommand):
    help = "Cria dados demonstrativos para testar o sistema."
    def handle(self, *args, **options):
        demo = [
            ("Ana Ribeiro", "Matemática Aplicada", "MAT-01", "DEV4", "2026"),
            ("Carlos Mendes", "Lógica de Programação", "LOG-01", "DEV4", "2026"),
            ("Mariana Souza", "Banco de Dados", "BD-01", "DEV4", "2026"),
        ]
        for teacher_name, subject_name, code, class_name, period in demo:
            teacher, _ = Teacher.objects.get_or_create(name=teacher_name, defaults={"email": ""})
            subject, _ = Subject.objects.get_or_create(name=subject_name, defaults={"code": code})
            TeachingAssignment.objects.get_or_create(teacher=teacher, subject=subject, class_name=class_name, period=period)
        self.stdout.write(self.style.SUCCESS("Dados demonstrativos criados."))
