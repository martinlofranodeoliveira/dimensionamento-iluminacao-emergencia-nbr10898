"""Testes dos modelos de dados imutáveis da NBR 10898."""

import unittest
from fractions import Fraction

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


class TestModels(unittest.TestCase):
    """Testa a integridade, dataclasses e imutabilidade dos modelos."""

    def test_enums(self) -> None:
        self.assertEqual(TipoAmbiente.CIRCULACAO_HORIZONTAL.value, "circulacao_horizontal")
        self.assertEqual(TipoAmbiente.ESCADA_OU_DESNIVEL.value, "escada_ou_desnivel")
        self.assertEqual(TipoSistemaAlimentacao.CENTRALIZADO_BATERIAS.value, "centralizado_baterias")
        self.assertEqual(TipoBalizamento.FACE_SIMPLES.value, "face_simples")

    def test_ambiente_imutabilidade(self) -> None:
        amb = Ambiente(
            nome="Corredor",
            area_m2=Fraction(100, 1),
            comprimento_rota_m=Fraction(25, 1),
            pe_direito_m=Fraction(3, 1),
            altura_montagem_m=Fraction(3, 1),
            tipo_ambiente=TipoAmbiente.CIRCULACAO_HORIZONTAL,
            portas_saida_emergencia=2,
            mudancas_direcao=1,
            modelo_aclaramento="bloco_led_250lm",
            reflexao_clara=True,
        )
        self.assertEqual(amb.nome, "Corredor")
        with self.assertRaises(Exception):
            amb.area_m2 = Fraction(150, 1)  # type: ignore

    def test_circuito_central_imutabilidade(self) -> None:
        c = CircuitoCentral(
            nome="Circuito 1",
            comprimento_total_m=Fraction(50, 1),
            secao_condutor_mm2=Fraction(25, 10),
            tensao_vcc=Fraction(24, 1),
        )
        self.assertEqual(c.tensao_vcc, Fraction(24, 1))
        with self.assertRaises(Exception):
            c.comprimento_total_m = Fraction(60, 1)  # type: ignore

    def test_dados_projeto_instanciacao(self) -> None:
        proj = DadosProjeto(
            nome_edificacao="Edifício Alfa",
            tipo_sistema=TipoSistemaAlimentacao.BLOCO_AUTONOMO,
            ambientes=(),
            circuitos=(),
            autonomia_horas=Fraction(2, 1),
        )
        self.assertEqual(proj.nome_edificacao, "Edifício Alfa")
        self.assertEqual(proj.autonomia_horas, Fraction(2, 1))


if __name__ == "__main__":
    unittest.main()
