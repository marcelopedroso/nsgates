import uuid
from django.db import models
from django.utils.timezone import now
from simple_history.models import HistoricalRecords
from simple_history.admin import SimpleHistoryAdmin

class ActiveManager(models.Manager):
    """Manager que retorna apenas registros ativos (não deletados)"""
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

    history = HistoricalRecords(inherit=False)  

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
    
class BaseAdmin(SimpleHistoryAdmin):
    """
    Classe base para administração de modelos com Soft Delete.
    Filtra automaticamente registros onde `deleted_at` é NULL.
    """
    
    readonly_fields = ('last_login', 'date_joined', 'deleted_at')  # Torna esses campos não editáveis
    
    def get_queryset(self, request):
        """Filtra apenas registros que não foram excluídos (soft delete)"""
        return super().get_queryset(request).filter(deleted_at__isnull=True)