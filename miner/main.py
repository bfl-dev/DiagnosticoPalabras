import os
import time
import json
import zipfile
import redis
from config import REDIS_HOST, REDIS_PORT, TARGET_LANGUAGES
from github_client import GitHubClient
from extractor import extract_python_methods, extract_java_methods
from tokenizer import tokenize_method_name

def wait_for_redis():
    """Espera a que Redis esté disponible antes de iniciar."""
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    while True:
        try:
            r.ping()
            print("Conectado a Redis exitosamente.")
            return r
        except redis.ConnectionError:
            print("Esperando conexión con Redis...")
            time.sleep(5)

redis_client = wait_for_redis()
github_client = GitHubClient()

def get_checkpoint():
    """Lee el punto de guardado desde Redis."""
    ckpt = redis_client.get("miner:checkpoint")
    if ckpt:
        try:
            return json.loads(ckpt)
        except json.JSONDecodeError:
            pass
    return {lang: {"page": 1} for lang in TARGET_LANGUAGES}

def save_checkpoint(ckpt):
    """Guarda en Redis de forma atómica el estado actual del minado."""
    redis_client.set("miner:checkpoint", json.dumps(ckpt))

def process_file_content(content: str, ext: str):
    """Procesa el contenido string en busca de firmas de métodos y genera conteo atómico."""
    methods = []
    if ext == ".py":
        methods = extract_python_methods(content)
    elif ext == ".java":
        methods = extract_java_methods(content)
        
    pipeline = redis_client.pipeline()
    for method in methods:
        words = tokenize_method_name(method)
        for word in words:
            # ZINCRBY: Incrementa atómicamente la puntuación sumando 1 al word en Sorted Set
            pipeline.zincrby("word_ranking", 1, word)
    pipeline.execute()

def process_repo(repo, lang):
    """Descarga, extrae y analiza el repositorio."""
    owner = repo['owner']['login']
    name = repo['name']
    branch = repo.get('default_branch', 'master')
    zip_path = f"/tmp/{name}.zip"
    
    print(f"Procesando => {owner}/{name} ({lang})")
    if github_client.download_repo_zip(owner, name, branch, zip_path):
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                for file_info in zf.infolist():
                    if file_info.is_dir():
                        continue
                    
                    ext = os.path.splitext(file_info.filename)[1].lower()
                    # Verifica compatibilidad de extensión del fichero y lenguaje principal
                    if (lang == 'Python' and ext == '.py') or (lang == 'Java' and ext == '.java'):
                        try:
                            # Sólo procesar archivos menores a 1MB heurísticamente
                            if file_info.file_size < 1_000_000:
                                with zf.open(file_info) as f:
                                    content = f.read().decode('utf-8', errors='ignore')
                                process_file_content(content, ext)
                        except Exception as e:
                            print(f"Ignorando archivo, error durante carga: {e}")
        except zipfile.BadZipFile:
            print(f"Archivo zip corrupto o descargado parcialmente para {owner}/{name}")
        finally:
            if os.path.exists(zip_path):
                os.remove(zip_path)

def start_miner():
    """Bucle infinito Productor."""
    ckpt = get_checkpoint()
    
    while True:
        try:
            for lang in TARGET_LANGUAGES:
                if lang not in ckpt:
                    ckpt[lang] = {"page": 1}
                    
                page = ckpt[lang]["page"]
                print(f"--- Consultando {lang} - Página {page} ---")
                
                repos = github_client.search_repositories(lang, page)
                
                if not repos:
                    print(f"No hay repositorios o hubo un fallo para {lang}. Se detendrá y continuará en el siguiente.")
                    continue
                    
                for repo in repos:
                    process_repo(repo, lang)
                
                # Siguiente página y guardar
                ckpt[lang]["page"] = page + 1
                save_checkpoint(ckpt)
                
            print("Iteración sobre todos los lenguajes completos. Pausa de refresco (15 seg).")
            time.sleep(15)
            
        except KeyboardInterrupt:
            print("Deteniendo Miner y guardando estado...")
            save_checkpoint(ckpt)
            break
        except Exception as e:
            print(f"Falla crítica en bucle principal: {e}. Reanudando automáticamente en 30s")
            time.sleep(30)

if __name__ == "__main__":
    start_miner()
