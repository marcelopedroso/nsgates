from fastapi import APIRouter
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from django.contrib.auth import authenticate
from api.security import create_access_token, create_refresh_token, get_current_user
from django.conf import settings
from core.models import CustomUser, TokenIntegration
import datetime
from django.utils.timezone import now
from django.core.exceptions import ObjectDoesNotExist
from sqlalchemy.orm import Session
from core.database import get_db
import os
#from datetime import datetime, timedelta


REPORT_PATH = os.path.abspath("reports/test_report.html")

router = APIRouter()

#TOKEN_EXPIRATION = int(os.getenv("JWT_EXPIRATION", 3600))


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

    # 🔥 Deletar o token do banco
    deleted, _ = TokenIntegration.objects.filter(user=user_obj).delete()

    if deleted:
        return {"message": "Logout realizado com sucesso"}
    
    raise HTTPException(status_code=400, detail="Erro ao deslogar usuário")


@app.post("/auth/admin/generate-token/")
def admin_generate_token(username: str, db: Session = Depends(get_db)):
    """
    🔒 Rota segura para o Django Admin gerar um token para um usuário autenticado.
    """
    try:
        user = CustomUser.objects.get(username=username)  # Usando Django ORM
        
        user_data = {"sub": user.username}

        access_token = create_access_token(user_data)
        refresh_token = create_refresh_token(user_data)
        expires_at = now() + datetime.timedelta(seconds=settings.JWT_EXPIRATION)
        
        token_obj, created = TokenIntegration.objects.update_or_create(
        user=user,
        defaults={"access_token": access_token, "refresh_token": refresh_token, "expires_at": expires_at}
    )
        
    except ObjectDoesNotExist:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return {"access_token": access_token , "refresh_token": refresh_token}


# 🔥 Nova rota para exibir o relatório de testes
@app.get("/test_report")
def get_test_report():
    """Retorna o relatório de testes HTML se existir."""
    if os.path.exists(REPORT_PATH):
        return FileResponse(REPORT_PATH, media_type="text/html")
    return {"error": "Relatório de testes não encontrado. Execute `python runtests.py` primeiro."}