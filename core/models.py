# models.py 
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now
from simple_history.models import HistoricalRecords
from simple_history.utils import update_change_reason

from django.contrib.auth.models import BaseUserManager

class ActiveManager(BaseUserManager):  # 🔥 Herdando BaseUserManager para evitar conflitos
    """Manager que retorna apenas registros não deletados"""
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)



class BaseModel(models.Model):
    """Modelo base para adicionar timestamps, soft delete e histórico"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    objects = ActiveManager()  # Usa este como padrão
    all_objects = models.Manager()  # Para buscar tudo (inclusive deletados)

    history = HistoricalRecords(inherit=True)  
    
    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["updated_at"]),
            models.Index(fields=["deleted_at"]),
        ]
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Soft Delete - Marca como excluído e salva a alteração"""
        self.__class__.all_objects.filter(id=self.id).update(deleted_at=now())
        self.refresh_from_db() 

    def restore(self):
        """Restaura um registro deletado"""
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])  

    @property
    def is_deleted(self):
        """Retorna True se o registro estiver marcado como excluído"""
        return self.deleted_at is not None
    

class CustomUser(AbstractUser, BaseModel):
    objects = ActiveManager() 
    """Modelo de usuário customizado herdando BaseModel"""
    def save(self, *args, **kwargs):
        """Salva com motivo de alteração"""
        if 'change_reason' in kwargs:
            update_change_reason(self, kwargs.pop('change_reason'))
        super().save(*args, **kwargs)
