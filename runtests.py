import os
import sys
import pytest

# Configura o Django corretamente
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Opções extras para pytest
pytest_args = [
    "--ds=core.settings",  # Usa o settings do Django
    "-v",  # Modo verbose (detalhado)
    "--color=yes",  # Ativa cores no terminal
    "--maxfail=1",  # Para execução no primeiro erro (opcional)
    "--durations=3",  # Mostra os 3 testes mais lentos
    "--tb=short",  # Mostra traceback reduzido para erros
    "--html=reports/test_report.html",  # Gera um relatório em HTML 📊
    "--self-contained-html"  # Permite abrir o HTML sem dependências externas
]

# Adiciona argumentos passados na execução
pytest_args.extend(sys.argv[1:])

# Executa os testes com pytest
exit_code = pytest.main(pytest_args)

# Exibe mensagem final no terminal
if exit_code == 0:
    print("\n✅ TODOS OS TESTES PASSARAM COM SUCESSO! 🎉")
else:
    print("\n❌ ALGUNS TESTES FALHARAM! VERIFIQUE O LOG! 🚨")

sys.exit(exit_code)



#import os
#import sys
#
## Configura o Django corretamente
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
#
## Garante que o pytest use o settings correto
#pytest_args = ["--ds=core.settings"]  # Aqui podemos adicionar mais opções se necessário
#
## Se houver argumentos extras ao rodar o script, adicionamos à lista
#pytest_args.extend(sys.argv[1:])
#
## Executa o pytest
#import pytest
#sys.exit(pytest.main(pytest_args))
