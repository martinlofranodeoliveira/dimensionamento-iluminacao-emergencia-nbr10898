"""Exportadores técnicos: memorial descritivo, CSV sanitizado e ZIP determinístico."""

import csv
import io
import os
import zipfile
from fractions import Fraction
from typing import Optional

from iluminacao_nbr10898.codecs import exportar_resultado_json
from iluminacao_nbr10898.models import ResultadoDimensionamento


def _fmt(val: Fraction, casas: int = 2) -> str:
    """Formata fração para string decimal com número fixo de casas sem IEEE float."""
    num = val.numerator
    den = val.denominator
    if den == 1:
        return f"{num}.0" if casas > 0 else str(num)
    inteiro = num // den
    resto = abs(num % den)
    fator = 10**casas
    frac_parte = (resto * fator + den // 2) // den
    return f"{inteiro}.{frac_parte:0{casas}d}"


def _sanitizar_campo_csv(val: str) -> str:
    """Sanitiza strings contra injeção de fórmulas de planilhas."""
    if val and val[0] in ("=", "+", "-", "@", "\t", "\r"):
        return f"'{val}"
    return val


def gerar_relatorio_texto(res: ResultadoDimensionamento) -> str:
    """Gera memorial descritivo e relatório técnico de engenharia detalhado."""
    linhas: list[str] = []
    w = 80
    linhas.append("=" * w)
    linhas.append("    LOFRANO TECNOLOGIA - ENGENHARIA DE SEGURANÇA CONTRA INCÊNDIO")
    linhas.append("    ILUMINAÇÃO DE EMERGÊNCIA E BALIZAMENTO - ABNT NBR 10898:2013")
    linhas.append("=" * w)
    linhas.append(f"Projeto: {res.nome_edificacao}")
    linhas.append(f"Sistema: {res.tipo_sistema.value.upper()}")
    linhas.append("-" * w)

    linhas.append("1. QUADRO GERAL DE DISPOSITIVOS E POTÊNCIA")
    linhas.append(f"  - Luminárias de Aclaramento:             {res.total_luminarias_aclaramento} unidades")
    linhas.append(f"  - Sinalizadores de Balizamento (Rotas):   {res.total_sinalizadores_balizamento} unidades")
    linhas.append(f"  - Total de Componentes Instalados:       {res.total_dispositivos} dispositivos")
    linhas.append(f"  - Potência Total em Emergência:          {_fmt(res.potencia_total_instalada_w)} W")
    linhas.append("-" * w)

    linhas.append("2. DETALHAMENTO TÉCNICO POR AMBIENTE")
    for amb in res.ambientes:
        status = "CONFORME" if amb.conformidade_espacamento else "REQUER ATENÇÃO"
        linhas.append(f"  • [{amb.nome}] Tipologia: {amb.tipo_ambiente.value} ({status})")
        linhas.append(f"      - Iluminância Requerida:     {_fmt(amb.iluminancia_requerida_lux)} lux")
        linhas.append(f"      - Fluxo Total Requerido:     {_fmt(amb.fluxo_total_requerido_lm)} lm")
        linhas.append(f"      - Luminárias de Aclaramento: {amb.luminarias_aclaramento} un ({_fmt(amb.fluxo_unitario_lm)} lm/un)")
        linhas.append(f"      - Espaçamento Médio:         {_fmt(amb.espacamento_medio_m)} m (Máx: {_fmt(amb.espacamento_maximo_permitido_m)} m)")
        linhas.append(f"      - Balizamento de Saída:      {amb.sinalizadores_balizamento} un")
        linhas.append(f"      - Potência Total Ambiente:   {_fmt(amb.potencia_total_w)} W")

    linhas.append("-" * w)
    if res.circuitos:
        linhas.append("3. CIRCUITOS DE CAMPO E QUEDA DE TENSÃO (NBR 10898, LIMITE <= 10%)")
        for circ in res.circuitos:
            st = "APROVADO" if circ.aprovado else "REPROVADO"
            linhas.append(f"  • Circuito: {circ.nome} [{st}]")
            linhas.append(f"      - Extensão:               {_fmt(circ.comprimento_m)} m")
            linhas.append(f"      - Condutor Adotado:       {_fmt(circ.secao_condutor_mm2)} mm² (Cobre flexível)")
            linhas.append(f"      - Corrente em Emergência: {_fmt(circ.corrente_total_a)} A")
            linhas.append(f"      - Queda de Tensão:        {_fmt(circ.queda_tensao_v)} V ({_fmt(circ.queda_tensao_percentual)}%)")
            linhas.append(f"      - Limite Regulamentar:    {_fmt(circ.limite_queda_tensao_v)} V (10,0%)")
        linhas.append("-" * w)

    if res.baterias is not None:
        bat = res.baterias
        linhas.append("4. BANCO CENTRAL DE BATERIAS SELADAS VRLA (AUTONOMIA 2 HORAS)")
        linhas.append(f"  - Tensão Nominal do Banco:      {_fmt(bat.tensao_banco_vcc)} Vcc")
        linhas.append(f"  - Corrente Total em Descarga:   {_fmt(bat.corrente_total_sistema_a)} A")
        linhas.append(f"  - Autonomia Contínua Exigida:   {_fmt(bat.autonomia_horas)} horas (120 minutos)")
        linhas.append(f"  - Capacidade Teórica Calculada: {_fmt(bat.capacidade_teorica_ah)} Ah")
        linhas.append(f"  - Fator de Segurança:           1,25 (Margem regulamentar de 25%)")
        linhas.append(f"  - Capacidade Mínima Requerida:  {_fmt(bat.capacidade_minima_requerida_ah)} Ah")
        linhas.append(f"  - BANCO VRLA COMERCIAL ADOTADO: {_fmt(bat.capacidade_comercial_adotada_ah)} Ah ({bat.quantidade_baterias_12v}x 12V em série)")
        linhas.append("-" * w)

    linhas.append("5. RECOMENDAÇÕES E DIRETRIZES TÉCNICAS")
    for rec in res.recomendacoes:
        linhas.append(f"  * {rec}")
    if res.alertas:
        linhas.append("-" * w)
        linhas.append("6. ALERTAS E CONDICIONANTES NORMATIVAS")
        for alt in res.alertas:
            linhas.append(f"  ! {alt}")

    linhas.append("=" * w)
    linhas.append("Emitido via Lofrano Tecnologia - Conforme ABNT NBR 10898:2013")
    linhas.append("=" * w)
    return "\n".join(linhas) + "\n"


def gerar_csv_sanitizado(res: ResultadoDimensionamento) -> str:
    """Gera planilha CSV com proteção contra injeção de fórmulas."""
    saida = io.StringIO()
    writer = csv.writer(saida, delimiter=";", lineterminator="\n")

    writer.writerow([
        _sanitizar_campo_csv("ambiente"),
        _sanitizar_campo_csv("tipo_ambiente"),
        _sanitizar_campo_csv("iluminancia_min_lux"),
        _sanitizar_campo_csv("fluxo_req_lm"),
        _sanitizar_campo_csv("luminarias_aclaramento"),
        _sanitizar_campo_csv("espacamento_medio_m"),
        _sanitizar_campo_csv("espacamento_max_m"),
        _sanitizar_campo_csv("balizamento_saida"),
        _sanitizar_campo_csv("potencia_total_w"),
        _sanitizar_campo_csv("conformidade"),
    ])

    for amb in res.ambientes:
        writer.writerow([
            _sanitizar_campo_csv(amb.nome),
            _sanitizar_campo_csv(amb.tipo_ambiente.value),
            _fmt(amb.iluminancia_requerida_lux),
            _fmt(amb.fluxo_total_requerido_lm),
            amb.luminarias_aclaramento,
            _fmt(amb.espacamento_medio_m),
            _fmt(amb.espacamento_maximo_permitido_m),
            amb.sinalizadores_balizamento,
            _fmt(amb.potencia_total_w),
            "CONFORME" if amb.conformidade_espacamento else "REPROVADO",
        ])

    return saida.getvalue()


def gerar_pacote_zip(res: ResultadoDimensionamento, caminho_zip: str, svg_conteudo: Optional[str] = None) -> None:
    """Gera pacote determinístico ZIP com O_EXCL, evitando sobrescrita acidental."""
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_BINARY", 0)
    fd = os.open(caminho_zip, flags, 0o644)
    fixed_time = (2026, 1, 1, 0, 0, 0)

    try:
        with open(fd, "wb", closefd=True) as f_out:
            with zipfile.ZipFile(f_out, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
                # 1. Memorial descritivo em texto
                txt = gerar_relatorio_texto(res).encode("utf-8")
                zi_txt = zipfile.ZipInfo(filename="memorial_descritivo.txt", date_time=fixed_time)
                zf.writestr(zi_txt, txt)

                # 2. Dados em JSON canônico
                js = exportar_resultado_json(res).encode("utf-8")
                zi_js = zipfile.ZipInfo(filename="dados_dimensionamento.json", date_time=fixed_time)
                zf.writestr(zi_js, js)

                # 3. Planilha CSV sanitizada
                csv_data = gerar_csv_sanitizado(res).encode("utf-8")
                zi_csv = zipfile.ZipInfo(filename="quadro_ambientes.csv", date_time=fixed_time)
                zf.writestr(zi_csv, csv_data)

                # 4. Painel vetorial SVG se disponível
                if svg_conteudo:
                    svg_bytes = svg_conteudo.encode("utf-8")
                    zi_svg = zipfile.ZipInfo(filename="painel_esquematico.svg", date_time=fixed_time)
                    zf.writestr(zi_svg, svg_bytes)
    except Exception:
        if os.path.exists(caminho_zip):
            try:
                os.remove(caminho_zip)
            except OSError:
                pass
        raise
