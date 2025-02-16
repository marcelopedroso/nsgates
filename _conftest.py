import os
import pytest
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")  # 🔥 Ajuste se necessário
django.setup()  # 🔥 Garante que o Django seja carregado corretamente

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Permite acesso ao banco de dados para todos os testes automaticamente"""
    pass
