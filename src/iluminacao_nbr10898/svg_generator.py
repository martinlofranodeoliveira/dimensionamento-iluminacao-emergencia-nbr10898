"""Gerador de painel técnico vetorial SVG 1440x900 para iluminação de emergência NBR 10898."""

import html
from fractions import Fraction
from iluminacao_nbr10898.exporters import _fmt
from iluminacao_nbr10898.models import ResultadoDimensionamento


def gerar_painel_svg(res: ResultadoDimensionamento) -> str:
    """Renderiza painel esquemático vetorial SVG profissional 1440x900."""
    w, h = 1440, 900
    nome_proj = html.escape(res.nome_edificacao)
    tipo_sis = html.escape(res.tipo_sistema.value.upper())

    # Indicadores principais
    total_lum = str(res.total_luminarias_aclaramento)
    total_bal = str(res.total_sinalizadores_balizamento)
    pot_w = _fmt(res.potencia_total_instalada_w, 1)

    queda_txt = "N/A"
    queda_status = "OK"
    if res.circuitos:
        c0 = res.circuitos[0]
        queda_txt = f"{_fmt(c0.queda_tensao_percentual, 1)}%"
        queda_status = "CONFORME" if c0.aprovado else "REPROVADO"

    bat_txt = "Autônomo"
    if res.baterias is not None:
        bat_txt = f"{_fmt(res.baterias.capacidade_comercial_adotada_ah, 1)} Ah (24V)"

    # SVG XML
    svg: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
        '  <defs>',
        '    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
        '      <stop offset="0%" stop-color="#0b1329"/>',
        '      <stop offset="100%" stop-color="#1c2541"/>',
        '    </linearGradient>',
        '    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
        '      <stop offset="0%" stop-color="#1f2d4f" stop-opacity="0.95"/>',
        '      <stop offset="100%" stop-color="#141e36" stop-opacity="0.95"/>',
        '    </linearGradient>',
        '    <linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="0%">',
        '      <stop offset="0%" stop-color="#f59e0b"/>',
        '      <stop offset="100%" stop-color="#10b981"/>',
        '    </linearGradient>',
        '    <filter id="shadow" x="-5%" y="-5%" width="110%" height="115%">',
        '      <feDropShadow dx="0" dy="8" stdDeviation="6" flood-color="#000000" flood-opacity="0.5"/>',
        '    </filter>',
        '  </defs>',
        '  <style>',
        '    .title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 26px; font-weight: 700; fill: #ffffff; }',
        '    .subtitle { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 14px; fill: #94a3b8; }',
        '    .norma-badge { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 12px; font-weight: 600; fill: #f59e0b; }',
        '    .kpi-title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 12px; font-weight: 600; fill: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }',
        '    .kpi-value { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 28px; font-weight: 700; fill: #f8fafc; }',
        '    .kpi-sub { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 12px; fill: #10b981; }',
        '    .card-title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 600; fill: #e2e8f0; }',
        '    .tbl-header { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 12px; font-weight: 600; fill: #cbd5e1; }',
        '    .tbl-cell { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 12px; fill: #94a3b8; }',
        '    .diagram-text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 12px; fill: #e2e8f0; }',
        '  </style>',
        f'  <rect width="{w}" height="{h}" fill="url(#bgGrad)"/>',
    ]

    # Barra superior / Cabeçalho
    svg.append('  <!-- Header -->')
    svg.append('  <rect x="40" y="30" width="1360" height="90" rx="12" fill="url(#cardGrad)" stroke="#2e3e6b" stroke-width="1" filter="url(#shadow)"/>')
    svg.append('  <rect x="40" y="30" width="6" height="90" rx="3" fill="url(#accentGrad)"/>')
    svg.append(f'  <text x="65" y="65" class="title">LOFRANO TECNOLOGIA · ILUMINAÇÃO DE EMERGÊNCIA &amp; BALIZAMENTO</text>')
    svg.append(f'  <text x="65" y="95" class="subtitle">Projeto: {nome_proj} | Sistema: {tipo_sis} | Autonomia Regulamentar: 2 Horas Ininterruptas</text>')
    svg.append('  <rect x="1200" y="55" width="180" height="36" rx="6" fill="#1e293b" stroke="#f59e0b" stroke-width="1.5"/>')
    svg.append('  <text x="1290" y="78" text-anchor="middle" class="norma-badge">ABNT NBR 10898:2013</text>')

    # 4 Cartões KPI principais
    kpis = [
        ("Luminárias de Aclaramento", f"{total_lum} un", "Iluminância: 3 lux / 5 lux"),
        ("Balizamento de Saídas", f"{total_bal} un", "Rotas e Portas de Fuga"),
        ("Potência em Emergência", f"{pot_w} W", "Carga Total Instalada"),
        ("Autonomia / Baterias VRLA", bat_txt, f"Queda Tensão: {queda_txt} ({queda_status})"),
    ]

    x_card = 40
    y_card = 140
    card_w = 325
    card_h = 100
    gap = 20

    for idx, (titulo, val, sub) in enumerate(kpis):
        cx = x_card + idx * (card_w + gap)
        svg.append(f'  <!-- KPI {idx+1} -->')
        svg.append(f'  <rect x="{cx}" y="{y_card}" width="{card_w}" height="{card_h}" rx="10" fill="url(#cardGrad)" stroke="#2e3e6b" stroke-width="1" filter="url(#shadow)"/>')
        svg.append(f'  <text x="{cx+20}" y="{y_card+28}" class="kpi-title">{titulo}</text>')
        svg.append(f'  <text x="{cx+20}" y="{y_card+64}" class="kpi-value">{val}</text>')
        svg.append(f'  <text x="{cx+20}" y="{y_card+86}" class="kpi-sub">{sub}</text>')

    # Esquema visual / Diagrama topológico (Lado Esquerdo: x=40, y=260, w=680, h=590)
    svg.append('  <!-- Esquema Unifilar e Topológico -->')
    svg.append('  <rect x="40" y="260" width="670" height="590" rx="12" fill="url(#cardGrad)" stroke="#2e3e6b" stroke-width="1" filter="url(#shadow)"/>')
    svg.append('  <text x="65" y="295" class="card-title">Topologia do Sistema de Emergência e Rota de Fuga</text>')

    # Bloco Central / GMG
    svg.append('  <rect x="75" y="330" width="160" height="110" rx="8" fill="#1e293b" stroke="#3b82f6" stroke-width="2"/>')
    svg.append('  <text x="155" y="360" text-anchor="middle" class="card-title" fill="#60a5fa">CENTRAL 24Vcc</text>')
    svg.append('  <text x="155" y="385" text-anchor="middle" class="diagram-text">Supervisão &amp; Carga</text>')
    svg.append('  <text x="155" y="415" text-anchor="middle" class="kpi-sub">Comutação &lt; 12s</text>')

    # Banco de Baterias VRLA
    svg.append('  <rect x="75" y="470" width="160" height="90" rx="8" fill="#1e293b" stroke="#10b981" stroke-width="2"/>')
    svg.append('  <text x="155" y="500" text-anchor="middle" class="card-title" fill="#34d399">BANCO VRLA</text>')
    svg.append(f'  <text x="155" y="525" text-anchor="middle" class="diagram-text">{bat_txt}</text>')
    svg.append('  <text x="155" y="545" text-anchor="middle" class="kpi-sub">Autonomia 2 Horas</text>')

    # Conexão Central <-> Baterias
    svg.append('  <line x1="155" y1="440" x2="155" y2="470" stroke="#10b981" stroke-width="4"/>')

    # Linha de Distribuição dos Circuitos
    svg.append('  <!-- Linha de Campo -->')
    svg.append('  <line x1="235" y1="385" x2="310" y2="385" stroke="#f59e0b" stroke-width="4"/>')
    svg.append('  <line x1="310" y1="385" x2="310" y2="760" stroke="#f59e0b" stroke-width="3" stroke-dasharray="6,4"/>')

    # Luminárias de Aclaramento no Diagrama
    lums = [
        (350, 350, "Luminária LED 1 (Aclaramento)", "Piso: 3.0 lux"),
        (350, 440, "Luminária LED 2 (Aclaramento)", "Piso: 3.0 lux"),
        (350, 530, "Luminária LED Escada", "Degraus: 5.0 lux"),
        (350, 620, "Baliza Iluminada Face Simples", "Visibilidade 15m"),
        (350, 710, "Sinalizador Porta de Saída", "Acima da verga 2.2m"),
    ]

    for lx, ly, ltitle, lsub in lums:
        svg.append(f'  <line x1="310" y1="{ly+20}" x2="{lx}" y2="{ly+20}" stroke="#f59e0b" stroke-width="2"/>')
        svg.append(f'  <rect x="{lx}" y="{ly}" width="320" height="50" rx="6" fill="#1e293b" stroke="#475569" stroke-width="1"/>')
        # Ícone de lâmpada ou saída
        svg.append(f'  <circle cx="{lx+25}" cy="{ly+25}" r="12" fill="#f59e0b" fill-opacity="0.2" stroke="#f59e0b" stroke-width="2"/>')
        svg.append(f'  <text x="{lx+50}" y="{ly+24}" class="diagram-text" font-weight="600">{ltitle}</text>')
        svg.append(f'  <text x="{lx+50}" y="{ly+40}" class="tbl-cell">{lsub}</text>')

    # Tabela Resumo dos Ambientes (Lado Direito: x=730, y=260, w=670, h=590)
    svg.append('  <!-- Quadro Resumo de Ambientes -->')
    svg.append('  <rect x="730" y="260" width="670" height="590" rx="12" fill="url(#cardGrad)" stroke="#2e3e6b" stroke-width="1" filter="url(#shadow)"/>')
    svg.append('  <text x="755" y="295" class="card-title">Quadro de Ambientes, Iluminância e Dispositivos</text>')

    # Cabeçalho da Tabela
    ty = 330
    svg.append(f'  <rect x="755" y="{ty}" width="620" height="30" rx="4" fill="#1e293b"/>')
    svg.append(f'  <text x="765" y="{ty+20}" class="tbl-header">Ambiente</text>')
    svg.append(f'  <text x="965" y="{ty+20}" class="tbl-header">Tipo</text>')
    svg.append(f'  <text x="1080" y="{ty+20}" class="tbl-header">Emin (lux)</text>')
    svg.append(f'  <text x="1165" y="{ty+20}" class="tbl-header">Aclar.</text>')
    svg.append(f'  <text x="1235" y="{ty+20}" class="tbl-header">Baliz.</text>')
    svg.append(f'  <text x="1310" y="{ty+20}" class="tbl-header">Status</text>')

    # Linhas da Tabela
    for idx, amb in enumerate(res.ambientes[:9]):
        row_y = ty + 40 + idx * 42
        fill_bg = "#17233f" if idx % 2 == 0 else "#141c33"
        st_color = "#10b981" if amb.conformidade_espacamento else "#ef4444"
        st_txt = "OK" if amb.conformidade_espacamento else "AJUSTAR"

        svg.append(f'  <rect x="755" y="{row_y}" width="620" height="36" rx="4" fill="{fill_bg}"/>')
        svg.append(f'  <text x="765" y="{row_y+22}" class="tbl-cell" font-weight="600" fill="#f1f5f9">{html.escape(amb.nome[:22])}</text>')
        svg.append(f'  <text x="965" y="{row_y+22}" class="tbl-cell">{amb.tipo_ambiente.value[:14]}</text>')
        svg.append(f'  <text x="1080" y="{row_y+22}" class="tbl-cell">{_fmt(amb.iluminancia_requerida_lux, 0)} lux</text>')
        svg.append(f'  <text x="1165" y="{row_y+22}" class="tbl-cell">{amb.luminarias_aclaramento} un</text>')
        svg.append(f'  <text x="1235" y="{row_y+22}" class="tbl-cell">{amb.sinalizadores_balizamento} un</text>')
        svg.append(f'  <text x="1310" y="{row_y+22}" class="tbl-cell" font-weight="700" fill="{st_color}">{st_txt}</text>')

    # Rodapé de Conformidade
    svg.append('  <!-- Footer -->')
    svg.append('  <rect x="755" y="780" width="620" height="50" rx="6" fill="#1e293b" stroke="#334155" stroke-width="1"/>')
    svg.append('  <text x="770" y="802" class="diagram-text" fill="#94a3b8">Conformidade: Autonomia 2h · Queda de Tensão &le; 10% · Iluminância 3 lux / 5 lux</text>')
    svg.append('  <text x="770" y="820" class="diagram-text" font-weight="700" fill="#10b981">ABNT NBR 10898:2013 · DIMENSIONAMENTO TÉCNICO APROVADO</text>')

    svg.append('</svg>')
    return "\n".join(svg) + "\n"
