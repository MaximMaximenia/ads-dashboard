"""Сборка HTML-дашборда из snapshot.json. Только чтение."""
import json, os, html, datetime

SNAP = os.path.expanduser("~/Desktop/Реклама/01_google_ads/snapshot.json")
OUTDIR = os.path.expanduser("~/Desktop/Реклама/dashboard")
d = json.load(open(SNAP))
PERIOD_LABEL = {"today": "Сегодня", "week": "7 дней"}
e = html.escape

def money(x): return f"${x:,.2f}".replace(",", " ")
def pct(x): return f"{x:.1f}%" if x else "—"
def cv(x): return f"{x:.0f}" if abs(x - round(x)) < 0.01 else f"{x:.2f}"
def cpa(cost, conv): return money(cost / conv) if conv else "—"
def slug(s): return "".join(c if c.isalnum() else "-" for c in s.lower())
def pane_id(per, name): return f"{per}--{slug(name)}"

STATUS = {"ENABLED": "Работает", "PAUSED": "Пауза", "REMOVED": "Удалена"}

CSS = """
:root{--bg:#f6f7f9;--card:#fff;--ink:#16181d;--mute:#6b7280;--line:#e3e6ea;
--accent:#1a73e8;--good:#137333;--bad:#c5221f;--warn:#b06000}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){
--bg:#14161a;--card:#1c1f25;--ink:#e8eaed;--mute:#9aa0a6;--line:#2c3038;
--accent:#8ab4f8;--good:#81c995;--bad:#f28b82;--warn:#fdd663;color-scheme:dark}}
:root[data-theme=dark]{
--bg:#14161a;--card:#1c1f25;--ink:#e8eaed;--mute:#9aa0a6;--line:#2c3038;
--accent:#8ab4f8;--good:#81c995;--bad:#f28b82;--warn:#fdd663;color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:1100px;margin:0 auto;padding-block:24px 64px;
padding-left:max(16px,env(safe-area-inset-left,0px));
padding-right:max(16px,env(safe-area-inset-right,0px))}
h1{font-size:24px;margin:0 0 4px}
.sub{color:var(--mute);font-size:13px;margin:0 0 20px}
nav{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 20px;position:sticky;top:env(safe-area-inset-top,0px);
background:var(--bg);padding:10px 0;z-index:5;border-bottom:1px solid var(--line)}
nav button{font:inherit;font-size:13px;padding:7px 13px;border:1px solid var(--line);
background:var(--card);color:var(--ink);border-radius:999px;cursor:pointer;white-space:nowrap}
nav.periods{border-bottom:0;padding-bottom:0;position:static;margin-bottom:8px}
nav.periods button{border-radius:8px;font-weight:500}
nav button[aria-selected=true]{background:var(--accent);color:#fff;border-color:var(--accent)}
section{display:none}section.on{display:block}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin:0 0 18px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px}
.kpi .v{font-size:21px;font-weight:600;letter-spacing:-.3px}
.kpi .l{color:var(--mute);font-size:12px;margin-top:2px}
h3{font-size:15px;margin:22px 0 8px}
.tw{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:12px}
table{border-collapse:collapse;width:100%;font-size:13.5px}
th,td{padding:9px 12px;text-align:left;border-bottom:1px solid var(--line);white-space:nowrap}
th{color:var(--mute);font-weight:500;font-size:12px;text-transform:uppercase;letter-spacing:.4px}
tr:last-child td{border-bottom:0}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}
td.term{white-space:normal;min-width:180px}
.note{color:var(--mute);font-size:12.5px;margin:8px 2px 0}
.pill{font-size:11px;padding:2px 8px;border-radius:999px;background:var(--line);color:var(--mute)}
.pill.live{background:rgba(19,115,51,.14);color:var(--good)}
.bad{color:var(--bad)}.warn{color:var(--warn)}.good{color:var(--good)}
footer{color:var(--mute);font-size:12.5px;margin-top:40px;border-top:1px solid var(--line);padding-top:14px}
"""

JS = """
const periods=[...document.querySelectorAll('nav.periods button')];
const tabs=[...document.querySelectorAll('nav.accounts button')];
const panes=[...document.querySelectorAll('section')];
let per='today', acc=tabs.length?tabs[0].dataset.t:'';
function paint(){
  periods.forEach(b=>b.setAttribute('aria-selected',b.dataset.p===per));
  tabs.forEach(b=>b.setAttribute('aria-selected',b.dataset.t===acc));
  const want=per+'--'+acc;
  panes.forEach(s=>s.classList.toggle('on',s.id===want));
  try{localStorage.setItem('ads-per',per);localStorage.setItem('ads-acc',acc)}catch(e){}
}
periods.forEach(b=>b.onclick=()=>{per=b.dataset.p;paint()});
tabs.forEach(b=>b.onclick=()=>{acc=b.dataset.t;paint()});
try{
  const sp=localStorage.getItem('ads-per'), sa=localStorage.getItem('ads-acc');
  if(periods.some(b=>b.dataset.p===sp)) per=sp;
  if(tabs.some(b=>b.dataset.t===sa)) acc=sa;
}catch(e){}
paint();
"""

p = []
p.append('<!doctype html><html lang="ru"><head><meta charset="utf-8">')
p.append('<meta name="viewport" content="width=device-width,initial-scale=1">')
p.append("<title>Google Ads — дашборд</title>")
p.append(f"<style>{CSS}</style></head><body><div class='wrap'>")
p.append("<h1>Google Ads — дашборд по аккаунтам</h1>")
p.append(f"<p class='sub'>Собрано {datetime.datetime.now():%d.%m.%Y в %H:%M}</p>")

p.append("<nav class='periods'>")
for key in ("today", "week"):
    p.append(f"<button data-p='{key}'>{PERIOD_LABEL[key]}</button>")
p.append("</nav>")

first = d["periods"]["week"]["accounts"]
p.append("<nav class='accounts'>")
for a in first:
    p.append(f"<button data-t='{slug(a['name'])}'>{e(a['name'])}</button>")
p.append("</nav>")

for per in ("today", "week"):
  for a in d["periods"][per]["accounts"]:
    camps = a["campaigns"]
    live = [c for c in camps if c["status"] == "ENABLED"]
    cost = sum(c["cost"] for c in camps)
    clicks = sum(c["clicks"] for c in camps)
    conv = sum(c["conv"] for c in camps)
    budget = sum(c["budget"] for c in live)
    p.append(f"<section id='{pane_id(per, a['name'])}'>")
    cls = "bad" if not conv and cost else ""
    p.append("<div class='kpis'>"
             f"<div class='kpi'><div class='v'>{money(cost)}</div><div class='l'>расход</div></div>"
             f"<div class='kpi'><div class='v {cls}'>{cv(conv)}</div><div class='l'>обращений</div></div>"
             f"<div class='kpi'><div class='v'>{cpa(cost, conv)}</div><div class='l'>цена обращения</div></div>"
             f"<div class='kpi'><div class='v'>{clicks}</div><div class='l'>кликов</div></div>"
             f"<div class='kpi'><div class='v'>{money(budget)}</div><div class='l'>бюджет в день</div></div>"
             f"<div class='kpi'><div class='v'>{len(live)} / {len(camps)}</div><div class='l'>кампаний работает</div></div>"
             "</div>")
    if per == "today":
        p.append("<p class='note'>Сегодняшние цифры Google отдаёт с задержкой — "
                 "за последние часы данные могут быть неполными.</p>")
    if a["errors"]:
        p.append("<p class='note bad'>Ошибки сбора: " + e("; ".join(a["errors"])) + "</p>")

    rows = sorted([c for c in camps if c["cost"] > 0 or c["status"] == "ENABLED"],
                  key=lambda c: -c["cost"])
    if rows:
        p.append("<h3>Кампании</h3><div class='tw'><table><tr><th>Кампания</th><th>Статус</th>"
                 "<th class='n'>Бюджет</th><th class='n'>Расход</th><th class='n'>Клики</th>"
                 "<th class='n'>Обращения</th><th class='n'>Цена обращения</th></tr>")
        for c in rows:
            pill = "<span class='pill live'>Работает</span>" if c["status"] == "ENABLED" \
                else f"<span class='pill'>{STATUS.get(c['status'], c['status'])}</span>"
            zero = " class='n bad'" if c["status"] == "ENABLED" and c["cost"] > 0 and not c["conv"] else " class='n'"
            p.append(f"<tr><td>{e(c['name'])}</td><td>{pill}</td>"
                     f"<td class='n'>{money(c['budget']) if c['status']=='ENABLED' else '—'}</td>"
                     f"<td class='n'>{money(c['cost'])}</td><td class='n'>{c['clicks']}</td>"
                     f"<td{zero}>{cv(c['conv'])}</td>"
                     f"<td class='n'>{cpa(c['cost'], c['conv'])}</td></tr>")
        p.append("</table></div>")

        isr = [c for c in rows if c["is"] or c["lost_budget"] or c["lost_rank"]]
        if isr:
            p.append("<h3>Доля показов: что выкупаем и где теряем</h3><div class='tw'><table>"
                     "<tr><th>Кампания</th><th class='n'>Получено</th>"
                     "<th class='n'>Потеряно: бюджет</th><th class='n'>Потеряно: ранг</th></tr>")
            for c in sorted(isr, key=lambda c: -c["lost_budget"]):
                b = " class='n warn'" if c["lost_budget"] > 20 else " class='n'"
                r = " class='n warn'" if c["lost_rank"] > 35 else " class='n'"
                p.append(f"<tr><td>{e(c['name'])}</td><td class='n'>{pct(c['is'])}</td>"
                         f"<td{b}>{pct(c['lost_budget'])}</td><td{r}>{pct(c['lost_rank'])}</td></tr>")
            p.append("</table></div>")
            p.append("<p class='note'>Потери из-за бюджета лечатся деньгами. "
                     "Потери из-за ранга — качеством объявлений, релевантностью и ставкой.</p>")

    terms = a["terms"]
    p.append("<h3>Поисковые запросы</h3>")
    if terms:
        work = sorted([t for t in terms if t["conv"] > 0], key=lambda t: -t["conv"])[:15]
        burn = sorted([t for t in terms if t["conv"] == 0 and t["cost"] > 0],
                      key=lambda t: -t["cost"])[:15]
        burn_cost = sum(t["cost"] for t in terms if t["conv"] == 0 and t["cost"] > 0)
        tconv = sum(t["conv"] for t in terms)
        p.append(f"<p class='note'>Всего запросов: {len(terms)}. "
                 f"С кликами, но без обращений — на {money(burn_cost)}.</p>")
        if conv and abs(tconv - conv) > 0.5:
            p.append(f"<p class='note'>По конкретным запросам отнесено {cv(tconv)} обращений "
                     f"из {cv(conv)}. Остальные Google к запросу не привязал — "
                     f"так бывает с редкими запросами и звонками.</p>")
        if work:
            p.append("<h3>Приносят обращения</h3><div class='tw'><table>"
                     "<tr><th>Запрос</th><th class='n'>Клики</th><th class='n'>Расход</th>"
                     "<th class='n'>Обращения</th></tr>")
            for t in work:
                p.append(f"<tr><td class='term'>{e(t['term'])}</td><td class='n'>{t['clicks']}</td>"
                         f"<td class='n'>{money(t['cost'])}</td>"
                         f"<td class='n good'>{cv(t['conv'])}</td></tr>")
            p.append("</table></div>")
        if burn:
            p.append("<h3>Тратят без обращений</h3><div class='tw'><table>"
                     "<tr><th>Запрос</th><th class='n'>Клики</th><th class='n'>Расход</th></tr>")
            for t in burn:
                p.append(f"<tr><td class='term'>{e(t['term'])}</td><td class='n'>{t['clicks']}</td>"
                         f"<td class='n'>{money(t['cost'])}</td></tr>")
            p.append("</table></div>")
    else:
        p.append("<p class='note'>Запросов не было.</p>")
    p.append("</section>")

p.append("<footer>Статистика аукционов — список конкурентов и их доля показов — "
         "в Google Ads API не отдаётся, она есть только в интерфейсе. "
         "Всё остальное здесь берётся из API напрямую.</footer>")
p.append(f"</div><script>{JS}</script></body></html>")

os.makedirs(OUTDIR, exist_ok=True)
page = "\n".join(p)
out = os.path.join(OUTDIR, "index.html")
open(out, "w").write(page)
print("Готово:", out, os.path.getsize(out), "байт")

# вариант для артефакта: без обёртки doctype/html/head/body
art = page
art = art.replace('<!doctype html><html lang="ru"><head><meta charset="utf-8">\n'
                  '<meta name="viewport" content="width=device-width,initial-scale=1">\n', "")
art = art.replace("</head><body><div class='wrap'>", "<div class='wrap'>")
art = art.replace("</div><script>", "</div>\n<script>")
art = art.replace("</body></html>", "")
art = art.replace("<title>Google Ads — дашборд</title>",
                  '<meta name="claude:viewport-fit-sides" content="cover">\n'
                  "<title>Google Ads — дашборд</title>")
outa = os.path.join(OUTDIR, "artifact.html")
open(outa, "w").write(art)
print("Готово:", outa, os.path.getsize(outa), "байт")
