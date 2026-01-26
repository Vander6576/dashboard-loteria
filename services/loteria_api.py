# services/loteria_api.py
from pathlib import Path
import requests
import pandas as pd
from typing import Optional, Dict, Any, List
from collections import Counter
from config import settings

# =============================
# PATHS COMPATÍVEIS COM CLOUD
# =============================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
HISTORICO_PATH = DATA_DIR / "historico.csv"


class LoteriaAPI:
    """Serviço para buscar, armazenar e analisar dados da Lotofácil"""

    def __init__(self):
        DATA_DIR.mkdir(exist_ok=True)

    # =============================
    # API
    # =============================
    def buscar_concurso(self, concurso: str = "latest") -> Optional[Dict[str, Any]]:
        try:
            url = f"{settings.LOTERIA_API_URL}/{concurso}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

    def processar_dezenas(self, dados: Dict[str, Any]) -> List[int]:
        if not dados:
            return []

        dezenas = (
            dados.get("dezenas")
            or dados.get("listaDezenas")
        )

        if dezenas:
            return sorted(map(int, dezenas))

        return []

    # =============================
    # HISTÓRICO
    # =============================
    def salvar_historico(self, dezenas: List[int], numero_concurso: Any) -> bool:
        try:
            novo = pd.DataFrame([{
                "concurso": str(numero_concurso),
                "data": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                "dezenas": ",".join(map(str, dezenas))
            }])

            if HISTORICO_PATH.exists():
                df = pd.read_csv(HISTORICO_PATH, dtype=str)
                df = pd.concat([df, novo], ignore_index=True)
                df = df.drop_duplicates(subset="concurso", keep="last")
            else:
                df = novo

            df.to_csv(HISTORICO_PATH, index=False, encoding="utf-8")
            return True
        except Exception:
            return False

    def carregar_historico(self) -> pd.DataFrame:
        if not HISTORICO_PATH.exists():
            return self._df_vazio()

        try:
            df = pd.read_csv(HISTORICO_PATH, dtype=str)
            df["dezenas_lista"] = df["dezenas"].apply(
                lambda x: [int(n) for n in x.split(",") if n.isdigit()]
            )
            return df
        except Exception:
            return self._df_vazio()

    def _df_vazio(self) -> pd.DataFrame:
        return pd.DataFrame(
            columns=["concurso", "data", "dezenas", "dezenas_lista"]
        )

    # =============================
    # CONSULTAS
    # =============================
    def get_ultimo_concurso_info(self) -> Optional[Dict]:
        dados = self.buscar_concurso("latest")
        if not dados:
            return None

        dezenas = self.processar_dezenas(dados)

        return {
            "numero": dados.get("concurso") or dados.get("numero"),
            "data": dados.get("data"),
            "dezenas": dezenas,
            "acumulado": dados.get("acumulado")
        }

    # =============================
    # ANÁLISES
    # =============================
    def obter_numeros_nao_sorteados(self, dezenas: List[int]) -> List[int]:
        return [n for n in range(1, 26) if n not in dezenas]

    def comparar_com_anteriores(self, dezenas_atual: List[int], quantidade: int = 5) -> Dict:
        df = self.carregar_historico()

        if df.empty:
            return self._comparacao_vazia()

        df = df.tail(quantidade + 1)

        comparacoes = []
        repetidos_geral = []

        for _, row in df.iterrows():
            dezenas_ant = row["dezenas_lista"]
            if dezenas_ant == dezenas_atual:
                continue

            repetidos = list(set(dezenas_atual) & set(dezenas_ant))
            repetidos_geral.extend(repetidos)

            comparacoes.append({
                "concurso": row["concurso"],
                "repetidos": len(repetidos),
                "numeros": sorted(repetidos)
            })

        freq = Counter(repetidos_geral)

        return {
            "concursos_anteriores": len(comparacoes),
            "media_repeticao": round(
                sum(c["repetidos"] for c in comparacoes) / len(comparacoes), 2
            ) if comparacoes else 0,
            "tendencias": {
                "numeros_quentes": [n for n, f in freq.items() if f >= 3],
                "frequencia": dict(freq)
            },
            "comparacao_detalhada": comparacoes
        }

    def _comparacao_vazia(self) -> Dict:
        return {
            "concursos_anteriores": 0,
            "media_repeticao": 0,
            "tendencias": {},
            "comparacao_detalhada": []
        }

    def analisar_sequencias(self, dezenas: List[int]) -> Dict:
        dezenas = sorted(dezenas)
        sequencias = []
        atual = [dezenas[0]] if dezenas else []

        for i in range(1, len(dezenas)):
            if dezenas[i] == dezenas[i - 1] + 1:
                atual.append(dezenas[i])
            else:
                if len(atual) > 1:
                    sequencias.append(atual)
                atual = [dezenas[i]]

        if len(atual) > 1:
            sequencias.append(atual)

        return {
            "sequencias": sequencias,
            "total": len(sequencias),
            "maior": max((len(s) for s in sequencias), default=0)
        }

    def obter_estatisticas_completas(self, dezenas: List[int]) -> Dict:
        from services.kpi_calculator import KPICalculator

        return {
            "kpis": KPICalculator.calcular(dezenas),
            "nao_sorteados": self.obter_numeros_nao_sorteados(dezenas),
            "comparacao": self.comparar_com_anteriores(dezenas),
            "sequencias": self.analisar_sequencias(dezenas)
        }
