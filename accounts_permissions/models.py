from django.db import models
from core.models import BaseModel  # 🔥 Importando BaseModel corretamente
from django.contrib.auth.models import Permission
from simple_history.models import HistoricalRecords  # 🔥 Importando histórico

class CustomGroup(BaseModel):
    """Modelo personalizado para substituir auth_group com UUID"""
    name = models.CharField(max_length=150, unique=True)
    permissions = models.ManyToManyField(Permission, related_name="custom_groups", blank=True)
    
    history = HistoricalRecords()  # 🔥 Rastreia mudanças no grupo

    class Meta:
        verbose_name = "Group"
        verbose_name_plural = "Groups"

    def __str__(self):
        return self.name

class CustomPermission(BaseModel):
    """Modelo personalizado para substituir auth_permission com UUID"""
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey("contenttypes.ContentType", on_delete=models.CASCADE)
    codename = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"

    def __str__(self):
        return self.name
