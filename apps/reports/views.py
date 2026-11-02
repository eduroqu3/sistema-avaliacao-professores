import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Avg, Count
from apps.evaluations.models import (
    ClassOffering, EvaluationCycle, EvaluationDimension, EvaluationResponse
)

@login_required
def report_index(request):
    """
    Central de emissão de relatórios e análises comparativas.
    """
    if not request.user.is_coordinator_or_admin:
        messages.error(request, "Acesso restrito à Coordenação.")
        return redirect('core:home')

    active_cycle = EvaluationCycle.objects.filter(is_active=True).first()
    offerings = ClassOffering.objects.select_related('teacher__user', 'discipline', 'class_group').all()

    offerings_summary = []
    for off in offerings:
        resp = EvaluationResponse.objects.filter(offering=off)
        if active_cycle:
            resp = resp.filter(cycle=active_cycle)

        avg_data = resp.aggregate(avg=Avg('overall_score'))
        avg_score = avg_data['avg'] or 0.0

        offerings_summary.append({
            'id': off.id,
            'teacher': off.teacher,
            'discipline': off.discipline,
            'class_group': off.class_group,
            'response_count': resp.count(),
            'avg_score': avg_score,
        })

    context = {
        'active_cycle': active_cycle,
        'offerings_summary': offerings_summary,
    }
    return render(request, 'reports/index.html', context)


@login_required
def printable_report(request, offering_id):
    """
    Relatório institucional em formato A4 para impressão ou salvamento em PDF.
    """
    offering = get_object_or_404(
        ClassOffering.objects.select_related('teacher__user', 'discipline', 'class_group__course'),
        id=offering_id
    )
    cycle = EvaluationCycle.objects.filter(is_active=True).first()

    responses = EvaluationResponse.objects.filter(offering=offering)
    if cycle:
        responses = responses.filter(cycle=cycle)

    response_count = responses.count()
    avg_data = responses.aggregate(avg=Avg('overall_score'))
    avg_score = avg_data['avg'] or 0.0

    # Total de alunos matriculados na turma
    enrolled_count = offering.class_group.students.count() or 5
    participation_rate = round((response_count / enrolled_count) * 100) if enrolled_count > 0 else 100

    # Dimensões
    dimensions = EvaluationDimension.objects.all().order_by('order')
    dimension_stats = []

    for dim in dimensions:
        dim_key = str(dim.id)
        scores = []
        for r in responses:
            if isinstance(r.dimension_scores, dict) and dim_key in r.dimension_scores:
                scores.append(float(r.dimension_scores[dim_key]))

        d_avg = round(sum(scores) / len(scores), 2) if scores else float(avg_score)
        dimension_stats.append({
            'name': dim.name,
            'description': dim.description,
            'avg_score': d_avg,
            'percent': int((d_avg / 5.0) * 100),
        })

    approved_comments = responses.filter(moderation_status='APPROVED').exclude(comment__isnull=True).exclude(comment='')

    context = {
        'offering': offering,
        'cycle': cycle,
        'response_count': response_count,
        'enrolled_count': enrolled_count,
        'participation_rate': participation_rate,
        'avg_score': avg_score,
        'dimension_stats': dimension_stats,
        'approved_comments': approved_comments,
    }
    return render(request, 'reports/printable_report.html', context)


@login_required
def export_excel(request, cycle_id):
    """
    Gera e faz o download da planilha Excel (.xlsx) institucional com dados consolidados.
    """
    if not request.user.is_coordinator_or_admin:
        messages.error(request, "Acesso restrito.")
        return redirect('core:home')

    cycle = get_object_or_404(EvaluationCycle, id=cycle_id)

    wb = openpyxl.Workbook()
    # Estilos SENAI
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    senai_red_fill = PatternFill(start_color="DC2626", end_color="DC2626", fill_type="solid")
    title_font = Font(name="Calibri", size=14, bold=True)
    border_thin = Border(
        left=Side(style='thin', color='E2E8F0'),
        right=Side(style='thin', color='E2E8F0'),
        top=Side(style='thin', color='E2E8F0'),
        bottom=Side(style='thin', color='E2E8F0')
    )

    # -------------------------------------------------------------
    # ABA 1: RESUMO GERAL INSTITUCIONAL
    # -------------------------------------------------------------
    ws1 = wb.active
    ws1.title = "Resumo Geral"

    ws1.append(["ESCOLA SENAI MORVAN FIGUEIREDO - AVALIA SENAI"])
    ws1.append([f"RELATÓRIO INSTITUCIONAL DO CICLO: {cycle.title}"])
    ws1.append([f"Período de Referência: {cycle.academic_period} | Turma: 2025_DEV4_SESI"])
    ws1.append([])

    ws1["A1"].font = title_font
    ws1["A2"].font = Font(size=12, bold=True, color="DC2626")

    responses = EvaluationResponse.objects.filter(cycle=cycle)
    total_evals = responses.count()
    school_avg = responses.aggregate(avg=Avg('overall_score'))['avg'] or 0.0

    ws1.append(["Indicador Institucional", "Valor Consolidado"])
    ws1.append(["Total de Avaliações Submetidas (100% Anônimas)", total_evals])
    ws1.append(["Média Geral de Satisfação Docente (1 a 5)", round(float(school_avg), 2)])
    ws1.append(["Protocolo de Anonimato", "Zero-Link Criptográfico"])

    for row in range(5, 9):
        ws1[f"A{row}"].border = border_thin
        ws1[f"B{row}"].border = border_thin
    ws1["A5"].fill = header_fill
    ws1["A5"].font = header_font
    ws1["B5"].fill = header_fill
    ws1["B5"].font = header_font

    # -------------------------------------------------------------
    # ABA 2: DESEMPENHO POR DOCENTE
    # -------------------------------------------------------------
    ws2 = wb.create_sheet(title="Docentes e Ofertas")
    headers2 = ["Docente", "Titulação", "Disciplina", "Turma", "Qtd. Respostas", "Média Geral"]
    ws2.append(headers2)

    for col_num in range(1, len(headers2) + 1):
        cell = ws2.cell(row=1, column=col_num)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")

    offerings = ClassOffering.objects.select_related('teacher__user', 'discipline', 'class_group').all()
    for off in offerings:
        off_resp = responses.filter(offering=off)
        off_avg = off_resp.aggregate(avg=Avg('overall_score'))['avg'] or 0.0
        ws2.append([
            off.teacher.user.get_full_name(),
            off.teacher.get_academic_title_display(),
            off.discipline.name,
            off.class_group.name,
            off_resp.count(),
            round(float(off_avg), 2)
        ])

    for row in ws2.iter_rows(min_row=2, max_col=6):
        for cell in row:
            cell.border = border_thin

    # -------------------------------------------------------------
    # ABA 3: FEEDBACKS MODERADOS
    # -------------------------------------------------------------
    ws3 = wb.create_sheet(title="Comentários Moderados")
    headers3 = ["ID Resposta", "Docente", "Disciplina", "Nota", "Status de Moderação", "Comentário do Aluno"]
    ws3.append(headers3)

    for col_num in range(1, len(headers3) + 1):
        cell = ws3.cell(row=1, column=col_num)
        cell.font = header_font
        cell.fill = senai_red_fill
        cell.alignment = Alignment(horizontal="center")

    for resp in responses.exclude(comment__isnull=True).exclude(comment='').select_related('offering__teacher__user', 'offering__discipline'):
        ws3.append([
            resp.id,
            resp.offering.teacher.user.get_full_name(),
            resp.offering.discipline.name,
            float(resp.overall_score),
            resp.get_moderation_status_display(),
            resp.comment
        ])

    for row in ws3.iter_rows(min_row=2, max_col=6):
        for cell in row:
            cell.border = border_thin

    # Ajusta largura automática das colunas
    for ws in [ws1, ws2, ws3]:
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 14)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    filename = f"Avalia_SENAI_Relatorio_{cycle.academic_period.replace('/', '_')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response
