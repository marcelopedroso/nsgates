import requests
from django.db import models
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from simple_history.admin import SimpleHistoryAdmin
from django.contrib import messages
from .models import CustomUser, TokenIntegration
from .forms import CustomUserAdminForm
from django.urls import reverse
from django.utils.html import format_html
from simple_history.utils import update_change_reason

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


class BaseRenewTokenAdmin(admin.ModelAdmin):
    """🔥 Classe base para permitir renovação de tokens apenas para usuários autorizados"""
    
    actions = ["renew_selected_tokens"]

#    def get_actions(self, request):
#        """🔒 Remove a opção de renovar tokens se o usuário não tiver permissão."""
#        actions = super().get_actions(request)
#        if not request.user.has_perm("core.renew_token"):
#            actions.pop("renew_selected_tokens", None)  # Remove a action se não tiver permissão
#        return actions

    def renew_selected_tokens(self, request, queryset):
        """🔄 Renova tokens apenas para usuários com permissão"""
        if not request.user.has_perm("core.renew_token"):
            self.message_user(request, "Você não tem permissão para renovar tokens!", level=messages.ERROR)
            return

        api_url = os.getenv("API_URL", "http://127.0.0.1:8000") + "/auth/admin/generate-token/"
        success_count = 0

        for obj in queryset:
            user = obj.user if hasattr(obj, "user") else obj
            url = f"{api_url}?username={user.username}"
            response = requests.post(url)

            if response.status_code == 200:
                success_count += 1
                
                # 🔥 Atualiza manualmente quem fez a alteração no histórico
                update_change_reason(obj, "Token renovado via Django Admin")
                obj.history_user = request.user  # 🔥 Salva quem fez a alteração
                obj.save()  # 🔥 Salva a modificação no histórico
                
            else:
                self.message_user(request, f"Erro ao renovar token para {user.username}: {response.text}", level=messages.ERROR)

        if success_count:
            self.message_user(request, f"{success_count} tokens renovados com sucesso!", level=messages.SUCCESS)

    renew_selected_tokens.short_description = "🔄 Renovar Tokens Selecionados"



@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin, BaseAdmin, BaseRenewTokenAdmin):  
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

#admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(TokenIntegration)
class TokenIntegrationAdmin(BaseAdmin, BaseRenewTokenAdmin):
    search_fields = ("user__username", "access_token")  # Permitir busca
    list_display = ("user", "updated_at", "expires_at", "access_token")  # Campos visíveis no admin
    #list_filter = ("user","expires_at")  # Filtro por validade    
    readonly_fields = ("access_token", "expires_at")  # Evita edição diret
    ordering = ["expires_at"]
    
    def has_add_permission(self, request):
        """ 🔥 Desativa o botão de adicionar novos tokens """
        return False
    
    def get_readonly_fields(self, request, obj=None):
        """ 🔥 Torna todos os campos somente leitura """
        return [field.name for field in self.model._meta.fields]