"""Constantes e parâmetros normativos da ABNT NBR 10898:2013.

ABNT NBR 10898:2013 - Sistema de iluminação de emergência.
"""

from fractions import Fraction
from typing import Final

# Níveis mínimos regulamentares de iluminância no plano do piso (lux)
ILUMINANCIA_MIN_HORIZONTAL_LUX: Final[Fraction] = Fraction(3, 1)  # 3.0 lux para áreas planas
ILUMINANCIA_MIN_DESNIVEL_ESCADA_LUX: Final[Fraction] = Fraction(5, 1)  # 5.0 lux para escadas e desníveis
ILUMINANCIA_MIN_RISCO_ELEVADO_LUX: Final[Fraction] = Fraction(5, 1)  # 5.0 lux para locais de alto risco

# Relação máxima de uniformidade de iluminação (Emax / Emin)
RELACAO_UNIFORMIDADE_MAXIMA: Final[Fraction] = Fraction(40, 1)

# Espaçamento máximo entre luminárias em função da altura de montagem
FATOR_ESPACAMENTO_MAX_ALTURA: Final[Fraction] = Fraction(4, 1)  # d <= 4 * h

# Distâncias máximas para sinalização de balizamento (metros)
DISTANCIA_MAX_BALIZAMENTO_FACE_SIMPLES_M: Final[Fraction] = Fraction(15, 1)  # 15 m
DISTANCIA_MAX_BALIZAMENTO_FACE_DUPLA_M: Final[Fraction] = Fraction(30, 1)  # 30 m

# Altura de fixação de sinalizadores de saída sobre vergas de portas (metros)
ALTURA_MIN_PORTA_SAIDA_M: Final[Fraction] = Fraction(20, 10)  # 2.00 m
ALTURA_MAX_PORTA_SAIDA_M: Final[Fraction] = Fraction(25, 10)  # 2.50 m

# Autonomia mínima regulamentar exigida para sistema de emergência (horas)
AUTONOMIA_MINIMA_HORAS: Final[Fraction] = Fraction(2, 1)  # 2 horas (120 minutos)
TEMPO_MAXIMO_PARTIDA_GERADOR_SEG: Final[Fraction] = Fraction(12, 1)  # 12 segundos

# Fatores fotométricos médios de projeto
FATOR_MANUTENCAO_PADRAO: Final[Fraction] = Fraction(4, 5)  # 0.80 (80% de conservação)
FATOR_UTILIZACAO_CLARO: Final[Fraction] = Fraction(6, 10)  # 0.60 (tetos e paredes claras)
FATOR_UTILIZACAO_ESCURO: Final[Fraction] = Fraction(5, 10)  # 0.50 (galpões e garagens)

# Parâmetros elétricos para sistemas centralizados de corrente contínua
TENSAO_NOMINAL_PADRAO_VCC: Final[Fraction] = Fraction(24, 1)  # 24 Vcc
QUEDA_TENSAO_MAXIMA_PERCENTUAL: Final[Fraction] = Fraction(10, 100)  # 10%
RESISTIVIDADE_COBRE_OHM_MM2_M: Final[Fraction] = Fraction(1, 58)  # ~0.017241 Ohm*mm²/m a 20°C
SECAO_MINIMA_CONDUTOR_MM2: Final[Fraction] = Fraction(15, 10)  # 1.50 mm²

# Fator de segurança e envelhecimento para dimensionamento de baterias
FATOR_SEGURANCA_BATERIA: Final[Fraction] = Fraction(5, 4)  # 1.25 (+25% de margem)

# Capacidades comerciais padrão de baterias seladas VRLA (Ah em 24Vcc ou 12V)
CAPACIDADES_BATERIAS_VRLA_AH: Final[tuple[Fraction, ...]] = (
    Fraction(45, 10),   # 4.5 Ah
    Fraction(7, 1),     # 7.0 Ah
    Fraction(9, 1),     # 9.0 Ah
    Fraction(12, 1),    # 12.0 Ah
    Fraction(18, 1),    # 18.0 Ah
    Fraction(26, 1),    # 26.0 Ah
    Fraction(40, 1),    # 40.0 Ah
    Fraction(65, 1),    # 65.0 Ah
    Fraction(100, 1),   # 100.0 Ah
    Fraction(150, 1),   # 150.0 Ah
    Fraction(200, 1),   # 200.0 Ah
)

# Catálogo de luminárias de aclaramento LED comerciais típicas
CATALOGO_LUMINARIAS_ACLARAMENTO: Final[dict[str, dict[str, Fraction]]] = {
    "bloco_led_100lm": {
        "fluxo_luminoso_lm": Fraction(100, 1),
        "potencia_eletrica_w": Fraction(1, 1),
        "angulo_abertura_graus": Fraction(120, 1),
    },
    "bloco_led_250lm": {
        "fluxo_luminoso_lm": Fraction(250, 1),
        "potencia_eletrica_w": Fraction(2, 1),
        "angulo_abertura_graus": Fraction(120, 1),
    },
    "luminaria_led_600lm": {
        "fluxo_luminoso_lm": Fraction(600, 1),
        "potencia_eletrica_w": Fraction(5, 1),
        "angulo_abertura_graus": Fraction(120, 1),
    },
    "luminaria_led_1200lm": {
        "fluxo_luminoso_lm": Fraction(1200, 1),
        "potencia_eletrica_w": Fraction(10, 1),
        "angulo_abertura_graus": Fraction(120, 1),
    },
    "farol_duplo_led_2400lm": {
        "fluxo_luminoso_lm": Fraction(2400, 1),
        "potencia_eletrica_w": Fraction(18, 1),
        "angulo_abertura_graus": Fraction(90, 1),
    },
}

# Catálogo de blocos de sinalização de balizamento LED típicos
CATALOGO_BALIZAMENTO_SAIDA: Final[dict[str, dict[str, Fraction]]] = {
    "baliza_face_simples_30lm": {
        "fluxo_luminoso_lm": Fraction(30, 1),
        "potencia_eletrica_w": Fraction(15, 10),  # 1.5 W
        "distancia_visibilidade_m": Fraction(15, 1),
    },
    "baliza_face_dupla_50lm": {
        "fluxo_luminoso_lm": Fraction(50, 1),
        "potencia_eletrica_w": Fraction(25, 10),  # 2.5 W
        "distancia_visibilidade_m": Fraction(30, 1),
    },
}
