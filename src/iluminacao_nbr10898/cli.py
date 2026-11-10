"""Interface de linha de comando (CLI) para iluminação de emergência NBR 10898."""

import argparse
import sys
from fractions import Fraction
from typing import Optional

from iluminacao_nbr10898.calculator import dimensionar_sistema_iluminacao
from iluminacao_nbr10898.codecs import carregar_projeto_json, exportar_resultado_json
from iluminacao_nbr10898.constants import (
    AUTONOMIA_MINIMA_HORAS,
    CAPACIDADES_BATERIAS_VRLA_AH,
    CATALOGO_BALIZAMENTO_SAIDA,
    CATALOGO_LUMINARIAS_ACLARAMENTO,
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
from iluminacao_nbr10898.svg_generator import gerar_painel_svg

VERSAO = "1.0.0"


def cmd_calcular(args: argparse.Namespace) -> int:
    """Executa o cálculo de dimensionamento luminotécnico e elétrico."""
    try:
        with open(args.arquivo, "r", encoding="utf-8") as f:
            conteudo = f.read()
    except OSError as err:
        print(f"Erro ao abrir arquivo de projeto '{args.arquivo}': {err}", file=sys.stderr)
        return 1

    try:
        projeto = carregar_projeto_json(conteudo)
    except ValueError as err:
        print(f"Erro de validação do arquivo JSON: {err}", file=sys.stderr)
        return 1

    resultado = dimensionar_sistema_iluminacao(projeto)
    svg_conteudo = gerar_painel_svg(resultado)

    # Pacote determinístico ZIP
    if args.pacote_zip:
        try:
            gerar_pacote_zip(resultado, args.pacote_zip, svg_conteudo=svg_conteudo)
            print(f"[ZIP] Pacote determinístico gerado com sucesso em '{args.pacote_zip}'")
        except OSError as err:
            print(f"Erro ao gerar pacote ZIP '{args.pacote_zip}': {err}", file=sys.stderr)
            return 1

    # Formatação da saída
    formato = args.formato.lower()
    if formato == "json":
        saida_str = exportar_resultado_json(resultado)
    elif formato == "csv":
        saida_str = gerar_csv_sanitizado(resultado)
    elif formato == "svg":
        saida_str = svg_conteudo
    else:
        saida_str = gerar_relatorio_texto(resultado)

    if args.saida:
        try:
            with open(args.saida, "w", encoding="utf-8") as f_out:
                f_out.write(saida_str)
            print(f"[OK] Saída ({formato}) salva com sucesso em '{args.saida}'")
        except OSError as err:
            print(f"Erro ao gravar arquivo de saída '{args.saida}': {err}", file=sys.stderr)
            return 1
    else:
        print(saida_str)

    return 0


def cmd_catalogo(_args: argparse.Namespace) -> int:
    """Exibe o catálogo normativo de luminárias, balizas e baterias VRLA."""
    print("=" * 80)
    print("    CATÁLOGO NORMATIVO - ABNT NBR 10898:2013")
    print("=" * 80)
    print("1. LUMINÁRIAS DE ACLARAMENTO COMERCIAIS:")
    for chave, dados in CATALOGO_LUMINARIAS_ACLARAMENTO.items():
        fluxo = dados["fluxo_luminoso_lm"]
        pot = dados["potencia_eletrica_w"]
        print(f"  • {chave:24s} -> Fluxo: {fluxo} lm | Potência: {pot} W | Abertura: 120°")

    print("\n2. SINALIZADORES DE BALIZAMENTO (ROTAS DE FUGA):")
    for chave, dados in CATALOGO_BALIZAMENTO_SAIDA.items():
        fluxo = dados["fluxo_luminoso_lm"]
        pot = dados["potencia_eletrica_w"]
        vis = dados["distancia_visibilidade_m"]
        print(f"  • {chave:26s} -> Fluxo: {fluxo} lm | Potência: {pot} W | Visibilidade máx: {vis} m")

    print("\n3. BANCO DE BATERIAS SELADAS VRLA (24 Vcc):")
    cap_str = ", ".join(f"{float(c):.1f} Ah" for c in CAPACIDADES_BATERIAS_VRLA_AH)
    print(f"  • Capacidades padronizadas: {cap_str}")

    print("\n4. PARÂMETROS NORMATIVOS MÍNIMOS:")
    print(f"  • Iluminância Mínima Horizontal:      {ILUMINANCIA_MIN_HORIZONTAL_LUX} lux")
    print(f"  • Iluminância Mínima Escadas/Risco:   {ILUMINANCIA_MIN_DESNIVEL_ESCADA_LUX} lux")
    print(f"  • Autonomia Mínima Regulamentar:      {AUTONOMIA_MINIMA_HORAS} horas (120 min)")
    print(f"  • Limite Máximo de Queda de Tensão:   {float(QUEDA_TENSAO_MAXIMA_PERCENTUAL)*100:.1f}%")
    print("=" * 80)
    return 0


def cmd_gerar_exemplo(args: argparse.Namespace) -> int:
    """Gera um arquivo JSON de exemplo pronto para preenchimento."""
    exemplo_json = """{
  "nome_edificacao": "Edifício Corporativo Paulista Tower",
  "tipo_sistema": "centralizado_baterias",
  "autonomia_horas": 2,
  "circuitos": [
    {
      "nome": "Circuito 1 - Pavimentos Tipo",
      "comprimento_total_m": 80,
      "secao_condutor_mm2": "2.5",
      "tensao_vcc": 24
    }
  ],
  "ambientes": [
    {
      "nome": "Corredor Central e Hall de Elevadores",
      "tipo_ambiente": "circulacao_horizontal",
      "area_m2": 120,
      "comprimento_rota_m": 40,
      "pe_direito_m": "2.8",
      "altura_montagem_m": "2.8",
      "portas_saida_emergencia": 2,
      "mudancas_direcao": 1,
      "modelo_aclaramento": "bloco_led_250lm",
      "reflexao_clara": true
    },
    {
      "nome": "Escada Pressurizada de Emergência",
      "tipo_ambiente": "escada_ou_desnivel",
      "area_m2": 45,
      "comprimento_rota_m": 20,
      "pe_direito_m": "2.8",
      "altura_montagem_m": "2.5",
      "portas_saida_emergencia": 1,
      "mudancas_direcao": 2,
      "modelo_aclaramento": "bloco_led_250lm",
      "reflexao_clara": true
    }
  ]
}
"""
    if args.saida:
        try:
            with open(args.saida, "w", encoding="utf-8") as f:
                f.write(exemplo_json)
            print(f"[OK] Modelo de exemplo gravado em '{args.saida}'")
        except OSError as err:
            print(f"Erro ao salvar arquivo de exemplo '{args.saida}': {err}", file=sys.stderr)
            return 1
    else:
        print(exemplo_json)
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    """Ponto de entrada principal da CLI."""
    parser = argparse.ArgumentParser(
        prog="iluminacao-nbr10898",
        description="Dimensionamento de iluminação de emergência e balizamento conforme ABNT NBR 10898:2013.",
    )
    parser.add_argument("--versao", action="version", version=f"%(prog)s {VERSAO}")

    subparsers = parser.add_subparsers(dest="comando", help="Comandos disponíveis")

    # Comando: calcular
    p_calc = subparsers.add_parser("calcular", help="Dimensionar projeto a partir de JSON")
    p_calc.add_argument("arquivo", help="Caminho do arquivo JSON com dados do projeto")
    p_calc.add_argument(
        "--formato",
        choices=["texto", "json", "csv", "svg"],
        default="texto",
        help="Formato de saída do memorial (padrão: texto)",
    )
    p_calc.add_argument("--saida", help="Caminho do arquivo para salvar o resultado")
    p_calc.add_argument("--pacote-zip", help="Gera pacote ZIP com memorial, JSON, CSV e SVG")

    # Comando: catalogo
    subparsers.add_parser("catalogo", help="Consultar catálogo normativo de luminárias e baterias")

    # Comando: gerar-exemplo
    p_ex = subparsers.add_parser("gerar-exemplo", help="Gerar arquivo JSON de exemplo")
    p_ex.add_argument("--saida", help="Arquivo onde gravar o exemplo JSON")

    args = parser.parse_args(argv)

    if not args.comando:
        parser.print_help()
        return 0

    if args.comando == "calcular":
        return cmd_calcular(args)
    if args.comando == "catalogo":
        return cmd_catalogo(args)
    if args.comando == "gerar-exemplo":
        return cmd_gerar_exemplo(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
