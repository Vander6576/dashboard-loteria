# services/generator.py - VERSÃO COMPLETA E ATUALIZADA
import random
from typing import Tuple, List, Dict
from collections import Counter
from config import settings

class JogoGenerator:
    """Gerador de jogos estratégicos com análise avançada"""
    
    @staticmethod
    def gerar_555(ultimo_resultado: List[int]) -> Tuple[List[int], List[int]]:
        """
        Método Estratégico: 5 Baixos, 5 Médios, 5 Altos
        Com análise inteligente do último resultado
        """
        baixos_pool = list(range(settings.RANGES['baixos'][0], settings.RANGES['baixos'][1] + 1))
        medios_pool = list(range(settings.RANGES['medios'][0], settings.RANGES['medios'][1] + 1))
        altos_pool = list(range(settings.RANGES['altos'][0], settings.RANGES['altos'][1] + 1))
        
        # Análise do último resultado
        baixos_ultimo = [n for n in ultimo_resultado if n in baixos_pool]
        medios_ultimo = [n for n in ultimo_resultado if n in medios_pool]
        altos_ultimo = [n for n in ultimo_resultado if n in altos_pool]
        
        # Números ausentes no último concurso
        ausentes = [n for n in range(1, settings.NUMEROS_TOTAL + 1) 
                   if n not in ultimo_resultado]
        
        # Define fixos estratégicos baseados no último resultado
        # Usa os números mais comuns em cada faixa
        fixo_b = 5 if 5 in ultimo_resultado else (3 if 3 in ultimo_resultado else random.choice(baixos_pool))
        fixo_m = 15 if 15 in ultimo_resultado else (13 if 13 in ultimo_resultado else random.choice(medios_pool))
        
        def montar_grupo(pool: List[int], meta: int, fixo: int, 
                        ausentes_lista: List[int], grupo_ultimo: List[int]) -> List[int]:
            """Monta um grupo de números seguindo regras estratégicas"""
            pool_clean = [n for n in pool if n != fixo]
            
            # Separa ausentes e presentes
            grupo_ausentes = [n for n in pool_clean if n in ausentes_lista]
            grupo_presentes = [n for n in pool_clean if n in grupo_ultimo]
            
            selecionados = [fixo]
            
            # Estratégia: 60% presentes, 40% ausentes
            qtd_ausentes = min(max(1, meta // 3), len(grupo_ausentes))
            qtd_presentes = meta - qtd_ausentes - 1  # -1 porque já tem o fixo
            
            # Adiciona ausentes
            if grupo_ausentes and qtd_ausentes > 0:
                selecionados.extend(random.sample(grupo_ausentes, qtd_ausentes))
            
            # Adiciona presentes
            if grupo_presentes and qtd_presentes > 0 and len(grupo_presentes) >= qtd_presentes:
                selecionados.extend(random.sample(grupo_presentes, qtd_presentes))
            else:
                # Completa com qualquer número disponível
                disponiveis = [n for n in pool_clean if n not in selecionados]
                if len(disponiveis) >= qtd_presentes:
                    selecionados.extend(random.sample(disponiveis, qtd_presentes))
            
            return selecionados
        
        # Monta os três grupos com análise do último
        grupo_baixos = montar_grupo(baixos_pool, 5, fixo_b, ausentes, baixos_ultimo)
        grupo_medios = montar_grupo(medios_pool, 5, fixo_m, ausentes, medios_ultimo)
        
        # Para altos, usa estratégia diferente (todos os números disponíveis)
        grupo_altos = []
        altos_disponiveis = altos_pool.copy()
        random.shuffle(altos_disponiveis)
        grupo_altos = altos_disponiveis[:5]
        
        jogo = grupo_baixos + grupo_medios + grupo_altos
        return sorted(jogo), [fixo_b, fixo_m]
    
    # ========== NOVOS MÉTODOS DE ANÁLISE ==========
    
    @staticmethod
    def analisar_palpite(palpite: List[int], ultimo_resultado: List[int]) -> Dict:
        """Analisa o palpite em relação ao último resultado"""
        from services.kpi_calculator import KPICalculator
        
        kpis = KPICalculator.calcular(palpite, ultimo_resultado)
        
        # Análise adicional específica para palpites
        analise = {
            'kpis': kpis,
            'coincidencias': len(set(palpite) & set(ultimo_resultado)),
            'ausentes_incluidos': len([n for n in palpite if n not in ultimo_resultado]),
            'distribuição_ideal': "5-5-5" if kpis['dist'] == "5B | 5M | 5A" else "Não ideal",
            'recomendacao': JogoGenerator._gerar_recomendacao(kpis)
        }
        
        return analise
    
    @staticmethod
    def analisar_palpite_completo(palpite: List[int], resultados_anteriores: List[List[int]]) -> Dict:
        """
        Análise completa do palpite comparando com múltiplos resultados anteriores
        Args:
            palpite: Lista de números do palpite
            resultados_anteriores: Lista de listas com resultados anteriores
        Returns:
            Dicionário com análise completa
        """
        from services.kpi_calculator import KPICalculator
        
        if not resultados_anteriores:
            return {
                'analises_por_concurso': [],
                'resumo': {
                    'media_repeticao': 0,
                    'min_repeticao': 0,
                    'max_repeticao': 0,
                    'numeros_quentes_palpite': [],
                    'numeros_frios_palpite': [],
                    'percentual_quentes': 0,
                    'soma_ideal': False,
                    'distribuicao_ideal': False
                },
                'recomendacoes': ["Sem dados históricos suficientes para análise"]
            }
        
        analises = []
        for i, resultado in enumerate(resultados_anteriores):
            kpis = KPICalculator.calcular(palpite, resultado)
            analise = {
                'concurso': f"Anterior-{i+1}",
                'repetidos': len(set(palpite) & set(resultado)),
                'kpis': kpis,
                'diferenca_soma': abs(kpis['soma'] - sum(resultado)),
                'distribuicao_original': KPICalculator.calcular(resultado)['dist']
            }
            analises.append(analise)
        
        # Média de repetições
        media_repeticao = sum(a['repetidos'] for a in analises) / len(analises) if analises else 0
        
        # Análise de números quentes/frios no palpite
        todos_numeros_anteriores = [num for resultado in resultados_anteriores for num in resultado]
        frequencia_numeros = Counter(todos_numeros_anteriores)
        
        # Números quentes: aparecem em pelo menos 50% dos concursos
        limite_quente = len(resultados_anteriores) * 0.5
        numeros_palpite_quentes = [n for n in palpite if frequencia_numeros.get(n, 0) >= limite_quente]
        
        # Números frios: não apareceram em nenhum concurso anterior
        numeros_palpite_frios = [n for n in palpite if n not in todos_numeros_anteriores]
        
        # Verifica se segue padrões históricos
        kpis_palpite = KPICalculator.calcular(palpite)
        soma_ideal = 180 <= kpis_palpite['soma'] <= 210
        distribuicao_ideal = kpis_palpite['dist'] == "5B | 5M | 5A"
        
        return {
            'analises_por_concurso': analises,
            'resumo': {
                'media_repeticao': round(media_repeticao, 2),
                'min_repeticao': min(a['repetidos'] for a in analises) if analises else 0,
                'max_repeticao': max(a['repetidos'] for a in analises) if analises else 0,
                'numeros_quentes_palpite': sorted(numeros_palpite_quentes),
                'numeros_frios_palpite': sorted(numeros_palpite_frios),
                'percentual_quentes': round(len(numeros_palpite_quentes) / 15 * 100, 1),
                'soma_ideal': soma_ideal,
                'distribuicao_ideal': distribuicao_ideal
            },
            'recomendacoes': JogoGenerator._gerar_recomendacoes_detalhadas(analises, kpis_palpite)
        }
    
    @staticmethod
    def _gerar_recomendacao(kpis: Dict) -> str:
        """Gera recomendação baseada nos KPIs do palpite"""
        recomendacoes = []
        
        dist = kpis['dist']
        if "5B | 5M | 5A" not in dist:
            recomendacoes.append("Ajustar para distribuição 5-5-5")
        
        soma = kpis['soma']
        if soma < 180:
            recomendacoes.append("Incluir números mais altos")
        elif soma > 210:
            recomendacoes.append("Incluir números mais baixos")
        
        if 'repetidas' in kpis:
            if kpis['repetidas'] < 8:
                recomendacoes.append("Aumentar repetições do último concurso")
            elif kpis['repetidas'] > 10:
                recomendacoes.append("Reduzir repetições do último concurso")
        
        if kpis['pares'] < 6:
            recomendacoes.append("Aumentar números pares")
        elif kpis['pares'] > 9:
            recomendacoes.append("Reduzir números pares")
        
        if 'moldura' in kpis and kpis['moldura'] < 10:
            recomendacoes.append("Incluir mais números da moldura")
        
        if 'primos' in kpis and kpis['primos'] < 4:
            recomendacoes.append("Incluir mais números primos")
        
        if not recomendacoes:
            return "Palpite bem equilibrado!"
        
        return "; ".join(recomendacoes)
    
    @staticmethod
    def _gerar_recomendacoes_detalhadas(analises: List[Dict], kpis_palpite: Dict) -> List[str]:
        """Gera recomendações detalhadas baseadas na análise"""
        recomendacoes = []
        
        if not analises:
            return ["Sem dados históricos suficientes para análise"]
        
        # Analisa repetição
        repeticoes = [a['repetidos'] for a in analises]
        media_rep = sum(repeticoes) / len(repeticoes)
        
        if media_rep < 8:
            recomendacoes.append(f"Aumentar repetições (média atual: {media_rep:.1f}, ideal: 8-10)")
        elif media_rep > 10:
            recomendacoes.append(f"Reduzir repetições (média atual: {media_rep:.1f}, ideal: 8-10)")
        
        # Analisa soma
        soma = kpis_palpite['soma']
        if soma < 180:
            recomendacoes.append(f"Aumentar soma total (atual: {soma}, ideal: 180-210)")
        elif soma > 210:
            recomendacoes.append(f"Reduzir soma total (atual: {soma}, ideal: 180-210)")
        
        # Analisa distribuição
        dist = kpis_palpite['dist']
        if "5B | 5M | 5A" not in dist:
            recomendacoes.append(f"Ajustar distribuição (atual: {dist}, ideal: 5-5-5)")
        
        # Analisa números quentes/frios
        if len(kpis_palpite.get('grupos', {}).get('baixos', [])) < 4:
            recomendacoes.append("Incluir mais números baixos (1-10)")
        if len(kpis_palpite.get('grupos', {}).get('altos', [])) < 4:
            recomendacoes.append("Incluir mais números altos (21-25)")
        
        # Analisa pares/ímpares
        pares = kpis_palpite['pares']
        if pares < 6:
            recomendacoes.append(f"Aumentar números pares (atual: {pares}, ideal: 6-9)")
        elif pares > 9:
            recomendacoes.append(f"Reduzir números pares (atual: {pares}, ideal: 6-9)")
        
        if not recomendacoes:
            recomendacoes.append("Palpite bem equilibrado! Mantenha a estratégia.")
        
        return recomendacoes
    
    # ========== NOVOS MÉTODOS DE GERAÇÃO ==========
    
    @staticmethod
    def gerar_palpite_inteligente(resultados_anteriores: List[List[int]], 
                                 usar_numeros_quentes: bool = True,
                                 balancear_distribuicao: bool = True,
                                 incluir_numeros_frios: bool = True) -> Tuple[List[int], Dict]:
        """
        Gera palpite inteligente baseado em análises anteriores
        Returns:
            Tuple (palpite, análise_da_geração)
        """
        from collections import Counter
        
        if not resultados_anteriores:
            # Fallback: gera palpite básico
            ultimo = resultados_anteriores[-1] if resultados_anteriores else list(range(1, 16))
            palpite, fixos = JogoGenerator.gerar_555(ultimo)
            return palpite, {
                'estrategia': 'Fallback (sem histórico)',
                'fixos': fixos,
                'analise': 'Gerado com método 5-5-5 básico'
            }
        
        # Analisa frequência dos números
        todos_numeros = [num for resultado in resultados_anteriores for num in resultado]
        frequencia = Counter(todos_numeros)
        
        # Separa números por frequência
        limite_quente = len(resultados_anteriores) * 0.7
        limite_frio = len(resultados_anteriores) * 0.3
        
        numeros_quentes = [num for num, freq in frequencia.items() 
                          if freq >= limite_quente]
        numeros_frios = [num for num in range(1, 26) 
                        if num not in frequencia or frequencia[num] <= limite_frio]
        numeros_medianos = [num for num in range(1, 26) 
                           if num not in numeros_quentes and num not in numeros_frios]
        
        # Estratégia configurável
        qtd_quentes = 6 if usar_numeros_quentes else 4
        qtd_frios = 3 if incluir_numeros_frios else 1
        qtd_medianos = 15 - qtd_quentes - qtd_frios
        
        # Garante que temos números suficientes
        qtd_quentes = min(qtd_quentes, len(numeros_quentes))
        qtd_frios = min(qtd_frios, len(numeros_frios))
        qtd_medianos = min(qtd_medianos, len(numeros_medianos))
        
        # Seleciona números
        selecionados = []
        
        if numeros_quentes and qtd_quentes > 0:
            selecionados.extend(random.sample(numeros_quentes, qtd_quentes))
        
        if numeros_medianos and qtd_medianos > 0:
            selecionados.extend(random.sample(numeros_medianos, qtd_medianos))
        
        if numeros_frios and qtd_frios > 0:
            selecionados.extend(random.sample(numeros_frios, qtd_frios))
        
        # Completa até 15 se necessário
        if len(selecionados) < 15:
            numeros_disponiveis = [n for n in range(1, 26) if n not in selecionados]
            selecionados.extend(random.sample(numeros_disponiveis, 15 - len(selecionados)))
        
        # Balanceia distribuição se solicitado
        if balancear_distribuicao:
            selecionados = JogoGenerator._balancear_distribuicao(selecionados)
        
        # Define fixos estratégicos
        ultimo_resultado = resultados_anteriores[-1]
        fixo_b = 5 if 5 in ultimo_resultado else 3
        fixo_m = 15 if 15 in ultimo_resultado else 13
        
        # Garante que os fixos estão no palpite
        if fixo_b not in selecionados and len(selecionados) > 0:
            # Substitui um número aleatório pelo fixo
            index = random.randint(0, len(selecionados)-1)
            selecionados[index] = fixo_b
        
        if fixo_m not in selecionados and len(selecionados) > 0:
            # Encontra um número que não seja fixo_b para substituir
            disponiveis = [i for i, n in enumerate(selecionados) if n != fixo_b]
            if disponiveis:
                index = random.choice(disponiveis)
                selecionados[index] = fixo_m
        
        palpite_final = sorted(selecionados)
        
        # Gera análise da geração
        analise_geracao = {
            'estrategia': 'Inteligente com análise histórica',
            'fixos': [fixo_b, fixo_m],
            'estatisticas': {
                'numeros_quentes_usados': len([n for n in palpite_final if n in numeros_quentes]),
                'numeros_frios_usados': len([n for n in palpite_final if n in numeros_frios]),
                'numeros_medianos_usados': len([n for n in palpite_final if n in numeros_medianos]),
                'total_concursos_analisados': len(resultados_anteriores)
            },
            'parametros': {
                'usar_numeros_quentes': usar_numeros_quentes,
                'balancear_distribuicao': balancear_distribuicao,
                'incluir_numeros_frios': incluir_numeros_frios
            }
        }
        
        return palpite_final, analise_geracao
    
    @staticmethod
    def _balancear_distribuicao(numeros: List[int]) -> List[int]:
        """Balanceia a distribuição dos números"""
        baixos = [n for n in numeros if settings.RANGES['baixos'][0] <= n <= settings.RANGES['baixos'][1]]
        medios = [n for n in numeros if settings.RANGES['medios'][0] <= n <= settings.RANGES['medios'][1]]
        altos = [n for n in numeros if settings.RANGES['altos'][0] <= n <= settings.RANGES['altos'][1]]
        
        # Meta: 5-5-5
        meta_baixos = 5
        meta_medios = 5
        meta_altos = 5
        
        # Ajusta se necessário
        ajustados = []
        
        # Mantém os que já estão bem distribuídos
        ajustados.extend(baixos[:meta_baixos])
        ajustados.extend(medios[:meta_medios])
        ajustados.extend(altos[:meta_altos])
        
        # Se faltarem números, completa
        if len(ajustados) < 15:
            numeros_disponiveis = [n for n in range(1, 26) if n not in ajustados]
            ajustados.extend(random.sample(numeros_disponiveis, 15 - len(ajustados)))
        
        return sorted(ajustados)
    
    @staticmethod
    def gerar_multiplos_palpites(ultimo_resultado: List[int], 
                                quantidade: int = 3,
                                estrategias: List[str] = None) -> List[Dict]:
        """
        Gera múltiplos palpites com estratégias diferentes
        Args:
            ultimo_resultado: Último resultado para análise
            quantidade: Quantidade de palpites a gerar
            estrategias: Lista de estratégias ['555', 'inteligente', 'aleatorio']
        Returns:
            Lista de dicionários com palpites e análises
        """
        if estrategias is None:
            estrategias = ['555', 'inteligente', 'aleatorio']
        
        palpites = []
        
        for i in range(quantidade):
            estrategia = estrategias[i % len(estrategias)]
            
            if estrategia == '555':
                palpite, fixos = JogoGenerator.gerar_555(ultimo_resultado)
                analise = JogoGenerator.analisar_palpite(palpite, ultimo_resultado)
                palpites.append({
                    'numero': i + 1,
                    'estrategia': '5-5-5 Balanceado',
                    'palpite': palpite,
                    'fixos': fixos,
                    'analise': analise
                })
            
            elif estrategia == 'inteligente':
                # Para estratégia inteligente, precisa de histórico
                # Simula histórico com o último resultado repetido
                historico_simulado = [ultimo_resultado] * 3
                palpite, info_geracao = JogoGenerator.gerar_palpite_inteligente(
                    historico_simulado,
                    usar_numeros_quentes=True,
                    balancear_distribuicao=True,
                    incluir_numeros_frios=True
                )
                analise = JogoGenerator.analisar_palpite(palpite, ultimo_resultado)
                palpites.append({
                    'numero': i + 1,
                    'estrategia': 'Inteligente com IA',
                    'palpite': palpite,
                    'fixos': info_geracao['fixos'],
                    'analise': analise,
                    'info_geracao': info_geracao
                })
            
            elif estrategia == 'aleatorio':
                # Gera palpite aleatório balanceado
                import numpy as np
                while True:
                    palpite = sorted(random.sample(range(1, 26), 15))
                    from services.kpi_calculator import KPICalculator
                    kpis = KPICalculator.calcular(palpite)
                    # Aceita apenas palpites razoáveis
                    if 160 <= kpis['soma'] <= 220 and 4 <= kpis['pares'] <= 11:
                        analise = JogoGenerator.analisar_palpite(palpite, ultimo_resultado)
                        palpites.append({
                            'numero': i + 1,
                            'estrategia': 'Aleatório Balanceado',
                            'palpite': palpite,
                            'fixos': [],
                            'analise': analise
                        })
                        break
        
        return palpites
    
    @staticmethod
    def obter_estatisticas_palpite(palpite: List[int], historico: List[List[int]] = None) -> Dict:
        """
        Obtém estatísticas detalhadas do palpite
        Args:
            palpite: Lista de números do palpite
            historico: Histórico de resultados anteriores (opcional)
        Returns:
            Dicionário com estatísticas detalhadas
        """
        from services.kpi_calculator import KPICalculator
        from services.loteria_api import LoteriaAPI
        
        kpis = KPICalculator.calcular(palpite)
        
        estatisticas = {
            'kpis': kpis,
            'distribuicao_detalhada': JogoGenerator._analisar_distribuicao_detalhada(palpite),
            'sequencias': JogoGenerator._analisar_sequencias_palpite(palpite),
            'padroes': JogoGenerator._identificar_padroes(palpite)
        }
        
        if historico and len(historico) > 0:
            estatisticas['comparacao_historica'] = {
                'media_repeticao': round(sum(len(set(palpite) & set(h)) for h in historico) / len(historico), 2),
                'min_repeticao': min(len(set(palpite) & set(h)) for h in historico),
                'max_repeticao': max(len(set(palpite) & set(h)) for h in historico),
                'numeros_mais_comuns': JogoGenerator._identificar_numeros_comuns(palpite, historico)
            }
        
        return estatisticas
    
    @staticmethod
    def _analisar_distribuicao_detalhada(palpite: List[int]) -> Dict:
        """Análise detalhada da distribuição do palpite"""
        # Análise por quadrantes (matriz 5x5)
        quadrantes = {
            'Q1': [1, 2, 3, 4, 5, 6, 11, 12, 13, 14, 15],
            'Q2': [7, 8, 9, 10, 16, 17, 18, 19, 20],
            'Q3': [21, 22, 23, 24, 25]
        }
        
        # Análise por linhas (matriz 5x5)
        linhas = {
            'Linha1': [1, 2, 3, 4, 5],
            'Linha2': [6, 7, 8, 9, 10],
            'Linha3': [11, 12, 13, 14, 15],
            'Linha4': [16, 17, 18, 19, 20],
            'Linha5': [21, 22, 23, 24, 25]
        }
        
        # Análise por colunas (matriz 5x5)
        colunas = {
            'Col1': [1, 6, 11, 16, 21],
            'Col2': [2, 7, 12, 17, 22],
            'Col3': [3, 8, 13, 18, 23],
            'Col4': [4, 9, 14, 19, 24],
            'Col5': [5, 10, 15, 20, 25]
        }
        
        return {
            'por_quadrante': {q: len([n for n in palpite if n in nums]) for q, nums in quadrantes.items()},
            'por_linha': {l: len([n for n in palpite if n in nums]) for l, nums in linhas.items()},
            'por_coluna': {c: len([n for n in palpite if n in nums]) for c, nums in colunas.items()},
            'balanceamento': {
                'ideal_quadrantes': all(3 <= count <= 7 for count in [len([n for n in palpite if n in nums]) for nums in quadrantes.values()]),
                'ideal_linhas': all(1 <= count <= 5 for count in [len([n for n in palpite if n in nums]) for nums in linhas.values()]),
                'ideal_colunas': all(1 <= count <= 5 for count in [len([n for n in palpite if n in nums]) for nums in colunas.values()])
            }
        }
    
    @staticmethod
    def _analisar_sequencias_palpite(palpite: List[int]) -> Dict:
        """Analisa sequências no palpite"""
        palpite_ordenado = sorted(palpite)
        
        sequencias = []
        sequencia_atual = [palpite_ordenado[0]]
        
        for i in range(1, len(palpite_ordenado)):
            if palpite_ordenado[i] == palpite_ordenado[i-1] + 1:
                sequencia_atual.append(palpite_ordenado[i])
            else:
                if len(sequencia_atual) >= 2:
                    sequencias.append(sequencia_atual.copy())
                sequencia_atual = [palpite_ordenado[i]]
        
        if len(sequencia_atual) >= 2:
            sequencias.append(sequencia_atual)
        
        return {
            'sequencias': sequencias,
            'total_sequencias': len(sequencias),
            'maior_sequencia': max([len(s) for s in sequencias]) if sequencias else 0,
            'tem_sequencias_longas': any(len(s) >= 3 for s in sequencias) if sequencias else False
        }
    
    @staticmethod
    def _identificar_padroes(palpite: List[int]) -> Dict:
        """Identifica padrões matemáticos no palpite"""
        # Verifica múltiplos
        multiplos = {
            'de_2': len([n for n in palpite if n % 2 == 0]),
            'de_3': len([n for n in palpite if n % 3 == 0]),
            'de_5': len([n for n in palpite if n % 5 == 0]),
            'de_7': len([n for n in palpite if n % 7 == 0])
        }
        
        # Verifica números terminados em...
        terminacoes = {}
        for n in palpite:
            terminacao = n % 10
            terminacoes[terminacao] = terminacoes.get(terminacao, 0) + 1
        
        # Verifica números primos
        primos = [2, 3, 5, 7, 11, 13, 17, 19, 23]
        quantidade_primos = len([n for n in palpite if n in primos])
        
        return {
            'multiplos': multiplos,
            'terminacoes': terminacoes,
            'primos': quantidade_primos,
            'media': sum(palpite) / len(palpite),
            'mediana': sorted(palpite)[len(palpite)//2]
        }
    
    @staticmethod
    def _identificar_numeros_comuns(palpite: List[int], historico: List[List[int]]) -> List[int]:
        """Identifica números do palpite que são comuns no histórico"""
        if not historico:
            return []
        
        # Conta frequência de cada número no histórico
        contador = Counter()
        for resultado in historico:
            contador.update(resultado)
        
        # Ordena números do palpite por frequência no histórico
        numeros_ordenados = sorted(palpite, key=lambda x: contador.get(x, 0), reverse=True)
        
        # Retorna os 5 mais comuns
        return numeros_ordenados[:5]