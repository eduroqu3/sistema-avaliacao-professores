from django.urls import path
from . import views

app_name = 'evaluations'

urlpatterns = [
    path('minhas/', views.student_evaluation_list, name='student_list'),
    path('avaliar/<int:offering_id>/', views.evaluate_offering, name='evaluate_form'),
    path('comprovante/<str:receipt_hash>/', views.receipt_view, name='receipt_view'),
    path('pin/', views.anonymous_pin_entry, name='anonymous_pin'),
    path('pin/<str:token_code>/', views.evaluate_by_token, name='evaluate_by_token'),
]
