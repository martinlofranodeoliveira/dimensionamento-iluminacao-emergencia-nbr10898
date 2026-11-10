"""Motor de dimensionamento de iluminação de emergência e balizamento ABNT NBR 10898:2013."""

from iluminacao_nbr10898.calculator import dimensionar_sistema_iluminacao
from iluminacao_nbr10898.codecs import carregar_projeto_json, exportar_resultado_json
from iluminacao_nbr10898.constants import (
    AUTONOMIA_MINIMA_HORAS,
    ILUMINANCIA_MIN_DESNIVEL_ESCADA_LUX,
    ILUMINANCIA_MIN_HORIZONTAL_LUX,
    QUEDA_TENSAO_MAXIMA_PERCENTUAL,
    TENSAO_NOMINAL_PADRAO_VCC,
)
from iluminacao_nbr10898.exporters import (
    gerar_csv_sanitizado,
    gerar_pacote_zip,
    gerar_relatorio_texto,
)
from iluminacao_nbr10898.models import (
    Ambiente,
    CircuitoCentral,
    DadosProjeto,
    ResultadoAmbiente,
    ResultadoBaterias,
    ResultadoCircuito,
    ResultadoDimensionamento,
    TipoAmbiente,
    TipoBalizamento,
    TipoSistemaAlimentacao,
)
from iluminacao_nbr10898.svg_generator import gerar_painel_svg

__version__ = "1.0.0"

__all__ = [
    "Ambiente",
    "CircuitoCentral",
    "DadosProjeto",
    "ResultadoAmbiente",
    "ResultadoBaterias",
    "ResultadoCircuito",
    "ResultadoDimensionamento",
    "TipoAmbiente",
    "TipoBalizamento",
    "TipoSistemaAlimentacao",
    "AUTONOMIA_MINIMA_HORAS",
    "ILUMINANCIA_MIN_DESNIVEL_ESCADA_LUX",
    "ILUMINANCIA_MIN_HORIZONTAL_LUX",
    "QUEDA_TENSAO_MAXIMA_PERCENTUAL",
    "TENSAO_NOMINAL_PADRAO_VCC",
    "carregar_projeto_json",
    "dimensionar_sistema_iluminacao",
    "exportar_resultado_json",
    "gerar_csv_sanitizado",
    "gerar_pacote_zip",
    "gerar_painel_svg",
    "gerar_relatorio_texto",
]
