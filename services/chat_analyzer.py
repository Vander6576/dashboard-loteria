# services/chat_analyzer.py
from typing import Dict, List
from services.loteria_api import LoteriaAPI


class ChatAnalyzer:
    """
    Analisador conversacional baseado em estatística real.
    Não usa aleatoriedade.
    Seguro para Streamlit Cloud.
    """

    def __init__(self):
        self.api = LoteriaAPI()

    # =============================
    # ENTRY POINT
    # =============================
    def gerar_resposta(self, pergunta: str, dados_concurso: Dict) -> str:
        pergunta = pergunta.lower()

        dezenas = dados_concurso.get("dezenas", [])
        kpis = dados_concurso.get("kpis", {})

        if not dezenas:
            return "Ainda não tenho dezenas para analisar. Atualize o concurso primeiro."

        if any(p in pergunta for p in ["padrão", "tendência", "sequência", "repetição"]):
            return self._analisar_padroes(dezenas, kpis)

        if any(p in pergunta for p in ["quente", "frio", "frequência"]):
            return self._analisar_frequencia(dezenas)

        if any(p in pergunta for p in ["jogar", "palpite", "estratégia", "dica"]):
            return self._gerar_estrategia(kpis)

        if any(p in pergunta for p in ["estatística", "probabilidade", "chance"]):
            return self._analisar_estatisticas(kpis)

        return self._resposta_padrao(kpis)

    # =============================
    # ANÁLISES
    # =============================
    def _analisar_padroes(self, dezenas: List[int], kpis: Dict) -> str:
        dezenas = sorted(dezenas)
        respostas = []

        # Sequências
        sequencias = []
        atual = [dezenas[0]]

        for i in range(1, len(dezenas)):
            if dezenas[i] == dezenas[i - 1] + 1:
                atual.append(dezenas[i])
            else:
                if len(atual) >= 2:
                    sequencias.append(atual)
                atual = [dezenas[i]]

        if len(atual) >= 2:
            sequencias.append(atual)

        if sequencias:
            respostas.append(
                f"Sequências encontradas: {', '.join('-'.join(map(str, s)) for s in sequencias)}"
            )

        # Pares x Ímpares
        pares = kpis.get("pares", 0)
        impares = 15 - pares

        if pares >= 10:
            respostas.append("Predomínio forte de números pares.")
        elif impares >= 10:
            respostas.append("Predomínio forte de números ímpares.")
        else:
            respostas.append("Equilíbrio saudável entre pares e ímpares.")

        # Distribuição
        dist = kpis.get("dist", "")
        if dist == "5B | 5M | 5A":
            respostas.append("Distribuição 5-5-5 perfeita.")
        else:
            respostas.append(f"Distribuição fora do padrão ideal (atual: {dist}).")

        return "📌 Padrões observados:\n" + "\n".join(f"• {r}" for r in respostas)

    def _analisar_frequencia(self, dezenas: List[int]) -> str:
        historico = self.api.carregar_historico()

        if historico.empty:
            return "Ainda não há histórico suficiente para analisar frequência."

        todos = []
        for lst in historico["dezenas_lista"]:
            todos.extend(lst)

        from collections import Counter
        freq = Counter(todos)

        quentes = [n for n, f in freq.most_common(5)]
        frios = [n for n in range(1, 26) if n not in freq][:5]

        coincidencias = len(set(dezenas) & set(quentes))

        return (
            "📊 Frequência histórica:\n"
            f"🔥 Números mais frequentes: {', '.join(map(str, quentes))}\n"
            f"❄️ Números menos frequentes: {', '.join(map(str, frios))}\n"
            f"🎯 Coincidências com o sorteio atual: {coincidencias}"
        )

    def _gerar_estrategia(self, kpis: Dict) -> str:
        estrategias = []

        soma = kpis.get("soma", 0)
        dist = kpis.get("dist", "")
        repetidas = kpis.get("repetidas", 0)

        if dist != "5B | 5M | 5A":
            estrategias.append("Busque a distribuição 5-5-5 (baixo, médio, alto).")

        if soma < 180:
            estrategias.append("Inclua mais números acima do 15 para elevar a soma.")
        elif soma > 210:
            estrategias.append("Reduza números altos para controlar a soma.")

        if repetidas < 8:
            estrategias.append("Aumente a repetição do concurso anterior (alvo: 8–10).")

        estrategias.extend([
            "Mantenha equilíbrio entre pares e ímpares.",
            "Inclua de 4 a 6 números primos.",
            "Não concentre muitos números em uma única coluna."
        ])

        return "🎯 Estratégia recomendada:\n" + "\n".join(f"• {e}" for e in estrategias)

    def _analisar_estatisticas(self, kpis: Dict) -> str:
        return (
            "📈 Estatísticas do concurso:\n"
            f"• Soma: {kpis.get('soma', 0)} (ideal: 180–210)\n"
            f"• Distribuição: {kpis.get('dist', '')}\n"
            f"• Repetições: {kpis.get('repetidas', 0)}\n"
            f"• Pares/Ímpares: {kpis.get('pares', 0)}/{15 - kpis.get('pares', 0)}\n"
            f"• Primos: {kpis.get('primos', 0)}\n"
            f"• Moldura: {kpis.get('moldura', 0)}/15"
        )

    def _resposta_padrao(self, kpis: Dict) -> str:
        return (
            "Posso analisar padrões, frequência, estatísticas ou sugerir estratégias.\n"
            f"Resumo rápido: soma {kpis.get('soma', 0)}, distribuição {kpis.get('dist', '')}."
        )
