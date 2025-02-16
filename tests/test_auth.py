import pytest
import httpx
import os
import environ
from django.conf import settings

@pytest.mark.asyncio
async def test_generate_oauth2_token(test_user, test_oauth_client):
    """Testa a geração de um token OAuth2 usando credenciais válidas"""

    url = "http://127.0.0.1:8000/auth/oauth2/token/"
    data = {
        "grant_type": "password",
        "username": test_user.username,
        "password": "Test@123456",
        "client_id": test_oauth_client.client_id,  # 🔥 Pegamos do teste
        "client_secret": test_oauth_client.client_secret,  # 🔥 Pegamos do teste
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data)

    assert response.status_code == 200, f"Erro ao gerar token: {response.text}"
    token_data = response.json()
    
    assert "access_token" in token_data, "Token de acesso não foi retornado"
    assert "token_type" in token_data and token_data["token_type"] == "Bearer", "Tipo de token inválido"
    
    print(f"✅ Token gerado: {token_data['access_token']}")  # 🔥 Apenas para debug



#@pytest.mark.asyncio
#async def test_generate_oauth2_token():
#    """Testa a geração de um token OAuth2 usando credenciais válidas"""
#    
#    url = "http://127.0.0.1:8000/auth/oauth2/token/"  # URL do token
#    data = {
#        "grant_type": "password",
#        "username": "testuser",
#        "password": "Test@123456",
#        "client_id": os.getenv("OAUTH2_CLIENT_ID"),
#        "client_secret": os.getenv("OAUTH2_CLIENT_SECRET")
#    }
#
#    async with httpx.AsyncClient() as client:
#        response = await client.post(url, data=data)
#
#    assert response.status_code == 200, f"Erro ao gerar token: {response.text}"
#    token_data = response.json()
#    
#    assert "access_token" in token_data, "Token de acesso não foi retornado"
#    assert "token_type" in token_data and token_data["token_type"] == "Bearer", "Tipo de token inválido"
#    
#    print(f"✅ Token gerado: {token_data['access_token']}")  # 🔥 Apenas para debug

