"""Testes unitários do motor de cálculo de iluminação de emergência NBR 10898."""

import unittest
from fractions import Fraction

from iluminacao_nbr10898.calculator import _teto_fracao, dimensionar_sistema_iluminacao
from iluminacao_nbr10898.constants import (
    AUTONOMIA_MINIMA_HORAS,
    ILUMINANCIA_MIN_DESNIVEL_ESCADA_LUX,
    ILUMINANCIA_MIN_HORIZONTAL_LUX,
)
from iluminacao_nbr10898.models import (
    Ambiente,
    CircuitoCentral,
    DadosProjeto,
    TipoAmbiente,
    TipoSistemaAlimentacao,
)


class TestCalculator(unittest.TestCase):
    """Testa os métodos analíticos de cálculo luminotécnico e elétrico."""

    def test_teto_fracao(self) -> None:
        self.assertEqual(_teto_fracao(Fraction(5, 1)), 5)
        self.assertEqual(_teto_fracao(Fraction(0, 1)), 0)
        self.assertEqual(_teto_fracao(Fraction(5, 2)), 3)
        self.assertEqual(_teto_fracao(Fraction(1, 10)), 1)
        self.assertEqual(_teto_fracao(Fraction(19, 4)), 5)

    def test_dimensionamento_circulacao_horizontal(self) -> None:
        amb = Ambiente(
            nome="Corredor",
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
        proj = DadosProjeto(
            nome_edificacao="Teste",
            tipo_sistema=TipoSistemaAlimentacao.BLOCO_AUTONOMO,
            ambientes=(amb,),
            circuitos=(),
            autonomia_horas=Fraction(2, 1),
        )
        res = dimensionar_sistema_iluminacao(proj)
        res_amb = res.ambientes[0]

        # 3 lux * 100 m² / (0.60 * 0.80) = 300 / 0.48 = 625 lm
        self.assertEqual(res_amb.iluminancia_requerida_lux, ILUMINANCIA_MIN_HORIZONTAL_LUX)
        self.assertEqual(res_amb.fluxo_total_requerido_lm, Fraction(625, 1))
        # 625 / 250 = 2.5 -> 3 luminárias
        self.assertEqual(res_amb.luminarias_aclaramento, 3)
        self.assertTrue(res_amb.conformidade_espacamento)
        self.assertIsNone(res.baterias)

    def test_dimensionamento_escada_exige_cinco_lux(self) -> None:
        amb = Ambiente(
            nome="Escada de Emergência",
            area_m2=Fraction(48, 1),
            comprimento_rota_m=Fraction(20, 1),
            pe_direito_m=Fraction(28, 10),
            altura_montagem_m=Fraction(25, 10),
            tipo_ambiente=TipoAmbiente.ESCADA_OU_DESNIVEL,
            portas_saida_emergencia=1,
            mudancas_direcao=2,
            modelo_aclaramento="bloco_led_250lm",
            reflexao_clara=True,
        )
        proj = DadosProjeto(
            nome_edificacao="Teste Escada",
            tipo_sistema=TipoSistemaAlimentacao.BLOCO_AUTONOMO,
            ambientes=(amb,),
            circuitos=(),
            autonomia_horas=Fraction(2, 1),
        )
        res = dimensionar_sistema_iluminacao(proj)
        res_amb = res.ambientes[0]

        # 5 lux * 48 m² / (0.60 * 0.80) = 240 / 0.48 = 500 lm
        self.assertEqual(res_amb.iluminancia_requerida_lux, ILUMINANCIA_MIN_DESNIVEL_ESCADA_LUX)
        self.assertEqual(res_amb.fluxo_total_requerido_lm, Fraction(500, 1))
        # 500 / 250 = 2 luminárias
        self.assertEqual(res_amb.luminarias_aclaramento, 2)

    def test_area_risco_elevado_exige_cinco_lux(self) -> None:
        amb = Ambiente(
            nome="Subestação Elétrica",
            area_m2=Fraction(50, 1),
            comprimento_rota_m=Fraction(15, 1),
            pe_direito_m=Fraction(3, 1),
            altura_montagem_m=Fraction(3, 1),
            tipo_ambiente=TipoAmbiente.AREA_RISCO_ELEVADO,
            portas_saida_emergencia=1,
            mudancas_direcao=0,
            modelo_aclaramento="luminaria_led_600lm",
            reflexao_clara=False,
        )
        proj = DadosProjeto(
            nome_edificacao="Teste Risco",
            tipo_sistema=TipoSistemaAlimentacao.BLOCO_AUTONOMO,
            ambientes=(amb,),
            circuitos=(),
            autonomia_horas=Fraction(2, 1),
        )
        res = dimensionar_sistema_iluminacao(proj)
        res_amb = res.ambientes[0]
        # 5 lux * 50 / (0.50 * 0.80) = 250 / 0.40 = 625 lm
        self.assertEqual(res_amb.iluminancia_requerida_lux, Fraction(5, 1))
        self.assertEqual(res_amb.fluxo_total_requerido_lm, Fraction(625, 1))
        # 625 / 600 = 1.04 -> 2 luminárias
        self.assertEqual(res_amb.luminarias_aclaramento, 2)

    def test_reflexao_escura_aumenta_fluxo_necessario(self) -> None:
        amb_claro = Ambiente(
            nome="Sala Clara",
            area_m2=Fraction(100, 1),
            comprimento_rota_m=Fraction(20, 1),
            pe_direito_m=Fraction(3, 1),
            altura_montagem_m=Fraction(3, 1),
            tipo_ambiente=TipoAmbiente.SALA_ESCRITORIO,
            portas_saida_emergencia=1,
            mudancas_direcao=0,
            modelo_aclaramento="bloco_led_250lm",
            reflexao_clara=True,
        )
        amb_escuro = Ambiente(
            nome="Sala Escura",
            area_m2=Fraction(100, 1),
            comprimento_rota_m=Fraction(20, 1),
            pe_direito_m=Fraction(3, 1),
            altura_montagem_m=Fraction(3, 1),
            tipo_ambiente=TipoAmbiente.SALA_ESCRITORIO,
            portas_saida_emergencia=1,
            mudancas_direcao=0,
            modelo_aclaramento="bloco_led_250lm",
            reflexao_clara=False,
        )
        proj = DadosProjeto(
            nome_edificacao="Teste Comparativo",
            tipo_sistema=TipoSistemaAlimentacao.BLOCO_AUTONOMO,
            ambientes=(amb_claro, amb_escuro),
            circuitos=(),
            autonomia_horas=Fraction(2, 1),
        )
        res = dimensionar_sistema_iluminacao(proj)
        self.assertGreater(res.ambientes[1].fluxo_total_requerido_lm, res.ambientes[0].fluxo_total_requerido_lm)

    def test_balizamento_rotas_longas(self) -> None:
        amb = Ambiente(
            nome="Corredor Extenso",
            area_m2=Fraction(150, 1),
            comprimento_rota_m=Fraction(60, 1),
            pe_direito_m=Fraction(3, 1),
            altura_montagem_m=Fraction(3, 1),
            tipo_ambiente=TipoAmbiente.CIRCULACAO_HORIZONTAL,
            portas_saida_emergencia=2,
            mudancas_direcao=1,
            modelo_aclaramento="bloco_led_250lm",
            reflexao_clara=True,
        )
        proj = DadosProjeto(
            nome_edificacao="Corredor",
            tipo_sistema=TipoSistemaAlimentacao.BLOCO_AUTONOMO,
            ambientes=(amb,),
            circuitos=(),
            autonomia_horas=Fraction(2, 1),
        )
        res = dimensionar_sistema_iluminacao(proj)
        res_amb = res.ambientes[0]
        # 60m / 15m = 4 -> 3 intermediários + 2 portas + 1 mudança = 6 balizas
        self.assertEqual(res_amb.sinalizadores_balizamento, 6)

    def test_alerta_pe_direito_elevado(self) -> None:
        amb = Ambiente(
            nome="Pé Direito Alto",
            area_m2=Fraction(200, 1),
            comprimento_rota_m=Fraction(30, 1),
            pe_direito_m=Fraction(7, 1),
            altura_montagem_m=Fraction(6, 1),
            tipo_ambiente=TipoAmbiente.GALPAO_DEPOSITO,
            portas_saida_emergencia=2,
            mudancas_direcao=1,
            modelo_aclaramento="farol_duplo_led_2400lm",
            reflexao_clara=False,
        )
        proj = DadosProjeto(
            nome_edificacao="Galpão",
            tipo_sistema=TipoSistemaAlimentacao.BLOCO_AUTONOMO,
            ambientes=(amb,),
            circuitos=(),
            autonomia_horas=Fraction(2, 1),
        )
        res = dimensionar_sistema_iluminacao(proj)
        self.assertTrue(any("pé-direito" in a for a in res.alertas))

    def test_sistema_centralizado_queda_tensao_e_baterias(self) -> None:
        amb = Ambiente(
            nome="Pavimento 1",
            area_m2=Fraction(200, 1),
            comprimento_rota_m=Fraction(40, 1),
            pe_direito_m=Fraction(3, 1),
            altura_montagem_m=Fraction(3, 1),
            tipo_ambiente=TipoAmbiente.CIRCULACAO_HORIZONTAL,
            portas_saida_emergencia=2,
            mudancas_direcao=1,
            modelo_aclaramento="bloco_led_250lm",
            reflexao_clara=True,
        )
        circ = CircuitoCentral(
            nome="Circuito 1",
            comprimento_total_m=Fraction(60, 1),
            secao_condutor_mm2=Fraction(25, 10),  # 2.5 mm²
            tensao_vcc=Fraction(24, 1),
        )
        proj = DadosProjeto(
            nome_edificacao="Edifício Central",
            tipo_sistema=TipoSistemaAlimentacao.CENTRALIZADO_BATERIAS,
            ambientes=(amb,),
            circuitos=(circ,),
            autonomia_horas=Fraction(2, 1),
        )
        res = dimensionar_sistema_iluminacao(proj)
        self.assertTrue(len(res.circuitos) > 0)
        self.assertTrue(res.circuitos[0].aprovado)
        self.assertIsNotNone(res.baterias)
        self.assertEqual(res.baterias.autonomia_horas, Fraction(2, 1))
        self.assertEqual(res.baterias.quantidade_baterias_12v, 2)
        self.assertGreater(res.baterias.capacidade_comercial_adotada_ah, Fraction(0, 1))

    def test_circuito_reprovado_por_queda_tensao_excessiva(self) -> None:
        amb = Ambiente(
            nome="Carga Pesada",
            area_m2=Fraction(1000, 1),
            comprimento_rota_m=Fraction(100, 1),
            pe_direito_m=Fraction(3, 1),
            altura_montagem_m=Fraction(3, 1),
            tipo_ambiente=TipoAmbiente.CIRCULACAO_HORIZONTAL,
            portas_saida_emergencia=2,
            mudancas_direcao=1,
            modelo_aclaramento="farol_duplo_led_2400lm",
            reflexao_clara=True,
        )
        # Circuito muito longo (1000m) e condutor fino (0.5 mm²)
        circ = CircuitoCentral(
            nome="Circuito Longo",
            comprimento_total_m=Fraction(1000, 1),
            secao_condutor_mm2=Fraction(5, 10),
            tensao_vcc=Fraction(24, 1),
        )
        proj = DadosProjeto(
            nome_edificacao="Teste Reprovado",
            tipo_sistema=TipoSistemaAlimentacao.CENTRALIZADO_BATERIAS,
            ambientes=(amb,),
            circuitos=(circ,),
            autonomia_horas=Fraction(2, 1),
        )
        res = dimensionar_sistema_iluminacao(proj)
        self.assertFalse(res.circuitos[0].aprovado)
        self.assertTrue(any("queda de tensão" in a for a in res.alertas))

    def test_correcao_autonomia_inferior_ao_minimo(self) -> None:
        amb = Ambiente(
            nome="Sala",
            area_m2=Fraction(50, 1),
            comprimento_rota_m=Fraction(10, 1),
            pe_direito_m=Fraction(3, 1),
            altura_montagem_m=Fraction(3, 1),
            tipo_ambiente=TipoAmbiente.SALA_ESCRITORIO,
            portas_saida_emergencia=1,
            mudancas_direcao=0,
            modelo_aclaramento="bloco_led_250lm",
            reflexao_clara=True,
        )
        circ = CircuitoCentral(
            nome="Circuito 1",
            comprimento_total_m=Fraction(30, 1),
            secao_condutor_mm2=Fraction(15, 10),
            tensao_vcc=Fraction(24, 1),
        )
        proj = DadosProjeto(
            nome_edificacao="Teste Autonomia",
            tipo_sistema=TipoSistemaAlimentacao.CENTRALIZADO_BATERIAS,
            ambientes=(amb,),
            circuitos=(circ,),
            autonomia_horas=Fraction(1, 1),  # 1h < 2h mínima
        )
        res = dimensionar_sistema_iluminacao(proj)
        self.assertTrue(any("Autonomia" in a for a in res.alertas))
        self.assertEqual(res.baterias.autonomia_horas, AUTONOMIA_MINIMA_HORAS)

    def test_recomendacoes_gmg(self) -> None:
        amb = Ambiente(
            nome="Área GMG",
            area_m2=Fraction(100, 1),
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
            nome_edificacao="Teste GMG",
            tipo_sistema=TipoSistemaAlimentacao.MOTO_GERADOR,
            ambientes=(amb,),
            circuitos=(),
            autonomia_horas=Fraction(2, 1),
        )
        res = dimensionar_sistema_iluminacao(proj)
        self.assertTrue(any("12 segundos" in r for r in res.recomendacoes))

    def test_multiplos_circuitos_divisao_de_carga(self) -> None:
        amb1 = Ambiente(
            nome="Setor Norte",
            area_m2=Fraction(200, 1),
            comprimento_rota_m=Fraction(40, 1),
            pe_direito_m=Fraction(3, 1),
            altura_montagem_m=Fraction(3, 1),
            tipo_ambiente=TipoAmbiente.CIRCULACAO_HORIZONTAL,
            portas_saida_emergencia=2,
            mudancas_direcao=1,
            modelo_aclaramento="bloco_led_250lm",
            reflexao_clara=True,
        )
        amb2 = Ambiente(
            nome="Setor Sul",
            area_m2=Fraction(200, 1),
            comprimento_rota_m=Fraction(40, 1),
            pe_direito_m=Fraction(3, 1),
            altura_montagem_m=Fraction(3, 1),
            tipo_ambiente=TipoAmbiente.CIRCULACAO_HORIZONTAL,
            portas_saida_emergencia=2,
            mudancas_direcao=1,
            modelo_aclaramento="bloco_led_250lm",
            reflexao_clara=True,
        )
        c1 = CircuitoCentral(
            nome="Circuito 1",
            comprimento_total_m=Fraction(50, 1),
            secao_condutor_mm2=Fraction(25, 10),
            tensao_vcc=Fraction(24, 1),
        )
        c2 = CircuitoCentral(
            nome="Circuito 2",
            comprimento_total_m=Fraction(50, 1),
            secao_condutor_mm2=Fraction(25, 10),
            tensao_vcc=Fraction(24, 1),
        )
        proj = DadosProjeto(
            nome_edificacao="Dois Setores",
            tipo_sistema=TipoSistemaAlimentacao.CENTRALIZADO_BATERIAS,
            ambientes=(amb1, amb2),
            circuitos=(c1, c2),
            autonomia_horas=Fraction(2, 1),
        )
        res = dimensionar_sistema_iluminacao(proj)
        self.assertEqual(len(res.circuitos), 2)
        # Cada circuito recebe metade da carga
        self.assertEqual(res.circuitos[0].corrente_total_a, res.circuitos[1].corrente_total_a)

    def test_modelo_aclaramento_nao_cadastrado_usa_fallback(self) -> None:
        amb = Ambiente(
            nome="Sala Especial",
            area_m2=Fraction(80, 1),
            comprimento_rota_m=Fraction(15, 1),
            pe_direito_m=Fraction(3, 1),
            altura_montagem_m=Fraction(3, 1),
            tipo_ambiente=TipoAmbiente.SALA_ESCRITORIO,
            portas_saida_emergencia=1,
            mudancas_direcao=0,
            modelo_aclaramento="modelo_desconhecido_xyz",
            reflexao_clara=True,
        )
        proj = DadosProjeto(
            nome_edificacao="Fallback",
            tipo_sistema=TipoSistemaAlimentacao.BLOCO_AUTONOMO,
            ambientes=(amb,),
            circuitos=(),
            autonomia_horas=Fraction(2, 1),
        )
        res = dimensionar_sistema_iluminacao(proj)
        # Fallback usa 250 lm
        self.assertEqual(res.ambientes[0].fluxo_unitario_lm, Fraction(250, 1))

    def test_ambiente_sem_rota_unidirecional(self) -> None:
        amb = Ambiente(
            nome="Auditório Quadrado",
            area_m2=Fraction(100, 1),
            comprimento_rota_m=Fraction(0, 1),
            pe_direito_m=Fraction(4, 1),
            altura_montagem_m=Fraction(4, 1),
            tipo_ambiente=TipoAmbiente.SALA_ESCRITORIO,
            portas_saida_emergencia=2,
            mudancas_direcao=0,
            modelo_aclaramento="luminaria_led_600lm",
            reflexao_clara=True,
        )
        proj = DadosProjeto(
            nome_edificacao="Auditório",
            tipo_sistema=TipoSistemaAlimentacao.BLOCO_AUTONOMO,
            ambientes=(amb,),
            circuitos=(),
            autonomia_horas=Fraction(2, 1),
        )
        res = dimensionar_sistema_iluminacao(proj)
        self.assertGreater(res.ambientes[0].espacamento_medio_m, Fraction(0, 1))
        self.assertTrue(res.ambientes[0].conformidade_espacamento)

    def test_tensao_banco_menor_que_24v_usa_uma_bateria(self) -> None:
        amb = Ambiente(
            nome="Sala 12V",
            area_m2=Fraction(50, 1),
            comprimento_rota_m=Fraction(10, 1),
            pe_direito_m=Fraction(3, 1),
            altura_montagem_m=Fraction(3, 1),
            tipo_ambiente=TipoAmbiente.CIRCULACAO_HORIZONTAL,
            portas_saida_emergencia=1,
            mudancas_direcao=0,
            modelo_aclaramento="bloco_led_250lm",
            reflexao_clara=True,
        )
        circ = CircuitoCentral(
            nome="Circuito 12V",
            comprimento_total_m=Fraction(20, 1),
            secao_condutor_mm2=Fraction(25, 10),
            tensao_vcc=Fraction(12, 1),
        )
        proj = DadosProjeto(
            nome_edificacao="Sistema 12V",
            tipo_sistema=TipoSistemaAlimentacao.CENTRALIZADO_BATERIAS,
            ambientes=(amb,),
            circuitos=(circ,),
            autonomia_horas=Fraction(2, 1),
        )
        res = dimensionar_sistema_iluminacao(proj)
        self.assertIsNotNone(res.baterias)
        self.assertEqual(res.baterias.quantidade_baterias_12v, 1)

    def test_farol_duplo_alto_fluxo(self) -> None:
        amb = Ambiente(
            nome="Pátio Industrial",
            area_m2=Fraction(1000, 1),
            comprimento_rota_m=Fraction(80, 1),
            pe_direito_m=Fraction(6, 1),
            altura_montagem_m=Fraction(5, 1),
            tipo_ambiente=TipoAmbiente.GALPAO_DEPOSITO,
            portas_saida_emergencia=4,
            mudancas_direcao=2,
            modelo_aclaramento="farol_duplo_led_2400lm",
            reflexao_clara=False,
        )
        proj = DadosProjeto(
            nome_edificacao="Indústria",
            tipo_sistema=TipoSistemaAlimentacao.BLOCO_AUTONOMO,
            ambientes=(amb,),
            circuitos=(),
            autonomia_horas=Fraction(2, 1),
        )
        res = dimensionar_sistema_iluminacao(proj)
        # Fluxo unitário = 2400 lm
        self.assertEqual(res.ambientes[0].fluxo_unitario_lm, Fraction(2400, 1))
        self.assertGreater(res.ambientes[0].luminarias_aclaramento, 0)


if __name__ == "__main__":
    unittest.main()
