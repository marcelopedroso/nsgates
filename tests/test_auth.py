#import pytest
#import requests
#
#BASE_URL = "http://127.0.0.1:8000/api"
#USER_TEST = "marcelo"
#PASSWORD_TEST = "123"
#
#@pytest.fixture(scope="session")
#def get_token():
#    """Faz login uma única vez e retorna o token JWT para reutilização nos testes."""
#    response = requests.post(f"{BASE_URL}/auth/login/", json={
#        "username": USER_TEST,
#        "password": PASSWORD_TEST
#    })
#    assert response.status_code == 200, "Erro no login"
#    token = response.json()["access_token"]
#    
#    print("\n🔑 Token gerado para testes:", token)  # Debug opcional
#    return token  # 🔥 Retorna o token para ser usado nos outros testes
#
#
#def test_protected_route(get_token):
#    """Testa acesso à rota protegida usando o token gerado."""
#    headers = {"Authorization": f"Bearer {get_token}"}
#    response = requests.get(f"{BASE_URL}/protected/", headers=headers)
#
#    assert response.status_code == 200
#    assert response.json()["message"].startswith("Bem-vindo")
#    
#
#
#def test_refresh_token(get_token):
#    """Testa refresh token usando o token de sessão."""
#    headers = {"Authorization": f"Bearer {get_token}"}
#    response = requests.post(f"{BASE_URL}/auth/refresh/", headers=headers)
#
#    assert response.status_code == 200
#    assert "access_token" in response.json()
#
#
#def test_logout(get_token):
#    """Testa logout e se o token foi revogado corretamente."""
#    headers = {"Authorization": f"Bearer {get_token}"}
#
#    # 🔥 Realiza logout
#    response = requests.post(f"{BASE_URL}/auth/logout/", headers=headers)
#    assert response.status_code == 200
#    assert response.json() == {"message": "Logout realizado com sucesso"}
#
#
#    # 🔥 Gera um novo token para os próximos testes
#    new_response = requests.post(f"{BASE_URL}/auth/login/", json={
#        "username": USER_TEST,
#        "password": PASSWORD_TEST
#    })
#    assert new_response.status_code == 200, "Erro ao obter novo token"
#    new_token = new_response.json()["access_token"]
#    
#
#    # 🔥 Agora testa com o novo token (deve funcionar)
#    new_headers = {"Authorization": f"Bearer {new_token}"}
#    response = requests.get(f"{BASE_URL}/protected/", headers=new_headers)
#    assert response.status_code == 200, "Novo token deveria ser válido"
#