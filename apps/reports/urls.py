from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_index, name='index'),
    path('imprimir/<int:offering_id>/', views.printable_report, name='printable_report'),
    path('exportar/excel/<int:cycle_id>/', views.export_excel, name='export_excel'),
]
