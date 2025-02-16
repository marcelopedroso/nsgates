from fastapi import APIRouter
from core.crud.base import CRUDBase

class RouterBase:
    def __init__(self, model_crud: CRUDBase, prefix: str):
        self.model_crud = model_crud
        self.router = APIRouter(prefix=prefix)  # 🔥 Removemos a definição fixa de tags

        @self.router.get("/")
        def get_all():
            return self.model_crud.get_all()

        @self.router.get("/{item_id}")
        def get_one(item_id: str):
            return self.model_crud.get(item_id)

        @self.router.patch("/{item_id}")
        def update_one(item_id: str, update_data: dict):
            return self.model_crud.update(item_id, update_data)

        @self.router.delete("/{item_id}")
        def delete_one(item_id: str):
            return self.model_crud.delete(item_id)
