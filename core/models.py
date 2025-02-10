# models.py 
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now
from simple_history.models import HistoricalRecords
from simple_history.utils import update_change_reason

from django.contrib.auth.models import BaseUserManager

class ActiveManager(models.Manager):
    """Manager que retorna apenas registros não deletados"""
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)
    
    
class CustomUserManager(BaseUserManager):
    """Manager específico para CustomUser, respeitando Soft Delete"""
    
    def get_queryset(self):
        """Retorna apenas usuários que não foram deletados"""
        return super().get_queryset().filter(deleted_at__isnull=True)

    def create_user(self, username, email, password=None, **extra_fields):
        """Cria um usuário normal"""
        if not email:
            raise ValueError("O email deve ser definido")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """Cria um superusuário"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, email, password, **extra_fields)




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
    """Modelo de usuário customizado herdando BaseModel"""

    objects = CustomUserManager()  # ✅ Manager padrão agora exclui deletados
    all_objects = models.Manager()  # ✅ Para buscar usuários deletados também

    def delete(self, using=None, keep_parents=False):
        """Soft Delete - Marca como deletado"""
        self.deleted_at = now()
        self.save(update_fields=["deleted_at"])

    def restore(self):
        """Restaura um usuário deletado"""
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    

class TokenIntegration(BaseModel):
    """Armazena os tokens JWT dos usuários autenticados"""
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="token")
    access_token = models.TextField()
    refresh_token = models.TextField()
    expires_at = models.DateTimeField()  # Data de expiração do access token
    
    class Meta:
        permissions = [
            ("renew_token", "Can Renew Token"),
        ]

    def is_expired(self):
        """Verifica se o token de acesso já expirou"""
        return self.expires_at < now()
    
    def __str__(self):
        return f"Token de {self.user.username}"
