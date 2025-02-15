import uuid
from django.db import models
from django.utils.timezone import now
from simple_history.models import HistoricalRecords
from sqlalchemy.orm import declarative_base

Base = declarative_base()  # 🔥 Isso precisa estar definido!


class ActiveManager(models.Manager):
    """Manager que retorna apenas registros não deletados"""
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class BaseModel(models.Model):
    """Modelo base para timestamps, soft delete e histórico"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = ActiveManager()  # Manager padrão
    all_objects = models.Manager()  # Para buscar tudo (incluindo deletados)

    history = HistoricalRecords(inherit=True)  

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Soft Delete"""
        self.__class__.all_objects.filter(id=self.id).update(deleted_at=now())
        self.refresh_from_db()

    def restore(self):
        """Restaura um registro deletado"""
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])

    @property
    def is_deleted(self):
        return self.deleted_at is not None
