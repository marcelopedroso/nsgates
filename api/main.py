import os
import django

# 🔥 Configurar o Django antes de importar modelos
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from fastapi import FastAPI, Depends
from api.auth import verify_token

app = FastAPI(
    title="NSGates API",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": False},  # 🔥 Garante que o Swagger sempre peça a autenticação
)


# Rota Status
@app.get("/status")
def status():
    return {"status": "online"}

@app.get("/secure-endpoint/")
async def secure_endpoint(user_data: dict = Depends(verify_token)):
    return {"message": "Acesso autorizado!", "user": user_data}



