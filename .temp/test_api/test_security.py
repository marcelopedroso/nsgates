import pytest
import httpx
from starlette.testclient import TestClient
from django.contrib.auth import get_user_model
from api.main import app

BASE_URL = "http://127.0.0.1:8000/api"
DJANGO_OAUTH2_TOKEN_URL = "http://127.0.0.1:8000/auth/oauth2/token/"

TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpassword"
TEST_EMAIL = "test@example.com"
OAUTH2_CLIENT_ID = "TigTIoAaY4wtsQIpV0edWL1t0Ds50D3CtmnM9tUm"
OAUTH2_CLIENT_SECRET = "k5epAm6aixzYzouFR3h3FSa50J77WfzsD7uyJ8M15BMgJGY9HdTBWvr2m26xnvhkfFxuGvdLfwxpjFHuig8ExpcdgbfvLOelz9p1H3CDBx8XWuLDUgY98aosTepB3UMM"

client = TestClient(app)

@pytest.fixture
def create_test_user(django_db_setup, django_db_blocker):
    """Cria um usuário de teste no banco de dados de testes do Django."""
    with django_db_blocker.unblock():
        User = get_user_model()
        if not User.objects.filter(username=TEST_USERNAME).exists():
            user = User.objects.create_user(
                username=TEST_USERNAME,
                email=TEST_EMAIL,
                password=TEST_PASSWORD
            )
            user.save()

@pytest.fixture
def mock_get_access_token(create_test_user, monkeypatch):
    """Mocka a obtenção do token OAuth2 para evitar dependência do servidor Django."""
    def mock_token_request(*args, **kwargs):
        class MockResponse:
            status_code = 200
            def json(self):
                return {"access_token": "mocked_token"}
        return MockResponse()
    
    monkeypatch.setattr(httpx, "post", mock_token_request)
    return "mocked_token"

def test_access_with_invalid_token():
    """Testa se um token inválido retorna erro 401 Unauthorized."""
    response = client.get(
        f"{BASE_URL}/secure-endpoint/",
        headers={"Authorization": "Bearer INVALIDO123"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Token inválido ou expirado"

def test_access_without_token():
    """Testa se acessar um endpoint protegido sem token retorna erro 401."""
    response = client.get(f"{BASE_URL}/secure-endpoint/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_access_with_valid_token(mock_get_access_token):
    """Testa se um token válido permite acessar o endpoint."""
    token = mock_get_access_token
    response = client.get(
        f"{BASE_URL}/secure-endpoint/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Acesso autorizado!"
