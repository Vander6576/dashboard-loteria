# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # APIs
    RAPID_API_KEY = os.getenv("RAPID_API_KEY", "")
    RAPID_API_HOST = os.getenv("RAPID_API_HOST", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", " ")
    
    # URLs
    LOTERIA_API_URL = "https://loteriascaixa-api.herokuapp.com/api/lotofacil"
    DEEPSEEK_API_URL = "https://deepseek-v31.p.rapidapi.com/"
    
    # Configurações do jogo
    NUMEROS_TOTAL = 25
    NUMEROS_SORTEIO = 15
    RANGES = {
        'baixos': (1, 10),
        'medios': (11, 20),
        'altos': (21, 25)
    }