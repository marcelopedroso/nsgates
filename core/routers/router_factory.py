from fastapi import APIRouter, Depends, HTTPException
from api.auth import check_permission, verify_api_key, generate_permissions, verify_token
from core.routers.base import RouterBase
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from simple_history.utils import update_change_reason
from core.models import CustomUser  # 🔥 Importar o modelo do usuário

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

    @oauth_router.patch("/{item_id}")
    async def update_object_oauth(item_id: str, data: dict, user=Depends(verify_token)):
        """
        Atualiza um objeto e salva no histórico o usuário autenticado via OAuth2.
        """
        try:
            obj = await sync_to_async(model_crud.get)(item_id)

            # 🔄 Atualiza os campos do objeto
            for key, value in data.items():
                setattr(obj, key, value)

            def save_with_history():
                # 🔥 Buscar o usuário correto no banco de dados
                history_user = CustomUser.objects.filter(username=user["username"]).first()

                if not history_user:
                    raise ValueError(f"Usuário {user['username']} não encontrado!")

                obj._history_user = history_user  # ✅ Passar a instância correta
                obj.save()  # 🔥 Salvar primeiro para garantir que o histórico existe
                update_change_reason(obj, f"Modificado por {user['username']}")  

            await sync_to_async(save_with_history)()
            
            return {"message": "Registro atualizado!", "modificado_por": user["username"]}
        
        except ObjectDoesNotExist:
            raise HTTPException(status_code=404, detail="Objeto não encontrado")

    @oauth_router.delete("/{item_id}", dependencies=[Depends(check_permission(permissions["delete"]))])
    async def delete_object_oauth(item_id: str, user=Depends(verify_token)):
        """
        Exclui um objeto e salva no histórico o usuário autenticado via OAuth2.
        """
        try:
            obj = await sync_to_async(model_crud.get)(item_id)

            def delete_with_history():
                history_user = CustomUser.objects.filter(username=user["username"]).first()

                if not history_user:
                    raise ValueError(f"Usuário {user['username']} não encontrado!")

                obj._history_user = history_user
                obj.save()  # 🔥 Garante que o histórico existe antes de deletar
                update_change_reason(obj, f"Removido por {user['username']}")
                obj.delete()

            await sync_to_async(delete_with_history)()
            
            return {"message": "Registro excluído!", "excluido_por": user["username"]}
        
        except ObjectDoesNotExist:
            raise HTTPException(status_code=404, detail="Objeto não encontrado")

    # 🔑 Criando roteador API Key (acesso total)
    apikey_router = APIRouter(prefix=f"/k/{model_name}s", tags=[f"{model_name.capitalize()}s (API Key)"], dependencies=[Depends(verify_api_key)])

    @apikey_router.patch("/{item_id}")
    async def update_object_apikey(item_id: str, data: dict, api_key=Depends(verify_api_key)):
        """
        Atualiza um objeto e salva no histórico o nome da API Key usada.
        """
        try:
            obj = await sync_to_async(model_crud.get)(item_id)

            # 🔄 Atualiza os campos do objeto
            for key, value in data.items():
                setattr(obj, key, value)

            def save_with_history():
                obj._history_user = None  # 🔥 API Key não tem usuário associado
                obj.save()  # 🔥 Salvar primeiro para garantir que o histórico existe
                update_change_reason(obj, f"Modificado via API Key {api_key.name}")

            await sync_to_async(save_with_history)()

            return {"message": "Registro atualizado!", "modificado_por": f"API Key: {api_key.name}"}

        except ObjectDoesNotExist:
            raise HTTPException(status_code=404, detail="Objeto não encontrado")

    apikey_router.include_router(router)

    return oauth_router, apikey_router