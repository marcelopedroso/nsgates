from django.http import JsonResponse
import os

class BlockDirectAccessMiddleware:
    """Middleware para bloquear acessos diretos ao Django por URLs protegidas"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Se a requisição é para uma URL protegida e não vem do FastAPI, bloqueia
        protected_paths = ["/auth/oauth2/token/", "/admin/"]
        allowed_origin = os.getenv("FASTAPI_HOST", "http://127.0.0.1:8001")  # Defina o host da FastAPI

        if request.path in protected_paths:
            referer = request.META.get("HTTP_REFERER", "")
            if allowed_origin not in referer:
                return JsonResponse({"error": "Acesso não autorizado"}, status=403)

        return self.get_response(request)
