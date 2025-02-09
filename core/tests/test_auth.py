import pytest
from fastapi.testclient import TestClient
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from core.models import TokenIntegration, CustomUser
from api.security import create_access_token, create_refresh_token  # ✅ Importa apenas o necessário
from core.asgi import application  # ✅ Importa `application` do `asgi.py` para evitar loop

client = TestClient(application)  # ✅ Usa `application`, não `app`
User = get_user_model()

@pytest.fixture
def test_user(db):
    """Cria um usuário de teste no banco de dados com senha corretamente hasheada"""
    user = User.objects.create_user(username="testuser", email="test@example.com")
    user.set_password("testpassword")  # 🔥 Garante que a senha está hasheada
    user.save()
    return user

@pytest.fixture(autouse=True)
def cleanup_tokens(db):
    """Limpa tokens antes de cada teste"""
    TokenIntegration.objects.all().delete()

def test_login_success(test_user):
    """Testa login com credenciais corretas."""
    response = client.post("/api/auth/login/", json={"username": "testuser", "password": "testpassword"})

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()

'''
def test_login_fail():
    """Testa login com credenciais incorretas."""
    response = client.post("/api/auth/login/", json={"username": "wronguser", "password": "wrongpassword"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Credenciais inválidas"}

def test_protected_route_without_token():
    """Testa acesso à rota protegida sem enviar token."""
    response = client.get("/api/protected/")
    assert response.status_code == 401  # ✅ Corrigimos para 401 Unauthorized

def test_protected_route_with_token(test_user):
    """Testa acesso à rota protegida com um token válido."""
    login_response = client.post("/api/auth/login/", json={"username": "testuser", "password": "testpassword"})
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    response = client.get("/api/protected/", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["message"] == "Bem-vindo, testuser!"

def test_refresh_token(test_user):
    """Testa refresh token."""
    login_response = client.post("/api/auth/login/", json={"username": "testuser", "password": "testpassword"})
    assert login_response.status_code == 200

    refresh_token = login_response.json()["refresh_token"]
    response = client.post("/api/auth/refresh/", headers={"Authorization": f"Bearer {refresh_token}"})

    assert response.status_code == 200
    assert "access_token" in response.json()

def test_logout(test_user):
    """Testa logout e tentativa de acesso após logout."""
    login_response = client.post("/api/auth/login/", json={"username": "testuser", "password": "testpassword"})
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # Realiza logout
    response = client.post("/api/auth/logout/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"message": "Logout realizado com sucesso"}

    # Testa se o token foi removido e o usuário não pode mais acessar
    response = client.get("/api/protected/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401  # 🔥 Agora retorna corretamente "Não autorizado"
    
'''