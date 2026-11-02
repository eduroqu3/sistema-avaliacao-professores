from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
import csv
from django.db import IntegrityError, transaction
from django.db.models import Avg
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from .forms import TeacherForm, SubjectForm, EvaluationForm, TeachingAssignmentForm, StudentCreateForm, StudentEditForm
from .models import Teacher, Subject, TeachingAssignment, Evaluation, StudentProfile, StudentEvaluationRecord
from .privacy import encrypt_evaluation_id, decrypt_evaluation_id

User = get_user_model()

def is_coordinator(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def coordinator_required(view):
    return login_required(user_passes_test(is_coordinator, login_url="login")(view))

def is_student(user):
    return user.is_authenticated and hasattr(user, "student_profile") and user.student_profile.active and user.is_active

def student_required(view):
    return login_required(user_passes_test(is_student, login_url="login")(view))

class RoleBasedLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = False
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if is_coordinator(request.user): return redirect("dashboard")
            if is_student(request.user): return redirect("student_portal")
            return HttpResponseForbidden("Esta conta não possui um perfil autorizado no Avalia SENAI.")
        return super().dispatch(request, *args, **kwargs)
    def get_success_url(self):
        user = self.request.user
        if is_coordinator(user): return reverse("dashboard")
        if is_student(user): return reverse("student_portal")
        return reverse("login")

def home(request):
    return render(request, "home.html")

def evaluate(request):
    if request.user.is_authenticated and is_student(request.user): return redirect("student_portal")
    if is_coordinator(request.user): return redirect("dashboard")
    return redirect(f'{reverse("login")}?next={reverse("student_portal")}')

def thanks(request):
    if is_student(request.user): return redirect("student_portal")
    return render(request, "thanks.html")

@coordinator_required
def dashboard(request):
    evaluations = Evaluation.objects.select_related("assignment__teacher", "assignment__subject")
    total = evaluations.count()
    overall = evaluations.aggregate(clarity=Avg("clarity"), knowledge=Avg("knowledge"), engagement=Avg("engagement"), respect=Avg("respect"), organization=Avg("organization"))
    min_responses = max(1, int(getattr(settings, "ANONYMITY_MIN_RESPONSES", 3)))
    if total >= min_responses:
        overall["avg"] = round(sum(float(overall[k] or 0) for k in ["clarity","knowledge","engagement","respect","organization"]) / 5, 2)
    else:
        overall["avg"] = None
        for key in ["clarity", "knowledge", "engagement", "respect", "organization"]: overall[key] = None
    rows = []
    for assignment in TeachingAssignment.objects.select_related("teacher", "subject"):
        qs = evaluations.filter(assignment=assignment); count = qs.count()
        if count >= min_responses:
            dims = qs.aggregate(clarity=Avg("clarity"), knowledge=Avg("knowledge"), engagement=Avg("engagement"), respect=Avg("respect"), organization=Avg("organization"))
            rows.append({"assignment": assignment, "count": count, "average": round(sum(float(v or 0) for v in dims.values()) / 5, 2), "dims": dims})
    return render(request, "dashboard.html", {"total": total, "overall": overall, "rows": rows, "teachers_count": Teacher.objects.filter(active=True).count(), "subjects_count": Subject.objects.filter(active=True).count(), "students_count": StudentProfile.objects.filter(active=True, user__is_active=True).count()})

@coordinator_required
def teachers(request): return render(request, "teachers.html", {"teachers": Teacher.objects.all()})
@coordinator_required
def teacher_create(request):
    form = TeacherForm(request.POST or None)
    if request.method == "POST" and form.is_valid(): form.save(); messages.success(request, "Professor cadastrado."); return redirect("teachers")
    return render(request, "object_form.html", {"form": form, "title": "Novo professor", "back": "teachers"})
@coordinator_required
def teacher_edit(request, pk):
    obj=get_object_or_404(Teacher,pk=pk); form=TeacherForm(request.POST or None,instance=obj)
    if request.method=="POST" and form.is_valid(): form.save(); messages.success(request,"Cadastro atualizado."); return redirect("teachers")
    return render(request,"object_form.html",{"form":form,"title":"Editar professor","back":"teachers"})
@coordinator_required
@require_POST
def teacher_delete(request,pk):
    obj=get_object_or_404(Teacher,pk=pk)
    if obj.assignments.exists(): obj.active=False; obj.save(); messages.info(request,"Professor desativado porque possui vínculos ou histórico.")
    else: obj.delete(); messages.success(request,"Professor excluído.")
    return redirect("teachers")

@coordinator_required
def subjects(request): return render(request,"subjects.html",{"subjects":Subject.objects.all()})
@coordinator_required
def subject_create(request):
    form=SubjectForm(request.POST or None)
    if request.method=="POST" and form.is_valid(): form.save(); messages.success(request,"Disciplina cadastrada."); return redirect("subjects")
    return render(request,"object_form.html",{"form":form,"title":"Nova disciplina","back":"subjects"})
@coordinator_required
def subject_edit(request,pk):
    obj=get_object_or_404(Subject,pk=pk); form=SubjectForm(request.POST or None,instance=obj)
    if request.method=="POST" and form.is_valid(): form.save(); messages.success(request,"Cadastro atualizado."); return redirect("subjects")
    return render(request,"object_form.html",{"form":form,"title":"Editar disciplina","back":"subjects"})
@coordinator_required
@require_POST
def subject_delete(request,pk):
    obj=get_object_or_404(Subject,pk=pk)
    if obj.assignments.exists(): obj.active=False; obj.save(); messages.info(request,"Disciplina desativada porque possui vínculos ou histórico.")
    else: obj.delete(); messages.success(request,"Disciplina excluída.")
    return redirect("subjects")

@coordinator_required
def assignments(request): return render(request,"assignments.html",{"assignments":TeachingAssignment.objects.select_related("teacher","subject").all()})
@coordinator_required
def assignment_create(request):
    form=TeachingAssignmentForm(request.POST or None)
    if request.method=="POST" and form.is_valid(): form.save(); messages.success(request,"Vínculo criado."); return redirect("assignments")
    return render(request,"object_form.html",{"form":form,"title":"Vincular professor e disciplina","back":"assignments"})
@coordinator_required
def assignment_edit(request,pk):
    obj=get_object_or_404(TeachingAssignment,pk=pk); form=TeachingAssignmentForm(request.POST or None,instance=obj)
    if request.method=="POST" and form.is_valid(): form.save(); messages.success(request,"Vínculo atualizado."); return redirect("assignments")
    return render(request,"object_form.html",{"form":form,"title":"Editar vínculo docente","back":"assignments"})
@coordinator_required
@require_POST
def assignment_delete(request,pk):
    obj=get_object_or_404(TeachingAssignment,pk=pk)
    if obj.evaluations.exists() or obj.participation_records.exists(): obj.active=False; obj.save(); messages.info(request,"Vínculo desativado porque possui histórico de participação ou avaliações.")
    else: obj.delete(); messages.success(request,"Vínculo excluído.")
    return redirect("assignments")

@coordinator_required
def reports(request):
    qs=Evaluation.objects.select_related("assignment__teacher","assignment__subject"); grouped=[]
    min_responses = max(1, int(getattr(settings, "ANONYMITY_MIN_RESPONSES", 3)))
    for teacher in Teacher.objects.all():
        teacher_qs=qs.filter(assignment__teacher=teacher); count=teacher_qs.count()
        if count >= min_responses:
            dims=teacher_qs.aggregate(clarity=Avg("clarity"),knowledge=Avg("knowledge"),engagement=Avg("engagement"),respect=Avg("respect"),organization=Avg("organization"))
            grouped.append({"teacher":teacher,"count":count,"average":round(sum(float(v or 0) for v in dims.values())/5,2),"dims":dims})
    return render(request,"reports.html",{"grouped":grouped,"total":qs.count(),"min_responses":min_responses})


@coordinator_required
def export_reports_csv(request):
    qs = Evaluation.objects.select_related("assignment__teacher", "assignment__subject")
    min_responses = max(1, int(getattr(settings, "ANONYMITY_MIN_RESPONSES", 3)))
    from django.http import HttpResponse
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="avalia_senai_relatorio.csv"'
    response.write("\ufeff")
    writer = csv.writer(response, delimiter=";")
    writer.writerow(["Professor", "Respostas", "Média geral", "Clareza", "Domínio do conteúdo", "Didática", "Respeito", "Organização"])
    for teacher in Teacher.objects.all():
        teacher_qs = qs.filter(assignment__teacher=teacher)
        count = teacher_qs.count()
        if count < min_responses:
            continue
        dims = teacher_qs.aggregate(clarity=Avg("clarity"), knowledge=Avg("knowledge"), engagement=Avg("engagement"), respect=Avg("respect"), organization=Avg("organization"))
        average = round(sum(float(v or 0) for v in dims.values()) / 5, 2)
        name = teacher.name
        if name.startswith(("=", "+", "-", "@")):
            name = "'" + name
        writer.writerow([name, count, average, round(dims["clarity"], 2), round(dims["knowledge"], 2), round(dims["engagement"], 2), round(dims["respect"], 2), round(dims["organization"], 2)])
    return response

@coordinator_required
def students(request):
    return render(request,"students.html",{"students":StudentProfile.objects.select_related("user").all()})
@coordinator_required
def student_create(request):
    form=StudentCreateForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        data=form.cleaned_data
        user=User.objects.create_user(username=data["username"],password=data["password"],is_active=True,is_staff=False,is_superuser=False)
        StudentProfile.objects.create(user=user,display_name=data["display_name"].strip())
        messages.success(request,"Conta do aluno criada. Entregue as credenciais por um canal seguro.")
        return redirect("students")
    return render(request,"object_form.html",{"form":form,"title":"Criar conta de aluno","back":"students"})
@coordinator_required
def student_edit(request,pk):
    profile=get_object_or_404(StudentProfile.objects.select_related("user"),pk=pk)
    form=StudentEditForm(request.POST or None,instance=profile)
    if request.method=="POST" and form.is_valid():
        obj=form.save(); obj.user.is_active=obj.active
        new_password=form.cleaned_data.get("new_password")
        if new_password: obj.user.set_password(new_password)
        obj.user.save(); messages.success(request,"Conta do aluno atualizada."); return redirect("students")
    return render(request,"object_form.html",{"form":form,"title":f"Editar conta: {profile.display_name}","back":"students"})

@student_required
def student_portal(request):
    user=request.user
    records={r.assignment_id:r for r in StudentEvaluationRecord.objects.filter(student=user)}
    assignments=TeachingAssignment.objects.filter(active=True,teacher__active=True,subject__active=True).select_related("teacher","subject")
    items=[]
    for assignment in assignments:
        record=records.get(assignment.pk)
        items.append({"assignment":assignment,"done":bool(record),"record":record})
    return render(request,"student_portal.html",{"items":items,"profile":user.student_profile,"completed":len(records)})

@student_required
def student_history(request):
    records=StudentEvaluationRecord.objects.filter(student=request.user).select_related("assignment__teacher","assignment__subject")
    items=[]
    for record in records:
        token=decrypt_evaluation_id(record.encrypted_evaluation_id)
        evaluation=Evaluation.objects.filter(public_id=token,assignment=record.assignment).first() if token else None
        items.append({"record":record,"evaluation":evaluation})
    return render(request,"student_history.html",{"items":items})

@student_required
def student_evaluate(request,assignment_id):
    assignment=get_object_or_404(TeachingAssignment.objects.select_related("teacher","subject"),pk=assignment_id)
    record=StudentEvaluationRecord.objects.filter(student=request.user,assignment=assignment).first()
    evaluation=None
    if record:
        token=decrypt_evaluation_id(record.encrypted_evaluation_id)
        if not token: return render(request,"student_evaluation.html",{"assignment":assignment,"form":EvaluationForm(),"integrity_error":True},status=500)
        evaluation=Evaluation.objects.filter(public_id=token,assignment=assignment).first()
        if evaluation is None: return render(request,"student_evaluation.html",{"assignment":assignment,"form":EvaluationForm(),"integrity_error":True},status=500)
    elif not (assignment.active and assignment.teacher.active and assignment.subject.active):
        return HttpResponseForbidden("Este vínculo não está disponível para novas avaliações.")
    form=EvaluationForm(request.POST or None,instance=evaluation)
    if request.method=="POST" and form.is_valid():
        try:
            with transaction.atomic():
                if record:
                    saved=form.save(commit=False); saved.assignment=assignment; saved.save()
                    messages.success(request,"Sua avaliação foi atualizada. O histórico registra a data da última alteração.")
                else:
                    saved=form.save(commit=False); saved.assignment=assignment; saved.save()
                    StudentEvaluationRecord.objects.create(student=request.user,assignment=assignment,encrypted_evaluation_id=encrypt_evaluation_id(saved.public_id))
                    messages.success(request,"Avaliação registrada. Você poderá editá-la pelo histórico, mas não criar outra para este vínculo.")
            return redirect("student_history")
        except IntegrityError:
            messages.error(request,"Já existe uma avaliação registrada para esse vínculo nesta conta. Abra o histórico para editá-la.")
            return redirect("student_history")
    return render(request,"student_evaluation.html",{"assignment":assignment,"form":form,"editing":bool(record)})
