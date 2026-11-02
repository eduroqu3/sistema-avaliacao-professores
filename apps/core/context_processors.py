from django.conf import settings

def global_context(request):
    """
    Context processor para injetar dados institucionais, informações do grupo de alunos,
    e estado de anonimato nas páginas.
    """
    students_team = [
        "Eduardo Vieira Roque",
        "Gustavo Costa Trindade",
        "Guilherme Vilares",
        "Aron Maestá",
        "Diogo Ferrata"
    ]
    return {
        'SCHOOL_NAME': 'Escola SENAI Morvan Figueiredo',
        'COURSE_TITLE': 'Desenvolvimento de Sistemas -- 2025_DEV4_SESI',
        'PROFESSOR_NAME': 'Johnny Braga de Oliveira',
        'STUDENTS_TEAM': students_team,
        'SYSTEM_NAME': 'Avalia SENAI',
        'SYSTEM_VERSION': 'v2.5-enterprise',
        'CURRENT_YEAR': 2025,
    }
