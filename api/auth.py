import os
import httpx
import environ
from fastapi import APIRouter
from fastapi import Depends, HTTPException, Security, Form
from fastapi.security.api_key import APIKeyHeader
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.status import HTTP_401_UNAUTHORIZED
from django.utils.timezone import now
from django.db.models import Q
from asgiref.sync import sync_to_async
from core.models.apikey import APIKey
from core.models.user import CustomUser  # 🔥 Agora buscamos direto do banco
from django.contrib.auth.models import Permission

# 🔥 Carregar variáveis do .env
env = environ.Env()
environ.Env.read_env()

# 🔥 Definir esquemas de autenticação para FastAPI
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
oauth2_scheme = HTTPBearer()

# 🔥 URLs do Django OAuth2
DJANGO_OAUTH2_VALIDATE_URL = os.getenv("DJANGO_OAUTH2_VALIDATE_URL", "http://127.0.0.1:8000/auth/oauth2/introspect/")
OAUTH2_CLIENT_ID = os.getenv("OAUTH2_CLIENT_ID")
OAUTH2_CLIENT_SECRET = os.getenv("OAUTH2_CLIENT_SECRET")


def generate_permissions(model_name: str):
    """
    Gera automaticamente permissões padrão para um modelo.
    Exemplo para `CustomUser` → `view_customuser`, `change_customuser`, `delete_customuser`
    """
    return {
        "view": f"view_{model_name.lower()}",
        "change": f"change_{model_name.lower()}",
        "delete": f"delete_{model_name.lower()}",
    }



async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    """
    Verifica se o token OAuth2 é válido no servidor Django e busca permissões diretamente do banco.
    """
    token = credentials.credentials
    async with httpx.AsyncClient() as client:
        response = await client.post(
            DJANGO_OAUTH2_VALIDATE_URL,
            data={"token": token, "client_id": OAUTH2_CLIENT_ID, "client_secret": OAUTH2_CLIENT_SECRET},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    token_data = response.json()

    # 🔍 Debugando a resposta do Django
    # print(f"🔍 Token Data Recebido: {token_data}")

    if response.status_code != 200 or not token_data.get("active"):
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado")

    username = token_data.get("username")
    if not username:
        raise HTTPException(status_code=403, detail="Usuário não encontrado no token")

    # 🔥 Buscar permissões diretamente do banco (SEM API DO DJANGO)
    def get_permissions():
        try:
            user = CustomUser.objects.get(username=username)
            return list(user.user_permissions.values_list("codename", flat=True))
        except CustomUser.DoesNotExist:
            return None

    user_permissions = await sync_to_async(get_permissions)()  # 🔥 Executa de forma assíncrona

    if user_permissions is None:
        raise HTTPException(status_code=403, detail="Usuário não encontrado no banco")

    token_data["permissions"] = user_permissions  # Adiciona permissões ao token

    return token_data  # Agora inclui permissões


def check_permission(required_permission: str):
    """
    Middleware para verificar se o usuário tem uma permissão específica.
    """
    async def has_permission(user_data: dict = Depends(verify_token)):
        user_permissions = user_data.get("permissions", [])
        if required_permission not in user_permissions:
            raise HTTPException(status_code=403, detail=f"Permissão `{required_permission}` necessária")
        return user_data
    return has_permission


async def verify_api_key(api_key: str = Security(api_key_header)):
    """Valida a API Key de forma eficiente sem SQL direto"""

    if not api_key:
        raise HTTPException(status_code=403, detail="API Key ausente")

    # 🔥 Consulta ao banco de forma síncrona para evitar bloqueio no FastAPI
    def get_api_key():
        return APIKey.objects.filter(
            Q(key=api_key, revoked=False) & (Q(expires_at__gte=now()) | Q(expires_at__isnull=True))
        ).first()

    key_instance = await sync_to_async(get_api_key)()  # 🔥 Executa de forma assíncrona

    if not key_instance:
        raise HTTPException(status_code=403, detail="API Key inválida ou expirada")

    return key_instance  # Retorna o objeto da API Key


# 🔥 URLs do Django OAuth2
DJANGO_OAUTH2_TOKEN_URL = os.getenv("DJANGO_OAUTH2_TOKEN_URL", "http://127.0.0.1:8000/auth/oauth2/token/")
router = APIRouter()
@router.post("/auth/token/")
async def generate_oauth2_token(
    grant_type: str = Form(...),
    username: str = Form(None),
    password: str = Form(None),
    client_id: str = Form(...),
    client_secret: str = Form(...)
):
    """
    🔥 Rota do FastAPI para gerar token OAuth2 via Django.
    """

    async with httpx.AsyncClient() as client:
        response = await client.post(
            DJANGO_OAUTH2_TOKEN_URL,
            data={
                "grant_type": grant_type,
                "username": username,
                "password": password,
                "client_id": client_id,
                "client_secret": client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    return response.json()