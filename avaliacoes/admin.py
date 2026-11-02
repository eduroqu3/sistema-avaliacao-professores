from django.contrib import admin
from .models import Teacher, Subject, TeachingAssignment, StudentProfile

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "active")
    search_fields = ("name", "email")
    list_filter = ("active",)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "active")
    search_fields = ("name", "code")
    list_filter = ("active",)

@admin.register(TeachingAssignment)
class TeachingAssignmentAdmin(admin.ModelAdmin):
    list_display = ("teacher", "subject", "class_name", "period", "active")
    list_filter = ("active", "period", "subject")

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "user", "active", "created_at")
    search_fields = ("display_name", "user__username")
    list_filter = ("active",)

# Intencionalmente não registramos Evaluation nem StudentEvaluationRecord no admin.
# Isso reduz a exposição de respostas individuais e da tabela que controla participação.
