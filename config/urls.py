from django.contrib import admin
<<<<<<< HEAD
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls', namespace='core')),
    path('conta/', include('apps.accounts.urls', namespace='accounts')),
    path('avaliacoes/', include('apps.evaluations.urls', namespace='evaluations')),
    path('dashboard/', include('apps.dashboards.urls', namespace='dashboards')),
    path('relatorios/', include('apps.reports.urls', namespace='reports')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
=======
from django.urls import path
from django.contrib.auth.views import LogoutView
from avaliacoes import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("avaliar/", views.evaluate, name="evaluate"),
    path("obrigado/", views.thanks, name="thanks"),
    path("entrar/", views.RoleBasedLoginView.as_view(), name="login"),
    path("sair/", LogoutView.as_view(), name="logout"),
    path("painel/", views.dashboard, name="dashboard"),
    path("professores/", views.teachers, name="teachers"),
    path("professores/novo/", views.teacher_create, name="teacher_create"),
    path("professores/<int:pk>/editar/", views.teacher_edit, name="teacher_edit"),
    path("professores/<int:pk>/excluir/", views.teacher_delete, name="teacher_delete"),
    path("disciplinas/", views.subjects, name="subjects"),
    path("disciplinas/nova/", views.subject_create, name="subject_create"),
    path("disciplinas/<int:pk>/editar/", views.subject_edit, name="subject_edit"),
    path("disciplinas/<int:pk>/excluir/", views.subject_delete, name="subject_delete"),
    path("vinculos/", views.assignments, name="assignments"),
    path("vinculos/novo/", views.assignment_create, name="assignment_create"),
    path("vinculos/<int:pk>/editar/", views.assignment_edit, name="assignment_edit"),
    path("vinculos/<int:pk>/excluir/", views.assignment_delete, name="assignment_delete"),
    path("relatorios/", views.reports, name="reports"),
    path("relatorios/exportar.csv", views.export_reports_csv, name="reports_csv"),
    path("coordenacao/alunos/", views.students, name="students"),
    path("coordenacao/alunos/novo/", views.student_create, name="student_create"),
    path("coordenacao/alunos/<int:pk>/editar/", views.student_edit, name="student_edit"),
    path("aluno/", views.student_portal, name="student_portal"),
    path("aluno/historico/", views.student_history, name="student_history"),
    path("aluno/avaliar/<int:assignment_id>/", views.student_evaluate, name="student_evaluate"),
]
>>>>>>> df73181025d511b4cfebb61908aad9e5724a56ef
