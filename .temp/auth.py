import os
import httpx
import hashlib
from fastapi import Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.status import HTTP_401_UNAUTHORIZED
from core.models.apikey import APIKey
from django.utils.timezone import now
from django.db import models
from asgiref.sync import sync_to_async
from django.db.models import Q

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# 🔥 Definir um esquema único para autenticação no FastAPI
oauth2_scheme = HTTPBearer()

# 🔥 URLs do Django OAuth2
DJANGO_OAUTH2_VALIDATE_URL = os.getenv("DJANGO_OAUTH2_VALIDATE_URL", "http://127.0.0.1:8000/auth/oauth2/introspect/")
OAUTH2_CLIENT_ID = os.getenv("OAUTH2_CLIENT_ID")
OAUTH2_CLIENT_SECRET = os.getenv("OAUTH2_CLIENT_SECRET")


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    """
    Verifica se o token OAuth2 é válido no servidor Django.
    """
    token = credentials.credentials
    print(f"🔍 Verificando token: {token}")  # 🔥 Adiciona um log para depuração

    async with httpx.AsyncClient() as client:
        response = await client.post(
            DJANGO_OAUTH2_VALIDATE_URL,
            data={
                "token": token,
                "client_id": OAUTH2_CLIENT_ID,
                "client_secret": OAUTH2_CLIENT_SECRET,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    print(f"🔍 Resposta do Django: {response.status_code}, {response.text}")  # 🔥 Depuração

    if response.status_code != 200:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = response.json()
    if not token_data.get("active"):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Token inativo",
        )

    return token_data  # Retorna os dados do usuário autenticado


async def verify_api_key(api_key: str = Security(api_key_header)):
    """Valida a API Key recebida no cabeçalho"""

    if not api_key:
        raise HTTPException(status_code=403, detail="API Key ausente")

    # 🔥 Evita chamada direta ao ORM dentro de um contexto async
    def get_api_key():
        return APIKey.objects.filter(
            Q(key=api_key, revoked=False) & (Q(expires_at__gte=now()) | Q(expires_at__isnull=True))
        ).first()

    key_instance = await sync_to_async(get_api_key)()  # 🔥 Correto para contexto assíncrono

    if not key_instance:
        raise HTTPException(status_code=403, detail="API Key inválida ou expirada")

    return key_instance  # Retorna o objeto da API Key
