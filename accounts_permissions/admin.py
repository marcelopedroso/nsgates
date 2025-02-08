from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin
from accounts_permissions.models import CustomGroup, CustomPermission

@admin.register(CustomGroup)
class CustomGroupAdmin(GroupAdmin):  # 🔥 Herdamos GroupAdmin para manter funcionalidades
    list_display = ("name", "created_at", "updated_at", "deleted_at")
    search_fields = ("name",)
    list_filter = ("created_at", "updated_at", "deleted_at")

@admin.register(CustomPermission)
class CustomPermissionAdmin(admin.ModelAdmin):
    list_display = ("name", "codename", "content_type")
    search_fields = ("name", "codename")
    list_filter = ("content_type",)
