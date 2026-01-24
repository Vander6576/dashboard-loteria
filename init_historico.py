# init_historico.py
import pandas as pd
import os

def inicializar_historico():
    """Cria arquivo de histórico vazio com estrutura correta"""
    historico_path = "data/historico.csv"
    
    # Cria pasta data se não existir
    os.makedirs("data", exist_ok=True)
    
    # Cria DataFrame vazio com estrutura correta
    df_vazio = pd.DataFrame(columns=['concurso', 'data', 'dezenas'])
    
    # Salva arquivo
    df_vazio.to_csv(historico_path, index=False, encoding='utf-8')
    print(f"✅ Histórico inicializado em {historico_path}")
    
    # Verifica
    if os.path.exists(historico_path):
        print(f"📁 Tamanho do arquivo: {os.path.getsize(historico_path)} bytes")
    else:
        print("❌ Erro ao criar arquivo")

if __name__ == "__main__":
    inicializar_historico()