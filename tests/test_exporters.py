"""Testes unitários dos exportadores técnicos da NBR 10898."""

import os
import tempfile
import unittest
import zipfile
from fractions import Fraction

from iluminacao_nbr10898.calculator import dimensionar_sistema_iluminacao
from iluminacao_nbr10898.exporters import (
    _fmt,
    _sanitizar_campo_csv,
    gerar_csv_sanitizado,
    gerar_pacote_zip,
    gerar_relatorio_texto,
)
from iluminacao_nbr10898.models import (
    Ambiente,
    CircuitoCentral,
    DadosProjeto,
    TipoAmbiente,
    TipoSistemaAlimentacao,
)


class TestExporters(unittest.TestCase):
    """Testa memorial de texto, sanitização CSV e ZIP determinístico."""

    def setUp(self) -> None:
        self.amb = Ambiente(
            nome="=PerigoFormula",
            area_m2=Fraction(120, 1),
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
            nome="Circuito 1",
            comprimento_total_m=Fraction(40, 1),
            secao_condutor_mm2=Fraction(25, 10),
            tensao_vcc=Fraction(24, 1),
        )
        self.proj = DadosProjeto(
            nome_edificacao="Empacotamento Teste",
            tipo_sistema=TipoSistemaAlimentacao.CENTRALIZADO_BATERIAS,
            ambientes=(self.amb,),
            circuitos=(self.circ,),
            autonomia_horas=Fraction(2, 1),
        )
        self.res = dimensionar_sistema_iluminacao(self.proj)

    def test_fmt_sem_float(self) -> None:
        self.assertEqual(_fmt(Fraction(10, 1), 2), "10.0")
        self.assertEqual(_fmt(Fraction(10, 4), 2), "2.50")
        self.assertEqual(_fmt(Fraction(1, 3), 3), "0.333")

    def test_sanitizar_campo_csv(self) -> None:
        self.assertEqual(_sanitizar_campo_csv("=1+1"), "'=1+1")
        self.assertEqual(_sanitizar_campo_csv("+cmd"), "'+cmd")
        self.assertEqual(_sanitizar_campo_csv("-123"), "'-123")
        self.assertEqual(_sanitizar_campo_csv("@calc"), "'@calc")
        self.assertEqual(_sanitizar_campo_csv("\ttab"), "'\ttab")
        self.assertEqual(_sanitizar_campo_csv("normal"), "normal")

    def test_gerar_relatorio_texto(self) -> None:
        txt = gerar_relatorio_texto(self.res)
        self.assertIn("ABNT NBR 10898:2013", txt)
        self.assertIn("QUADRO GERAL", txt)
        self.assertIn("BANCO CENTRAL DE BATERIAS", txt)
        self.assertIn("CIRCUITOS DE CAMPO", txt)

    def test_gerar_csv_sanitizado(self) -> None:
        csv_txt = gerar_csv_sanitizado(self.res)
        self.assertIn("'=PerigoFormula", csv_txt)
        self.assertIn("circulacao_horizontal", csv_txt)

    def test_gerar_pacote_zip_deterministico(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho_zip = os.path.join(tmpdir, "teste_pacote.zip")
            gerar_pacote_zip(self.res, caminho_zip, svg_conteudo="<svg></svg>")

            self.assertTrue(os.path.exists(caminho_zip))
            with zipfile.ZipFile(caminho_zip, "r") as zf:
                nomes = zf.namelist()
                self.assertIn("memorial_descritivo.txt", nomes)
                self.assertIn("dados_dimensionamento.json", nomes)
                self.assertIn("quadro_ambientes.csv", nomes)
                self.assertIn("painel_esquematico.svg", nomes)

                # Verificar timestamp fixo determinístico 2026-01-01
                for info in zf.infolist():
                    self.assertEqual(info.date_time[:3], (2026, 1, 1))

            # Verificar que O_EXCL impede sobrescrita
            with self.assertRaises(FileExistsError):
                gerar_pacote_zip(self.res, caminho_zip)


if __name__ == "__main__":
    unittest.main()
