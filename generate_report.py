import pandas as pd
import json
import base64
import sys
from datetime import datetime, date, timedelta
from collections import defaultdict
from pathlib import Path

# ── CAMINHOS ──────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
XLSX_FILE  = BASE_DIR / "ManualCMG.xlsx"
HTML_OUT   = BASE_DIR / "index.html"
LOGO_FULL  = BASE_DIR / "gerdau.png"
LOGO_TAG   = BASE_DIR / "gerdau_o_futuro.png"
TEMPLATE   = BASE_DIR / "template.html"  # opcional (veja abaixo)

# ── LER PLANILHA ──────────────────────────────────────────────────────────
xl = pd.read_excel(XLSX_FILE, sheet_name="Plano de Trabalho (Ajustado)", header=None)
df = xl

nivel1  = df.iloc[10]
av_prev = round(float(nivel1[16]) * 100, 1)   # Coluna Q
av_real = round(float(nivel1[17]) * 100, 1)   # Coluna R
today   = date.today()

# ── CURVA S (das colunas semanais) ────────────────────────────────────────
weekly_planned = []
for col in range(18, 36):
    hdr = df.iloc[9, col]
    val = nivel1[col]
    if not pd.notna(hdr) or not isinstance(hdr, str): continue
    if not pd.notna(val) or float(val) <= 0 or float(val) > 1.5: continue
    try:
        w_date = datetime.strptime(hdr.strip(), "%d/%m/%Y").date()
        weekly_planned.append((w_date, w_date.strftime("%d/%m"), round(float(val)*100, 2)))
    except:
        pass

# Interpolar valor planejado em "hoje"
today_plan_val = 50.0
for i in range(len(weekly_planned) - 1):
    d0, _, p0 = weekly_planned[i]
    d1, _, p1 = weekly_planned[i + 1]
    if d0 <= today <= d1:
        frac = (today - d0).days / max((d1 - d0).days, 1)
        today_plan_val = p0 + (p1 - p0) * frac
        break

ratio = av_real / today_plan_val if today_plan_val > 0 else 1.0

sc = [{"date": "2026-03-09", "label": "09/03", "plan": 0.0, "real": 0.0, "proj": None}]
run_max = 0
for w_date, lbl, plan_pct in weekly_planned:
    if w_date <= today:
        scaled   = round(plan_pct * ratio, 1)
        run_max  = max(run_max, scaled)
        real_v   = min(run_max, av_real)
        proj_v   = None
    else:
        real_v = None
        proj_v = plan_pct
    sc.append({"date": w_date.strftime("%Y-%m-%d"), "label": lbl,
               "plan": plan_pct, "real": real_v, "proj": proj_v})

# ── TAREFAS / KPI ─────────────────────────────────────────────────────────
tasks = []
for i in range(10, len(df)):
    row   = df.iloc[i]
    nivel = str(row[1]) if pd.notna(row[1]) else ""
    eap   = str(row[2]) if pd.notna(row[2]) else ""
    task  = str(row[7]) if pd.notna(row[7]) else ""
    resp  = str(row[12]) if pd.notna(row[12]) else ""
    status = str(row[13]) if pd.notna(row[13]) else "Não iniciado"
    av_p  = float(row[16]) if pd.notna(row[16]) else 0.0
    av_r  = float(row[17]) if pd.notna(row[17]) else 0.0
    if not task or not nivel: continue

    def fmt(d):
        if pd.notna(d) and hasattr(d, "date") and callable(d.date): return d.date().strftime("%Y-%m-%d")
        if pd.notna(d) and hasattr(d, "year"): return d.strftime("%Y-%m-%d")
        return None

    parts    = eap.split(".")
    fase_map = {"1":"A","2":"B","3":"C","4":"D","5":"E"}
    fase     = fase_map.get(parts[1] if len(parts) > 1 else "0", "?")
    if nivel == "Nível 1": fase = "Projeto"

    tasks.append({"nivel": nivel, "eap": eap, "task": task, "fase": fase,
                  "resp": resp, "status": status, "s": fmt(row[8]), "e": fmt(row[9]),
                  "av_p": round(av_p, 4), "av_r": round(av_r, 4),
                  "is_marco": "MARCO" in task.upper() or "◆" in task})

leaf = [t for t in tasks if t["nivel"] == "Nível 5" and not t["is_marco"]]
total    = len(leaf)
done_cnt = sum(1 for t in leaf if t["status"] == "Concluído")
atr_cnt  = sum(1 for t in leaf if t["status"] == "Atrasado")
wip_cnt  = sum(1 for t in leaf if t["status"] == "Em andamento")
no_cnt   = sum(1 for t in leaf if t["status"] == "Não iniciado")

# ── GANTT ─────────────────────────────────────────────────────────────────
gantt = []
seen  = set()
for t in tasks:
    n    = t["nivel"]
    show = (n in ("Nível 1","Nível 2") or t["is_marco"] or
            (n == "Nível 5" and t["fase"] in ("A","B","D","E")) or
            (n == "Nível 5" and t["fase"] == "C" and
             any(k in t["task"] for k in ["Entendimento","Redação","Validação"])))
    if show and t["eap"] not in seen:
        seen.add(t["eap"]); gantt.append(t)

# ── LOGOS ─────────────────────────────────────────────────────────────────
def to_b64(path):
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

logo_full = to_b64(LOGO_FULL)
logo_tag  = to_b64(LOGO_TAG)

# ── GERAR HTML ────────────────────────────────────────────────────────────
# Lê o template e injeta os dados como variáveis JS
with open(TEMPLATE, "r", encoding="utf-8") as f:
    html = f.read()

replacements = {
    "%%SC_DATA%%"   : json.dumps(sc),
    "%%GANTT_DATA%%": json.dumps(gantt),
    "%%AV_PREV%%"   : str(av_prev).replace(".", ",") + "%",
    "%%AV_REAL%%"   : str(av_real).replace(".", ",") + "%",
    "%%DONE%%"      : str(done_cnt),
    "%%WIP%%"       : str(wip_cnt),
    "%%ATR%%"       : str(atr_cnt),
    "%%NO%%"        : str(no_cnt),
    "%%TOTAL%%"     : str(total),
    "%%TODAY%%"     : today.strftime("%d/%m/%Y"),
    "%%DIAS%%"      : str((date(2026, 7, 31) - today).days),
    "%%GAP%%"       : ("+{:.1f}".format(av_real - av_prev) if av_real >= av_prev
                       else "{:.1f}".format(av_real - av_prev)).replace(".", ","),
    "%%LOGO_FULL%%": logo_full,
    "%%LOGO_TAG%%":  logo_tag,
    "%%DONUT_DATA%%": f"{done_cnt},{wip_cnt},{atr_cnt},{no_cnt}",
}
for placeholder, value in replacements.items():
    html = html.replace(placeholder, value)

HTML_OUT.write_text(html, encoding="utf-8")
print(f"✅ index.html gerado — {today} — av_prev={av_prev}% av_real={av_real}%")