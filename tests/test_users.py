import pytest
from fastapi.testclient import TestClient

# 🔥 Dados de teste (mock de API Key e Token OAuth2)
API_KEY = "test-api-key"
OAUTH_TOKEN = "test-oauth-token"

@pytest.fixture
def headers_oauth():
    """Mock de headers para autenticação OAuth2"""
    return {"Authorization": f"Bearer {OAUTH_TOKEN}"}

@pytest.fixture
def headers_api_key():
    """Mock de headers para autenticação via API Key"""
    return {"X-API-Key": API_KEY}

def test_get_users_oauth(test_client: TestClient, headers_oauth, test_user, mock_verify_token):
    """Testa se a API retorna usuários autenticados com OAuth2"""
    response = test_client.get("/api/o/users/", headers=headers_oauth)
    assert response.status_code == 200  # 🔥 Esperamos sucesso (200 OK)
    assert isinstance(response.json(), list)  # Deve retornar uma lista de usuários


def test_get_users_api_key(test_client: TestClient, headers_api_key):
    """Testa se a API retorna usuários autenticados com API Key"""
    response = test_client.get("/api/k/users/", headers=headers_api_key)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_patch_user_oauth(test_client: TestClient, headers_oauth):
    """Testa atualização de usuário via PATCH autenticado com OAuth2"""
    user_id = "fake-user-id"  # 🔥 Mock de ID
    payload = {"first_name": "Novo Nome"}
    
    response = test_client.patch(f"/api/o/users/{user_id}", json=payload, headers=headers_oauth)
    
    assert response.status_code in [200, 404]  # 🔥 Depende se o usuário existir ou não
    if response.status_code == 200:
        assert response.json()["first_name"] == "Novo Nome"

def test_delete_user_oauth(test_client: TestClient, headers_oauth):
    """Testa exclusão de usuário via DELETE autenticado com OAuth2"""
    user_id = "fake-user-id"  # 🔥 Mock de ID
    
    response = test_client.delete(f"/api/o/users/{user_id}", headers=headers_oauth)
    
    assert response.status_code in [204, 404]  # 204 (sucesso), 404 (não encontrado)
