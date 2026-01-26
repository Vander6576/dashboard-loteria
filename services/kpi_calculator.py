# services/kpi_calculator.py
from typing import Dict, List, Optional


class KPICalculator:
    """
    Calculadora de KPIs estatísticos da Lotofácil.
    Classe pura (sem IO, sem dependência externa).
    Segura para cache e Streamlit Cloud.
    """

    @staticmethod
    def calcular(
        dezenas: List[int],
        dezenas_anterior: Optional[List[int]] = None
    ) -> Dict:
        if not dezenas or len(dezenas) != 15:
            return KPICalculator._kpi_vazio()

        dezenas = sorted(dezenas)

        # =============================
        # DEFINIÇÕES FIXAS (SEM SETTINGS)
        # =============================
        primos = {2, 3, 5, 7, 11, 13, 17, 19, 23}
        moldura = {
            1, 2, 3, 4, 5,
            6, 10, 11, 15, 16,
            20, 21, 22, 23, 24, 25
        }

        # Faixas padrão Lotofácil
        baixos = [n for n in dezenas if 1 <= n <= 8]
        medios = [n for n in dezenas if 9 <= n <= 17]
        altos = [n for n in dezenas if 18 <= n <= 25]

        # =============================
        # KPIs
        # =============================
        soma = sum(dezenas)
        pares = len([n for n in dezenas if n % 2 == 0])
        primos_qtd = len([n for n in dezenas if n in primos])
        moldura_qtd = len([n for n in dezenas if n in moldura])

        repetidas = 0
        if dezenas_anterior:
            repetidas = len(set(dezenas) & set(dezenas_anterior))

        return {
            "soma": soma,
            "pares": pares,
            "impares": 15 - pares,
            "primos": primos_qtd,
            "moldura": moldura_qtd,
            "repetidas": repetidas,
            "dist": f"{len(baixos)}B | {len(medios)}M | {len(altos)}A",
            "grupos": {
                "baixos": baixos,
                "medios": medios,
                "altos": altos
            },
            "flags": {
                "soma_ideal": 180 <= soma <= 210,
                "dist_ideal": len(baixos) == 5 and len(medios) == 5 and len(altos) == 5,
                "pares_ideal": 6 <= pares <= 9,
                "primos_ideal": 4 <= primos_qtd <= 6,
                "moldura_ideal": 7 <= moldura_qtd <= 10
            }
        }

    @staticmethod
    def _kpi_vazio() -> Dict:
        return {
            "soma": 0,
            "pares": 0,
            "impares": 0,
            "primos": 0,
            "moldura": 0,
            "repetidas": 0,
            "dist": "0B | 0M | 0A",
            "grupos": {
                "baixos": [],
                "medios": [],
                "altos": []
            },
            "flags": {}
        }
