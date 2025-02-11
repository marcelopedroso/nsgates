from watchman.decorators import check
from django.db import connection
from django.core.cache import caches
from django.core.files.storage import default_storage
import os
import time

### 🔹 Banco de Dados ###
@check
def advanced_database_check():
    """Verifica a conexão com o banco e retorna mais detalhes"""
    start_time = time.time()
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
            table_count = cursor.fetchone()[0]
        
        response = {
            "status": "OK",
            "database": connection.settings_dict["NAME"],
            "engine": connection.settings_dict["ENGINE"],
            "host": connection.settings_dict["HOST"],
            "port": connection.settings_dict["PORT"],
            "tables_count": table_count,
            "query_time": round(time.time() - start_time, 4),
        }
    except Exception as e:
        response = {"status": "ERROR", "error": str(e)}
    
    return response

#
#### 🔹 Cache ###
#@check
#def advanced_cache_check():
#    """Verifica se o cache está funcionando corretamente e retorna detalhes"""
#    import time
#    start_time = time.time()
#    cache = caches["default"]
#
#    try:
#        # Teste de escrita e leitura
#        cache.set("health_check", "ok", timeout=5)
#        test_value = cache.get("health_check")
#        cache_status = "OK" if test_value == "ok" else "ERROR"
#
#        # Verificar backend
#        backend_name = cache.__class__.__module__
#
#        # Se o backend for Redis, tente obter informações do servidor
#        cache_info = {}
#        if "redis" in backend_name.lower():
#            try:
#                client = cache.client.get_client(write=True)
#                cache_info = client.info()  # Obtém estatísticas do Redis
#            except Exception:
#                cache_info = {"info": "N/A"}
#
#        response = {
#            "status": cache_status,
#            "backend": backend_name,
#            "query_time": round(time.time() - start_time, 4),
#            "extra_info": cache_info
#        }
#    except Exception as e:
#        response = {"status": "ERROR", "error": str(e)}
#
#    return response
#
#
#### 🔹 Storage ###
#@check
#def advanced_storage_check():
#    """Verifica se o storage está acessível e retorna detalhes"""
#    start_time = time.time()
#    storage_path = default_storage.location
#    test_file = os.path.join(storage_path, "health_check_test.txt")
#
#    try:
#        # Teste de escrita no storage
#        with open(test_file, "w") as f:
#            f.write("ok")
#        
#        # Teste de leitura
#        with open(test_file, "r") as f:
#            test_value = f.read()
#        
#        # Remover o arquivo de teste
#        os.remove(test_file)
#
#        # Calcular espaço usado
#        total_size = sum(os.path.getsize(os.path.join(storage_path, f)) for f in os.listdir(storage_path) if os.path.isfile(os.path.join(storage_path, f)))
#
#        response = {
#            "status": "OK" if test_value == "ok" else "ERROR",
#            "storage_path": storage_path,
#            "storage_size_mb": round(total_size / (1024 * 1024), 2),
#            "query_time": round(time.time() - start_time, 4),
#        }
#    except Exception as e:
#        response = {"status": "ERROR", "error": str(e)}
#    
#    return response
#