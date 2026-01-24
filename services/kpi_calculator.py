# services/kpi_calculator.py
import pandas as pd
from typing import Dict, List, Optional
from config import settings

class KPICalculator:
    """Calculadora de KPIs estatísticos"""
    
    @staticmethod
    def calcular(dezenas: List[int], dezenas_anterior: Optional[List[int]] = None) -> Dict:
        df = pd.Series(dezenas)
        
        primos = [2, 3, 5, 7, 11, 13, 17, 19, 23]
        moldura = [1, 2, 3, 4, 5, 6, 10, 11, 15, 16, 20, 21, 22, 23, 24, 25]
        
        repetidas = 0
        if dezenas_anterior:
            repetidas = len(set(dezenas).intersection(set(dezenas_anterior)))
        
        baixos = [n for n in dezenas if settings.RANGES['baixos'][0] <= n <= settings.RANGES['baixos'][1]]
        medios = [n for n in dezenas if settings.RANGES['medios'][0] <= n <= settings.RANGES['medios'][1]]
        altos = [n for n in dezenas if settings.RANGES['altos'][0] <= n <= settings.RANGES['altos'][1]]
        
        return {
            "soma": sum(dezenas),
            "pares": len(df[df % 2 == 0]),
            "primos": len(df[df.isin(primos)]),
            "moldura": len(df[df.isin(moldura)]),
            "repetidas": repetidas,
            "dist": f"{len(baixos)}B | {len(medios)}M | {len(altos)}A",
            "grupos": {
                "baixos": baixos,
                "medios": medios,
                "altos": altos
            }
        }