import re
from typing import List
from config import MIN_WORD_LENGTH, IGNORED_WORDS

def tokenize_method_name(name: str) -> List[str]:
    """
    Toma el nombre de un método y lo separa según convenciones de nombrado
    (camelCase, PascalCase, snake_case) limpiando y filtrando las palabras resultantes.
    """
    if not name or name.startswith('__'):
        return []
        
    # Agrega un espacio antes de una mayúscula que sigue a una minúscula (camelCase y PascalCase)
    # Por ejemplo: getHTTPResponse -> get HTTPResponse
    name_spaced = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
    
    # Reemplaza guiones bajos por espacios (snake_case)
    name_spaced = name_spaced.replace('_', ' ')
    
    # Convierte a minúsculas y separa por espacios
    words = name_spaced.lower().split()
    
    # Filtra palabras cortas, palabras ignoradas o que no sean sólo caracteres alfabéticos
    valid_words = []
    for word in words:
        # Algunos métodos pueden haber dejado números o caracteres, los removemos.
        clean_word = re.sub(r'[^a-z]', '', word)
        if len(clean_word) >= MIN_WORD_LENGTH and clean_word not in IGNORED_WORDS:
            valid_words.append(clean_word)
            
    return valid_words
