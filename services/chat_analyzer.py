# services/chat_analyzer.py
from typing import Dict, List
import random
from config import settings

class ChatAnalyzer:
    """Analisador de chat para conversar sobre resultados"""
    
    @staticmethod
    def gerar_resposta(pergunta: str, dados_concurso: Dict) -> str:
        """Gera resposta baseada na pergunta e dados do concurso"""
        
        pergunta_lower = pergunta.lower()
        dezenas = dados_concurso.get('dezenas', [])
        kpis = dados_concurso.get('kpis', {})
        
        # Análise de padrões
        if any(palavra in pergunta_lower for palavra in ['padrão', 'tendência', 'repetição']):
            return ChatAnalyzer._analisar_padroes(dezenas, kpis)
        
        # Análise de números quentes/frios
        elif any(palavra in pergunta_lower for palavra in ['quente', 'frio', 'frequência']):
            return ChatAnalyzer._analisar_frequencia(dezenas)
        
        # Estratégia de jogo
        elif any(palavra in pergunta_lower for palavra in ['jogar', 'palpite', 'estratégia', 'dica']):
            return ChatAnalyzer._gerar_estrategia(kpis)
        
        # Análise estatística
        elif any(palavra in pergunta_lower for palavra in ['estatística', 'probabilidade', 'chance']):
            return ChatAnalyzer._analisar_estatisticas(kpis)
        
        # Resposta padrão
        else:
            return ChatAnalyzer._resposta_padrao(kpis)
    
    @staticmethod
    def _analisar_padroes(dezenas: List[int], kpis: Dict) -> str:
        padroes = []
        
        # Verifica sequências
        sequencias = []
        for i in range(len(dezenas)-1):
            if dezenas[i+1] - dezenas[i] == 1:
                sequencias.append(f"{dezenas[i]}-{dezenas[i+1]}")
        
        if sequencias:
            padroes.append(f"Sequências encontradas: {', '.join(sequencias[:3])}")
        
        # Verifica pares/ímpares
        pares = kpis.get('pares', 0)
        impares = 15 - pares
        if pares > 9:
            padroes.append("Muitos números pares (mais de 9)")
        elif impares > 9:
            padroes.append("Muitos números ímpares (mais de 9)")
        
        # Verifica distribuição
        dist = kpis.get('dist', '')
        if "5B | 5M | 5A" in dist:
            padroes.append("Distribuição perfeita 5-5-5")
        elif "6" in dist or "4" in dist:
            padroes.append(f"Distribuição assimétrica: {dist}")
        
        if padroes:
            return "Padrões observados:\n" + "\n".join(f"• {p}" for p in padroes)
        else:
            return "Não foram identificados padrões claros neste concurso."
    
    @staticmethod
    def _analisar_frequencia(dezenas: List[int]) -> str:
        # Neste exemplo, usamos dados fictícios. Em produção, use histórico real
        numeros_quentes = random.sample(range(1, 26), 5)
        numeros_frios = [n for n in range(1, 26) if n not in numeros_quentes][:5]
        
        resposta = [
            "Baseado em análises recentes:",
            f"🔥 Números quentes (frequentes): {', '.join(map(str, sorted(numeros_quentes)))}",
            f"❄️ Números frios (ausentes): {', '.join(map(str, sorted(numeros_frios)))}",
            f"🎯 Números sorteados agora: {', '.join(map(str, sorted(dezenas)))}",
            f"Coincidências com quentes: {len(set(dezenas) & set(numeros_quentes))}"
        ]
        
        return "\n".join(resposta)
    
    @staticmethod
    def _gerar_estrategia(kpis: Dict) -> str:
        dist = kpis.get('dist', '')
        soma = kpis.get('soma', 0)
        
        estrategias = []
        
        if "5B | 5M | 5A" not in dist:
            estrategias.append("Use o método 5-5-5 para equilíbrio")
        
        if soma < 180:
            estrategias.append("Aposta em números mais altos para aumentar a soma")
        elif soma > 210:
            estrategias.append("Aposta em números mais baixos para reduzir a soma")
        
        if kpis.get('repetidas', 0) < 8:
            estrategias.append("Aumente repetições do concurso anterior (média: 8-10)")
        
        estrategias.append("Inclua 2-3 números da moldura")
        estrategias.append("Mantenha equilíbrio par/ímpar (6-9 / 9-6)")
        estrategias.append("Inclua 4-6 números primos")
        
        return "Estratégias recomendadas:\n" + "\n".join(f"• {e}" for e in estrategias)
    
    @staticmethod
    def _analisar_estatisticas(kpis: Dict) -> str:
        estatisticas = [
            f"Soma total: {kpis.get('soma', 0)} (ideal: 180-210)",
            f"Distribuição: {kpis.get('dist', '')} (alvo: 5-5-5)",
            f"Repetições vs anterior: {kpis.get('repetidas', 0)} (média: 8-10)",
            f"Pares/Ímpares: {kpis.get('pares', 0)}/{15-kpis.get('pares', 0)}",
            f"Números primos: {kpis.get('primos', 0)}",
            f"Números na moldura: {kpis.get('moldura', 0)}/15"
        ]
        
        return "Estatísticas do concurso:\n" + "\n".join(f"• {e}" for e in estatisticas)
    
    @staticmethod
    def _resposta_padrao(kpis: Dict) -> str:
        respostas = [
            f"Analisando o concurso... A soma foi {kpis.get('soma', 0)} e a distribuição {kpis.get('dist', '')}.",
            f"Este resultado tem {kpis.get('repetidas', 0)} repetições do concurso anterior.",
            f"Distribuição: {kpis.get('dist', '')}. {kpis.get('primos', 0)} números primos.",
            "Para uma análise mais detalhada, pergunte sobre padrões, estratégias ou estatísticas específicas."
        ]
        
        return random.choice(respostas)