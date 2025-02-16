from fastapi import APIRouter, Depends
from api.auth import check_permission, verify_api_key, generate_permissions
from core.routers.base import RouterBase

def create_routers(model_crud, model_name: str):
    """
    Gera automaticamente os roteadores para um modelo.
    - `model_crud`: O CRUD do modelo (ex: `user_crud`)
    - `model_name`: Nome do modelo (ex: `"customuser"`)
    """
    permissions = generate_permissions(model_name)

    # 🔥 Criando roteador base
    router = RouterBase(model_crud, "").router

    # 🔐 Criando roteador OAuth2 com permissões dinâmicas
    oauth_router = APIRouter(prefix=f"/o/{model_name}s", tags=[f"{model_name.capitalize()}s (OAuth)"])
    oauth_router.get("/", dependencies=[Depends(check_permission(permissions["view"]))])(router.routes[0].endpoint)
    oauth_router.get("/{item_id}", dependencies=[Depends(check_permission(permissions["view"]))])(router.routes[1].endpoint)
    oauth_router.patch("/{item_id}", dependencies=[Depends(check_permission(permissions["change"]))])(router.routes[2].endpoint)
    oauth_router.delete("/{item_id}", dependencies=[Depends(check_permission(permissions["delete"]))])(router.routes[3].endpoint)

    # 🔑 Criando roteador API Key (acesso total)
    apikey_router = APIRouter(prefix=f"/k/{model_name}s", tags=[f"{model_name.capitalize()}s (API Key)"], dependencies=[Depends(verify_api_key)])
    apikey_router.include_router(router)

    return oauth_router, apikey_router
