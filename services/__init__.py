# services/__init__.py
"""
Pacote de serviços da LotoAnalytica PRO v18
Contém classes responsáveis por API, IA, geração de jogos,
cálculo de KPIs e análise de chat.
"""

from .loteria_api import LoteriaAPI
from .ai_engine import AIEngine
from .generator import JogoGenerator
from .kpi_calculator import KPICalculator
from .chat_analyzer import ChatAnalyzer

__all__ = [
    "LoteriaAPI",
    "AIEngine",
    "JogoGenerator",
    "KPICalculator",
    "ChatAnalyzer",
]

__version__ = "2.2.0"
