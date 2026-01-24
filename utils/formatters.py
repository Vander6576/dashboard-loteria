# utils/formatters.py
class Formatters:
    """Utilitários de formatação"""
    
    @staticmethod
    def parse_dezenas_manual(entrada: str) -> list:
        try:
            entrada_limpa = entrada.replace('-', ' ').replace(',', ' ').replace(';', ' ')
            numeros = [int(n.strip()) for n in entrada_limpa.split() if n.strip().isdigit()]
            return numeros
        except Exception:
            return []