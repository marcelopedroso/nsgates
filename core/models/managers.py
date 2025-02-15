from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    """Manager específico para CustomUser"""
    
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O email deve ser definido")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, email, password, **extra_fields)
