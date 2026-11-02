from django.shortcuts import render
from django.db.models import Avg, Count
from apps.evaluations.models import EvaluationCycle, EvaluationResponse, EvaluationDimension

def home(request):
    active_cycle = EvaluationCycle.objects.filter(is_active=True).first()
    
    total_responses = EvaluationResponse.objects.count()
    overall_avg_data = EvaluationResponse.objects.aggregate(avg=Avg('overall_score'))
    overall_average = round(overall_avg_data['avg'], 1) if overall_avg_data['avg'] else 4.6

    dimensions = EvaluationDimension.objects.all().order_by('order')

    context = {
        'active_cycle': active_cycle,
        'total_responses': total_responses,
        'overall_average': overall_average,
        'dimensions': dimensions,
    }
    return render(request, 'core/home.html', context)

def about(request):
    return render(request, 'core/about.html')
