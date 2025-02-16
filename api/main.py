import os
import django

# 🔥 Configurar o Django antes de importar modelos
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from fastapi import FastAPI, Depends
from api.auth import verify_token
from api.auth import verify_api_key

app = FastAPI(
    title="NSGates API",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": False},  # 🔥 Garante que o Swagger sempre peça a autenticação
)

from core.routers import user
# 🔥 Adicionando rotas protegidas
app.include_router(user.oauth_router)   # /api/o/users/ (OAuth2)
app.include_router(user.apikey_router)  # /api/k/users/ (API Key)

# Rota Status
@app.get("/status")
def status():
    return {"status": "online"}

@app.get("/secure-endpoint/")
async def secure_endpoint(user_data: dict = Depends(verify_token)):
    return {"message": "Acesso autorizado!", "user": user_data}


@app.get("/secure-data/")
async def secure_data(api_key=Depends(verify_api_key)):
    return {"message": "Acesso autorizado via API Key!", "api_key_owner": api_key.name}