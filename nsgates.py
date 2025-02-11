import uvicorn
import environ
import multiprocessing

# 🔥 Carregar variáveis de ambiente do .env
env = environ.Env()
environ.Env.read_env()  # Isso garante que o .env seja carregado

# 🔥 Define o número de workers baseado na CPU
NUM_WORKERS = env.int("API_WORKERS", default=(multiprocessing.cpu_count() * 2) + 1)

# 🔥 Definir a porta com valor padrão (caso API_PORT não esteja no .env)
API_PORT = env.int("API_PORT", default=8000)  # Se API_PORT não existir, usa 8000

if __name__ == "__main__":
    uvicorn.run(
        "core.asgi:application",  # Aponta para sua aplicação ASGI
        host="0.0.0.0",  # Permite acesso externo (troque para "127.0.0.1" se quiser só local)
        port=API_PORT,  # Porta definida no .env ou 8000 por padrão
        reload=True,  # Recarrega automaticamente em mudanças no código
        workers=NUM_WORKERS,  # Número de processos para melhor performance
        log_level="info"  # Define nível de log (info, debug, warning, error)
    )
