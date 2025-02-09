import pytest
from django.utils.timezone import now
from core.models import CustomUser

@pytest.mark.django_db
def test_create_user():
    """Testa a criação de um usuário"""
    user = CustomUser.objects.create(username="testuser", email="test@example.com")
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.deleted_at is None  # Deve ser None ao criar

@pytest.mark.django_db
def test_soft_delete_user():
    """Testa o soft delete de um usuário"""
    user = CustomUser.objects.create(username="testuser", email="test@example.com")
    user.delete()

    assert user.deleted_at is not None  # Deve ter um timestamp de deleção
    assert CustomUser.objects.filter(username="testuser").exists() is False  # ✅ Agora passa
    assert CustomUser.all_objects.filter(username="testuser").exists() is True  # ✅ Ainda está no banco


@pytest.mark.django_db
def test_restore_user():
    """Testa a restauração de um usuário deletado"""
    user = CustomUser.objects.create(username="testuser", email="test@example.com")
    user.delete()
    user.restore()

    assert user.deleted_at is None  # Deve voltar a ser None
    assert CustomUser.objects.filter(username="testuser").exists() is True  # Deve aparecer novamente

@pytest.mark.django_db
def test_history_tracking():
    """Testa se o histórico está sendo salvo corretamente"""
    user = CustomUser.objects.create(username="testuser", email="test@example.com")
    user.email = "updated@example.com"
    user.save()

    history = user.history.all()
    assert history.count() == 2  # Deve ter pelo menos 2 versões (criação + update)
    assert history.first().email == "updated@example.com"
    assert history.last().email == "test@example.com"  # Versão inicial

