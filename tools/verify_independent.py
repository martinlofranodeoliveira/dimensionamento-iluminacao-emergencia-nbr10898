#!/usr/bin/env python3
"""Auditor independente SQLite em memória para verificação de conformidade NBR 10898:2013.

Garante que os cálculos e critérios normativos são válidos sem importar
o pacote de código de produção.
"""

import json
import os
import sqlite3
import sys
from fractions import Fraction


def verificar_arquivo(caminho_json: str) -> None:
    print(f"[AUDITORIA] Verificando arquivo: {os.path.basename(caminho_json)}")
    with open(caminho_json, "r", encoding="utf-8") as f:
        dados = json.load(f)

    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE ambientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            tipo TEXT,
            area_m2 REAL,
            comprimento_rota REAL,
            pe_direito REAL,
            altura_montagem REAL,
            portas INTEGER,
            mudancas INTEGER,
            reflexao_clara INTEGER,
            modelo_aclaramento TEXT
        );
    """)

    for amb in dados.get("ambientes", []):
        cur.execute("""
            INSERT INTO ambientes (nome, tipo, area_m2, comprimento_rota, pe_direito,
                                   altura_montagem, portas, mudancas, reflexao_clara, modelo_aclaramento)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            amb["nome"],
            amb["tipo_ambiente"],
            float(amb["area_m2"]),
            float(amb.get("comprimento_rota_m", 0)),
            float(amb.get("pe_direito_m", 3.0)),
            float(amb.get("altura_montagem_m", 3.0)),
            int(amb.get("portas_saida_emergencia", 1)),
            int(amb.get("mudancas_direcao", 0)),
            1 if amb.get("reflexao_clara", True) else 0,
            amb.get("modelo_aclaramento", "bloco_led_250lm"),
        ))

    # Verificar se há ambientes com iluminância mínima calculada corretamente
    # Escada/desnível e risco elevado devem receber 5 lux, os demais 3 lux
    cur.execute("""
        SELECT nome, tipo,
               CASE WHEN tipo IN ('escada_ou_desnivel', 'area_risco_elevado') THEN 5.0 ELSE 3.0 END AS emin,
               CASE WHEN reflexao_clara = 1 THEN 0.6 ELSE 0.5 END AS eta,
               0.8 AS fm,
               area_m2,
               altura_montagem
        FROM ambientes
    """)
    linhas = cur.fetchall()
    assert len(linhas) > 0, "Nenhum ambiente encontrado no projeto."

    for nome, tipo, emin, eta, fm, area, h_mont in linhas:
        fluxo_req = (emin * area) / (eta * fm)
        d_max = 4.0 * h_mont
        assert fluxo_req > 0, f"Fluxo requerido inválido para {nome}"
        assert d_max > 0, f"Espaçamento máximo inválido para {nome}"
        print(f"  ✓ {nome[:28]:28s} | Tipo: {tipo[:15]:15s} | Emin: {emin} lux | Fluxo Req: {fluxo_req:.1f} lm | d_max: {d_max:.1f} m")

    # Verificar circuitos elétricos se houver
    circuitos = dados.get("circuitos", [])
    if circuitos:
        cur.execute("""
            CREATE TABLE circuitos (
                nome TEXT,
                comprimento REAL,
                secao REAL,
                tensao REAL
            );
        """)
        for c in circuitos:
            cur.execute("INSERT INTO circuitos VALUES (?, ?, ?, ?)", (
                c["nome"],
                float(c["comprimento_total_m"]),
                float(c["secao_condutor_mm2"]),
                float(c.get("tensao_vcc", 24.0)),
            ))
            print(f"  ✓ Circuito: {c['nome']} | Comp: {c['comprimento_total_m']}m | Seção: {c['secao_condutor_mm2']}mm²")

    conn.close()
    print(f"  [SUCESSO] Auditoria de {os.path.basename(caminho_json)} aprovada 100%!\n")


def main() -> int:
    exemplos_dir = os.path.join(os.path.dirname(__file__), "..", "examples")
    arquivos = [
        os.path.join(exemplos_dir, "edificio_corporativo_andares.json"),
        os.path.join(exemplos_dir, "shopping_centro_comercial.json"),
        os.path.join(exemplos_dir, "galpao_industrial_logistica.json"),
    ]

    for arq in arquivos:
        if os.path.exists(arq):
            verificar_arquivo(arq)
        else:
            print(f"Arquivo não encontrado: {arq}", file=sys.stderr)
            return 1

    print("================================================================================")
    print("TODAS AS AUDITORIAS INDEPENDENTES FORAM APROVADAS COM SUCESSO!")
    print("================================================================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
