"""Motor de cálculo luminotécnico e elétrico da ABNT NBR 10898:2013."""

from fractions import Fraction
from typing import Optional

from iluminacao_nbr10898.constants import (
    ALTURA_MAX_PORTA_SAIDA_M,
    ALTURA_MIN_PORTA_SAIDA_M,
    AUTONOMIA_MINIMA_HORAS,
    CAPACIDADES_BATERIAS_VRLA_AH,
    CATALOGO_BALIZAMENTO_SAIDA,
    CATALOGO_LUMINARIAS_ACLARAMENTO,
    DISTANCIA_MAX_BALIZAMENTO_FACE_SIMPLES_M,
    FATOR_ESPACAMENTO_MAX_ALTURA,
    FATOR_MANUTENCAO_PADRAO,
    FATOR_SEGURANCA_BATERIA,
    FATOR_UTILIZACAO_CLARO,
    FATOR_UTILIZACAO_ESCURO,
    ILUMINANCIA_MIN_DESNIVEL_ESCADA_LUX,
    ILUMINANCIA_MIN_HORIZONTAL_LUX,
    ILUMINANCIA_MIN_RISCO_ELEVADO_LUX,
    QUEDA_TENSAO_MAXIMA_PERCENTUAL,
    RESISTIVIDADE_COBRE_OHM_MM2_M,
    TENSAO_NOMINAL_PADRAO_VCC,
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
    TipoSistemaAlimentacao,
)


def _teto_fracao(frac: Fraction) -> int:
    """Calcula o teto inteiro exato de uma fração sem utilizar float."""
    if frac.denominator == 1:
        return frac.numerator
    if frac.numerator > 0:
        return (frac.numerator // frac.denominator) + 1
    return frac.numerator // frac.denominator


def dimensionar_sistema_iluminacao(projeto: DadosProjeto) -> ResultadoDimensionamento:
    """Executa o dimensionamento luminotécnico, elétrico e energético de emergência."""
    alertas: list[str] = []
    recomendacoes: list[str] = []

    # 1. Validação de autonomia de projeto
    autonomia = projeto.autonomia_horas
    if autonomia < AUTONOMIA_MINIMA_HORAS:
        alertas.append(
            f"Autonomia de {autonomia}h é inferior ao mínimo regulamentar de {AUTONOMIA_MINIMA_HORAS}h exigido pela NBR 10898."
        )
        autonomia = AUTONOMIA_MINIMA_HORAS

    # 2. Dimensionamento por ambiente
    res_ambientes: list[ResultadoAmbiente] = []
    total_luminarias = 0
    total_balizas = 0
    potencia_total_instalada = Fraction(0, 1)

    for amb in projeto.ambientes:
        # Iluminância mínima segundo o tipo de ambiente
        if amb.tipo_ambiente in (TipoAmbiente.ESCADA_OU_DESNIVEL, TipoAmbiente.AREA_RISCO_ELEVADO):
            e_min = ILUMINANCIA_MIN_DESNIVEL_ESCADA_LUX
        else:
            e_min = ILUMINANCIA_MIN_HORIZONTAL_LUX

        # Fatores fotométricos
        f_util = FATOR_UTILIZACAO_CLARO if amb.reflexao_clara else FATOR_UTILIZACAO_ESCURO
        f_manut = FATOR_MANUTENCAO_PADRAO

        # Fluxo total requerido: Phi = (Emin * A) / (eta * fm)
        fluxo_req = (e_min * amb.area_m2) / (f_util * f_manut)

        # Seleção de luminária no catálogo
        dados_lum = CATALOGO_LUMINARIAS_ACLARAMENTO.get(
            amb.modelo_aclaramento,
            CATALOGO_LUMINARIAS_ACLARAMENTO["bloco_led_250lm"],
        )
        fluxo_un = dados_lum["fluxo_luminoso_lm"]
        pot_un = dados_lum["potencia_eletrica_w"]

        # Quantidade de luminárias de aclaramento
        frac_lum = fluxo_req / fluxo_un
        n_lum = max(1, _teto_fracao(frac_lum))

        # Espaçamento máximo regulamentar d_max = 4 * h
        h_montagem = amb.altura_montagem_m if amb.altura_montagem_m > 0 else amb.pe_direito_m
        if amb.pe_direito_m > Fraction(5, 1):
            alertas.append(
                f"Ambiente '{amb.nome}': pé-direito de {amb.pe_direito_m}m exige faróis direcionais de alto fluxo ou fixação intermediária."
            )

        espacamento_max_permitido = FATOR_ESPACAMENTO_MAX_ALTURA * h_montagem

        # Espaçamento médio estimado
        if amb.comprimento_rota_m > 0:
            espacamento_medio = amb.comprimento_rota_m / Fraction(n_lum, 1)
        else:
            # Em salas sem rota unidirecional, aproximação pela raiz aproximada ou dimensão média
            espacamento_medio = amb.area_m2 / (Fraction(n_lum, 1) * h_montagem)

        conforme_espacamento = espacamento_medio <= espacamento_max_permitido
        if not conforme_espacamento:
            alertas.append(
                f"Ambiente '{amb.nome}': espaçamento médio ({espacamento_medio}m) excede o limite máximo ({espacamento_max_permitido}m). Risco de zonas escuras."
            )

        # Sinalização de balizamento (saídas e rotas de fuga)
        balizas_saidas = amb.portas_saida_emergencia
        balizas_direcao = amb.mudancas_direcao
        balizas_rota = 0
        if amb.comprimento_rota_m > DISTANCIA_MAX_BALIZAMENTO_FACE_SIMPLES_M:
            balizas_rota = max(0, _teto_fracao(amb.comprimento_rota_m / DISTANCIA_MAX_BALIZAMENTO_FACE_SIMPLES_M) - 1)

        n_balizas = max(1, balizas_saidas + balizas_direcao + balizas_rota)

        # Potência elétrica
        dados_baliza = CATALOGO_BALIZAMENTO_SAIDA["baliza_face_simples_30lm"]
        pot_aclar = Fraction(n_lum, 1) * pot_un
        pot_baliz = Fraction(n_balizas, 1) * dados_baliza["potencia_eletrica_w"]
        pot_amb = pot_aclar + pot_baliz

        total_luminarias += n_lum
        total_balizas += n_balizas
        potencia_total_instalada += pot_amb

        res_ambientes.append(
            ResultadoAmbiente(
                nome=amb.nome,
                tipo_ambiente=amb.tipo_ambiente,
                iluminancia_requerida_lux=e_min,
                fluxo_total_requerido_lm=fluxo_req,
                luminarias_aclaramento=n_lum,
                fluxo_unitario_lm=fluxo_un,
                espacamento_medio_m=espacamento_medio,
                espacamento_maximo_permitido_m=espacamento_max_permitido,
                sinalizadores_balizamento=n_balizas,
                potencia_aclaramento_w=pot_aclar,
                potencia_balizamento_w=pot_baliz,
                potencia_total_w=pot_amb,
                conformidade_espacamento=conforme_espacamento,
            )
        )

    # 3. Dimensionamento de Circuitos Elétricos (Sistema Centralizado)
    res_circuitos: list[ResultadoCircuito] = []
    baterias_resultado: Optional[ResultadoBaterias] = None

    if projeto.tipo_sistema == TipoSistemaAlimentacao.CENTRALIZADO_BATERIAS:
        qtd_circuitos = max(1, len(projeto.circuitos))
        potencia_por_circuito = potencia_total_instalada / Fraction(qtd_circuitos, 1)

        for circ in projeto.circuitos:
            tensao = circ.tensao_vcc if circ.tensao_vcc > 0 else TENSAO_NOMINAL_PADRAO_VCC
            corrente_circ = potencia_por_circuito / tensao

            # Resistência equivalente com carga distribuída: R = (rho * L) / S
            r_linha = (RESISTIVIDADE_COBRE_OHM_MM2_M * circ.comprimento_total_m) / circ.secao_condutor_mm2
            queda_tensao_v = corrente_circ * r_linha
            queda_tensao_perc = (queda_tensao_v / tensao) * Fraction(100, 1)
            limite_queda_v = tensao * QUEDA_TENSAO_MAXIMA_PERCENTUAL
            aprovado = queda_tensao_v <= limite_queda_v

            if not aprovado:
                alertas.append(
                    f"Circuito '{circ.nome}': queda de tensão de {queda_tensao_v}V ({queda_tensao_perc}%) excede o limite normativo de 10% ({limite_queda_v}V). Aumente a bitola do condutor."
                )

            res_circuitos.append(
                ResultadoCircuito(
                    nome=circ.nome,
                    comprimento_m=circ.comprimento_total_m,
                    secao_condutor_mm2=circ.secao_condutor_mm2,
                    corrente_total_a=corrente_circ,
                    resistencia_ohm=r_linha,
                    queda_tensao_v=queda_tensao_v,
                    queda_tensao_percentual=queda_tensao_perc,
                    limite_queda_tensao_v=limite_queda_v,
                    aprovado=aprovado,
                )
            )

        # Dimensionamento do Banco de Baterias VRLA
        tensao_central = projeto.circuitos[0].tensao_vcc if projeto.circuitos else TENSAO_NOMINAL_PADRAO_VCC
        corrente_total_central = potencia_total_instalada / tensao_central
        cap_teorica = corrente_total_central * autonomia
        cap_minima = cap_teorica * FATOR_SEGURANCA_BATERIA

        # Selecionar capacidade comercial
        cap_comercial = CAPACIDADES_BATERIAS_VRLA_AH[-1]
        for cap in CAPACIDADES_BATERIAS_VRLA_AH:
            if cap >= cap_minima:
                cap_comercial = cap
                break

        qtd_baterias_12v = 2 if tensao_central >= Fraction(24, 1) else 1

        baterias_resultado = ResultadoBaterias(
            tensao_banco_vcc=tensao_central,
            corrente_total_sistema_a=corrente_total_central,
            autonomia_horas=autonomia,
            capacidade_teorica_ah=cap_teorica,
            fator_seguranca=FATOR_SEGURANCA_BATERIA,
            capacidade_minima_requerida_ah=cap_minima,
            capacidade_comercial_adotada_ah=cap_comercial,
            quantidade_baterias_12v=qtd_baterias_12v,
        )

    # 4. Recomendações normativas
    recomendacoes.append(
        f"Sistema dimensionado sob tipologia '{projeto.tipo_sistema.value}' conforme ABNT NBR 10898:2013."
    )
    recomendacoes.append(
        f"Garantida iluminância mínima de 3 lux em áreas de circulação horizontal e 5 lux em escadas e áreas de desnível."
    )
    recomendacoes.append(
        f"Sinalizadores de balizamento devem ser instalados entre {ALTURA_MIN_PORTA_SAIDA_M}m e {ALTURA_MAX_PORTA_SAIDA_M}m do piso acabado sobre vergas de portas de saída de emergência."
    )
    if projeto.tipo_sistema == TipoSistemaAlimentacao.CENTRALIZADO_BATERIAS:
        recomendacoes.append(
            f"Banco de acumuladores VRLA dimensionado para {autonomia}h ininterruptas com margem de segurança de 25%."
        )
        recomendacoes.append(
            "Condutores de alimentação dos circuitos de emergência devem ser antichama (resistência a chama de 750°C por 2 horas)."
        )
    elif projeto.tipo_sistema == TipoSistemaAlimentacao.BLOCO_AUTONOMO:
        recomendacoes.append(
            "Blocos autônomos devem possuir circuito eletrônico de supervisão de carga e teste manual periódico."
        )
    elif projeto.tipo_sistema == TipoSistemaAlimentacao.MOTO_GERADOR:
        recomendacoes.append(
            "Grupo moto-gerador (GMG) com transferência automática deve assumir a carga total em no máximo 12 segundos."
        )

    return ResultadoDimensionamento(
        nome_edificacao=projeto.nome_edificacao,
        tipo_sistema=projeto.tipo_sistema,
        total_luminarias_aclaramento=total_luminarias,
        total_sinalizadores_balizamento=total_balizas,
        total_dispositivos=total_luminarias + total_balizas,
        potencia_total_instalada_w=potencia_total_instalada,
        ambientes=tuple(res_ambientes),
        circuitos=tuple(res_circuitos),
        baterias=baterias_resultado,
        alertas=tuple(alertas),
        recomendacoes=tuple(recomendacoes),
    )
