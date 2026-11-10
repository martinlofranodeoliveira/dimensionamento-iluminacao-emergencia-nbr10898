"""Testes da interface de linha de comando (CLI) da NBR 10898."""

import io
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

from iluminacao_nbr10898.cli import main


class TestCLI(unittest.TestCase):
    """Testa os comandos, flags e saídas da CLI iluminacao-nbr10898."""

    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.exemplo_json = os.path.join(self.tmpdir.name, "projeto_teste.json")
        with open(self.exemplo_json, "w", encoding="utf-8") as f:
            f.write("""{
                "nome_edificacao": "Prédio Teste CLI",
                "tipo_sistema": "centralizado_baterias",
                "autonomia_horas": 2,
                "circuitos": [
                    {
                        "nome": "C1",
                        "comprimento_total_m": 45,
                        "secao_condutor_mm2": "2.5",
                        "tensao_vcc": 24
                    }
                ],
                "ambientes": [
                    {
                        "nome": "Corredor 1",
                        "area_m2": 150,
                        "comprimento_rota_m": 40,
                        "pe_direito_m": 3,
                        "altura_montagem_m": 3,
                        "tipo_ambiente": "circulacao_horizontal",
                        "portas_saida_emergencia": 2,
                        "mudancas_direcao": 1,
                        "modelo_aclaramento": "bloco_led_250lm",
                        "reflexao_clara": true
                    }
                ]
            }""")

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_cli_sem_argumentos(self) -> None:
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            code = main([])
            self.assertEqual(code, 0)
            self.assertIn("iluminacao-nbr10898", fake_out.getvalue())

    def test_cli_catalogo(self) -> None:
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            code = main(["catalogo"])
            self.assertEqual(code, 0)
            saida = fake_out.getvalue()
            self.assertIn("CATÁLOGO NORMATIVO", saida)
            self.assertIn("bloco_led_250lm", saida)
            self.assertIn("baliza_face_simples_30lm", saida)

    def test_cli_gerar_exemplo_stdout(self) -> None:
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            code = main(["gerar-exemplo"])
            self.assertEqual(code, 0)
            self.assertIn("nome_edificacao", fake_out.getvalue())

    def test_cli_gerar_exemplo_arquivo(self) -> None:
        caminho_arq = os.path.join(self.tmpdir.name, "modelo.json")
        code = main(["gerar-exemplo", "--saida", caminho_arq])
        self.assertEqual(code, 0)
        self.assertTrue(os.path.exists(caminho_arq))

    def test_cli_calcular_arquivo_inexistente(self) -> None:
        with patch("sys.stderr", new=io.StringIO()) as fake_err:
            code = main(["calcular", "nao_existe.json"])
            self.assertEqual(code, 1)
            self.assertIn("Erro ao abrir", fake_err.getvalue())

    def test_cli_calcular_json_invalido(self) -> None:
        arq_inv = os.path.join(self.tmpdir.name, "invalido.json")
        with open(arq_inv, "w", encoding="utf-8") as f:
            f.write("{ json quebrado ")
        with patch("sys.stderr", new=io.StringIO()) as fake_err:
            code = main(["calcular", arq_inv])
            self.assertEqual(code, 1)
            self.assertIn("Erro de validação", fake_err.getvalue())

    def test_cli_calcular_formatos(self) -> None:
        for fmt in ["texto", "json", "csv", "svg"]:
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                code = main(["calcular", self.exemplo_json, "--formato", fmt])
                self.assertEqual(code, 0)
                conteudo = fake_out.getvalue()
                if fmt == "svg":
                    self.assertIn("<svg", conteudo)
                elif fmt == "json":
                    self.assertIn("ABNT NBR 10898:2013", conteudo)
                elif fmt == "csv":
                    self.assertIn("ambiente;", conteudo)
                else:
                    self.assertIn("LOFRANO TECNOLOGIA", conteudo)

    def test_cli_calcular_saida_arquivo(self) -> None:
        saida_txt = os.path.join(self.tmpdir.name, "relatorio.txt")
        code = main(["calcular", self.exemplo_json, "--saida", saida_txt])
        self.assertEqual(code, 0)
        self.assertTrue(os.path.exists(saida_txt))

    def test_cli_calcular_pacote_zip(self) -> None:
        zip_path = os.path.join(self.tmpdir.name, "pacote.zip")
        code = main(["calcular", self.exemplo_json, "--pacote-zip", zip_path])
        self.assertEqual(code, 0)
        self.assertTrue(os.path.exists(zip_path))


if __name__ == "__main__":
    unittest.main()
