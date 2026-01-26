# services/ai_engine.py
import os
import requests
from typing import Dict, Tuple, Optional

from config import settings


class AIEngine:
    """
    Motor de IA para análise de jogos.
    Preparado para Streamlit Cloud.
    Fallback automático quando APIs falham.
    """

    def __init__(self):
        # Flags de disponibilidade
        self.gemini_disponivel = False

        # Gemini (import seguro)
        try:
            from google import genai
            api_key = os.getenv("GEMINI_API_KEY") or settings.GEMINI_API_KEY

            if api_key:
                self.client_gemini = genai.Client(api_key=api_key)
                self.gemini_disponivel = True
        except Exception:
            self.gemini_disponivel = False

    # =========================
    # API PRINCIPAL
    # =========================
    def analisar_concurso(self, dados_concurso: Dict) -> Tuple[str, str]:
        """
        Analisa um concurso usando IA.
        Retorna: (texto_da_analise, motor_utilizado)
        """

        prompt = self._criar_prompt_analise(dados_concurso)

        # 1️⃣ DeepSeek (prioridade)
        analise, motor = self._consultar_deepseek(prompt)
        if analise:
            return analise, motor

        # 2️⃣ Gemini
        if self.gemini_disponivel:
            analise, motor = self._consultar_gemini(prompt)
            if analise:
                return analise, motor

        # 3️⃣ Fallback local
        return self._analise_local(dados_concurso), "Análise Local"

    # =========================
    # PROMPT
    # =========================
    def _criar_prompt_analise(self, dados: Dict) -> str:
        return f"""
ANALISTA ESPECIALIZADO EM LOTOFÁCIL – RESPOSTA TÉCNICA

CONCURSO: {dados['concurso']}

DADOS:
- Dezenas: {dados['dezenas']}
- Soma: {dados['soma']} (ideal 180–210)
- Repetidas: {dados['repetidas']}/15 (ideal 8–10)
- Distribuição: {dados['dist']} (ideal 5-5-5)
- Pares: {dados['pares']}
- Ímpares: {15 - dados['pares']}
- Moldura: {dados['moldura']}
- Primos: {dados['primos']}

FORMATO OBRIGATÓRIO:
1. DECISÃO:
2. ANÁLISE TÉCNICA (máx. 3 linhas)
3. PADRÕES IDENTIFICADOS (•)
4. RECOMENDAÇÃO (1 linha)

Seja técnico, direto e estatístico.
"""

    # =========================
    # DEEPSEEK
    # =========================
    def _consultar_deepseek(self, prompt: str) -> Tuple[Optional[str], str]:
        api_key = os.getenv("RAPID_API_KEY") or settings.RAPID_API_KEY
        api_host = os.getenv("RAPID_API_HOST") or settings.RAPID_API_HOST

        if not api_key or not api_host:
            return None, "DeepSeek (sem credenciais)"

        try:
            response = requests.post(
                "https://deepseek-v31.p.rapidapi.com/chat/completions",
                headers={
                    "x-rapidapi-key": api_key,
                    "x-rapidapi-host": api_host,
                    "Content-Type": "application/json",
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "Você é um analista estatístico de loteria."},
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": 500,
                },
                timeout=15,
            )

            if response.status_code != 200:
                return None, f"DeepSeek ({response.status_code})"

            data = response.json()
            return data["choices"][0]["message"]["content"], "DeepSeek AI"

        except requests.exceptions.Timeout:
            return None, "DeepSeek (timeout)"
        except Exception:
            return None, "DeepSeek (erro)"

    # =========================
    # GEMINI
    # =========================
    def _consultar_gemini(self, prompt: str) -> Tuple[Optional[str], str]:
        try:
            response = self.client_gemini.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
                generation_config={
                    "temperature": 0.3,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 500,
                },
            )

            return response.text, "Gemini AI"

        except Exception as e:
            msg = str(e).lower()
            if "quota" in msg or "limit" in msg:
                return None, "Gemini (quota)"
            if "key" in msg:
                return None, "Gemini (api key)"
            return None, "Gemini (erro)"

    # =========================
    # FALLBACK LOCAL
    # =========================
    def _analise_local(self, dados: Dict) -> str:
        soma = dados["soma"]
        repetidas = dados["repetidas"]
        dist = dados["dist"]
        pares = dados["pares"]

        ok_soma = 180 <= soma <= 210
        ok_rep = 8 <= repetidas <= 10
        ok_dist = dist == "5B | 5M | 5A"
        ok_pares = 6 <= pares <= 9

        score = sum([ok_soma, ok_rep, ok_dist, ok_pares])

        decisao = (
            "ALTA PROBABILIDADE" if score >= 3 else
            "PROBABILIDADE MÉDIA" if score == 2 else
            "BAIXA PROBABILIDADE"
        )

        return f"""
DECISÃO: {decisao}

ANÁLISE TÉCNICA:
Soma {soma} | Repetidas {repetidas} | Distribuição {dist} | Pares {pares}

PADRÕES IDENTIFICADOS:
• Soma {'adequada' if ok_soma else 'fora da faixa'}
• Repetição {'adequada' if ok_rep else 'fora do padrão'}
• Distribuição {'equilibrada' if ok_dist else 'irregular'}
• Pares {'equilibrados' if ok_pares else 'desbalanceados'}

RECOMENDAÇÃO:
{'Manter estratégia atual' if score >= 3 else 'Ajustar composição do jogo'}
"""
