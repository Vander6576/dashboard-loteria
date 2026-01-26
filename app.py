# =====================================================
# LotoAnalytica PRO v18 - Streamlit Cloud Ready
# =====================================================

# ============================
# IMPORTAÇÕES
# ============================
import os
from pathlib import Path
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

# Importações internas
from config import settings
from services import LoteriaAPI, AIEngine, JogoGenerator, KPICalculator
from utils import Formatters, validar_dezenas
from assets.components import UIComponents
from services.chat_analyzer import ChatAnalyzer

# ============================
# CONFIGURAÇÃO DA PÁGINA
# ============================
st.set_page_config(
    page_title="LotoAnalytica PRO v18",
    page_icon="🎱",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Exibir imagem de capa
st.image("assets/capa.png", use_column_width=True)

# ============================
# PATHS (Cloud Safe)
# ============================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

# ============================
# FUNÇÃO DE INICIALIZAÇÃO
# ============================
def inicializar_sistema():
    """Inicializa componentes do sistema e estado da sessão"""
    # Garante que a pasta de dados existe
    os.makedirs(DATA_DIR, exist_ok=True)

    # Cria arquivo de histórico se não existir
    historico_path = DATA_DIR / "historico.csv"
    if not historico_path.exists():
        pd.DataFrame(columns=['concurso', 'data', 'dezenas']).to_csv(
            historico_path, index=False, encoding='utf-8'
        )
        print("✅ Histórico inicializado")

    # ============================
# INICIALIZAÇÃO DO SESSION_STATE
# ============================
if "dezenas" not in st.session_state:
    st.session_state.dezenas = []   # lista de dezenas sorteadas
if "concurso" not in st.session_state:
    st.session_state.concurso = None   # número do concurso atual
if "anteriores" not in st.session_state:
    st.session_state.anteriores = []   # dezenas do concurso anterior
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []  # histórico do chat


# Executa inicialização logo no início do app
inicializar_sistema()

# ============================
# CARREGAR CSS
# ============================
def carregar_css(path: Path):
    """Carrega arquivo CSS externo"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("CSS não carregado. Usando estilo padrão.")

carregar_css(ASSETS_DIR / "styles.css")

# ============================
# INICIALIZAR SERVIÇOS
# ============================
def inicializar_servicos():
    """Inicializa e cacheia os serviços"""
    if 'servicos' not in st.session_state:
        st.session_state.servicos = {
            'api': LoteriaAPI(),
            'ai': AIEngine(),
            'gerador': JogoGenerator(),
            'kpi': KPICalculator(),
            'ui': UIComponents(),
            'formatador': Formatters(),
            'chat': ChatAnalyzer()
        }
    return st.session_state.servicos

# Obter serviços
servicos = inicializar_servicos()
api = servicos['api']
ai = servicos['ai']
gerador = servicos['gerador']
kpi_calc = servicos['kpi']
ui = servicos['ui']
formatador = servicos['formatador']
chat_analyzer = servicos['chat']

# ============================================
# FUNÇÕES AUXILIARES
# ============================================

def carregar_ultimo_concurso():
    """Carrega o último concurso da API"""
    with st.spinner("🔄 Buscando último resultado..."):
        # Certifique-se que 'api' está definido
        dados = api.buscar_concurso("latest")
        
        if dados:
            # Processa dezenas - AGORA DEVE FUNCIONAR
            dezenas = api.processar_dezenas(dados)
            numero_concurso = dados.get('concurso') or dados.get('numero')
            
            # Salva no histórico
            api.salvar_historico(dezenas, numero_concurso)
            
            # Busca anterior para comparação
            dezenas_anterior = []
            if numero_concurso and str(numero_concurso).isdigit():
                try:
                    num_anterior = int(str(numero_concurso)) - 1
                    dados_anterior = api.buscar_concurso(str(num_anterior))
                    if dados_anterior:
                        dezenas_anterior = api.processar_dezenas(dados_anterior)
                        api.salvar_historico(dezenas_anterior, num_anterior)
                except:
                    pass
            
            # Salva no session_state
            st.session_state.dez = dezenas
            st.session_state.conc = numero_concurso
            st.session_state.ant = dezenas_anterior
            
            st.success(f"✅ Concurso {numero_concurso} carregado e salvo no histórico!")
            st.rerun()
        else:
            st.error("❌ Erro ao buscar dados da API")

def processar_entrada_manual(entrada):
    """Processa entrada manual de dezenas"""
    numeros = formatador.parse_dezenas_manual(entrada)
    
    if validar_dezenas(numeros):
        st.session_state.dez = sorted(numeros)
        st.session_state.conc = "Manual"
        st.session_state.ant = []
        st.success("✅ Dados manuais processados!")
        
        # Salva no histórico como "Manual - [data]"
        data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        api.salvar_historico(numeros, f"Manual - {data_atual}")
        
        st.rerun()
    else:
        st.error(f"❌ Precisam ser exatamente {settings.NUMEROS_SORTEIO} números válidos (1-25, sem repetições)")

def gerar_e_exibir_palpite():
    """Gera e exibe palpite estratégico"""
    if 'dez' in st.session_state:
        dezenas = st.session_state.dez
        jogo_gerado, fixos = gerador.gerar_555(dezenas)
        
        st.session_state.jogo_gerado = jogo_gerado
        st.session_state.fixos = fixos
        st.session_state.kpis_palpite = kpi_calc.calcular(jogo_gerado, dezenas)
        st.rerun()

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.title("🚀 LotoPRO v18")
    st.markdown("---")
    
    # Botão para buscar último resultado
    if st.button("🔄 ÚLTIMO RESULTADO (API)", 
                 type="primary", 
                 use_container_width=True,
                 help="Busca o último resultado oficial da loteria"):
        carregar_ultimo_concurso()
    
    st.markdown("---")
    
    # Busca de concurso específico
    st.subheader("🔍 Buscar Concurso Anterior")
    col_busca1, col_busca2 = st.columns([3, 1])
    
    with col_busca1:
        concurso_busca = st.number_input(
            "Número do concurso:",
            min_value=1,
            value=1,
            step=1,
            key="input_busca"
        )
    
    with col_busca2:
        if st.button("Buscar", use_container_width=True):
            with st.spinner("Buscando..."):
                # Primeiro tenta na API
                dados = api.buscar_concurso(str(concurso_busca))
                if dados:
                    dezenas = api.processar_dezenas(dados)
                    st.session_state.dez = dezenas
                    st.session_state.conc = concurso_busca
                    st.session_state.ant = []
                    api.salvar_historico(dezenas, concurso_busca)
                    st.success(f"✅ Concurso {concurso_busca} encontrado!")
                    st.rerun()
                else:
                    # Tenta no histórico local
                    dezenas = api.buscar_por_numero(concurso_busca)
                    if dezenas:
                        st.session_state.dez = dezenas
                        st.session_state.conc = concurso_busca
                        st.session_state.ant = []
                        st.success(f"✅ Concurso {concurso_busca} do histórico!")
                        st.rerun()
                    else:
                        st.error("Concurso não encontrado")
    
    st.markdown("---")
    
    # Entrada manual
    st.subheader("📥 Entrada Manual")
    manual_input = st.text_area(
        "Digite 15 números (1-25):",
        placeholder="Exemplo:\n1 2 3 4 5 6 7 8 9 10 11 12 13 14 15\n\nou:\n1,2,3,4,5,6,7,8,9,10,11,12,13,14,15\n\nou:\n01-02-03-04-05-06-07-08-09-10-11-12-13-14-15",
        height=100,
        key="input_manual"
    )
    
    if st.button("📊 Processar Manual", use_container_width=True, key="btn_manual"):
        if manual_input.strip():
            processar_entrada_manual(manual_input)
        else:
            st.warning("Digite os números primeiro")
    
    st.markdown("---")
    
    # Histórico salvo
    st.subheader("📁 Histórico Local")
    if st.button("📋 Ver Histórico", use_container_width=True):
        df_historico = api.carregar_historico()
        if not df_historico.empty:
            st.dataframe(df_historico[['concurso', 'data']], use_container_width=True)
        else:
            st.info("Nenhum concurso no histórico")
    
    st.markdown("---")
    
    # Informações do sistema
    with st.expander("ℹ️ Sobre o Sistema"):
        st.markdown("""
        **LotoAnalytica PRO v18**
        
        Recursos:
        - 📊 Análise estatística avançada
        - 🤖 IA com DeepSeek/Gemini
        - 🎲 Gerador estratégico 5-5-5
        - 📈 Visualizações interativas
        - 💬 Chat analítico
        - 📁 Histórico local
        
        Método 5-5-5:
        Distribui igualmente entre:
        - 1-10 (Baixos)
        - 11-20 (Médios) 
        - 21-25 (Altos)
        """)

# ============================================
# DASHBOARD PRINCIPAL
# ============================================

# Tela inicial (quando não há dados)
if 'dez' not in st.session_state:
    st.markdown("# 🎱 LotoAnalytica PRO v18")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 🎯 Sistema Avançado de Análise de Loteria
        
        **Para começar:**
        1. **Clique em "ÚLTIMO RESULTADO"** na barra lateral para carregar dados reais
        2. **Ou** digite 15 números manualmente
        3. **Ou** busque um concurso específico
        
        **Análises disponíveis:**
        - 📈 Métricas estatísticas detalhadas
        - 🤖 Consulta com IA profissional
        - 🎲 Geração de palpites estratégicos
        - 📊 Gráficos interativos
        - 💬 Chat analítico
        - 📁 Histórico de concursos
        """)
        
        st.info("💡 **Dica:** O sistema usa o método 5-5-5 para equilíbrio estatístico")
    
    with col2:
        # Mostrar estatísticas do histórico
        df_historico = api.carregar_historico()
        if not df_historico.empty:
            st.metric("Concursos no histórico", len(df_historico))
            ultimo = df_historico.iloc[-1]
            st.metric("Último salvo", f"Concurso {ultimo['concurso']}")
        else:
            st.metric("Concursos no histórico", "0", "Carregue dados para começar")
    
    # Exemplo de entrada
    with st.expander("📋 Exemplo de entrada rápida"):
        if st.button("Carregar exemplo"):
            exemplo = list(range(1, 16))
            st.session_state.dez = exemplo
            st.session_state.conc = "Exemplo"
            st.session_state.ant = []
            
            # Salva exemplo no histórico
            api.salvar_historico(exemplo, "Exemplo")
            
            st.rerun()

# Dashboard quando há dados
else:
    dezenas = st.session_state.dez
    dezenas_anterior = st.session_state.get('ant', [])
    numero_concurso = st.session_state.conc
    
    # ============================================
    # 1. CABEÇALHO E DEZENAS
    # ============================================
    
    st.title(f"🎯 Análise Concurso #{numero_concurso}")
    
    # Exibir dezenas
    st.subheader("🔢 Dezenas Sorteadas")
    ui.mostrar_dezenas(dezenas)
    
    # ============================================
    # 2. KPIs
    # ============================================
    
    st.subheader("📈 Métricas de Performance")
    
    # Calcular KPIs
    kpis = kpi_calc.calcular(dezenas, dezenas_anterior)
    
    # Métricas em colunas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ui.mostrar_kpi_card(
            "Soma Total", 
            str(kpis['soma']), 
            "Ideal: 180-210"
        )
    
    with col2:
        status_repetidas = "✅" if 8 <= kpis['repetidas'] <= 10 else "⚠️"
        ui.mostrar_kpi_card(
            "Repetidas vs Anterior", 
            f"{kpis['repetidas']} {status_repetidas}", 
            "Esperado: 8-10"
        )
    
    with col3:
        dist_alvo = kpis['dist']
        status_dist = "✅" if dist_alvo == "5B | 5M | 5A" else "⚠️"
        ui.mostrar_kpi_card(
            "Distribuição", 
            f"{dist_alvo} {status_dist}", 
            "Alvo: 5|5|5"
        )
    
    with col4:
        ui.mostrar_kpi_card(
            "Moldura", 
            f"{kpis['moldura']}/15", 
            ""
        )
    
    # KPIs adicionais
    col5, col6, col7 = st.columns(3)
    
    with col5:
        st.metric("Números Pares", kpis['pares'], f"{15 - kpis['pares']} ímpares")
    
    with col6:
        st.metric("Números Primos", kpis['primos'])
    
    with col7:
        if dezenas_anterior:
            acertos = len(set(dezenas).intersection(set(dezenas_anterior)))
            st.metric("Acertos se jogasse anterior", acertos, 
                     f"Base: {len(dezenas_anterior)} números")
    
    # ============================================
    # 3. CHAT ANALÍTICO
    # ============================================
    
    st.markdown("---")
    st.subheader("💬 Chat Analítico")
    
    # Inicializar chat no session_state
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    
    # Exibir histórico do chat
    for msg in st.session_state.chat_messages[-10:]:  # Mostra últimas 10 mensagens
        if msg['role'] == 'user':
            st.chat_message("user").write(msg['content'])
        else:
            st.chat_message("assistant").write(msg['content'])
    
    # Input do usuário
    pergunta = st.chat_input("Pergunte sobre padrões, estratégias ou estatísticas...")
    
    if pergunta:
        # Adiciona pergunta ao chat
        st.session_state.chat_messages.append({'role': 'user', 'content': pergunta})
        st.chat_message("user").write(pergunta)
        
        # Gera resposta
        dados_para_chat = {
            'dezenas': dezenas,
            'concurso': numero_concurso,
            'kpis': kpis
        }
        
        with st.spinner("Analisando..."):
            resposta = chat_analyzer.gerar_resposta(pergunta, dados_para_chat)
            
            # Adiciona resposta ao chat
            st.session_state.chat_messages.append({'role': 'assistant', 'content': resposta})
            st.chat_message("assistant").write(resposta)
    
    # Botão para limpar chat
    if st.button("🧹 Limpar Chat", type="secondary"):
        st.session_state.chat_messages = []
        st.rerun()
    
    # ============================================
    # 4. ANÁLISE DE IA
    # ============================================
    
    st.markdown("---")
    st.subheader("🤖 Análise com Inteligência Artificial")
    
    # Botão para análise
    if st.button("🧠 EXECUTAR ANÁLISE PROFISSIONAL", 
                type="primary",
                use_container_width=True,
                key="btn_ia"):
        
        with st.spinner("Consultando motores de IA..."):
            dados_analise = {
                **kpis,
                'dezenas': dezenas,
                'concurso': numero_concurso
            }
            
            try:
                veredito, motor = ai.analisar_concurso(dados_analise)
                
                # Exibir resultado
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #0f172a, #1e293b);
                    padding: 20px;
                    border-radius: 10px;
                    border-left: 5px solid #00b894;
                    margin: 10px 0;
                    color: white;
                ">
                    {veredito}
                </div>
                """, unsafe_allow_html=True)
                
                ui.mostrar_status_badge(f"Motor: {motor}", "success")
                
            except Exception as e:
                st.error(f"Erro na análise: {str(e)}")
    
    # ============================================
    # 5. GERADOR ESTRATÉGICO
    # ============================================
    
    st.markdown("---")
    st.subheader("🎲 Gerador de Palpite Estratégico")
    
    col_gen1, col_gen2 = st.columns([3, 1])
    
    with col_gen1:
        if st.button("🚀 GERAR PALPITE 5-5-5", 
                    type="secondary",
                    use_container_width=True,
                    key="btn_gerar"):
            gerar_e_exibir_palpite()
    
    with col_gen2:
        if 'jogo_gerado' in st.session_state:
            if st.button("🗑️ Limpar", type="secondary", key="btn_limpar"):
                del st.session_state.jogo_gerado
                del st.session_state.fixos
                del st.session_state.kpis_palpite
                st.rerun()
    
    # Exibir palpite gerado (se existir)
    if 'jogo_gerado' in st.session_state:
        st.markdown("### 📋 Palpite Gerado")
        ui.mostrar_dezenas(st.session_state.jogo_gerado, st.session_state.fixos)
        
        kpis_palpite = st.session_state.kpis_palpite
        
        col_ana1, col_ana2 = st.columns(2)
        
        with col_ana1:
            st.success(f"""
            **✅ Método 5-5-5 Aplicado**
            
            Distribuição: {kpis_palpite['dist']}
            Fixos estratégicos: {st.session_state.fixos[0]} e {st.session_state.fixos[1]}
            Soma total: {kpis_palpite['soma']}
            Repetidas vs atual: {kpis_palpite['repetidas']}
            """)
        
        with col_ana2:
            st.info(f"""
            **📊 Comparação com o último sorteio:**
            
            Repetidas: {kpis_palpite['repetidas']} números
            Pares/Ímpares: {kpis_palpite['pares']}/{15 - kpis_palpite['pares']}
            Primos: {kpis_palpite['primos']}
            Moldura: {kpis_palpite['moldura']}/15
            """)
        
        # Botão para copiar palpite
        palpite_str = " ".join(f"{n:02d}" for n in st.session_state.jogo_gerado)
        st.code(palpite_str, language="text")
    
    # ============================================
    # 6. VISUALIZAÇÕES GRÁFICAS
    # ============================================
    
    st.markdown("---")
    st.subheader("📊 Visualizações Analíticas")
    
    tab1, tab2, tab3 = st.tabs(["📈 Distribuição", "⚖️ Equilíbrio", "🎯 Análise Detalhada"])
    
    with tab1:
        # Distribuição por faixa
        dist_data = {
            'Baixos (1-10)': len(kpis['grupos']['baixos']),
            'Médios (11-20)': len(kpis['grupos']['medios']),
            'Altos (21-25)': len(kpis['grupos']['altos'])
        }
        
        df_dist = pd.DataFrame({
            'Faixa': list(dist_data.keys()),
            'Quantidade': list(dist_data.values()),
            'Meta': [5, 5, 5]
        })
        
        fig_dist = px.bar(
            df_dist, 
            x='Faixa', 
            y=['Quantidade', 'Meta'],
            barmode='group',
            color_discrete_map={
                'Quantidade': '#3b82f6',
                'Meta': '#94a3b8'
            },
            title="📊 Distribuição por Faixa de Números vs Meta (5-5-5)",
            text='Quantidade'
        )
        
        fig_dist.update_layout(
            showlegend=True,
            yaxis_range=[0, 10],
            legend_title="",
            xaxis_title="",
            yaxis_title="Quantidade de Números"
        )
        
        fig_dist.update_traces(textposition='outside')
        st.plotly_chart(fig_dist, use_container_width=True)
        
        # Análise da distribuição
        col_dist1, col_dist2, col_dist3 = st.columns(3)
        with col_dist1:
            status_baixos = "✅" if dist_data['Baixos (1-10)'] == 5 else "⚠️"
            st.metric("Baixos (1-10)", dist_data['Baixos (1-10)'], f"Meta: 5 {status_baixos}")
        with col_dist2:
            status_medios = "✅" if dist_data['Médios (11-20)'] == 5 else "⚠️"
            st.metric("Médios (11-20)", dist_data['Médios (11-20)'], f"Meta: 5 {status_medios}")
        with col_dist3:
            status_altos = "✅" if dist_data['Altos (21-25)'] == 5 else "⚠️"
            st.metric("Altos (21-25)", dist_data['Altos (21-25)'], f"Meta: 5 {status_altos}")
    
    with tab2:
        # Equilíbrio Par/Ímpar
        pares = kpis['pares']
        impares = 15 - pares
        
        fig_pizza = px.pie(
            names=['Pares', 'Ímpares'],
            values=[pares, impares],
            hole=0.4,
            color=['Pares', 'Ímpares'],
            color_discrete_map={
                'Pares': '#3b82f6',
                'Ímpares': '#10b981'
            },
            title="⚖️ Equilíbrio Par/Ímpar"
        )
        
        fig_pizza.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        
        st.plotly_chart(fig_pizza, use_container_width=True)
        
        # Estatísticas de par/ímpar
        col_eq1, col_eq2, col_eq3 = st.columns(3)
        with col_eq1:
            status_pares = "✅" if 6 <= pares <= 9 else "⚠️"
            st.metric("Números Pares", pares, f"{pares/15*100:.1f}% {status_pares}")
        with col_eq2:
            status_impares = "✅" if 6 <= impares <= 9 else "⚠️"
            st.metric("Números Ímpares", impares, f"{impares/15*100:.1f}% {status_impares}")
        with col_eq3:
            diferenca = abs(pares - impares)
            status_dif = "✅" if diferenca <= 3 else "⚠️"
            st.metric("Diferença", diferenca, f"P-I {status_dif}")
        
        # Gráfico adicional: Tendência histórica (simulado)
        st.markdown("##### 📈 Tendência de Pares/Ímpares (últimos 10 concursos)")
        # Dados simulados para exemplo
        import numpy as np
        concursos_simulados = list(range(1, 11))
        pares_simulados = np.random.randint(5, 10, size=10)
        
        df_tendencia = pd.DataFrame({
            'Concurso': concursos_simulados,
            'Pares': pares_simulados,
            'Ímpares': [15 - p for p in pares_simulados]
        })
        
        fig_tendencia = px.line(
            df_tendencia,
            x='Concurso',
            y=['Pares', 'Ímpares'],
            markers=True,
            title="Evolução do Equilíbrio",
            color_discrete_map={
                'Pares': '#3b82f6',
                'Ímpares': '#10b981'
            }
        )
        
        fig_tendencia.update_layout(
            yaxis_range=[0, 15],
            yaxis_title="Quantidade",
            xaxis_title="Concurso",
            showlegend=True
        )
        
        st.plotly_chart(fig_tendencia, use_container_width=True)
    
    with tab3:
        # Tabela de análise detalhada
        st.markdown("### 📋 Tabela de Análise Detalhada")
        
                # Cálculos estatísticos avançados
        serie_dezenas = pd.Series(dezenas)
        
        # Cria dados garantindo tipos corretos
        dados_tabela = {
            'Métrica': ['Soma Total', 'Média por Número', 'Desvio Padrão', 
                       'Variância', 'Moda', 'Mediana', 'Amplitude',
                       'Coef. Variação', 'Assimetria', 'Curtose'],
            'Valor': [
                int(kpis['soma']),  # Garante int
                float(kpis['soma']/15),  # Garante float
                float(serie_dezenas.std()),
                float(serie_dezenas.var()),
                str(serie_dezenas.mode().iloc[0]) if not serie_dezenas.mode().empty else '-',
                float(serie_dezenas.median()),
                int(max(dezenas) - min(dezenas)),
                f"{(serie_dezenas.std()/serie_dezenas.mean()*100):.1f}%",
                float(serie_dezenas.skew()),
                float(serie_dezenas.kurtosis())
            ],
            'Status': [
                '✅' if 180 <= kpis['soma'] <= 210 else '⚠️',
                '✅' if 12 <= kpis['soma']/15 <= 14 else '⚠️',
                '📊',
                '📊',
                '📊',
                '📊',
                '📊',
                '📊',
                '📊',
                '📊'
            ],
            'Descrição': [
                'Soma de todos os números',
                'Média aritmética das dezenas',
                'Dispersão dos dados',
                'Variabilidade dos dados',
                'Valor mais frequente',
                'Valor central da distribuição',
                'Diferença entre maior e menor',
                'Desvio padrão em % da média',
                'Simetria da distribuição',
                'Medida de "achatamento"'
            ]
        }
        
        df_analise = pd.DataFrame(dados_tabela)
        
        # Função de estilização
        def color_status(val):
            if val == '✅':
                return 'color: #10b981; font-weight: bold'
            elif val == '⚠️':
                return 'color: #f59e0b; font-weight: bold'
            else:
                return 'color: #64748b'
        
        # Display com tipos explícitos
        st.dataframe(
            df_analise.style.map(color_status, subset=['Status']),
            use_container_width=True,
            hide_index=True,
            height=400,
            column_config={
                "Métrica": st.column_config.TextColumn("Métrica", width="medium"),
                "Valor": st.column_config.TextColumn("Valor"),  # Usa TextColumn para valores mistos
                "Status": st.column_config.TextColumn("Status", width="small"),
                "Descrição": st.column_config.TextColumn("Descrição", width="large")
            }
        )

        # NOVO MAPA DE NÚMEROS SORTEADOS - TABELA 5x5
        st.markdown("### 🗺️ Mapa de Números Sorteados (01-25)")
        
        # Cria uma grade 5x5
        colunas = st.columns(5)
        
        for i in range(25):
            numero = i + 1
            linha = i // 5
            coluna = i % 5
            
            with colunas[coluna]:
                # Define estilo baseado se o número foi sorteado
                if numero in dezenas:
                    estilo = """
                    <div style="
                        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
                        color: white;
                        border-radius: 10px;
                        padding: 10px;
                        margin: 3px;
                        text-align: center;
                        font-weight: bold;
                        font-size: 16px;
                        box-shadow: 0 3px 8px rgba(59, 130, 246, 0.3);
                        border: 3px solid #1e40af;
                        transform: scale(1.05);
                        transition: all 0.3s ease;
                    ">
                        <div style="font-size: 12px; opacity: 0.9;">{numero:02d}</div>
                        <div style="font-size: 14px;">✅</div>
                    </div>
                    """
                else:
                    estilo = """
                    <div style="
                        background: #f8fafc;
                        color: #64748b;
                        border-radius: 8px;
                        padding: 10px;
                        margin: 3px;
                        text-align: center;
                        font-weight: bold;
                        font-size: 16px;
                        border: 2px solid #e2e8f0;
                        transition: all 0.3s ease;
                    ">
                        <div style="font-size: 12px; opacity: 0.7;">{numero:02d}</div>
                        <div style="font-size: 14px; opacity: 0.5;">○</div>
                    </div>
                    """
                
                st.markdown(estilo.format(numero=numero), unsafe_allow_html=True)
        
        # Estatísticas do mapa
        col_map1, col_map2, col_map3, col_map4 = st.columns(4)
        
        with col_map1:
            percentual = (len(dezenas) / 25) * 100
            st.metric("Sorteados", f"{len(dezenas)}/25", f"{percentual:.1f}%")
        
        with col_map2:
            nao_sorteados = 25 - len(dezenas)
            st.metric("Não Sorteados", f"{nao_sorteados}/25")
        
        with col_map3:
            # Análise por quadrantes
            q1 = [1,2,3,4,5,6,11,12,13,14,15]
            q2 = [7,8,9,10,16,17,18,19,20]
            q3 = [21,22,23,24,25]
            
            q1_count = len([n for n in dezenas if n in q1])
            q2_count = len([n for n in dezenas if n in q2])
            q3_count = len([n for n in dezenas if n in q3])
            
            st.metric("Quadrantes", f"Q1:{q1_count} Q2:{q2_count} Q3:{q3_count}")
        
        with col_map4:
            # Números mais próximos uns dos outros
            diferencas = [dezenas[i+1] - dezenas[i] for i in range(len(dezenas)-1)]
            sequencias = sum(1 for d in diferencas if d == 1)
            st.metric("Sequências", sequencias, "números consecutivos")
        
        # Gráfico de dispersão melhorado
        st.markdown("### 📊 Visualização em Grade")
        
        numeros_grid = list(range(1, 26))
        presentes = [1 if n in dezenas else 0 for n in numeros_grid]
        
        df_grid = pd.DataFrame({
            'Número': numeros_grid,
            'X': [(n-1)%5 for n in numeros_grid],  # Coluna 0-4
            'Y': [4-((n-1)//5) for n in numeros_grid],  # Linha 0-4 (invertido)
            'Presente': presentes,
            'Tamanho': [20 if n in dezenas else 10 for n in numeros_grid],
            'Tipo': ['Baixo' if 1 <= n <= 10 else 'Médio' if 11 <= n <= 20 else 'Alto' for n in numeros_grid],
            'Label': [f"{n:02d} ✅" if n in dezenas else f"{n:02d}" for n in numeros_grid]
        })
        
        fig_grid = px.scatter(
            df_grid,
            x='X',
            y='Y',
            color='Tipo',
            size='Tamanho',
            hover_name='Número',
            text='Label',
            color_discrete_map={
                'Baixo': '#3b82f6',
                'Médio': '#8b5cf6',
                'Alto': '#10b981'
            },
            title="Visualização em Grade dos Números 01-25",
            size_max=25
        )
        
        fig_grid.update_traces(
            textposition='middle center',
            marker=dict(line=dict(width=2, color='DarkSlateGrey')),
            textfont=dict(size=12, color='white')
        )
        
        fig_grid.update_layout(
            xaxis=dict(
                visible=True,
                tickmode='array',
                tickvals=[0, 1, 2, 3, 4],
                ticktext=['Col 1', 'Col 2', 'Col 3', 'Col 4', 'Col 5'],
                range=[-0.5, 4.5]
            ),
            yaxis=dict(
                visible=True,
                tickmode='array',
                tickvals=[0, 1, 2, 3, 4],
                ticktext=['Linha 5', 'Linha 4', 'Linha 3', 'Linha 2', 'Linha 1'],
                range=[-0.5, 4.5]
            ),
            showlegend=True,
            height=500,
            plot_bgcolor='rgba(240, 242, 245, 0.5)'
        )
        
        # Adicionar grid
        fig_grid.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
        fig_grid.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
        
        st.plotly_chart(fig_grid, use_container_width=True)
        
        # Análise de clusters
        st.markdown("##### 🔍 Análise de Agrupamentos")
        
        col_cluster1, col_cluster2, col_cluster3 = st.columns(3)
        
        with col_cluster1:
            # Verifica se há números isolados
            isolados = 0
            for num in dezenas:
                if (num-1) not in dezenas and (num+1) not in dezenas:
                    isolados += 1
            st.metric("Números Isolados", isolados)
        
        with col_cluster2:
            # Maior sequência consecutiva
            sequencia_atual = 1
            maior_sequencia = 1
            for i in range(len(dezenas)-1):
                if dezenas[i+1] - dezenas[i] == 1:
                    sequencia_atual += 1
                    maior_sequencia = max(maior_sequencia, sequencia_atual)
                else:
                    sequencia_atual = 1
            st.metric("Maior Sequência", maior_sequencia)
        
        with col_cluster3:
            # Distribuição por colunas (na grade 5x5)
            colunas_count = [0, 0, 0, 0, 0]
            for num in dezenas:
                coluna = (num - 1) % 5
                colunas_count[coluna] += 1
            coluna_mais = colunas_count.index(max(colunas_count)) + 1
            st.metric("Coluna Mais Populosa", f"Col {coluna_mais}", f"{max(colunas_count)} números")
            
# ============================================
# RODAPÉ
# ============================================

