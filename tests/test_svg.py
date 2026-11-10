"""Testes do gerador vetorial SVG do painel de iluminação de emergência NBR 10898."""

import unittest
from fractions import Fraction

from iluminacao_nbr10898.calculator import dimensionar_sistema_iluminacao
from iluminacao_nbr10898.models import (
    Ambiente,
    CircuitoCentral,
    DadosProjeto,
    TipoAmbiente,
    TipoSistemaAlimentacao,
)
from iluminacao_nbr10898.svg_generator import gerar_painel_svg


class TestSVGGenerator(unittest.TestCase):
    """Verifica a integridade do XML/SVG 1440x900 gerado."""

    def setUp(self) -> None:
        self.amb = Ambiente(
            nome="Hall Principal",
            area_m2=Fraction(100, 1),
            comprimento_rota_m=Fraction(30, 1),
            pe_direito_m=Fraction(3, 1),
            altura_montagem_m=Fraction(3, 1),
            tipo_ambiente=TipoAmbiente.CIRCULACAO_HORIZONTAL,
            portas_saida_emergencia=2,
            mudancas_direcao=1,
            modelo_aclaramento="bloco_led_250lm",
            reflexao_clara=True,
        )
        self.circ = CircuitoCentral(
            nome="Circuito Central",
            comprimento_total_m=Fraction(50, 1),
            secao_condutor_mm2=Fraction(25, 10),
            tensao_vcc=Fraction(24, 1),
        )
        self.proj = DadosProjeto(
            nome_edificacao="Prédio SVG Teste",
            tipo_sistema=TipoSistemaAlimentacao.CENTRALIZADO_BATERIAS,
            ambientes=(self.amb,),
            circuitos=(self.circ,),
            autonomia_horas=Fraction(2, 1),
        )
        self.res = dimensionar_sistema_iluminacao(self.proj)

    def test_svg_dimensoes_e_namespaces(self) -> None:
        svg = gerar_painel_svg(self.res)
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.strip().endswith("</svg>"))
        self.assertIn('viewBox="0 0 1440 900"', svg)
        self.assertIn('xmlns="http://www.w3.org/2000/svg"', svg)

    def test_svg_elementos_obrigatorios(self) -> None:
        svg = gerar_painel_svg(self.res)
        self.assertIn("ABNT NBR 10898:2013", svg)
        self.assertIn("LOFRANO TECNOLOGIA", svg)
        self.assertIn("Prédio SVG Teste", svg)
        self.assertIn("CENTRAL 24Vcc", svg)
        self.assertIn("BANCO VRLA", svg)
        self.assertIn("Hall Principal", svg)

    def test_svg_sistema_bloco_autonomo(self) -> None:
        proj_aut = DadosProjeto(
            nome_edificacao="Autônomo",
            tipo_sistema=TipoSistemaAlimentacao.BLOCO_AUTONOMO,
            ambientes=(self.amb,),
            circuitos=(),
            autonomia_horas=Fraction(2, 1),
        )
        res_aut = dimensionar_sistema_iluminacao(proj_aut)
        svg = gerar_painel_svg(res_aut)
        self.assertIn("Autônomo", svg)
        self.assertIn("BLOCO_AUTONOMO", svg)


if __name__ == "__main__":
    unittest.main()
