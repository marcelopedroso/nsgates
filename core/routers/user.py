from core.routers.base import RouterBase
from core.crud.user import user_crud
from api.auth import verify_token, verify_api_key, check_permission
from fastapi import Depends, APIRouter

user_router = RouterBase(user_crud, "").router

oauth_router = APIRouter(prefix="/o/users", tags=["Users (OAuth)"])
apikey_router = APIRouter(prefix="/k/users", tags=["Users (API Key)"], dependencies=[Depends(verify_api_key)])

# 🔥 Aplicando permissões específicas nas rotas protegidas por OAuth2
oauth_router.get("/", dependencies=[Depends(check_permission("view_customuser"))])(user_router.routes[0].endpoint)
oauth_router.get("/{item_id}", dependencies=[Depends(check_permission("view_customuser"))])(user_router.routes[1].endpoint)
oauth_router.patch("/{item_id}", dependencies=[Depends(check_permission("change_customuser"))])(user_router.routes[2].endpoint)
oauth_router.delete("/{item_id}", dependencies=[Depends(check_permission("delete_customuser"))])(user_router.routes[3].endpoint)

apikey_router.include_router(user_router)  # 🔑 API Key tem acesso total
