"""Testes unitários das constantes normativas da ABNT NBR 10898:2013."""

import unittest
from fractions import Fraction

from iluminacao_nbr10898.constants import (
    ALTURA_MAX_PORTA_SAIDA_M,
    ALTURA_MIN_PORTA_SAIDA_M,
    AUTONOMIA_MINIMA_HORAS,
    CAPACIDADES_BATERIAS_VRLA_AH,
    CATALOGO_BALIZAMENTO_SAIDA,
    CATALOGO_LUMINARIAS_ACLARAMENTO,
    DISTANCIA_MAX_BALIZAMENTO_FACE_DUPLA_M,
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
    RELACAO_UNIFORMIDADE_MAXIMA,
    RESISTIVIDADE_COBRE_OHM_MM2_M,
    SECAO_MINIMA_CONDUTOR_MM2,
    TEMPO_MAXIMO_PARTIDA_GERADOR_SEG,
    TENSAO_NOMINAL_PADRAO_VCC,
)


class TestConstants(unittest.TestCase):
    """Verifica conformidade estrita das constantes com a NBR 10898:2013."""

    def test_iluminancias_minimas(self) -> None:
        self.assertEqual(ILUMINANCIA_MIN_HORIZONTAL_LUX, Fraction(3, 1))
        self.assertEqual(ILUMINANCIA_MIN_DESNIVEL_ESCADA_LUX, Fraction(5, 1))
        self.assertEqual(ILUMINANCIA_MIN_RISCO_ELEVADO_LUX, Fraction(5, 1))

    def test_autonomia_e_gmg(self) -> None:
        self.assertEqual(AUTONOMIA_MINIMA_HORAS, Fraction(2, 1))
        self.assertEqual(TEMPO_MAXIMO_PARTIDA_GERADOR_SEG, Fraction(12, 1))

    def test_fatores_luminotecnicos(self) -> None:
        self.assertEqual(FATOR_MANUTENCAO_PADRAO, Fraction(4, 5))
        self.assertEqual(FATOR_UTILIZACAO_CLARO, Fraction(6, 10))
        self.assertEqual(FATOR_UTILIZACAO_ESCURO, Fraction(5, 10))
        self.assertEqual(FATOR_ESPACAMENTO_MAX_ALTURA, Fraction(4, 1))
        self.assertEqual(RELACAO_UNIFORMIDADE_MAXIMA, Fraction(40, 1))

    def test_balizamento_distancias_e_alturas(self) -> None:
        self.assertEqual(DISTANCIA_MAX_BALIZAMENTO_FACE_SIMPLES_M, Fraction(15, 1))
        self.assertEqual(DISTANCIA_MAX_BALIZAMENTO_FACE_DUPLA_M, Fraction(30, 1))
        self.assertEqual(ALTURA_MIN_PORTA_SAIDA_M, Fraction(2, 1))
        self.assertEqual(ALTURA_MAX_PORTA_SAIDA_M, Fraction(25, 10))

    def test_parametros_eletricos_e_queda_tensao(self) -> None:
        self.assertEqual(TENSAO_NOMINAL_PADRAO_VCC, Fraction(24, 1))
        self.assertEqual(QUEDA_TENSAO_MAXIMA_PERCENTUAL, Fraction(10, 100))
        self.assertEqual(RESISTIVIDADE_COBRE_OHM_MM2_M, Fraction(1, 58))
        self.assertEqual(SECAO_MINIMA_CONDUTOR_MM2, Fraction(15, 10))

    def test_baterias_e_seguranca(self) -> None:
        self.assertEqual(FATOR_SEGURANCA_BATERIA, Fraction(5, 4))
        self.assertTrue(len(CAPACIDADES_BATERIAS_VRLA_AH) >= 8)
        self.assertEqual(CAPACIDADES_BATERIAS_VRLA_AH[0], Fraction(45, 10))

    def test_catalogos_dispositivos(self) -> None:
        self.assertIn("bloco_led_250lm", CATALOGO_LUMINARIAS_ACLARAMENTO)
        self.assertIn("luminaria_led_600lm", CATALOGO_LUMINARIAS_ACLARAMENTO)
        self.assertIn("baliza_face_simples_30lm", CATALOGO_BALIZAMENTO_SAIDA)


if __name__ == "__main__":
    unittest.main()
