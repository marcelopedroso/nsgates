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

import os
import environ
env = environ.Env()
API_URL=os.getenv("API_URL")


class BaseAdmin (SimpleHistoryAdmin):
    """Admin base com suporte ao Unfold e SimpleHistory"""
    list_per_page = 20
    list_per_page_options = [10, 20, 50, 100]

    readonly_fields = ["created_at", "updated_at", "deleted_at"]  

    
    def get_search_fields(self, request):
        """Filtra automaticamente apenas os campos de texto do modelo"""
        if not self.search_fields:  # Se o admin não tiver search_fields definido
            return [
                field.name
                for field in self.model._meta.fields
                if isinstance(field, (models.CharField, models.TextField))
            ]
        return super().get_search_fields(request)
    
    def get_queryset(self, request):
        """Exibe apenas usuários que não foram deletados (soft delete)."""
        return super().get_queryset(request).filter(deleted_at__isnull=True)

    def delete_model(self, request, obj):
        """Intercepta a deleção para aplicar Soft Delete."""
        if obj.deleted_at is None:
            obj.delete()  # ✅ Marca como deletado
            messages.success(request, f'O registro "{obj}" foi marcado como excluído!')
        else:
            obj.restore()  # ✅ Restaura se já estava deletado
            messages.success(request, f'O registro "{obj}" foi restaurado!')

    def has_delete_permission(self, request, obj=None):
        """Habilita a deleção apenas para Soft Delete."""
        return True  # ✅ Mantém a opção de exclusão ativa para Soft Delete

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

#admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(TokenIntegration)
class TokenIntegrationAdmin(BaseAdmin):
    search_fields = ("user__username", "access_token")  # Permitir busca
    list_display = ("user", "updated_at", "expires_at", "access_token")  # Campos visíveis no admin
    #list_filter = ("user","expires_at")  # Filtro por validade    
    readonly_fields = ("token", "expires_at")  # Evita edição diret
    ordering = ["expires_at"]
    
    actions = ["renew_selected_tokens"]

    def renew_selected_tokens(self, request, queryset):
        """
        Permite renovar tokens para múltiplos usuários via Django Admin.
        """
        api_url = API_URL+"/auth/admin/generate-token/"
        success_count = 0

        for token_obj in queryset:
            url = f"{api_url}?username={token_obj.user.username}"  # 🔥 Agora passa `username` na URL
            response = requests.post(url)

            if response.status_code == 200:
                success_count += 1
            else:
                self.message_user(
                    request, 
                    f"Erro ao renovar token para {token_obj.user.username}: {response.text}", 
                    level=messages.ERROR
                )

        if success_count:
            self.message_user(
                request, 
                f"{success_count} tokens renovados com sucesso!", 
                level=messages.SUCCESS
            )

    renew_selected_tokens.short_description = "🔄 Renovar Tokens Selecionados"


#    renew_selected_tokens.short_description = "🔄 Renovar Tokens Selecionados"
#
#    def renew_token_button(self, obj):
#        """ Adiciona um botão para renovar o token diretamente na tabela """
#        return format_html(f'<a href="/admin/core/tokenintegration/{obj.id}/renew/" class="button">🔄 Renovar</a>')
#
#    renew_token_button.allow_tags = True
#    renew_token_button.short_description = "Renovar Token"