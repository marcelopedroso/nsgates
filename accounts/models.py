from django.contrib.auth.models import AbstractUser
from django.db import models
from simple_history.utils import update_change_reason
from core.models import BaseModel  # 🔥 Importando BaseModel corretamente

class CustomUser(AbstractUser, BaseModel):
    """Usuário customizado herdando BaseModel"""

    def save(self, *args, **kwargs):
        """Salva com motivo de alteração"""
        if 'change_reason' in kwargs:
            update_change_reason(self, kwargs.pop('change_reason'))
        super().save(*args, **kwargs)
