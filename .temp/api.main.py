from fastapi import APIRouter
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from django.contrib.auth import authenticate
from django.conf import settings
from core.models import CustomUser
import datetime
from django.utils.timezone import now
from django.core.exceptions import ObjectDoesNotExist
from sqlalchemy.orm import Session
from core.database import get_db
import os


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


@app.get("/protected/")
def protected_route(user: dict = Depends(get_current_user)):
    """Rota protegida que exige autenticação JWT."""
    return {"message": f"Bem-vindo, {user['sub']}!"}



# 🔥 Nova rota para exibir o relatório de testes
@app.get("/test_report")
def get_test_report():
    """Retorna o relatório de testes HTML se existir."""
    if os.path.exists(REPORT_PATH):
        return FileResponse(REPORT_PATH, media_type="text/html")
    return {"error": "Relatório de testes não encontrado. Execute `python runtests.py` primeiro."}