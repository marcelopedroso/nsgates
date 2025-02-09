import os
import sys

# Configura o Django corretamente
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Garante que o pytest use o settings correto
pytest_args = ["--ds=core.settings"]  # Aqui podemos adicionar mais opções se necessário

# Se houver argumentos extras ao rodar o script, adicionamos à lista
pytest_args.extend(sys.argv[1:])

# Executa o pytest
import pytest
sys.exit(pytest.main(pytest_args))
