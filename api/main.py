from fastapi import FastAPI
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from django.contrib.auth import authenticate
from api.security import create_access_token, create_refresh_token, get_current_user
from django.conf import settings
from core.models import CustomUser, TokenIntegration
import datetime
from django.utils.timezone import now


app = FastAPI(title="NSGates API", version="1.0.0")

# 🔥 Modelo para receber login e senha
class LoginRequest(BaseModel):
    username: str
    password: str

#
@app.get("/")
def read_root():
    return {"message": "FastAPI rodando junto com Django!"}

# Rota Status
@app.get("/status")
def status():
    return {"status": "online"}

# Rota para fazer login e receber um token JWT
@app.post("/auth/login/")
def login(data: LoginRequest):
    """Autenticação de usuários e geração de tokens JWT."""
    user = authenticate(username=data.username, password=data.password)
    
    if not user:
        raise HTTPException(status_code=400, detail="Credenciais inválidas")
    
    # Gerar tokens
    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})
    expires_at = now() + datetime.timedelta(seconds=settings.JWT_EXPIRATION)

    # 🔥 Criar ou atualizar o token no banco
    token_obj, created = TokenIntegration.objects.update_or_create(
        user=user,
        defaults={"access_token": access_token, "refresh_token": refresh_token, "expires_at": expires_at}
    )
    
    return {"access_token": access_token, "refresh_token": refresh_token}

@app.get("/protected/")
def protected_route(user: dict = Depends(get_current_user)):
    """Rota protegida que exige autenticação JWT."""
    return {"message": f"Bem-vindo, {user['sub']}!"}


@app.post("/auth/refresh/")
def refresh_token(user: dict = Depends(get_current_user)):
    """Gera um novo access token com base no refresh token"""
    user_obj = CustomUser.objects.get(username=user["sub"])
    
    # Buscar token no banco
    token_obj = TokenIntegration.objects.filter(user=user_obj).first()
    
    if not token_obj or token_obj.is_expired():
        raise HTTPException(status_code=401, detail="Refresh token expirado ou inválido")
    
    # Criar novo access token
    new_access_token = create_access_token({"sub": user_obj.username})
    token_obj.access_token = new_access_token
    token_obj.expires_at = now() + datetime.timedelta(seconds=settings.JWT_EXPIRATION)
    token_obj.save()

    return {"access_token": new_access_token}


@app.post("/auth/logout/")
def logout(user: dict = Depends(get_current_user)):
    """Remove o token de autenticação do usuário"""
    user_obj = CustomUser.objects.get(username=user["sub"])
    
    # Deletar o token do banco
    TokenIntegration.objects.filter(user=user_obj).delete()

    return {"message": "Logout realizado com sucesso"}
