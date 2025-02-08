from django.contrib.auth.models import AbstractUser
from django.db import models
from simple_history.utils import update_change_reason
from core.models import BaseModel  # Importando BaseModel corretamente
from accounts_permissions.models import CustomGroup, CustomPermission  # Importando nossos modelos

class CustomUser(AbstractUser, BaseModel):
    """Modelo de usuário customizado herdando BaseModel"""
    groups = models.ManyToManyField(
        CustomGroup,
        related_name="custom_users",
        blank=True,
        verbose_name="groups",
        help_text="The groups this user belongs to.",
    )

    user_permissions = models.ManyToManyField(
        CustomPermission,
        related_name="custom_users_permissions",
        blank=True,
        verbose_name="user permissions",
        help_text="Specific permissions for this user.",
    )

    def save(self, *args, **kwargs):
        """Salva com motivo de alteração"""
        if 'change_reason' in kwargs:
            update_change_reason(self, kwargs.pop('change_reason'))
        super().save(*args, **kwargs)
