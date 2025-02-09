import os
import django
from fastapi.middleware.cors import CORSMiddleware
from django.core.asgi import get_asgi_application
from fastapi import FastAPI
from django.core.handlers.asgi import ASGIHandler
from fastapi.staticfiles import StaticFiles  # 🔥 Para servir arquivos estáticos corretamente
from api.main import app as fastapi_app  # 🔥 Importando FastAPI do `api/main.py`

# 🔥 Configurar Django antes de inicializar o ASGI
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

# 🔥 Criar a aplicação Django ASGI
django_asgi_app = ASGIHandler()

# 🔥 Configurar CORS no FastAPI (se necessário para chamadas externas)
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 Montar FastAPI na rota `/api`
app = FastAPI(title="NSGates ASGI")
app.mount("/api", fastapi_app)
# 🔥 Montar Django na raiz `/`
app.mount("/", django_asgi_app)



# 🔥 Definir FastAPI como a aplicação ASGI principal
application = app
