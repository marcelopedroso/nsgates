#import pytest
#import httpx
#from starlette.testclient import TestClient
#from api.main import app
#from django.contrib.auth import get_user_model
#
#client = TestClient(app)
#
## 🔥 Configuração do Django OAuth2
#DJANGO_OAUTH2_TOKEN_URL = "http://127.0.0.1:8000/auth/oauth2/token/"
#TEST_USERNAME = "testuser"
#TEST_PASSWORD = "testpassword"
#OAUTH2_CLIENT_ID = "TigTIoAaY4wtsQIpV0edWL1t0Ds50D3CtmnM9tUm"
#OAUTH2_CLIENT_SECRET = "k5epAm6aixzYzouFR3h3FSa50J77WfzsD7uyJ8M15BMgJGY9HdTBWvr2m26xnvhkfFxuGvdLfwxpjFHuig8ExpcdgbfvLOelz9p1H3CDBx8XWuLDUgY98aosTepB3UMM"
#
#
#@pytest.fixture
#def create_test_user(django_db_setup, django_db_blocker):
#    """
#    Cria um usuário de teste no banco de dados de teste do Django.
#    """
#    with django_db_blocker.unblock():
#        User = get_user_model()
#        if not User.objects.filter(username=TEST_USERNAME).exists():
#            user = User.objects.create_user(username=TEST_USERNAME, password=TEST_PASSWORD)
#            user.save()
#
#
#@pytest.fixture
#def get_access_token(create_test_user):
#    """
#    Obtém um token OAuth2 válido do Django.
#    """
#    response = httpx.post(
#        DJANGO_OAUTH2_TOKEN_URL,
#        data={
#            "grant_type": "password",
#            "username": TEST_USERNAME,
#            "password": TEST_PASSWORD,
#            "client_id": OAUTH2_CLIENT_ID,
#            "client_secret": OAUTH2_CLIENT_SECRET,
#        },
#        headers={"Content-Type": "application/x-www-form-urlencoded"},
#    )
#    assert response.status_code == 200, f"Erro ao obter token: {response.text}"
#    return response.json()["access_token"]
#
#def test_public_endpoint():
#    """
#    Testa se um endpoint público pode ser acessado sem autenticação.
#    """
#    response = client.get("/api/status/")
#    assert response.status_code == 200
#    assert response.json() == {"status": "online"}
#
#def test_protected_endpoint(get_access_token):
#    """
#    Testa se o endpoint protegido retorna 200 com um token válido.
#    """
#    token = get_access_token
#    response = client.get(
#        "/api/secure-endpoint/",
#        headers={"Authorization": f"Bearer {token}"}
#    )
#    assert response.status_code == 200
#    assert response.json()["message"] == "Acesso autorizado!"
#