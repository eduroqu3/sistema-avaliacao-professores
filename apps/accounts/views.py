from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.urls import reverse

User = get_user_model()

def login_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    if request.method == 'POST':
        username_or_rm = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username_or_rm, password=password)
        
        # If not authenticated by username, attempt to find user by registration_number (RM/RF)
        if user is None:
            user_by_rm = User.objects.filter(registration_number__iexact=username_or_rm).first()
            if user_by_rm:
                user = authenticate(request, username=user_by_rm.username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f"Bem-vindo(a), {user.get_full_name() or user.username}!")
                return redirect_by_role(user)
            else:
                messages.error(request, "Esta conta de usuário está inativa.")
        else:
            messages.error(request, "Usuário ou senha incorretos. Tente novamente ou use o atalho de demonstração.")

    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, "Você encerrou sua sessão no Avalia SENAI com segurança.")
    return redirect('accounts:login')

def demo_switch_view(request, username):
    """
    Atalho rápido para testes e bancas avaliadoras alternarem papéis no sistema com 1 clique.
    """
    user = User.objects.filter(username=username).first()
    if user:
        login(request, user)
        messages.success(request, f"Sessão alterada para {user.get_full_name() or user.username} ({user.get_role_display()})!")
        return redirect_by_role(user)
    else:
        messages.warning(request, f"Usuário '{username}' não encontrado. Execute o comando seed_data.")
        return redirect('accounts:login')

def redirect_by_role(user):
    if user.is_student:
        return redirect('evaluations:student_list')
    elif user.is_teacher:
        return redirect('dashboards:teacher_dashboard')
    elif user.is_coordinator_or_admin:
        return redirect('dashboards:coordination_dashboard')
    return redirect('core:home')
