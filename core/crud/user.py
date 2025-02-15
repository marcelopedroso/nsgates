from core.models.user import CustomUser
from core.crud.base import CRUDBase

user_crud = CRUDBase(CustomUser)
