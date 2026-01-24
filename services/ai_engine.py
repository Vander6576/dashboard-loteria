# services/ai_engine.py - COM TRATAMENTO DE ERROS MELHORADO
import requests
import json
from typing import Dict, Tuple, Optional
from google import genai
from config import settings

class AIEngine:
    """Motor de IA para análise de jogos"""
    
    def __init__(self):
        try:
            self.client_gemini = genai.Client(api_key=settings.GEMINI_API_KEY)
            self.gemini_disponivel = True
        except:
            self.gemini_disponivel = False
    
    def analisar_concurso(self, dados_concurso: Dict) -> Tuple[str, str]:
        """
        Analisa um concurso usando IA
        Retorna: (análise, motor_utilizado)
        """
        prompt = self._criar_prompt_analise(dados_concurso)
        
        # Tenta DeepSeek primeiro
        try:
            analise, motor = self._consultar_deepseek(prompt)
            if analise and analise.strip():
                return analise, motor
        except Exception as e:
            print(f"Erro DeepSeek: {e}")
        
        # Tenta Gemini
        try:
            if self.gemini_disponivel:
                analise, motor = self._consultar_gemini(prompt)
                if analise and analise.strip():
                    return analise, motor
        except Exception as e:
            print(f"Erro Gemini: {e}")
        
        # Fallback: análise local
        return self._analise_local(dados_concurso), "Análise Local"
    
    def _criar_prompt_analise(self, dados: Dict) -> str:
        """Cria prompt estruturado para análise"""
        return f"""
        ANALISTA ESPECIALIZADO EM LOTOFÁCIL - RESPOSTA TÉCNICA
        
        CONCURSO: {dados['concurso']}
        
        DADOS TÉCNICOS:
        - Dezenas: {dados['dezenas']}
        - Soma Total: {dados['soma']} (faixa ideal: 180-210)
        - Repetição do anterior: {dados['repetidas']}/15 (média histórica: 8-10)
        - Distribuição: {dados['dist']} (alvo: 5-5-5)
        - Pares/Ímpares: {dados['pares']}/{15-dados['pares']} (equilíbrio: 6-9 a 9-6)
        - Números na Moldura: {dados['moldura']}/15
        - Números Primos: {dados['primos']}
        
        FORMATO DE RESPOSTA OBRIGATÓRIO:
        1. DECISÃO: [ALTA PROBABILIDADE / PROBABILIDADE MÉDIA / BAIXA PROBABILIDADE]
        2. ANÁLISE TÉCNICA: (máximo 3 linhas)
        3. PADRÕES IDENTIFICADOS: (lista com •)
        4. RECOMENDAÇÃO: (1 linha específica)
        
        Seja objetivo e técnico. Use apenas dados estatísticos.
        """
    
    def _consultar_deepseek(self, prompt: str) -> Tuple[Optional[str], str]:
        """Consulta API DeepSeek via RapidAPI"""
        try:
            headers = {
                "x-rapidapi-key": settings.RAPID_API_KEY,
                "x-rapidapi-host": settings.RAPID_API_HOST,
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "Você é um analista estatístico especializado em loteria."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500
            }
            
            response = requests.post(
                "https://deepseek-v31.p.rapidapi.com/chat/completions",
                json=payload,
                headers=headers,
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    return data['choices'][0]['message']['content'], "DeepSeek AI"
            
            return None, "DeepSeek (sem resposta)"
            
        except requests.exceptions.Timeout:
            return None, "DeepSeek (timeout)"
        except Exception as e:
            return None, f"DeepSeek (erro: {str(e)[:50]})"
    
    def _consultar_gemini(self, prompt: str) -> Tuple[str, str]:
        """Consulta Google Gemini"""
        try:
            response = self.client_gemini.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
                generation_config={
                    "temperature": 0.3,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 500,
                }
            )
            
            if response and hasattr(response, 'text'):
                return response.text, "Gemini AI"
            else:
                return "Resposta não disponível no momento.", "Gemini (sem resposta)"
                
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "limit" in error_msg.lower():
                return "Serviço temporariamente indisponível devido a limitações de quota.", "Gemini (limite)"
            elif "api key" in error_msg.lower():
                return "Configuração de API necessária.", "Gemini (config)"
            else:
                return f"Serviço indisponível no momento: {error_msg[:100]}", "Gemini (erro)"
    
    def _analise_local(self, dados: Dict) -> str:
        """Análise local quando as APIs falham"""
        soma = dados['soma']
        repetidas = dados['repetidas']
        dist = dados['dist']
        pares = dados['pares']
        
        # Análise baseada em estatísticas
        status_soma = "✅" if 180 <= soma <= 210 else "⚠️"
        status_repet = "✅" if 8 <= repetidas <= 10 else "⚠️"
        status_dist = "✅" if dist == "5B | 5M | 5A" else "⚠️"
        status_pares = "✅" if 6 <= pares <= 9 else "⚠️"
        
        return f"""
        DECISÃO: ANÁLISE LOCAL (APIs indisponíveis)
        
        ANÁLISE TÉCNICA:
        Soma {soma} {status_soma} | Repetidas {repetidas} {status_repet}
        Distribuição {dist} {status_dist} | Pares {pares} {status_pares}
        
        PADRÕES IDENTIFICADOS:
        • Soma {'dentro' if 180 <= soma <= 210 else 'fora'} da faixa ideal
        • {'Adequada' if 8 <= repetidas <= 10 else 'Inadequada'} repetição do anterior
        • Distribuição {dist}
        
        RECOMENDAÇÃO: {'Jogo equilibrado' if status_soma == '✅' and status_repet == '✅' else 'Analisar com cautela'}
        """