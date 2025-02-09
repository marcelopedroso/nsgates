from django.db import models
from unfold.admin import ModelAdmin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from simple_history.admin import SimpleHistoryAdmin
from .models import CustomUser


class BaseAdmin(ModelAdmin, SimpleHistoryAdmin):
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


class CustomUserAdmin(UserAdmin, BaseAdmin):  
    model = CustomUser
    list_display = ["username", "email", "first_name", "last_name", "is_active", "is_staff", "is_superuser"]
    list_filter = ["is_staff", "is_superuser", "is_active"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering = ["username"]
    
    readonly_fields = ["last_login", "date_joined"]

    def get_queryset(self, request):
        """Exibe apenas usuários que não foram deletados (soft delete)."""
        return super().get_queryset(request).filter(deleted_at__isnull=True)

admin.site.register(CustomUser, CustomUserAdmin)
