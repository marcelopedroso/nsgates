import os
import jwt
import datetime
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# 🔥 Configuração para garantir que Django esteja configurado antes de acessar `settings`
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django
django.setup()

from django.conf import settings  # 🔥 Agora podemos importar `settings`

# 🔥 Configuração de hashing de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 🔥 Função para gerar um JWT (Access Token)
def create_access_token(data: dict, expires_delta: int = None):
    """Gera um token JWT com os dados do usuário."""
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(
        seconds=expires_delta or settings.JWT_EXPIRATION
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

# 🔥 Função para gerar um Refresh Token
def create_refresh_token(data: dict):
    """Gera um Refresh Token com validade maior."""
    return create_access_token(data, settings.JWT_REFRESH_EXPIRATION)

# 🔥 Função para verificar um token JWT
def verify_token(token: str):
    """Verifica se um token JWT é válido."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload  # Retorna os dados do usuário
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

# 🔥 Middleware para verificar tokens JWT nas requisições
security = HTTPBearer()

def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
    """Middleware que protege rotas autenticadas."""
    payload = verify_token(token.credentials)
    return payload
