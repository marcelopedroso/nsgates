import hashlib
import logging
import secrets
from django.db import models
from django.utils.crypto import get_random_string
from .base import BaseModel
from .user import CustomUser
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)  # 🔥 Para debug no terminal

class APIKey(BaseModel):
    """Modelo para armazenar chaves de API seguras com Soft Delete e UUID"""
    
    name = models.CharField(_("Nome"), max_length=255, unique=True, help_text="Nome do serviço/sistema que usará a API Key.")
    key = models.CharField(_("Chave de API"), max_length=64, unique=True, editable=False)
    expires_at = models.DateTimeField(_("Expira em"), null=True, blank=True, help_text="Defina uma data de expiração opcional.")
    revoked = models.BooleanField(_("Revogado"), default=False, help_text="Se marcado, a API Key não será mais válida.")

    def save(self, *args, **kwargs):
        """Gera uma chave segura apenas ao criar uma nova instância"""
        if not self.key:
            self.key = secrets.token_urlsafe(48)  # 🔥 Gera uma chave segura
            logger.info(f"Nova API Key gerada: {self.key}")  # 🔥 Log para debug
        super().save(*args, **kwargs)

    def __str__(self):
        status = "Ativa" if not self.revoked else "Revogada"
        return f"{self.name} - {status}"



'''
class APIKey(BaseModel):
    """Modelo para armazenar API Keys de forma segura"""
    key = models.CharField(max_length=128, unique=True, editable=False, blank=True)  # 🔥 Permite salvar vazia antes do primeiro save
    name = models.CharField(max_length=100, help_text="Nome identificador da API Key")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def generate_key(self):
        """Gera uma nova API Key e retorna"""
        raw_key = get_random_string(50)
        hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()  # 🔥 Armazena o hash no banco
        self.key = hashed_key
        logger.info(f"Nova API Key gerada: {raw_key}")  # 🔥 Log para debug
        return raw_key

    def save(self, *args, **kwargs):
        """Garante que a chave seja gerada antes de salvar"""
        if not self.key:
            logger.info("Gerando nova API Key antes de salvar...")
            self.generate_key()
        else:
            logger.info("API Key já existente, mantendo a chave atual.")
        super().save(*args, **kwargs)
'''