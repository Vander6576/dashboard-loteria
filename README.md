🎯 LotoAnalytica PRO v18
LotoAnalytica é um dashboard de inteligência estatística para análise e geração de jogos da Lotofácil. O projeto utiliza APIs de resultados oficiais e modelos de Inteligência Artificial (DeepSeek e Gemini) para fornecer vereditos técnicos baseados em probabilidade, sem promessas irreais.

🚀 Funcionalidades Principais
Sincronização via API: Obtém resultados oficiais da Caixa em tempo real.

Dual-IA Analysis: Análise de tendência utilizando os motores DeepSeek-V3 e Gemini 1.5 Flash.

Método Estratégico 5-5-5: Gerador de jogos que divide o volante em grupos de 5 dezenas (Baixas, Médias e Altas).

KPIs Avançadas:

Cálculo de Soma, Pares/Ímpares e Números Primos.

Índice de Repetição do concurso anterior.

Frequência de Linhas e Colunas.

Veredito Visual: Status coloridos (Badges) para decisão rápida (Jogar, Aguardar ou Moderado).

🛠️ Tecnologias Utilizadas
Linguagem: Python 3.12

Interface: Streamlit

Gráficos: Plotly Express / Altair

IA: Google Generative AI & RapidAPI (DeepSeek)

Dados: LoteriasCaixa-API

Bash
streamlit run app.py
⚖️ Metodologia Estatística
O projeto baseia-se na Distribuição Normal (Curva de Gauss). A maioria dos sorteios da Lotofácil concentra a soma das dezenas entre 180 e 210. O LotoAnalytica prioriza gerar jogos que se mantenham dentro desta "zona de ouro", aumentando as chances matemáticas de acerto.

Aviso Legal: Este software é uma ferramenta de estudo estatístico. Loterias envolvem risco e não há garantia de lucros. Jogue com responsabilidade.
