import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
TARGET_LANGUAGES = os.getenv("TARGET_LANGUAGES", "Python,Java").split(",")

# Parámetros de minado
SEARCH_PER_PAGE = 30
MIN_WORD_LENGTH = 3
IGNORED_WORDS = {'get', 'set', 'is', 'has', 'to', 'from', 'run', 'main', 'test', 'init'}
