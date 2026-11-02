import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count
from django.utils import timezone
from apps.evaluations.models import (
    TeacherProfile, ClassOffering, EvaluationCycle,
    EvaluationDimension, EvaluationResponse
)

@login_required
def teacher_dashboard(request, teacher_id=None):
    """
    Dashboard individual do docente com métricas pedagógicas, radar de competências e distribuição.
    """
    if teacher_id and request.user.is_coordinator_or_admin:
        teacher_profile = get_object_or_404(TeacherProfile.objects.select_related('user'), id=teacher_id)
    else:
        if not request.user.is_teacher and not hasattr(request.user, 'teacher_profile'):
            messages.info(request, "Acesso restrito ao perfil docente.")
            return redirect('dashboards:coordination_dashboard')
        teacher_profile = request.user.teacher_profile

    active_cycle = EvaluationCycle.objects.filter(is_active=True).first()
    offerings = ClassOffering.objects.filter(teacher=teacher_profile)

    responses = EvaluationResponse.objects.filter(offering__in=offerings)
    if active_cycle:
        responses = responses.filter(cycle=active_cycle)

    total_responses = responses.count()

    # Média Geral
    avg_data = responses.aggregate(avg=Avg('overall_score'))
    overall_avg = avg_data['avg'] or Decimal('0.00')

    # Dimensões e Radar Chart
    dimensions = EvaluationDimension.objects.all().order_by('order')
    radar_labels = []
    radar_scores = []
    dimension_averages = []

    for dim in dimensions:
        dim_key = str(dim.id)
        scores_for_dim = []
        for r in responses:
            if isinstance(r.dimension_scores, dict) and dim_key in r.dimension_scores:
                scores_for_dim.append(float(r.dimension_scores[dim_key]))
        
        dim_avg = round(sum(scores_for_dim) / len(scores_for_dim), 2) if scores_for_dim else float(overall_avg)
        radar_labels.append(dim.name)
        radar_scores.append(dim_avg)
        dimension_averages.append({
            'order': dim.order,
            'name': dim.name,
            'description': dim.description,
            'avg_score': dim_avg,
            'percent': int((dim_avg / 5.0) * 100),
        })

    # Ponto mais forte e ponto de atenção
    sorted_dims = sorted(dimension_averages, key=lambda x: x['avg_score'], reverse=True)
    best_dimension = {'name': sorted_dims[0]['name'], 'score': sorted_dims[0]['avg_score']} if sorted_dims else None
    attention_dimension = {'name': sorted_dims[-1]['name'], 'score': sorted_dims[-1]['avg_score']} if sorted_dims else None

    # Distribuição de Notas (1 a 5 estrelas)
    distribution = [0, 0, 0, 0, 0]
    for r in responses:
        rounded_val = min(5, max(1, round(float(r.overall_score))))
        distribution[rounded_val - 1] += 1

    # Comentários Qualitativos Aprovados
    approved_comments = responses.filter(
        moderation_status='APPROVED'
    ).exclude(comment__isnull=True).exclude(comment='').select_related('offering__discipline', 'offering__class_group')

    context = {
        'teacher_profile': teacher_profile,
        'active_cycle': active_cycle,
        'total_responses': total_responses,
        'overall_avg': overall_avg,
        'best_dimension': best_dimension,
        'attention_dimension': attention_dimension,
        'dimension_averages': dimension_averages,
        'radar_labels_json': json.dumps(radar_labels),
        'radar_scores_json': json.dumps(radar_scores),
        'distribution_json': json.dumps(distribution),
        'approved_comments': approved_comments,
    }
    return render(request, 'dashboards/teacher_dashboard.html', context)


@login_required
def coordination_dashboard(request):
    """
    Dashboard institucional da coordenação com comparativo de docentes, ranking e alertas.
    """
    if not request.user.is_coordinator_or_admin:
        messages.error(request, "Acesso restrito à Coordenação e Administração.")
        return redirect('core:home')

    active_cycle = EvaluationCycle.objects.filter(is_active=True).first()

    all_responses = EvaluationResponse.objects.all()
    if active_cycle:
        all_responses = all_responses.filter(cycle=active_cycle)

    total_evaluations_count = all_responses.count()
    school_avg_data = all_responses.aggregate(avg=Avg('overall_score'))
    overall_school_avg = school_avg_data['avg'] or Decimal('0.00')

    # Dados comparativos de professores
    teachers = TeacherProfile.objects.select_related('user').all()
    teachers_data = []
    comparison_teachers = []
    comparison_averages = []

    for t in teachers:
        t_offerings = ClassOffering.objects.filter(teacher=t)
        t_resp = all_responses.filter(offering__in=t_offerings)
        t_avg_data = t_resp.aggregate(avg=Avg('overall_score'))
        t_avg = round(float(t_avg_data['avg']), 2) if t_avg_data['avg'] else 0.0

        teachers_data.append({
            'profile': t,
            'offerings': t_offerings.select_related('discipline', 'class_group'),
            'response_count': t_resp.count(),
            'average_score': t_avg,
        })

    # Ordena pelo ranking de média decrescente
    teachers_data.sort(key=lambda x: x['average_score'], reverse=True)

    for td in teachers_data:
        comparison_teachers.append(td['profile'].user.get_full_name() or td['profile'].user.username)
        comparison_averages.append(td['average_score'])

    pending_moderation_count = EvaluationResponse.objects.filter(
        moderation_status='PENDING'
    ).exclude(comment__isnull=True).exclude(comment='').count()

    context = {
        'active_cycle': active_cycle,
        'overall_school_avg': overall_school_avg,
        'total_evaluations_count': total_evaluations_count,
        'teachers_data': teachers_data,
        'pending_moderation_count': pending_moderation_count,
        'comparison_teachers_json': json.dumps(comparison_teachers),
        'comparison_averages_json': json.dumps(comparison_averages),
    }
    return render(request, 'dashboards/coordination_dashboard.html', context)


@login_required
def moderation_view(request):
    """
    Fila de moderação pedagógica para comentários livres dos alunos.
    """
    if not request.user.is_coordinator_or_admin:
        messages.error(request, "Acesso restrito à Coordenação.")
        return redirect('core:home')

    current_filter = request.GET.get('status', 'PENDING').upper()

    base_query = EvaluationResponse.objects.exclude(comment__isnull=True).exclude(comment='').select_related(
        'offering__teacher__user', 'offering__discipline', 'offering__class_group', 'moderated_by'
    )

    total_count = base_query.count()
    pending_count = base_query.filter(moderation_status='PENDING').count()
    approved_count = base_query.filter(moderation_status='APPROVED').count()
    rejected_count = base_query.filter(moderation_status='REJECTED').count()

    if current_filter == 'PENDING':
        responses = base_query.filter(moderation_status='PENDING')
    elif current_filter == 'APPROVED':
        responses = base_query.filter(moderation_status='APPROVED')
    elif current_filter == 'REJECTED':
        responses = base_query.filter(moderation_status='REJECTED')
    else:
        responses = base_query

    context = {
        'responses': responses,
        'current_filter': current_filter,
        'total_count': total_count,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    }
    return render(request, 'dashboards/moderation.html', context)


@login_required
def moderation_action(request, response_id):
    """
    Aprova ou rejeita um comentário na moderação pedagógica.
    """
    if not request.user.is_coordinator_or_admin:
        messages.error(request, "Acesso negado.")
        return redirect('core:home')

    response_obj = get_object_or_404(EvaluationResponse, id=response_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '').strip()

        if action == 'APPROVE':
            response_obj.moderation_status = 'APPROVED'
            response_obj.moderation_notes = notes or "Aprovado para exibição no painel docente."
            messages.success(request, f"Comentário #{response_obj.id} aprovado com sucesso!")
        elif action == 'REJECT':
            response_obj.moderation_status = 'REJECTED'
            response_obj.moderation_notes = notes or "Rejeitado pela moderação pedagógica institucional."
            messages.warning(request, f"Comentário #{response_obj.id} rejeitado.")

        response_obj.moderated_by = request.user
        response_obj.moderated_at = timezone.now()
        response_obj.save()

    return redirect('dashboards:moderation')
