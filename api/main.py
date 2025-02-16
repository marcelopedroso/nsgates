import os
import django
import importlib
import pkgutil
import logging
import json
from logging.handlers import TimedRotatingFileHandler
import time
from datetime import datetime

from prometheus_fastapi_instrumentator import Instrumentator

# 🔥 Configurar o Django antes de importar modelos
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

# 🔥 Diretório dos logs organizados por API
LOG_DIR = "logs/api"
os.makedirs(LOG_DIR, exist_ok=True)  # 🔥 Garante que o diretório existe

# 🔥 Nome do arquivo de log baseado na data
LOG_FILE = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.log")

handler = TimedRotatingFileHandler(
    LOG_FILE, when="midnight", interval=1, backupCount=7, encoding="utf-8"
)
handler.suffix = "%Y-%m-%d"  # 🔥 Agora cada arquivo terá a data correta no nome

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[handler]  # 🔥 Apenas salva no arquivo, sem exibir no terminal
)

logger = logging.getLogger(__name__)

from fastapi import FastAPI, Depends, Request
from api.auth import verify_token
from api.auth import verify_api_key
from core.routers import user

app = FastAPI(
    title="NSGates API",
    version="1.0.0",
    swagger_ui_parameters={
        "persistAuthorization": True,  # 🔥 Mantém a autenticação após recarregar
        "docExpansion": "none",  # 🔥 Minimiza os endpoints por padrão
        "defaultModelsExpandDepth": -1,  # 🔥 Remove a exibição de modelos automáticos
    }, # 🔥 Garante que o Swagger sempre peça a autenticação
)


from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

# 🔥 Criar o Rate Limiter armazenando os limites em memória
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# 🔥 Tratamento de erro quando atingir o limite
@app.exception_handler(RateLimitExceeded)
async def rate_limit_error(request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Muitas requisições! Tente novamente mais tarde."},
    )


# 🔥 Middleware para logar requisições com tempo de resposta
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()  # ⏳ Marca o início da requisição

    log_data = {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "client": request.client.host,
    }
    logger.info(json.dumps(log_data))  # 🔥 Log da requisição recebida

    response = await call_next(request)  # 🔥 Processa a requisição

    duration = round(time.time() - start_time, 4)  # ⏳ Calcula tempo de resposta

    logger.info(json.dumps({
        "status_code": response.status_code,
        "method": request.method,
        "url": str(request.url),
        "response_time": f"{duration}s",  # 🔥 Tempo de resposta adicionado!
    }))

    return response

@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    """Middleware global para aplicar Rate Limiting corretamente"""
    try:
        response = await limiter.limit("100000/minute")(call_next)(request)
        return response
    except RateLimitExceeded as exc:
        logger.warning(f"🔥 Rate limit atingido: {exc.detail}")
        return JSONResponse(
            status_code=429,
            content={"detail": "Muitas requisições! Tente novamente mais tarde."},
        )


# 🔥 Incluindo os roteadores dinâmicos
def load_routers():
    routers_package = "core.routers"
    
    for _, module_name, _ in pkgutil.iter_modules([os.path.join(os.path.dirname(__file__), "../core/routers")]):
        if module_name not in ["base", "router_factory"]:  # Ignora arquivos base
            module_path = f"{routers_package}.{module_name}"
            module = importlib.import_module(module_path)

            # 🔥 Verifica se o módulo tem `oauth_router` e `apikey_router`
            if hasattr(module, "oauth_router"):
                app.include_router(getattr(module, "oauth_router"))
            if hasattr(module, "apikey_router"):
                app.include_router(getattr(module, "apikey_router"))

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


# 🔥 Criar o monitoramento de métricas
#instrumentator = Instrumentator().instrument(app)
#instrumentator.expose(app, endpoint="/metrics")