import uuid
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from .models import (
    ClassGroup, ClassOffering, EvaluationCycle, EvaluationDimension,
    EvaluationCriterion, EvaluationReceipt, EvaluationResponse,
    DisposableEvaluationToken
)

@login_required
def student_evaluation_list(request):
    """
    Lista de disciplinas e professores que o aluno matriculado deve avaliar no ciclo vigente.
    """
    if not request.user.is_student and not request.user.is_superuser:
        messages.info(request, "Redirecionado para o painel correspondente ao seu perfil.")
        if request.user.is_teacher:
            return redirect('dashboards:teacher_dashboard')
        return redirect('dashboards:coordination_dashboard')

    active_cycle = EvaluationCycle.objects.filter(is_active=True).first()
    if not active_cycle:
        messages.warning(request, "Não há nenhum ciclo de avaliação institucional ativo no momento.")
        return render(request, 'evaluations/student_evaluations.html', {'offerings_data': [], 'active_cycle': None})

    # Localiza a turma do estudante (ou usa a primeira turma vinculada)
    class_group = request.user.enrolled_classes.first()
    if not class_group:
        # Fallback de segurança para demonstração da turma 2025_DEV4_SESI
        class_group = ClassGroup.objects.filter(name="2025_DEV4_SESI").first()

    offerings = ClassOffering.objects.filter(class_group=class_group, is_active=True).select_related('discipline', 'teacher__user')

    # Identifica quais avaliações já foram concluídas pelo estudante
    completed_receipts = EvaluationReceipt.objects.filter(
        student=request.user,
        cycle=active_cycle
    ).select_related('offering')

    receipts_by_offering = {r.offering_id: r for r in completed_receipts}

    offerings_data = []
    pending_count = 0
    for off in offerings:
        receipt = receipts_by_offering.get(off.id)
        is_completed = receipt is not None
        if not is_completed:
            pending_count += 1

        offerings_data.append({
            'offering': off,
            'is_completed': is_completed,
            'receipt': receipt,
        })

    context = {
        'class_group': class_group,
        'active_cycle': active_cycle,
        'offerings_data': offerings_data,
        'total_offerings': len(offerings_data),
        'pending_count': pending_count,
    }
    return render(request, 'evaluations/student_evaluations.html', context)


@login_required
def evaluate_offering(request, offering_id):
    """
    Formulário interativo de avaliação docente com garantia de desacoplamento criptográfico (Zero-Link).
    """
    offering = get_object_or_404(ClassOffering.objects.select_related('discipline', 'teacher__user', 'class_group'), id=offering_id)
    active_cycle = EvaluationCycle.objects.filter(is_active=True).first()

    if not active_cycle:
        messages.error(request, "Ciclo de avaliação encerrado.")
        return redirect('evaluations:student_list')

    # Verifica se já avaliou
    existing_receipt = EvaluationReceipt.objects.filter(student=request.user, offering=offering, cycle=active_cycle).first()
    if existing_receipt:
        messages.info(request, "Você já concluiu a avaliação desta disciplina. Seu comprovante está disponível abaixo.")
        return redirect('evaluations:receipt_view', receipt_hash=existing_receipt.receipt_hash)

    dimensions = EvaluationDimension.objects.prefetch_related('criteria').order_by('order')
    all_criteria = EvaluationCriterion.objects.filter(dimension__in=dimensions)
    total_criteria = all_criteria.count()

    if request.method == 'POST':
        criteria_scores = {}
        dim_totals = {}
        dim_counts = {}
        missing_answers = False

        for crit in all_criteria:
            val_str = request.POST.get(f'criterion_{crit.id}')
            if not val_str:
                missing_answers = True
                break
            score = int(val_str)
            criteria_scores[str(crit.id)] = score
            
            d_id = str(crit.dimension.id)
            dim_totals[d_id] = dim_totals.get(d_id, 0) + score
            dim_counts[d_id] = dim_counts.get(d_id, 0) + 1

        if missing_answers:
            messages.error(request, "Por favor, responda a todos os critérios antes de enviar a avaliação.")
            return render(request, 'evaluations/evaluation_form.html', {
                'offering': offering,
                'active_cycle': active_cycle,
                'dimensions': dimensions,
                'total_criteria': total_criteria,
            })

        # Calcula a média geral e as médias por dimensão
        overall_avg = round(sum(criteria_scores.values()) / len(criteria_scores), 2)
        dim_scores = {d_id: round(dim_totals[d_id] / dim_counts[d_id], 2) for d_id in dim_totals}

        comment_text = request.POST.get('comment', '').strip()
        moderation_status = 'PENDING' if comment_text else 'APPROVED'

        # Transação Atômica: desacoplamento físico absoluto
        with transaction.atomic():
            # 1. Registra o recibo do estudante (SEM link com as notas)
            receipt_hash = EvaluationReceipt.generate_receipt_token(request.user.id, offering.id, active_cycle.id)
            receipt = EvaluationReceipt.objects.create(
                student=request.user,
                offering=offering,
                cycle=active_cycle,
                receipt_hash=receipt_hash
            )

            # 2. Registra as notas anonimizadas (SEM student_id, nem IP)
            EvaluationResponse.objects.create(
                offering=offering,
                cycle=active_cycle,
                overall_score=Decimal(str(overall_avg)),
                criteria_scores=criteria_scores,
                dimension_scores=dim_scores,
                comment=comment_text if comment_text else None,
                moderation_status=moderation_status
            )

        messages.success(request, "Sua avaliação foi registrada com 100% de sigilo e anonimato garantidos pelo SENAI!")
        return redirect('evaluations:receipt_view', receipt_hash=receipt.receipt_hash)

    context = {
        'offering': offering,
        'active_cycle': active_cycle,
        'dimensions': dimensions,
        'total_criteria': total_criteria,
    }
    return render(request, 'evaluations/evaluation_form.html', context)


@login_required
def receipt_view(request, receipt_hash):
    """
    Exibição do comprovante criptográfico de realização da avaliação.
    """
    receipt = get_object_or_404(
        EvaluationReceipt.objects.select_related('offering__discipline', 'offering__teacher__user', 'offering__class_group__course', 'cycle'),
        receipt_hash=receipt_hash
    )
    
    # Valida permissão de acesso ao comprovante
    if receipt.student != request.user and not request.user.is_coordinator_or_admin:
        messages.error(request, "Você não tem autorização para visualizar este comprovante.")
        return redirect('evaluations:student_list')

    return render(request, 'evaluations/receipt.html', {'receipt': receipt})


def anonymous_pin_entry(request):
    """
    Ponto de entrada para votação anônima via PIN/Token descartável em laboratório.
    """
    available_tokens = DisposableEvaluationToken.objects.filter(is_used=False).select_related('offering__discipline')[:5]

    if request.method == 'POST':
        pin_code = request.POST.get('pin_token', '').strip().upper()
        token_obj = DisposableEvaluationToken.objects.filter(token=pin_code, is_used=False).first()

        if token_obj:
            return redirect('evaluations:evaluate_by_token', token_code=token_obj.token)
        else:
            messages.error(request, "PIN inválido ou já utilizado. Verifique o código e tente novamente.")

    return render(request, 'evaluations/anonymous_pin_entry.html', {'available_tokens': available_tokens})


def evaluate_by_token(request, token_code):
    """
    Questionário de avaliação 100% anônimo consumido via PIN de uso único (sem login).
    """
    token_obj = get_object_or_404(
        DisposableEvaluationToken.objects.select_related('offering__discipline', 'offering__teacher__user', 'offering__class_group', 'cycle'),
        token=token_code,
        is_used=False
    )

    dimensions = EvaluationDimension.objects.prefetch_related('criteria').order_by('order')
    all_criteria = EvaluationCriterion.objects.filter(dimension__in=dimensions)
    total_criteria = all_criteria.count()

    if request.method == 'POST':
        criteria_scores = {}
        dim_totals = {}
        dim_counts = {}
        missing = False

        for crit in all_criteria:
            val_str = request.POST.get(f'criterion_{crit.id}')
            if not val_str:
                missing = True
                break
            score = int(val_str)
            criteria_scores[str(crit.id)] = score
            d_id = str(crit.dimension.id)
            dim_totals[d_id] = dim_totals.get(d_id, 0) + score
            dim_counts[d_id] = dim_counts.get(d_id, 0) + 1

        if missing:
            messages.error(request, "Por favor, responda a todos os critérios antes de enviar.")
            return render(request, 'evaluations/evaluation_form.html', {
                'offering': token_obj.offering,
                'active_cycle': token_obj.cycle,
                'dimensions': dimensions,
                'total_criteria': total_criteria,
            })

        overall_avg = round(sum(criteria_scores.values()) / len(criteria_scores), 2)
        dim_scores = {d_id: round(dim_totals[d_id] / dim_counts[d_id], 2) for d_id in dim_totals}
        comment_text = request.POST.get('comment', '').strip()
        moderation_status = 'PENDING' if comment_text else 'APPROVED'

        with transaction.atomic():
            # Invalida o token para impedir reuso
            token_obj.is_used = True
            token_obj.used_at = timezone.now()
            token_obj.save()

            # Grava a resposta anônima
            EvaluationResponse.objects.create(
                offering=token_obj.offering,
                cycle=token_obj.cycle,
                overall_score=Decimal(str(overall_avg)),
                criteria_scores=criteria_scores,
                dimension_scores=dim_scores,
                comment=comment_text if comment_text else None,
                moderation_status=moderation_status
            )

        messages.success(request, f"Avaliação registrada com sucesso pelo PIN {token_code}! Obrigado pela sua colaboração.")
        return redirect('core:home')

    return render(request, 'evaluations/evaluation_form.html', {
        'offering': token_obj.offering,
        'active_cycle': token_obj.cycle,
        'dimensions': dimensions,
        'total_criteria': total_criteria,
    })
