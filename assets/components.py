# assets/components.py
import streamlit as st
from typing import List, Optional


class UIComponents:
    """
    Componentes de UI reutilizáveis.
    Compatível com Streamlit Cloud.
    Seguro para HTML/CSS customizado.
    """

    @staticmethod
    def mostrar_dezenas(
        dezenas: List[int],
        fixos: Optional[List[int]] = None,
        colunas: int = 15
    ):
        if not dezenas:
            st.warning("Nenhuma dezena para exibir.")
            return

        if fixos is None:
            fixos = []

        dezenas = sorted(dezenas)

        cols = st.columns(colunas)

        for i, numero in enumerate(dezenas):
            classe = "ball-fixed" if numero in fixos else "ball"

            with cols[i]:
                st.markdown(
                    f"""
                    <div class="{classe}">
                        {numero:02d}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    @staticmethod
    def mostrar_kpi_card(
        titulo: str,
        valor: str,
        referencia: str = ""
    ):
        st.markdown(
            f"""
            <div class="kpi-card">
                <div style="font-size:12px; color:#94a3b8;">
                    {titulo}
                </div>
                <div style="font-size:28px; font-weight:600; color:white;">
                    {valor}
                </div>
                <div style="font-size:11px; color:#64748b;">
                    {referencia}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    @staticmethod
    def mostrar_status_badge(
        texto: str,
        tipo: str = "info"
    ):
        cores = {
            "info": "#3b82f6",
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444"
        }

        cor = cores.get(tipo, cores["info"])

        st.markdown(
            f"""
            <span class="status-badge"
                  style="
                    background-color:{cor};
                    padding:4px 10px;
                    border-radius:999px;
                    font-size:11px;
                    color:white;
                    font-weight:500;
                  ">
                {texto}
            </span>
            """,
            unsafe_allow_html=True
        )
