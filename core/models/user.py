from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now
from .base import BaseModel
from .managers import CustomUserManager

class CustomUser(AbstractUser, BaseModel):
    """Modelo de usuário customizado herdando BaseModel"""
    
    objects = CustomUserManager()  # Manager padrão
    all_objects = models.Manager()  # Para buscar usuários deletados também

    def delete(self, using=None, keep_parents=False):
        """Soft Delete"""
        self.deleted_at = now()
        self.save(update_fields=["deleted_at"])

    def restore(self):
        """Restaura um usuário deletado"""
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])

    @property
    def is_deleted(self):
        return self.deleted_at is not None
