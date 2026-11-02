from django.urls import path
from . import views

app_name = 'dashboards'

urlpatterns = [
    path('docente/', views.teacher_dashboard, name='teacher_dashboard'),
    path('docente/<int:teacher_id>/', views.teacher_dashboard, name='teacher_detail'),
    path('coordenacao/', views.coordination_dashboard, name='coordination_dashboard'),
    path('moderacao/', views.moderation_view, name='moderation'),
    path('moderacao/acao/<int:response_id>/', views.moderation_action, name='moderation_action'),
]
