import pytest
from fastapi.testclient import TestClient
from api.main import app
from unittest.mock import patch
from core.models.user import CustomUser
from oauth2_provider.models import Application
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password


@pytest.fixture
def test_user(db):
    """Cria um usuário de teste no banco de dados de TESTE"""
    from django.contrib.auth import get_user_model
    from django.contrib.auth.hashers import make_password

    User = get_user_model()
    
    user, created = User.objects.get_or_create(
        username="testuser",
        defaults={
            "password": make_password("Test@123456"),
            "email": "testuser@email.com",
            "is_active": True
        }
    )

    if not created:
        user.password = make_password("Test@123456")  # 🔥 Garante que a senha está correta
        user.is_active = True
        user.save()
    
    return user


@pytest.fixture
def test_oauth_client(db, django_user_model):
    """Cria um client_id e client_secret de teste para autenticação OAuth2"""

    user = django_user_model.objects.create(username="fakeuser")

    app, created = Application.objects.get_or_create(
        name="Test App",
        client_id="test-client-id",
        client_type=Application.CLIENT_CONFIDENTIAL,
        authorization_grant_type=Application.GRANT_PASSWORD,
        user=user
    )

    if created:
        # 🔥 Atualizando diretamente via QuerySet para evitar hashing automático
        Application.objects.filter(id=app.id).update(client_secret="test-client-secret")
        app.refresh_from_db()  # 🔥 Recarrega para pegar o novo valor

    print(f"✅ Test OAuth2 Client Criado: client_id={app.client_id}, client_secret={app.client_secret}")

    return app



@pytest.fixture(scope="module")
def test_client():
    """Cliente de teste para simular requisições HTTP na API"""
    with TestClient(app) as client:
        yield client

def test_get_users_oauth(test_client, headers_oauth, test_user):
    """Testa a rota GET /api/o/users/ com autenticação OAuth2"""
    response = test_client.get("/api/o/users/", headers=headers_oauth)


    print(f"🔥 DEBUG: Response status {response.status_code}, Body: {response.json()}")  # Debug temporário
    assert response.status_code == 200  # 🔥 Esperamos sucesso (200 OK)


@pytest.fixture
def mock_verify_token():
    """Mocka a verificação do token para testes"""
    with patch("api.auth.verify_token", return_value={"username": "testuser", "permissions": ["view_customuser"]}):
        yield
