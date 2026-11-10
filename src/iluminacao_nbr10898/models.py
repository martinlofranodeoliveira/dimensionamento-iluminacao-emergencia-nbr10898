"""Modelos de dados e estruturas imutáveis para iluminação de emergência NBR 10898."""

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Optional


class TipoAmbiente(str, Enum):
    """Classificação funcional do ambiente segundo requisitos de aclaramento."""
    CIRCULACAO_HORIZONTAL = "circulacao_horizontal"
    ESCADA_OU_DESNIVEL = "escada_ou_desnivel"
    SALA_ESCRITORIO = "sala_escritorio"
    GALPAO_DEPOSITO = "galpao_deposito"
    AREA_RISCO_ELEVADO = "area_risco_elevado"


class TipoSistemaAlimentacao(str, Enum):
    """Tipologia de fonte e distribuição de energia de emergência."""
    BLOCO_AUTONOMO = "bloco_autonomo"
    CENTRALIZADO_BATERIAS = "centralizado_baterias"
    MOTO_GERADOR = "moto_gerador"


class TipoBalizamento(str, Enum):
    """Tipo de sinalizador luminoso de rota de fuga e saída."""
    FACE_SIMPLES = "face_simples"
    FACE_DUPLA = "face_dupla"


@dataclass(frozen=True)
class Ambiente:
    """Dados de entrada de um compartimento ou setor da edificação."""
    nome: str
    area_m2: Fraction
    comprimento_rota_m: Fraction
    pe_direito_m: Fraction
    altura_montagem_m: Fraction
    tipo_ambiente: TipoAmbiente
    portas_saida_emergencia: int
    mudancas_direcao: int
    modelo_aclaramento: str
    reflexao_clara: bool = True


@dataclass(frozen=True)
class CircuitoCentral:
    """Circuito elétrico de distribuição em corrente contínua."""
    nome: str
    comprimento_total_m: Fraction
    secao_condutor_mm2: Fraction
    tensao_vcc: Fraction


@dataclass(frozen=True)
class DadosProjeto:
    """Especificações globais do projeto de iluminação de emergência."""
    nome_edificacao: str
    tipo_sistema: TipoSistemaAlimentacao
    ambientes: tuple[Ambiente, ...]
    circuitos: tuple[CircuitoCentral, ...]
    autonomia_horas: Fraction


@dataclass(frozen=True)
class ResultadoAmbiente:
    """Dimensionamento luminotécnico e de sinalização de um ambiente."""
    nome: str
    tipo_ambiente: TipoAmbiente
    iluminancia_requerida_lux: Fraction
    fluxo_total_requerido_lm: Fraction
    luminarias_aclaramento: int
    fluxo_unitario_lm: Fraction
    espacamento_medio_m: Fraction
    espacamento_maximo_permitido_m: Fraction
    sinalizadores_balizamento: int
    potencia_aclaramento_w: Fraction
    potencia_balizamento_w: Fraction
    potencia_total_w: Fraction
    conformidade_espacamento: bool


@dataclass(frozen=True)
class ResultadoCircuito:
    """Avaliação elétrica de queda de tensão em circuito centralizado."""
    nome: str
    comprimento_m: Fraction
    secao_condutor_mm2: Fraction
    corrente_total_a: Fraction
    resistencia_ohm: Fraction
    queda_tensao_v: Fraction
    queda_tensao_percentual: Fraction
    limite_queda_tensao_v: Fraction
    aprovado: bool


@dataclass(frozen=True)
class ResultadoBaterias:
    """Dimensionamento de autonomia do banco central de baterias VRLA."""
    tensao_banco_vcc: Fraction
    corrente_total_sistema_a: Fraction
    autonomia_horas: Fraction
    capacidade_teorica_ah: Fraction
    fator_seguranca: Fraction
    capacidade_minima_requerida_ah: Fraction
    capacidade_comercial_adotada_ah: Fraction
    quantidade_baterias_12v: int


@dataclass(frozen=True)
class ResultadoDimensionamento:
    """Resultado consolidado do projeto conforme ABNT NBR 10898:2013."""
    nome_edificacao: str
    tipo_sistema: TipoSistemaAlimentacao
    total_luminarias_aclaramento: int
    total_sinalizadores_balizamento: int
    total_dispositivos: int
    potencia_total_instalada_w: Fraction
    ambientes: tuple[ResultadoAmbiente, ...]
    circuitos: tuple[ResultadoCircuito, ...]
    baterias: Optional[ResultadoBaterias]
    alertas: tuple[str, ...]
    recomendacoes: tuple[str, ...]
