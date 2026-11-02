from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Teacher, Subject, TeachingAssignment, Evaluation, StudentProfile

User = get_user_model()

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ["name", "email", "active"]
        widgets = {"name": forms.TextInput(attrs={"placeholder": "Nome completo"}), "email": forms.EmailInput(attrs={"placeholder": "nome@escola.edu.br"})}

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ["name", "code", "active"]
        widgets = {"name": forms.TextInput(attrs={"placeholder": "Ex.: Matemática Aplicada"}), "code": forms.TextInput(attrs={"placeholder": "Ex.: MAT-01"})}

RATING_CHOICES = [(i, f"{i} — {'Muito ruim' if i==1 else 'Ruim' if i==2 else 'Regular' if i==3 else 'Bom' if i==4 else 'Excelente'}") for i in range(1,6)]
class EvaluationForm(forms.ModelForm):
    clarity = forms.ChoiceField(label="Clareza das explicações", choices=RATING_CHOICES, widget=forms.RadioSelect)
    knowledge = forms.ChoiceField(label="Domínio do conteúdo", choices=RATING_CHOICES, widget=forms.RadioSelect)
    engagement = forms.ChoiceField(label="Didática e participação", choices=RATING_CHOICES, widget=forms.RadioSelect)
    respect = forms.ChoiceField(label="Respeito e ambiente em sala", choices=RATING_CHOICES, widget=forms.RadioSelect)
    organization = forms.ChoiceField(label="Organização das aulas", choices=RATING_CHOICES, widget=forms.RadioSelect)
    class Meta:
        model = Evaluation
        fields = ["clarity", "knowledge", "engagement", "respect", "organization", "comment"]
        widgets = {"comment": forms.Textarea(attrs={"rows":4, "placeholder":"Compartilhe uma sugestão construtiva. Não informe nomes ou dados pessoais."})}

class TeachingAssignmentForm(forms.ModelForm):
    class Meta:
        model = TeachingAssignment
        fields = ["teacher", "subject", "class_name", "period", "active"]
        widgets = {"class_name": forms.TextInput(attrs={"placeholder": "Ex.: Desenvolvimento de Sistemas - 2A"}), "period": forms.TextInput(attrs={"placeholder": "Ex.: 2º semestre / 2026"})}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["teacher"].queryset = Teacher.objects.filter(active=True)
        self.fields["subject"].queryset = Subject.objects.filter(active=True)

class StudentCreateForm(forms.Form):
    username = forms.CharField(label="Usuário de acesso", max_length=150, help_text="Use um código interno que não seja exibido nas respostas.")
    display_name = forms.CharField(label="Nome do aluno", max_length=120)
    password = forms.CharField(label="Senha inicial", widget=forms.PasswordInput, validators=[validate_password])
    password_confirm = forms.CharField(label="Confirmar senha", widget=forms.PasswordInput)
    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Esse usuário já existe.")
        return username
    def clean(self):
        data = super().clean()
        if data.get("password") and data.get("password_confirm") and data["password"] != data["password_confirm"]:
            self.add_error("password_confirm", "As senhas não coincidem.")
        return data

class StudentEditForm(forms.ModelForm):
    new_password = forms.CharField(label="Nova senha (opcional)", required=False, widget=forms.PasswordInput,
                                   validators=[validate_password], help_text="Preencha somente se precisar redefinir a senha.")
    class Meta:
        model = StudentProfile
        fields = ["display_name", "active"]
