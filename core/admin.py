from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from simple_history.admin import SimpleHistoryAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin, SimpleHistoryAdmin):
    model = CustomUser
    list_display = ["username", "email", "first_name", "last_name", "is_active", "is_staff", "is_superuser"]
    list_filter = ["is_staff", "is_superuser", "is_active"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering = ["username"]

    def get_queryset(self, request):
        """Exibe apenas usuários que não foram deletados (soft delete)."""
        return super().get_queryset(request).filter(deleted_at__isnull=True)

admin.site.register(CustomUser, CustomUserAdmin)
