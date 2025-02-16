import os
import django
import importlib
import pkgutil

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

# 🔥 Incluindo os roteadores dinâmicos
#app.include_router(user.oauth_router, prefix="/api")   # 🔐 OAuth2
#app.include_router(user.apikey_router, prefix="/api")  # 🔑 API Key
def load_routers():
    routers_package = "core.routers"
    
    for _, module_name, _ in pkgutil.iter_modules([os.path.join(os.path.dirname(__file__), "../core/routers")]):
        if module_name not in ["base", "router_factory"]:  # Ignora arquivos base
            module_path = f"{routers_package}.{module_name}"
            module = importlib.import_module(module_path)

            # 🔥 Verifica se o módulo tem `oauth_router` e `apikey_router`
            if hasattr(module, "oauth_router"):
                app.include_router(getattr(module, "oauth_router"), prefix="/api")
            if hasattr(module, "apikey_router"):
                app.include_router(getattr(module, "apikey_router"), prefix="/api")

# 🔥 Carregar roteadores automaticamente
load_routers()


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