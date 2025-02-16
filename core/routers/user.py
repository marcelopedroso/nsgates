from core.routers.router_factory import create_routers
from core.crud.user import user_crud

oauth_router, apikey_router = create_routers(user_crud, "customuser")
