# utils/formatters.py
from typing import List


class Formatters:
    """Utilitários de formatação e validação"""

    @staticmethod
    def parse_dezenas_manual(entrada: str) -> List[int]:
        """
        Converte entrada manual em lista de dezenas válidas (1 a 25).
        Aceita: espaço, vírgula, ponto-e-vírgula, hífen.
        Remove duplicados, ordena e valida intervalo.
        """

        if not entrada:
            return []

        try:
            # Normaliza separadores
            entrada_limpa = (
                entrada.replace("-", " ")
                .replace(",", " ")
                .replace(";", " ")
            )

            numeros = []
            for item in entrada_limpa.split():
                if item.isdigit():
                    n = int(item)
                    if 1 <= n <= 25:
                        numeros.append(n)

            # Remove duplicados e ordena
            dezenas = sorted(set(numeros))

            return dezenas

        except Exception:
            return []

    @staticmethod
    def dezenas_para_texto(dezenas: List[int]) -> str:
        """Formata dezenas como string 01 02 03"""
        return " ".join(f"{n:02d}" for n in dezenas)

    @staticmethod
    def validar_qtd_dezenas(dezenas: List[int], esperado: int = 15) -> bool:
        """Valida quantidade exata de dezenas"""
        return len(dezenas) == esperado
