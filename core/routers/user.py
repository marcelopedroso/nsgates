from core.routers.base import RouterBase
from core.crud.user import user_crud
from core.database import get_db

router = RouterBase(user_crud, "/users", "Users").router
