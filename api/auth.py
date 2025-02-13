import os
import httpx
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.status import HTTP_401_UNAUTHORIZED

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
