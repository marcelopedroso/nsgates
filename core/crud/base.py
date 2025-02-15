from fastapi import HTTPException
from typing import Type, TypeVar, Generic, List
from django.db import models

ModelType = TypeVar("ModelType", bound=models.Model)  # 🔥 Agora suporta Django ORM

class CRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get_all(self) -> List[ModelType]:  # 🔥 Remove `db`, usa Django ORM diretamente
        return list(self.model.objects.all())

    def get(self, id: str) -> ModelType:
        obj = self.model.objects.filter(id=id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Objeto não encontrado")
        return obj

    def update(self, id: str, update_data: dict) -> ModelType:
        obj = self.get(id)
        for key, value in update_data.items():
            setattr(obj, key, value)
        obj.save()  # 🔥 Agora usa `.save()` do Django ORM
        return obj

    def delete(self, id: str):
        obj = self.get(id)
        obj.delete()  # 🔥 Agora usa `.delete()` do Django ORM
        return {"message": "Objeto deletado com sucesso"}
