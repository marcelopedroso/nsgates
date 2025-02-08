from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from core.models import BaseAdmin
from .models import  CustomUser  # Importamos apenas modelos aqui


class CustomUserAdmin(UserAdmin, BaseAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser']
    list_filter = ['is_staff', 'is_superuser', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['username']

    def get_fieldsets(self, request, obj=None):
        """Mostra o campo deleted_at apenas se o usuário já existir e for superusuário"""
        fieldsets = super().get_fieldsets(request, obj)
        if obj and request.user.is_superuser:
            fieldsets += ((None, {'fields': ('deleted_at',)}),)
        return fieldsets

admin.site.register(CustomUser, CustomUserAdmin)