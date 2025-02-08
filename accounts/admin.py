from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets
    list_display = ("username", "email", "is_staff", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email")

    class Meta:
        app_label = "auth"  # 🔥 Mantém no menu "Authentication and Authorization"
