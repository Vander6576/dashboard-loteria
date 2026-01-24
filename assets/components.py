# assets/components.py
import streamlit as st
from typing import List

class UIComponents:
    """Componentes de UI reutilizáveis"""
    
    @staticmethod
    def mostrar_dezenas(dezenas: List[int], fixos: List[int] = None, colunas: int = 15):
        if fixos is None:
            fixos = []
        
        cols = st.columns(colunas)
        for i, numero in enumerate(dezenas):
            classe = "ball-fixed" if numero in fixos else "ball"
            cols[i].markdown(
                f'<div class="{classe}">{numero:02d}</div>', 
                unsafe_allow_html=True
            )
    
    @staticmethod
    def mostrar_kpi_card(titulo: str, valor: str, referencia: str = ""):
        st.markdown(f"""
        <div class="kpi-card">
            <h4 style="margin:0; color:#94a3b8">{titulo}</h4>
            <h2 style="margin:5px 0; color:white">{valor}</h2>
            <p style="margin:0; font-size:12px; color:#64748b">{referencia}</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def mostrar_status_badge(texto: str, tipo: str = "info"):
        cores = {
            "info": "#3b82f6",
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444"
        }
        cor = cores.get(tipo, "#3b82f6")
        
        st.markdown(f"""
        <div class="status-badge" style="background:{cor}">
            {texto}
        </div>
        """, unsafe_allow_html=True)