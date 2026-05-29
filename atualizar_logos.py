"""
atualizar_logos.py
Atualiza as logos embutidas (base64) nos dois dashboards HTML.

Coloque este script em QUALQUER pasta — ele usa caminhos absolutos.
Uso: python atualizar_logos.py
"""

import base64
import re
from pathlib import Path

# ── CONFIGURAÇÃO — AJUSTE ESTES CAMINHOS ─────────────────────────────────

# Pasta onde estão os arquivos PNG
PASTA_LOGOS = Path(r"C:\Users\b.souza\OneDrive - Alvarez and Marsal\Documents\Alvarez & Marsal\GERDAU\Manual_CMG\Report_GitHub")

# Caminhos completos dos dois index.html
HTML_FILES = [
    # Dashboard Manual CMG
    Path(r"C:\Users\b.souza\OneDrive - Alvarez and Marsal\Documents\Alvarez & Marsal\GERDAU\Manual_CMG\Report_GitHub\index.html"),
    # Dashboard Eventos — AJUSTE O CAMINHO ABAIXO
    Path(r"C:\Users\b.souza\OneDrive - Alvarez and Marsal\Documents\Alvarez & Marsal\GERDAU\PMO de Performance\Report_GitHub\index.html"),
]

# Arquivos de logo na PASTA_LOGOS
LOGOS = [
    PASTA_LOGOS / "gerdau.png",
    PASTA_LOGOS / "gerdau_o_futuro.png",
]

# ── CONVERTER LOGOS PARA BASE64 ───────────────────────────────────────────
print("=" * 50)
print("ATUALIZANDO LOGOS NOS DASHBOARDS")
print("=" * 50)

logo_b64 = []
for caminho in LOGOS:
    if not caminho.exists():
        print(f"ERRO: Logo nao encontrada: {caminho}")
        print("   Verifique o caminho em PASTA_LOGOS")
        exit(1)
    with open(caminho, "rb") as f:
        dados = base64.b64encode(f.read()).decode()
    logo_b64.append(f"data:image/png;base64,{dados}")
    print(f"OK  {caminho.name} lida ({len(dados) // 1024} KB em base64)")

B64_PATTERN = re.compile(r"data:image/png;base64,[A-Za-z0-9+/=]+")

print()
for html_path in HTML_FILES:
    if not html_path.exists():
        print(f"AVISO: Arquivo nao encontrado: {html_path}")
        print("   Verifique o caminho em HTML_FILES")
        print()
        continue

    html    = html_path.read_text(encoding="utf-8")
    antigas = list(dict.fromkeys(B64_PATTERN.findall(html)))

    if not antigas:
        print(f"AVISO: Nenhuma imagem base64 encontrada em: {html_path.name}")
        continue

    print(f"Arquivo: {html_path.parent.name} / {html_path.name}")
    print(f"   {len(antigas)} imagem(ns) encontrada(s)")

    for i, antiga in enumerate(antigas):
        if i < len(logo_b64):
            html = html.replace(antiga, logo_b64[i])
            print(f"   -> imagem {i + 1} ({LOGOS[i].name}) substituida")
        else:
            print(f"   -> imagem {i + 1} mantida (sem logo correspondente)")

    html_path.write_text(html, encoding="utf-8")
    print(f"   OK Salvo\n")

print("=" * 50)
print("Logos atualizadas!")
print()
print("Agora faca push nos dois repositorios:")
print()
print("  1. Dashboard Manual CMG:")
print(f"     cd \"{HTML_FILES[0].parent}\"")
print("     git add index.html")
print('     git commit -m "Atualiza logos"')
print("     git push origin main")
print()
print("  2. Dashboard Eventos:")
print(f"     cd \"{HTML_FILES[1].parent}\"")
print("     git add index.html")
print('     git commit -m "Atualiza logos"')
print("     git push origin main")
print("=" * 50)
