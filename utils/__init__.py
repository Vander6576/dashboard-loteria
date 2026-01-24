# utils/__init__.py
from .formatters import Formatters

__all__ = ['Formatters']

def validar_dezenas(dezenas, quantidade=15):
    if not dezenas or len(dezenas) != quantidade:
        return False
    
    if min(dezenas) < 1 or max(dezenas) > 25:
        return False
    
    if len(set(dezenas)) != quantidade:
        return False
    
    return True