"""Testes unitários do codec JSON canônico RFC 8259 da NBR 10898."""

import json
import unittest
from fractions import Fraction

from iluminacao_nbr10898.calculator import dimensionar_sistema_iluminacao
from iluminacao_nbr10898.codecs import carregar_projeto_json, exportar_resultado_json
from iluminacao_nbr10898.models import (
    Ambiente,
    CircuitoCentral,
    DadosProjeto,
    TipoAmbiente,
    TipoSistemaAlimentacao,
)


class TestCodecs(unittest.TestCase):
    """Validação estrita do codec JSON canônico sem ponto flutuante."""

    def test_carregar_projeto_valido(self) -> None:
        json_str = """{
            "nome_edificacao": "Prédio Teste",
            "tipo_sistema": "centralizado_baterias",
            "autonomia_horas": "2",
            "circuitos": [
                {
                    "nome": "C1",
                    "comprimento_total_m": 50,
                    "secao_condutor_mm2": "2.5",
                    "tensao_vcc": 24
                }
            ],
            "ambientes": [
                {
                    "nome": "Hall",
                    "area_m2": 100,
                    "comprimento_rota_m": 30,
                    "pe_direito_m": "2.8",
                    "altura_montagem_m": "2.8",
                    "tipo_ambiente": "circulacao_horizontal",
                    "portas_saida_emergencia": 2,
                    "mudancas_direcao": 1,
                    "modelo_aclaramento": "bloco_led_250lm",
                    "reflexao_clara": true
                }
            ]
        }"""
        proj = carregar_projeto_json(json_str)
        self.assertEqual(proj.nome_edificacao, "Prédio Teste")
        self.assertEqual(len(proj.ambientes), 1)
        self.assertEqual(proj.ambientes[0].area_m2, Fraction(100, 1))

    def test_rejeitar_bom(self) -> None:
        json_bom = "\ufeff" + '{"nome_edificacao": "Teste"}'
        with self.assertRaises(ValueError) as ctx:
            carregar_projeto_json(json_bom)
        self.assertIn("BOM", str(ctx.exception))

    def test_rejeitar_chaves_duplicadas(self) -> None:
        json_dup = '{"nome_edificacao": "A", "nome_edificacao": "B"}'
        with self.assertRaises(ValueError) as ctx:
            carregar_projeto_json(json_dup)
        self.assertIn("duplicada", str(ctx.exception).lower())

    def test_rejeitar_ponto_flutuante(self) -> None:
        json_float = '{"nome_edificacao": "Teste", "autonomia_horas": 2.5}'
        with self.assertRaises(ValueError) as ctx:
            carregar_projeto_json(json_float)
        self.assertIn("Ponto flutuante", str(ctx.exception))

    def test_rejeitar_profundidade_excessiva(self) -> None:
        profundo: dict = {"nivel": 0}
        atual = profundo
        for i in range(35):
            atual["sub"] = {"nivel": i + 1}
            atual = atual["sub"]
        json_profundo = json.dumps(profundo)
        with self.assertRaises(ValueError) as ctx:
            carregar_projeto_json(json_profundo)
        self.assertIn("Profundidade", str(ctx.exception))

    def test_exportar_json_resultado(self) -> None:
        amb = Ambiente(
            nome="Hall",
            area_m2=Fraction(80, 1),
            comprimento_rota_m=Fraction(20, 1),
            pe_direito_m=Fraction(3, 1),
            altura_montagem_m=Fraction(3, 1),
            tipo_ambiente=TipoAmbiente.CIRCULACAO_HORIZONTAL,
            portas_saida_emergencia=1,
            mudancas_direcao=0,
            modelo_aclaramento="bloco_led_250lm",
            reflexao_clara=True,
        )
        proj = DadosProjeto(
            nome_edificacao="Teste Serializacao",
            tipo_sistema=TipoSistemaAlimentacao.BLOCO_AUTONOMO,
            ambientes=(amb,),
            circuitos=(),
            autonomia_horas=Fraction(2, 1),
        )
        res = dimensionar_sistema_iluminacao(proj)
        res_json = exportar_resultado_json(res)
        self.assertIn("ABNT NBR 10898:2013", res_json)
        self.assertIn("Teste Serializacao", res_json)
        self.assertIn("luminarias_aclaramento", res_json)

    def test_rejeitar_json_raiz_lista(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            carregar_projeto_json("[]")
        self.assertIn("dicionário", str(ctx.exception))

    def test_rejeitar_ambientes_nao_lista(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            carregar_projeto_json('{"ambientes": "invalido"}')
        self.assertIn("deve ser uma lista", str(ctx.exception))

    def test_rejeitar_circuitos_nao_lista(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            carregar_projeto_json('{"ambientes": [], "circuitos": "invalido"}')
        self.assertIn("deve ser uma lista", str(ctx.exception))

    def test_ambiente_com_fracao_string(self) -> None:
        json_frac = """{
            "nome_edificacao": "Fracoes",
            "ambientes": [
                {
                    "nome": "Sala",
                    "area_m2": "100/3",
                    "comprimento_rota_m": "15/2"
                }
            ]
        }"""
        proj = carregar_projeto_json(json_frac)
        self.assertEqual(proj.ambientes[0].area_m2, Fraction(100, 3))
        self.assertEqual(proj.ambientes[0].comprimento_rota_m, Fraction(15, 2))


if __name__ == "__main__":
    unittest.main()
