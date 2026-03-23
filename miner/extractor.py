import ast
import javalang
from typing import List

def extract_python_methods(code: str) -> List[str]:
    """
    Extrae los nombres de todos los métodos y funciones en código Python
    utilizando Abstract Syntax Trees (AST).
    """
    methods = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(node.name)
    except SyntaxError:
        pass
    except Exception as e:
        print(f"Error inesperado al parsear Python: {e}")
        
    return methods

def extract_java_methods(code: str) -> List[str]:
    """
    Extrae los nombres de todos los métodos en código Java
    utilizando la librería javalang.
    """
    methods = []
    try:
        tree = javalang.parse.parse(code)
        for path, node in tree.filter(javalang.tree.MethodDeclaration):
            methods.append(node.name)
    except javalang.parser.JavaSyntaxError:
        pass
    except Exception as e:
        print(f"Error inesperado al parsear Java: {e}")
        
    return methods
