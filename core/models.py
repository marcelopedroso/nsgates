import uuid
from django.db import models
from django.utils.timezone import now
from simple_history.models import HistoricalRecords

class ActiveManager(models.Manager):
    """Manager personalizado para buscar apenas registros ativos (não deletados)"""
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class BaseModel(models.Model):
    """Modelo base para adicionar timestamps, soft delete e histórico"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    objects = ActiveManager()  # Gerenciador padrão retorna apenas registros ativos
    all_objects = models.Manager()  # Gerenciador alternativo retorna todos os registros

    history = HistoricalRecords(inherit=False)  # 🔥 Corrigido para suportar herança corretamente

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["updated_at"]),
            models.Index(fields=["deleted_at"]),
        ]
        abstract = True  # Não cria tabela no banco

    def delete(self, using=None, keep_parents=False):
        """Soft Delete - Marca como excluído em vez de deletar do banco"""
        self.__class__.all_objects.filter(id=self.id).update(deleted_at=now())

    def restore(self):
        """Restaura um registro deletado"""
        self.__class__.all_objects.filter(id=self.id).update(deleted_at=None)

    @property
    def is_deleted(self):
        """Retorna True se o registro estiver marcado como excluído"""
        return self.deleted_at is not None
