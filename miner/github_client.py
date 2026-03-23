import time
import requests
from config import GITHUB_TOKEN

class GitHubClient:
    def __init__(self, token_override=None):
        self.token = token_override or GITHUB_TOKEN
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Miner-Bot"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    def _handle_rate_limit(self, response):
        """
        Observa los headers de la respuesta. Si quedan 0 peticiones en el Rate Limit,
        duerme la ejecución hasta poder reanudar basándose en X-RateLimit-Reset.
        """
        remaining = int(response.headers.get("X-RateLimit-Remaining", 1))
        
        # En caso de hit (HTTP 403 / 429) u agotamiento preventivo
        if remaining <= 0 or response.status_code in [403, 429]:
            reset_time = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
            sleep_time = max(0, reset_time - time.time()) + 1
            print(f"[!] Límite de API GitHub alcanzado. Durmiendo por {sleep_time} segundos...")
            time.sleep(sleep_time)

    def search_repositories(self, language: str, page: int = 1):
        """
        Busca repositorios por lenguaje ordenados por stars descendente.
        """
        url = f"https://api.github.com/search/repositories?q=language:{language}&sort=stars&order=desc&page={page}"
        
        while True:
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                self._handle_rate_limit(response)
                
                if response.status_code == 200:
                    return response.json().get('items', [])
                elif response.status_code in [403, 429]:
                    # Excepción de rate_limit controlada
                    continue
                else:
                    print(f"Error fetching repos: {response.status_code} - {response.text}")
                    return []
            except requests.exceptions.RequestException as e:
                print(f"Error de red al buscar repositorios: {e}. Reintentando en 10s...")
                time.sleep(10)

    def download_repo_zip(self, owner: str, repo: str, default_branch: str, dest_path: str) -> bool:
        """
        Descarga el snapshot (zipball) completo del repositorio desde su rama principal.
        Guarda el zip en la ruta indicada y retorna True si es exitoso.
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{default_branch}"
        
        while True:
            try:
                response = requests.get(url, headers=self.headers, stream=True, timeout=15)
                self._handle_rate_limit(response)
                
                if response.status_code == 200:
                    with open(dest_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    return True
                elif response.status_code in [403, 429]:
                    # Deberíamos ya haber esperado en _handle_rate_limit
                    continue
                else:
                    print(f"Llamada fallida al descargar {owner}/{repo}: status_code {response.status_code}")
                    return False
            except requests.exceptions.RequestException as e:
                print(f"Error de red al descargar zip de {repo}: {e}. Reintentando en 10s...")
                time.sleep(10)
