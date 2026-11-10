"""Codec JSON canônico RFC 8259 para dados de iluminação de emergência NBR 10898."""

import json
from fractions import Fraction
from typing import Any

from iluminacao_nbr10898.models import (
    Ambiente,
    CircuitoCentral,
    DadosProjeto,
    ResultadoAmbiente,
    ResultadoBaterias,
    ResultadoCircuito,
    ResultadoDimensionamento,
    TipoAmbiente,
    TipoSistemaAlimentacao,
)


def _rejeitar_float(valor: str) -> None:
    raise ValueError(f"Ponto flutuante ({valor}) não é permitido. Utilize inteiros ou strings decimais exatas.")


def _rejeitar_chaves_duplicadas(pares: list[tuple[str, Any]]) -> dict[str, Any]:
    resultado: dict[str, Any] = {}
    for chave, valor in pares:
        if chave in resultado:
            raise ValueError(f"Chave duplicada encontrada no JSON: '{chave}'")
        resultado[chave] = valor
    return resultado


def _verificar_profundidade(obj: Any, profundidade: int = 1, limite: int = 32) -> None:
    if profundidade > limite:
        raise ValueError(f"Profundidade da estrutura JSON ({profundidade}) excede o limite máximo permitido de {limite}.")
    if isinstance(obj, dict):
        for v in obj.values():
            _verificar_profundidade(v, profundidade + 1, limite)
    elif isinstance(obj, list):
        for elem in obj:
            _verificar_profundidade(elem, profundidade + 1, limite)


def _para_fracao(val: Any) -> Fraction:
    if isinstance(val, (int, str)):
        return Fraction(val)
    if isinstance(val, Fraction):
        return val
    raise ValueError(f"Tipo inválido para conversão fracionária: {type(val).__name__} ({val})")


def carregar_projeto_json(conteudo: str) -> DadosProjeto:
    """Carrega e valida um projeto em JSON canônico sem aceitar ponto flutuante."""
    if conteudo.startswith(("\ufeff", "\xef\xbb\xbf")):
        raise ValueError("Byte Order Mark (BOM) detectado. O arquivo deve ser codificado estritamente em UTF-8 puro.")

    try:
        dados = json.loads(
            conteudo,
            object_pairs_hook=_rejeitar_chaves_duplicadas,
            parse_float=_rejeitar_float,
        )
    except json.JSONDecodeError as err:
        raise ValueError(f"Erro de decodificação JSON: {err}") from err

    _verificar_profundidade(dados)

    if not isinstance(dados, dict):
        raise ValueError("O JSON raiz deve ser um objeto dicionário.")

    nome = str(dados.get("nome_edificacao", "Edificação sem nome"))
    tipo_sis_str = str(dados.get("tipo_sistema", "bloco_autonomo")).lower()
    try:
        tipo_sistema = TipoSistemaAlimentacao(tipo_sis_str)
    except ValueError:
        tipo_sistema = TipoSistemaAlimentacao.BLOCO_AUTONOMO

    autonomia_horas = _para_fracao(dados.get("autonomia_horas", 2))

    ambientes_raw = dados.get("ambientes", [])
    if not isinstance(ambientes_raw, list):
        raise ValueError("O campo 'ambientes' deve ser uma lista.")

    ambientes_list: list[Ambiente] = []
    for item in ambientes_raw:
        if not isinstance(item, dict):
            raise ValueError("Cada ambiente deve ser um dicionário.")
        nome_amb = str(item.get("nome", "Ambiente sem nome"))
        area = _para_fracao(item.get("area_m2", 0))
        comprimento = _para_fracao(item.get("comprimento_rota_m", 0))
        pe_direito = _para_fracao(item.get("pe_direito_m", 3))
        h_montagem = _para_fracao(item.get("altura_montagem_m", pe_direito))
        tipo_amb_str = str(item.get("tipo_ambiente", "circulacao_horizontal")).lower()
        try:
            tipo_amb = TipoAmbiente(tipo_amb_str)
        except ValueError:
            tipo_amb = TipoAmbiente.CIRCULACAO_HORIZONTAL
        portas = int(item.get("portas_saida_emergencia", 1))
        mudancas = int(item.get("mudancas_direcao", 0))
        modelo_aclar = str(item.get("modelo_aclaramento", "bloco_led_250lm"))
        reflexao = bool(item.get("reflexao_clara", True))

        ambientes_list.append(
            Ambiente(
                nome=nome_amb,
                area_m2=area,
                comprimento_rota_m=comprimento,
                pe_direito_m=pe_direito,
                altura_montagem_m=h_montagem,
                tipo_ambiente=tipo_amb,
                portas_saida_emergencia=portas,
                mudancas_direcao=mudancas,
                modelo_aclaramento=modelo_aclar,
                reflexao_clara=reflexao,
            )
        )

    circuitos_raw = dados.get("circuitos", [])
    if not isinstance(circuitos_raw, list):
        raise ValueError("O campo 'circuitos' deve ser uma lista.")

    circuitos_list: list[CircuitoCentral] = []
    for item in circuitos_raw:
        if not isinstance(item, dict):
            raise ValueError("Cada circuito deve ser um dicionário.")
        nome_circ = str(item.get("nome", "Circuito 1"))
        comp_circ = _para_fracao(item.get("comprimento_total_m", 50))
        secao_circ = _para_fracao(item.get("secao_condutor_mm2", "1.5"))
        tensao_circ = _para_fracao(item.get("tensao_vcc", 24))

        circuitos_list.append(
            CircuitoCentral(
                nome=nome_circ,
                comprimento_total_m=comp_circ,
                secao_condutor_mm2=secao_circ,
                tensao_vcc=tensao_circ,
            )
        )

    return DadosProjeto(
        nome_edificacao=nome,
        tipo_sistema=tipo_sistema,
        ambientes=tuple(ambientes_list),
        circuitos=tuple(circuitos_list),
        autonomia_horas=autonomia_horas,
    )


def _serializar_valor(val: Any) -> Any:
    if isinstance(val, Fraction):
        if val.denominator == 1:
            return val.numerator
        # Representação decimal exata com precisão controlada
        num = val.numerator
        den = val.denominator
        # Se for representável com poucos decimais ou fração
        inteiro = num // den
        resto = num % den
        # Exibir como string decimal amigável
        return f"{num}/{den}"
    if isinstance(val, Enum):
        return val.value
    if isinstance(val, tuple):
        return [_serializar_valor(x) for x in val]
    if isinstance(val, dict):
        return {k: _serializar_valor(v) for k, v in val.items()}
    return val


def exportar_resultado_json(res: ResultadoDimensionamento) -> str:
    """Serializa o resultado em JSON canônico RFC 8259 determinístico."""
    dados: dict[str, Any] = {
        "norma": "ABNT NBR 10898:2013",
        "nome_edificacao": res.nome_edificacao,
        "tipo_sistema": res.tipo_sistema.value,
        "total_luminarias_aclaramento": res.total_luminarias_aclaramento,
        "total_sinalizadores_balizamento": res.total_sinalizadores_balizamento,
        "total_dispositivos": res.total_dispositivos,
        "potencia_total_instalada_w": _serializar_valor(res.potencia_total_instalada_w),
        "ambientes": [
            {
                "nome": amb.nome,
                "tipo_ambiente": amb.tipo_ambiente.value,
                "iluminancia_requerida_lux": _serializar_valor(amb.iluminancia_requerida_lux),
                "fluxo_total_requerido_lm": _serializar_valor(amb.fluxo_total_requerido_lm),
                "luminarias_aclaramento": amb.luminarias_aclaramento,
                "fluxo_unitario_lm": _serializar_valor(amb.fluxo_unitario_lm),
                "espacamento_medio_m": _serializar_valor(amb.espacamento_medio_m),
                "espacamento_maximo_permitido_m": _serializar_valor(amb.espacamento_maximo_permitido_m),
                "sinalizadores_balizamento": amb.sinalizadores_balizamento,
                "potencia_aclaramento_w": _serializar_valor(amb.potencia_aclaramento_w),
                "potencia_balizamento_w": _serializar_valor(amb.potencia_balizamento_w),
                "potencia_total_w": _serializar_valor(amb.potencia_total_w),
                "conformidade_espacamento": amb.conformidade_espacamento,
            }
            for amb in res.ambientes
        ],
        "circuitos": [
            {
                "nome": circ.nome,
                "comprimento_m": _serializar_valor(circ.comprimento_m),
                "secao_condutor_mm2": _serializar_valor(circ.secao_condutor_mm2),
                "corrente_total_a": _serializar_valor(circ.corrente_total_a),
                "resistencia_ohm": _serializar_valor(circ.resistencia_ohm),
                "queda_tensao_v": _serializar_valor(circ.queda_tensao_v),
                "queda_tensao_percentual": _serializar_valor(circ.queda_tensao_percentual),
                "limite_queda_tensao_v": _serializar_valor(circ.limite_queda_tensao_v),
                "aprovado": circ.aprovado,
            }
            for circ in res.circuitos
        ],
        "baterias": (
            {
                "tensao_banco_vcc": _serializar_valor(res.baterias.tensao_banco_vcc),
                "corrente_total_sistema_a": _serializar_valor(res.baterias.corrente_total_sistema_a),
                "autonomia_horas": _serializar_valor(res.baterias.autonomia_horas),
                "capacidade_teorica_ah": _serializar_valor(res.baterias.capacidade_teorica_ah),
                "fator_seguranca": _serializar_valor(res.baterias.fator_seguranca),
                "capacidade_minima_requerida_ah": _serializar_valor(res.baterias.capacidade_minima_requerida_ah),
                "capacidade_comercial_adotada_ah": _serializar_valor(res.baterias.capacidade_comercial_adotada_ah),
                "quantidade_baterias_12v": res.baterias.quantidade_baterias_12v,
            }
            if res.baterias is not None
            else None
        ),
        "alertas": list(res.alertas),
        "recomendacoes": list(res.recomendacoes),
    }

    return json.dumps(dados, indent=2, sort_keys=True, ensure_ascii=False)
