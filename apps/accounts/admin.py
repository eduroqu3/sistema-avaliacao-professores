from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'get_full_name', 'email', 'role', 'registration_number', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'registration_number')
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Acadêmicas e Perfil', {
            'fields': ('role', 'registration_number', 'phone', 'avatar_url')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Acadêmicas e Perfil', {
            'fields': ('role', 'registration_number', 'phone', 'avatar_url')
        }),
    )
