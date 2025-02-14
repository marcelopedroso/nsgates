import requests
from django.db import models
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from simple_history.admin import SimpleHistoryAdmin
from django.contrib import messages
from .models import CustomUser
from .forms import CustomUserAdminForm
from django.urls import reverse
from django.utils.html import format_html
from simple_history.utils import update_change_reason
from oauth2_provider.models import AccessToken, RefreshToken, Grant, Application


import os
import environ
env = environ.Env()
API_URL=os.getenv("API_URL")


class BaseAdmin(SimpleHistoryAdmin):
    """Admin base com suporte ao SimpleHistory e controle de permissões para Actions."""
    
    list_per_page = 20
    list_per_page_options = [10, 20, 50, 100]
    readonly_fields = ["created_at", "updated_at", "deleted_at"]

    # 🔥 Mapeia as ações do Django Admin para permissões específicas
    action_permissions = {
        "renew_selected_tokens": "core.renew_token",  # 🔥 Apenas quem tem "core.renew_token" pode renovar tokens
        # "outra_action": "core.outra_permissao",  # Se precisar de mais, adicione aqui
    }

    def get_search_fields(self, request):
        """Filtra automaticamente apenas os campos de texto do modelo"""
        if not self.search_fields:
            return [
                field.name
                for field in self.model._meta.fields
                if isinstance(field, (models.CharField, models.TextField))
            ]
        return super().get_search_fields(request)

    def get_queryset(self, request):
        """Exibe apenas registros que não foram deletados (soft delete)."""
        return super().get_queryset(request).filter(deleted_at__isnull=True)

    def has_delete_permission(self, request, obj=None):
        """Habilita a deleção apenas se o usuário tiver permissão específica."""
        return request.user.has_perm(f"{self.model._meta.app_label}.delete_{self.model._meta.model_name}") or request.user.is_superuser

    def get_actions(self, request):
        """
        🔒 Remove ações para usuários sem permissão específica.
        Exemplo: 'renew_selected_tokens' só aparece se o usuário tiver 'core.renew_token'.
        """
        actions = super().get_actions(request)
        for action_name, permission in self.action_permissions.items():
            if not request.user.has_perm(permission) and not request.user.is_superuser:
                actions.pop(action_name, None)  # 🔥 Remove action se não tiver permissão
        return actions


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin, BaseAdmin):  
    model = CustomUser
    list_display = ["username", "email", "first_name", "last_name", "is_active", "is_staff", "is_superuser"]
    list_filter = ["is_staff", "is_superuser", "is_active"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering = ["username"]

    readonly_fields = ["last_login", "date_joined","password"]
    form = CustomUserAdminForm  # 🔥 Usa o formulário customizado


    def save_model(self, request, obj, form, change):
        """Se o usuário já existir e estiver deletado, restaura em vez de criar um novo"""
        existing_user = CustomUser.all_objects.filter(username=obj.username).first()

        if existing_user and existing_user.deleted_at is not None:  # 🔥 Corrigido para verificar corretamente
            existing_user.deleted_at = None  # 🔥 Restaura o usuário
            existing_user.save(update_fields=["deleted_at"])
            messages.success(request, f'O usuário "{obj.username}" foi restaurado com sucesso!')
            return  # Evita criar um novo usuário

        super().save_model(request, obj, form, change)  # Cria normalmente se não existir



from django.contrib import admin
from oauth2_provider.models import AccessToken, RefreshToken, Application
from oauth2_provider.admin import AccessTokenAdmin, RefreshTokenAdmin, ApplicationAdmin

# 🔥 Remover os registros padrão do Django OAuth Toolkit
admin.site.unregister(AccessToken)
admin.site.unregister(RefreshToken)
admin.site.unregister(Application)

# 🔥 Personalizar os campos que NÃO podem ser editados
class CustomApplicationAdmin(ApplicationAdmin):
    readonly_fields = ("client_id", "client_secret", "created", "updated")
    fieldsets = (
        ("Informações do Cliente", {
            "fields": ("client_id", "client_secret", "user", "name", "redirect_uris", "client_type", "authorization_grant_type", "created", "updated")
        }),
    )

class CustomAccessTokenAdmin(AccessTokenAdmin):
    readonly_fields = ("token", "user", "application", "expires", "created", "updated")
    fieldsets = (
        ("Informações do Token", {
            "fields": ("token", "user", "application", "scope", "expires", "created", "updated"),
        }),
    )

class CustomRefreshTokenAdmin(RefreshTokenAdmin):
    readonly_fields = ("token", "user", "application", "access_token")
    fieldsets = (
        ("Informações do Refresh Token", {
            "fields": ("token", "user", "application", "access_token", "created"),
        }),
    )

# 🔥 Registrar novamente os modelos com os campos somente leitura
admin.site.register(Application, CustomApplicationAdmin)
admin.site.register(AccessToken, CustomAccessTokenAdmin)
admin.site.register(RefreshToken, CustomRefreshTokenAdmin)