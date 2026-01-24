# services/loteria_api.py - VERSÃO COMPLETA E ATUALIZADA
import requests
import pandas as pd
import os
from typing import Optional, Dict, Any, List
from collections import Counter
from config import settings

class LoteriaAPI:
    """Serviço para buscar dados da loteria"""
    
    def __init__(self):
        """Inicializador da classe"""
        pass
    
    # ========== MÉTODOS PRINCIPAIS ==========
    
    def buscar_concurso(self, concurso: str = "latest") -> Optional[Dict[str, Any]]:
        """
        Busca dados de um concurso específico
        Args:
            concurso: Número do concurso ou 'latest'
        Returns:
            Dicionário com dados do concurso ou None
        """
        try:
            url = f"{settings.LOTERIA_API_URL}/{concurso}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Erro ao buscar concurso: {e}")
            return None
    
    def processar_dezenas(self, dados: Dict[str, Any]) -> List[int]:
        """
        Extrai e formata as dezenas dos dados da API
        Args:
            dados: Dicionário com dados do concurso
        Returns:
            Lista ordenada de dezenas (inteiros)
        """
        if not dados:
            return []
        
        # Tenta diferentes formatos de resposta da API
        dezenas = None
        
        # Formato 1: chave 'dezenas'
        if 'dezenas' in dados:
            dezenas = dados['dezenas']
        
        # Formato 2: chave 'listaDezenas'  
        elif 'listaDezenas' in dados:
            dezenas = dados['listaDezenas']
        
        # Formato 3: busca em lista premiada
        elif 'listaRateioPremio' in dados and dados['listaRateioPremio']:
            primeiro_premio = dados['listaRateioPremio'][0]
            if 'listaDezenas' in primeiro_premio:
                dezenas = primeiro_premio['listaDezenas']
        
        if dezenas:
            # Converte para inteiros e ordena
            return sorted([int(d) for d in dezenas])
        
        return []
    
    # ========== MÉTODOS DE HISTÓRICO ==========
    
    def salvar_historico(self, dezenas: List[int], numero_concurso: Any) -> bool:
        """
        Salva o concurso no histórico CSV
        Args:
            dezenas: Lista de dezenas sorteadas
            numero_concurso: Número do concurso
        Returns:
            True se salvou com sucesso
        """
        try:
            historico_path = "data/historico.csv"
            
            # Cria pasta data se não existir
            os.makedirs("data", exist_ok=True)
            
            # Cria DataFrame com os dados
            novo_registro = pd.DataFrame({
                'concurso': [str(numero_concurso)],
                'data': [pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")],
                'dezenas': [','.join(map(str, dezenas))]
            })
            
            # Se o arquivo existe e não está vazio, adiciona
            if os.path.exists(historico_path) and os.path.getsize(historico_path) > 0:
                try:
                    df_existente = pd.read_csv(historico_path, dtype={'concurso': str})
                    df_novo = pd.concat([df_existente, novo_registro], ignore_index=True)
                except (pd.errors.EmptyDataError, pd.errors.ParserError):
                    # Arquivo existe mas está vazio/corrompido
                    df_novo = novo_registro
            else:
                df_novo = novo_registro
            
            # Remove duplicatas mantendo a última
            df_novo = df_novo.drop_duplicates(subset=['concurso'], keep='last')
            
            # Salva o arquivo
            df_novo.to_csv(historico_path, index=False, encoding='utf-8')
            
            return True
        except Exception as e:
            print(f"Erro ao salvar histórico: {e}")
            return False
    
    def carregar_historico(self) -> pd.DataFrame:
        """
        Carrega o histórico de concursos
        Returns:
            DataFrame com histórico
        """
        try:
            historico_path = "data/historico.csv"
            if os.path.exists(historico_path) and os.path.getsize(historico_path) > 0:
                df = pd.read_csv(historico_path, dtype={'concurso': str}, encoding='utf-8')
                # Verifica se tem colunas necessárias
                if not df.empty and 'dezenas' in df.columns:
                    # Converte string de dezenas para lista
                    df['dezenas_lista'] = df['dezenas'].apply(
                        lambda x: [int(n.strip()) for n in str(x).split(',') if n.strip().isdigit()]
                    )
                    return df
            # Retorna DataFrame vazio com estrutura correta
            return pd.DataFrame(columns=['concurso', 'data', 'dezenas', 'dezenas_lista'])
        except Exception as e:
            print(f"Erro ao carregar histórico: {e}")
            return pd.DataFrame(columns=['concurso', 'data', 'dezenas', 'dezenas_lista'])
    
    def buscar_por_numero(self, numero: int) -> Optional[List[int]]:
        """
        Busca dezenas de um concurso específico no histórico
        Args:
            numero: Número do concurso
        Returns:
            Lista de dezenas ou None
        """
        try:
            df = self.carregar_historico()
            if not df.empty and str(numero) in df['concurso'].values:
                dezenas_str = df.loc[df['concurso'] == str(numero), 'dezenas'].iloc[0]
                return [int(n) for n in dezenas_str.split(',')]
            return None
        except:
            return None
    
    # ========== MÉTODOS AUXILIARES ==========
    
    def testar_conexao(self) -> bool:
        """
        Testa se a API está funcionando
        Returns:
            True se conseguiu conectar
        """
        try:
            dados = self.buscar_concurso("latest")
            return dados is not None
        except:
            return False
    
    def get_ultimo_concurso_info(self) -> Optional[Dict]:
        """
        Obtém informações do último concurso
        Returns:
            Dicionário com informações ou None
        """
        dados = self.buscar_concurso("latest")
        if dados:
            dezenas = self.processar_dezenas(dados)
            return {
                'numero': dados.get('concurso') or dados.get('numero'),
                'dezenas': dezenas,
                'data': dados.get('data'),
                'acumulado': dados.get('acumulado')
            }
        return None
    
    # ========== NOVAS FUNÇÕES DE ANÁLISE (ADICIONADAS) ==========
    
    def obter_numeros_nao_sorteados(self, dezenas: List[int]) -> List[int]:
        """
        Retorna os números que NÃO foram sorteados
        Args:
            dezenas: Lista de dezenas sorteadas
        Returns:
            Lista de números de 1 a 25 que não foram sorteados
        """
        todos_numeros = list(range(1, 26))
        return [n for n in todos_numeros if n not in dezenas]
    
    def comparar_com_anteriores(self, dezenas_atual: List[int], 
                               quantidade: int = 5) -> Dict:
        """
        Compara com concursos anteriores do histórico
        Args:
            dezenas_atual: Dezenas do concurso atual
            quantidade: Quantos concursos anteriores analisar
        Returns:
            Dicionário com análise comparativa
        """
        df_historico = self.carregar_historico()
        
        if df_historico.empty or len(df_historico) < 2:
            return {
                'concursos_anteriores': 0,
                'media_repeticao': 0,
                'tendencias': {
                    'numeros_quentes': [],
                    'numeros_frios': [],
                    'frequencia_repeticao': {}
                },
                'comparacao_detalhada': []
            }
        
        # Pega os últimos concursos (excluindo o atual se estiver no histórico)
        df_recente = df_historico.tail(quantidade + 1)
        
        comparacoes = []
        todos_numeros_repetidos = []
        
        for i, row in df_recente.iterrows():
            if 'dezenas_lista' in df_recente.columns:
                dezenas_anterior = row['dezenas_lista']
                
                # Evita comparar consigo mesmo
                if dezenas_anterior != dezenas_atual:
                    numeros_repetidos = list(set(dezenas_atual) & set(dezenas_anterior))
                    percentual = (len(numeros_repetidos) / 15) * 100
                    
                    comparacao = {
                        'concurso': row['concurso'],
                        'data': row['data'],
                        'repetidos': len(numeros_repetidos),
                        'percentual': round(percentual, 1),
                        'numeros_repetidos': sorted(numeros_repetidos)
                    }
                    comparacoes.append(comparacao)
                    
                    todos_numeros_repetidos.extend(numeros_repetidos)
        
        # Calcula frequência de repetição
        frequencia_repeticao = Counter(todos_numeros_repetidos)
        
        # Identifica tendências
        numeros_quentes = [num for num, freq in frequencia_repeticao.items() 
                          if freq >= len(comparacoes) * 0.7] if comparacoes else []
        
        # Números frios: não apareceram nos últimos concursos analisados
        todos_numeros_analisados = []
        for comp in comparacoes:
            if 'numeros_repetidos' in comp:
                todos_numeros_analisados.extend(comp['numeros_repetidos'])
        
        numeros_frios = [num for num in range(1, 26) 
                        if num not in todos_numeros_analisados and num not in dezenas_atual]
        
        return {
            'concursos_anteriores': len(comparacoes),
            'media_repeticao': round(sum(c['repetidos'] for c in comparacoes) / len(comparacoes), 2) if comparacoes else 0,
            'tendencias': {
                'numeros_quentes': sorted(numeros_quentes),
                'numeros_frios': sorted(numeros_frios),
                'frequencia_repeticao': dict(frequencia_repeticao)
            },
            'comparacao_detalhada': comparacoes
        }
    
    def analisar_sequencias(self, dezenas: List[int]) -> Dict:
        """
        Analisa sequências e padrões nos números sorteados
        Args:
            dezenas: Lista de dezenas sorteadas
        Returns:
            Dicionário com análise de sequências
        """
        if not dezenas:
            return {
                'sequencias': [],
                'maior_sequencia': 0,
                'total_sequencias': 0,
                'gaps': [],
                'maior_gap': 0
            }
        
        dezenas_ordenadas = sorted(dezenas)
        
        # Encontra sequências consecutivas
        sequencias = []
        sequencia_atual = [dezenas_ordenadas[0]]
        
        for i in range(1, len(dezenas_ordenadas)):
            if dezenas_ordenadas[i] == dezenas_ordenadas[i-1] + 1:
                sequencia_atual.append(dezenas_ordenadas[i])
            else:
                if len(sequencia_atual) >= 2:
                    sequencias.append(sequencia_atual.copy())
                sequencia_atual = [dezenas_ordenadas[i]]
        
        if len(sequencia_atual) >= 2:
            sequencias.append(sequencia_atual)
        
        # Encontra gaps (números não sorteados entre sorteados)
        gaps = []
        for i in range(1, len(dezenas_ordenadas)):
            gap = dezenas_ordenadas[i] - dezenas_ordenadas[i-1] - 1
            if gap > 0:
                gaps.append({
                    'entre': (dezenas_ordenadas[i-1], dezenas_ordenadas[i]),
                    'tamanho': gap,
                    'numeros_faltantes': list(range(dezenas_ordenadas[i-1] + 1, dezenas_ordenadas[i]))
                })
        
        # Calcula maior sequência
        maior_sequencia = max([len(s) for s in sequencias]) if sequencias else 0
        
        # Calcula maior gap
        maior_gap = max([g['tamanho'] for g in gaps]) if gaps else 0
        
        return {
            'sequencias': sequencias,
            'maior_sequencia': maior_sequencia,
            'total_sequencias': len(sequencias),
            'gaps': gaps,
            'maior_gap': maior_gap
        }
    
    def analisar_distribuicao_temporal(self, dezenas: List[int]) -> Dict:
        """
        Analisa distribuição dos números ao longo do tempo (baseado na posição 1-25)
        Args:
            dezenas: Lista de dezenas sorteadas
        Returns:
            Dicionário com análise de distribuição temporal
        """
        # Análise por quadrantes (dividindo 1-25 em 4 partes)
        quadrantes = {
            'Q1': list(range(1, 7)),      # 1-6
            'Q2': list(range(7, 13)),     # 7-12
            'Q3': list(range(13, 19)),    # 13-18
            'Q4': list(range(19, 26))     # 19-25
        }
        
        # Análise por dezenas (grupos de 10)
        dezenas_grupos = {
            '01-10': list(range(1, 11)),
            '11-20': list(range(11, 21)),
            '21-25': list(range(21, 26))
        }
        
        # Análise por colunas (na matriz 5x5)
        colunas = {
            'Col1': [1, 6, 11, 16, 21],
            'Col2': [2, 7, 12, 17, 22],
            'Col3': [3, 8, 13, 18, 23],
            'Col4': [4, 9, 14, 19, 24],
            'Col5': [5, 10, 15, 20, 25]
        }
        
        # Contagem por categoria
        contagem_quadrantes = {q: len([n for n in dezenas if n in nums]) 
                              for q, nums in quadrantes.items()}
        contagem_dezenas = {d: len([n for n in dezenas if n in nums]) 
                           for d, nums in dezenas_grupos.items()}
        contagem_colunas = {c: len([n for n in dezenas if n in nums]) 
                           for c, nums in colunas.items()}
        
        # Encontra categorias com mais/menos números
        quadrante_mais = max(contagem_quadrantes, key=contagem_quadrantes.get) if contagem_quadrantes else None
        quadrante_menos = min(contagem_quadrantes, key=contagem_quadrantes.get) if contagem_quadrantes else None
        
        dezena_mais = max(contagem_dezenas, key=contagem_dezenas.get) if contagem_dezenas else None
        dezena_menos = min(contagem_dezenas, key=contagem_dezenas.get) if contagem_dezenas else None
        
        coluna_mais = max(contagem_colunas, key=contagem_colunas.get) if contagem_colunas else None
        coluna_menos = min(contagem_colunas, key=contagem_colunas.get) if contagem_colunas else None
        
        return {
            'quadrantes': contagem_quadrantes,
            'dezenas_grupos': contagem_dezenas,
            'colunas': contagem_colunas,
            'analise': {
                'quadrante_mais_populoso': quadrante_mais,
                'quadrante_menos_populoso': quadrante_menos,
                'dezena_mais_populosa': dezena_mais,
                'dezena_menos_populosa': dezena_menos,
                'coluna_mais_populosa': coluna_mais,
                'coluna_menos_populosa': coluna_menos
            }
        }
    
    def obter_estatisticas_completas(self, dezenas: List[int]) -> Dict:
        """
        Obtém estatísticas completas das dezenas sorteadas
        Args:
            dezenas: Lista de dezenas sorteadas
        Returns:
            Dicionário com todas as estatísticas
        """
        from services.kpi_calculator import KPICalculator
        
        kpis = KPICalculator.calcular(dezenas)
        numeros_nao_sorteados = self.obter_numeros_nao_sorteados(dezenas)
        comparacao = self.comparar_com_anteriores(dezenas)
        sequencias = self.analisar_sequencias(dezenas)
        distribuicao = self.analisar_distribuicao_temporal(dezenas)
        
        return {
            'kpis_basicos': kpis,
            'numeros_nao_sorteados': numeros_nao_sorteados,
            'quantidade_nao_sorteados': len(numeros_nao_sorteados),
            'percentual_nao_sorteados': round(len(numeros_nao_sorteados) / 25 * 100, 1),
            'comparacao_historica': comparacao,
            'analise_sequencias': sequencias,
            'analise_distribuicao': distribuicao,
            'resumo': {
                'soma_ideal': 180 <= kpis['soma'] <= 210,
                'distribuicao_ideal': kpis['dist'] == "5B | 5M | 5A",
                'repeticao_ideal': 8 <= kpis.get('repetidas', 0) <= 10 if 'repetidas' in kpis else True,
                'pares_ideal': 6 <= kpis['pares'] <= 9
            }
        }
    
    def gerar_relatorio_completo(self, dezenas: List[int], numero_concurso: Any = "Desconhecido") -> str:
        """
        Gera um relatório textual completo da análise
        Args:
            dezenas: Lista de dezenas sorteadas
            numero_concurso: Número do concurso
        Returns:
            String com relatório formatado
        """
        stats = self.obter_estatisticas_completas(dezenas)
        
        relatorio = f"""
{'='*60}
RELATÓRIO DE ANÁLISE - CONCURSO #{numero_concurso}
{'='*60}

DEZENAS SORTEADAS: {', '.join(f'{n:02d}' for n in sorted(dezenas))}

📊 ESTATÍSTICAS BÁSICAS:
• Soma Total: {stats['kpis_basicos']['soma']} ({'✅ Ideal' if stats['resumo']['soma_ideal'] else '⚠️ Fora da faixa'})
• Distribuição: {stats['kpis_basicos']['dist']} ({'✅ 5-5-5' if stats['resumo']['distribuicao_ideal'] else '⚠️ Não ideal'})
• Pares/Ímpares: {stats['kpis_basicos']['pares']}/{15-stats['kpis_basicos']['pares']} ({'✅ Balanceado' if stats['resumo']['pares_ideal'] else '⚠️ Desbalanceado'})
• Números Primos: {stats['kpis_basicos']['primos']}
• Moldura: {stats['kpis_basicos']['moldura']}/15

🔍 ANÁLISE DE NÚMEROS:
• Não sorteados: {len(stats['numeros_nao_sorteados'])} números ({stats['percentual_nao_sorteados']}%)
• Faixa com mais números: {max(stats['analise_distribuicao']['dezenas_grupos'], key=stats['analise_distribuicao']['dezenas_grupos'].get)}
• Coluna mais populosa: {stats['analise_distribuicao']['analise']['coluna_mais_populosa']}

📈 COMPARAÇÃO HISTÓRICA:
• Concursos analisados: {stats['comparacao_historica']['concursos_anteriores']}
• Média de repetição: {stats['comparacao_historica']['media_repeticao']:.1f} ({'✅ Ideal' if 8 <= stats['comparacao_historica']['media_repeticao'] <= 10 else '⚠️ Fora da média'})
• Números quentes: {', '.join(map(str, stats['comparacao_historica']['tendencias']['numeros_quentes'])) if stats['comparacao_historica']['tendencias']['numeros_quentes'] else 'Nenhum'}
• Números frios: {', '.join(map(str, stats['comparacao_historica']['tendencias']['numeros_frios'])) if stats['comparacao_historica']['tendencias']['numeros_frios'] else 'Nenhum'}

🔢 SEQUÊNCIAS E PADRÕES:
• Sequências encontradas: {stats['analise_sequencias']['total_sequencias']}
• Maior sequência: {stats['analise_sequencias']['maior_sequencia']} números
• Maior intervalo: {stats['analise_sequencias']['maior_gap']} números

🎯 RECOMENDAÇÕES PARA PRÓXIMO JOGO:
1. {'Mantenha a soma atual' if stats['resumo']['soma_ideal'] else f'Ajuste soma para 180-210 (atual: {stats["kpis_basicos"]["soma"]})'}
2. {'Mantenha distribuição 5-5-5' if stats['resumo']['distribuicao_ideal'] else f'Busque distribuição 5-5-5 (atual: {stats["kpis_basicos"]["dist"]})'}
3. Considere incluir 2-3 números frios: {', '.join(map(str, stats['comparacao_historica']['tendencias']['numeros_frios'][:3])) if stats['comparacao_historica']['tendencias']['numeros_frios'] else 'Nenhum número frio identificado'}
4. Evite muitos números da coluna {stats['analise_distribuicao']['analise']['coluna_mais_populosa']} (já tem {stats['analise_distribuicao']['colunas'][stats['analise_distribuicao']['analise']['coluna_mais_populosa']]})

{'='*60}
        """
        
        return relatorio