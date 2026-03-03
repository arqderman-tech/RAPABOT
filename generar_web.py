import json
from pathlib import Path
from datetime import datetime

DIR_DATA = Path("data")
DIR_DOCS = Path("docs")

def leer_json(n):
    r = DIR_DATA / n
    return json.load(open(r, encoding="utf-8")) if r.exists() else None

def fmt_pct(v):
    if v is None: return "—"
    return ("+" if v > 0 else "") + f"{v:.2f}%"

def color_pct(v):
    if v is None: return "#999"
    return "#dc2626" if v > 0 else "#16a34a" if v < 0 else "#999"

def main():
    DIR_DOCS.mkdir(exist_ok=True)
    resumen  = leer_json("resumen.json") or {}
    graficos = leer_json("graficos.json") or {}
    rank_dia = leer_json("ranking_dia.json") or []
    rank_7d  = leer_json("ranking_7d.json") or []
    rank_mes = leer_json("ranking_mes.json") or []

    fecha_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    v1    = resumen.get("variacion_dia")
    v30   = resumen.get("variacion_mes")
    total = resumen.get("total_productos", 0)
    cats  = resumen.get("categorias", {})

    cat_cards = ""
    for cat, cd in cats.items():
        v = cd.get("variacion_dia"); n = cd.get("total", 0)
        cat_cards += f'<div class="stat-card"><div class="label">{cat}</div><div class="value" style="color:{color_pct(v)}">{fmt_pct(v)}</div><div class="sub">{n} productos</div></div>'

    graficos_js = json.dumps(graficos, ensure_ascii=False)
    rank_dia_js = json.dumps(rank_dia[:20], ensure_ascii=False)
    rank_7d_js  = json.dumps(rank_7d[:20], ensure_ascii=False)
    rank_mes_js = json.dumps(rank_mes[:20], ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rapa Nui Price Tracker</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{{
  --bg:#ffffff;
  --surface:#f8f8f6;
  --surface2:#f0f0ec;
  --border:#e8e8e4;
  --border2:#d4d4ce;
  --text:#1a1a18;
  --muted:#888884;
  --accent:#7c3aed;
}}
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{background:var(--bg);color:var(--text);font-family:'DM Sans',sans-serif;font-size:15px;}}
header{{border-bottom:1px solid var(--border);padding:1.5rem 2.5rem;display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap;}}
.brand{{display:flex;align-items:baseline;gap:0.75rem;}}
.brand h1{{font-family:'DM Mono',monospace;font-size:1rem;font-weight:500;letter-spacing:0.05em;color:var(--text);}}
.brand .dot{{width:8px;height:8px;border-radius:50%;background:var(--accent);display:inline-block;margin-bottom:1px;}}
.tagline{{font-size:0.78rem;color:var(--muted);font-weight:300;}}
.timestamp{{font-family:'DM Mono',monospace;font-size:0.72rem;color:var(--muted);}}
.container{{max-width:1100px;margin:0 auto;padding:2rem 2rem 4rem;}}
.hero{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:1px;background:var(--border);border:1px solid var(--border);border-radius:12px;overflow:hidden;margin-bottom:2.5rem;}}
.stat-card{{background:var(--bg);padding:1.25rem 1.5rem;}}
.stat-card .label{{font-size:0.65rem;text-transform:uppercase;letter-spacing:0.12em;color:var(--muted);font-weight:500;margin-bottom:0.5rem;}}
.stat-card .value{{font-family:'DM Mono',monospace;font-size:1.6rem;font-weight:500;line-height:1;}}
.stat-card .sub{{font-size:0.72rem;color:var(--muted);margin-top:0.35rem;font-weight:300;}}
.section{{margin-bottom:2.5rem;}}
.section-title{{font-size:0.65rem;text-transform:uppercase;letter-spacing:0.14em;color:var(--muted);font-weight:500;margin-bottom:1.25rem;display:flex;align-items:center;gap:0.5rem;}}
.section-title::after{{content:'';flex:1;height:1px;background:var(--border);}}
.chart-wrap{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1.5rem;height:260px;}}
.period-tabs{{display:flex;gap:0.25rem;margin-bottom:1rem;}}
.period-tab{{padding:0.25rem 0.65rem;border-radius:6px;border:1px solid var(--border);background:transparent;color:var(--muted);cursor:pointer;font-size:0.72rem;font-family:'DM Mono',monospace;transition:all 0.15s;}}
.period-tab:hover{{border-color:var(--border2);color:var(--text);}}
.period-tab.active{{background:var(--text);color:var(--bg);border-color:var(--text);}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;}}
.rank-label{{font-size:0.7rem;font-weight:500;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.75rem;}}
table{{width:100%;border-collapse:collapse;font-size:0.83rem;}}
th{{padding:0.5rem 0.75rem;text-align:left;font-size:0.62rem;text-transform:uppercase;letter-spacing:0.1em;color:var(--muted);font-weight:500;border-bottom:1px solid var(--border);}}
td{{padding:0.55rem 0.75rem;border-bottom:1px solid var(--border);}}
tr:last-child td{{border-bottom:none;}}
tr:hover td{{background:var(--surface);}}
.pct-up{{color:#dc2626;font-family:'DM Mono',monospace;font-weight:500;}}
.pct-dn{{color:#16a34a;font-family:'DM Mono',monospace;font-weight:500;}}
.num{{font-family:'DM Mono',monospace;}}
.idx{{color:var(--muted);font-size:0.72rem;}}
@media(max-width:680px){{.grid2{{grid-template-columns:1fr;}}header{{padding:1rem 1.25rem;}}.container{{padding:1.25rem 1rem 3rem;}}}}
footer{{text-align:center;padding:2rem;color:var(--muted);font-size:0.7rem;border-top:1px solid var(--border);font-family:'DM Mono',monospace;letter-spacing:0.05em;}}
</style>
</head>
<body>
<header>
  <div class="brand">
    <span class="dot"></span>
    <h1>RAPA NUI PRICE TRACKER</h1>
    <span class="tagline">Córdoba</span>
  </div>
  <span class="timestamp">{fecha_str}</span>
</header>
<div class="container">
  <div class="hero">
    <div class="stat-card">
      <div class="label">Variación hoy</div>
      <div class="value" style="color:{color_pct(v1)}">{fmt_pct(v1)}</div>
      <div class="sub">{total} productos</div>
    </div>
    <div class="stat-card">
      <div class="label">Variación 30d</div>
      <div class="value" style="color:{color_pct(v30)}">{fmt_pct(v30)}</div>
    </div>
    {cat_cards}
  </div>

  <div class="section">
    <div class="section-title">Evolución de precios</div>
    <div class="period-tabs" id="ptabs">
      <button class="period-tab active" onclick="cambiarPeriodo('7d',this)">7d</button>
      <button class="period-tab" onclick="cambiarPeriodo('30d',this)">30d</button>
      <button class="period-tab" onclick="cambiarPeriodo('6m',this)">6m</button>
    </div>
    <div class="chart-wrap"><canvas id="chartMain"></canvas></div>
  </div>

  <div class="section">
    <div class="section-title">Por categoría</div>
    <div class="chart-wrap"><canvas id="chartCats"></canvas></div>
  </div>

  <div class="section">
    <div class="section-title">Rankings</div>
    <div class="period-tabs" id="rtabs">
      <button class="period-tab active" onclick="cambiarRanking('dia',this)">Hoy</button>
      <button class="period-tab" onclick="cambiarRanking('7d',this)">7 días</button>
      <button class="period-tab" onclick="cambiarRanking('mes',this)">30 días</button>
    </div>
    <div class="grid2" style="margin-top:1.25rem">
      <div>
        <div class="rank-label">↑ Más subieron</div>
        <table><thead><tr><th>#</th><th>Producto</th><th>Cat.</th><th>Var%</th><th>Precio</th></tr></thead><tbody id="rank-sube"></tbody></table>
      </div>
      <div>
        <div class="rank-label">↓ Más bajaron</div>
        <table><thead><tr><th>#</th><th>Producto</th><th>Cat.</th><th>Var%</th><th>Precio</th></tr></thead><tbody id="rank-baja"></tbody></table>
      </div>
    </div>
  </div>
</div>
<footer>rapanui.com.ar · RAPANUIBOT · actualización diaria via github actions</footer>

<script>
const G = {graficos_js};
const RANK = {{dia:{rank_dia_js},d7:{rank_7d_js},mes:{rank_mes_js}}};

// Paleta bien diferenciada para categorías
const PALETTE = [
  '#7c3aed','#dc2626','#0284c7','#d97706','#16a34a',
  '#db2777','#0891b2','#65a30d','#9333ea','#ea580c',
  '#0d9488','#be185d','#1d4ed8','#b45309','#15803d'
];
const catColorMap = {{}};
let colorIdx = 0;
function getCatColor(cat) {{
  if (!catColorMap[cat]) catColorMap[cat] = PALETTE[colorIdx++ % PALETTE.length];
  return catColorMap[cat];
}}

let chartMain, chartCats;

function chartBaseOpts(legend) {{
  return {{
    responsive: true, maintainAspectRatio: false,
    plugins: {{
      legend: {{ display: legend, labels: {{ color: '#888884', font: {{ size: 11, family: "'DM Sans'" }}, boxWidth: 10, padding: 12 }} }},
      tooltip: {{ backgroundColor: '#1a1a18', titleColor: '#fff', bodyColor: '#ccc', borderColor: '#333', borderWidth: 1, padding: 10 }}
    }},
    scales: {{
      x: {{ ticks: {{ color: '#aaa', maxTicksLimit: 7, font: {{ size: 10 }} }}, grid: {{ color: '#f0f0ec' }} }},
      y: {{ ticks: {{ color: '#aaa', callback: v => (v > 0 ? '+' : '') + v.toFixed(1) + '%', font: {{ size: 10 }} }}, grid: {{ color: '#f0f0ec' }}, afterDataLimits: ax => {{ if (ax.min > 0) ax.min = 0; if (ax.max < 0) ax.max = 0; }} }}
    }}
  }};
}}

function renderMain(p) {{
  const d = G[p]?.total || [];
  if (chartMain) chartMain.destroy();
  chartMain = new Chart(document.getElementById('chartMain').getContext('2d'), {{
    type: 'line',
    data: {{ labels: d.map(x => x.fecha), datasets: [{{ label: 'Promedio general', data: d.map(x => x.pct), borderColor: '#7c3aed', backgroundColor: 'rgba(124,58,237,0.05)', borderWidth: 2, pointRadius: d.length > 60 ? 0 : 3, pointBackgroundColor: '#7c3aed', tension: 0.3, fill: true }}] }},
    options: chartBaseOpts(false)
  }});
}}

function renderCats(p) {{
  const pc = G[p]?.por_categoria || {{}};
  if (chartCats) chartCats.destroy();
  const datasets = Object.entries(pc).map(([cat, datos]) => {{
    const c = getCatColor(cat);
    return {{ label: cat, data: datos.map(d => d.pct), borderColor: c, backgroundColor: 'transparent', borderWidth: 2, pointRadius: datos.length > 60 ? 0 : 2, tension: 0.3 }};
  }});
  const labels = [...new Set(Object.values(pc).flat().map(d => d.fecha))].sort();
  chartCats = new Chart(document.getElementById('chartCats').getContext('2d'), {{
    type: 'line', data: {{ labels, datasets }}, options: chartBaseOpts(true)
  }});
}}

function cambiarPeriodo(p, btn) {{
  document.querySelectorAll('#ptabs .period-tab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active'); renderMain(p); renderCats(p);
}}

function rankRow(p, i, esBaja) {{
  const cls = esBaja ? 'pct-dn' : 'pct-up';
  const s = p.diff_pct > 0 ? '+' : '';
  return `<tr>
    <td class="idx">${{i+1}}</td>
    <td style="font-size:0.8rem;max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${{p.nombre||''}}</td>
    <td style="font-size:0.7rem;color:var(--muted)">${{(p.categoria||'').substring(0,14)}}</td>
    <td class="${{cls}}">${{s}}${{p.diff_pct?.toFixed(1)}}%</td>
    <td class="num" style="font-size:0.8rem">${{p.precio_hoy ? '$'+Number(p.precio_hoy).toLocaleString('es-AR') : '—'}}</td>
  </tr>`;
}}

function mostrarRanking(k) {{
  const data = RANK[k] || [];
  const sube = data.filter(x => x.diff_pct > 0).slice(0, 10);
  const baja = [...data].filter(x => x.diff_pct < 0).sort((a, b) => a.diff_pct - b.diff_pct).slice(0, 10);
  const noData = '<tr><td colspan="5" style="color:var(--muted);text-align:center;padding:1.5rem;font-size:0.8rem">Sin cambios aún</td></tr>';
  document.getElementById('rank-sube').innerHTML = sube.length ? sube.map((p,i) => rankRow(p,i,false)).join('') : noData;
  document.getElementById('rank-baja').innerHTML = baja.length ? baja.map((p,i) => rankRow(p,i,true)).join('') : noData;
}}

function cambiarRanking(k, btn) {{
  document.querySelectorAll('#rtabs .period-tab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');
  mostrarRanking(k === 'dia' ? 'dia' : k === '7d' ? 'd7' : 'mes');
}}

renderMain('7d'); renderCats('7d'); mostrarRanking('dia');
</script>
</body></html>"""

    with open(DIR_DOCS / "index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Web RAPANUIBOT generada: docs/index.html")

if __name__ == "__main__":
    main()
