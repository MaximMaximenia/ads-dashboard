# -*- coding: utf-8 -*-
"""Прогноз на неделю. Вводные по доезду и чеку — от Максима."""
import os, html
OUT=os.path.expanduser("~/Desktop/Реклама/dashboard")
RATE=3.3
# кампания, конверсий/нед (факт 17-23.10), доезд, средний чек Br
BASE=[("СТО — По маркам",24,0.55,125),
      ("Регулировка фар",11,0.95,40),
      ("Развал-схождение",5,0.80,60),
      ("СТО — Общая",3,0.55,125),
      ("Ремонт подвески",1,0.60,80)]
SPEND_USD=165.07; SPEND=SPEND_USD*RATE
UPLIFT=16  # +конверсий/нед от переноса денег
K=(sum(b[1] for b in BASE)+UPLIFT)/sum(b[1] for b in BASE)

def calc(mult=1.0):
    rows=[]
    for n,c,d,p in BASE:
        cc=c*mult; cl=cc*d; rv=cl*p
        rows.append({"n":n,"conv":cc,"dz":d,"cl":cl,"price":p,"rev":rv})
    return rows
A=calc(); B=calc(K)
TA=sum(r["rev"] for r in A); TB=sum(r["rev"] for r in B)
CA=sum(r["conv"] for r in A); CB=sum(r["conv"] for r in B)
LA=sum(r["cl"] for r in A);  LB=sum(r["cl"] for r in B)
def br(x): return f"{x:,.0f}".replace(","," ")+" Br"
e=html.escape

CSS="""
:root{--bg:#f2f4f7;--card:#fff;--ink:#0f1115;--mute:#747b86;--line:#e6e9ee;
--a:#2563eb;--a2:#93b4fd;--g:#059669;--g2:#6ee7b7;--r:#dc2626;--soft:#f7f9fc}
@media(prefers-color-scheme:dark){:root:not([data-theme=light]){
--bg:#0d0f13;--card:#161a20;--ink:#eef1f5;--mute:#8e96a3;--line:#242a33;
--a:#60a5fa;--a2:#1e40af;--g:#34d399;--g2:#065f46;--r:#f87171;--soft:#1b2029;color-scheme:dark}}
:root[data-theme=dark]{--bg:#0d0f13;--card:#161a20;--ink:#eef1f5;--mute:#8e96a3;--line:#242a33;
--a:#60a5fa;--a2:#1e40af;--g:#34d399;--g2:#065f46;--r:#f87171;--soft:#1b2029;color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
-webkit-font-smoothing:antialiased}
.w{max-width:960px;margin:0 auto;padding-block:32px 72px;
padding-left:max(18px,env(safe-area-inset-left,0px));padding-right:max(18px,env(safe-area-inset-right,0px))}
h1{font-size:28px;margin:0 0 5px;letter-spacing:-.6px}
.sub{color:var(--mute);font-size:13px;margin:0 0 26px}
h2{font-size:15px;margin:34px 0 12px;letter-spacing:.2px}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:22px 24px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:8px}
.k{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px}
.k .v{font-size:25px;font-weight:650;letter-spacing:-.8px;font-variant-numeric:tabular-nums}
.k .l{font-size:12px;color:var(--mute);margin-top:4px}
.k .d{font-size:12px;margin-top:6px;font-weight:600}
.up{color:var(--g)}
table{border-collapse:collapse;width:100%;font-size:13.5px}
.tw{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:16px}
th,td{padding:11px 16px;text-align:left;white-space:nowrap;border-bottom:1px solid var(--line)}
th{font-size:11px;text-transform:uppercase;letter-spacing:.6px;color:var(--mute);font-weight:600}
tr:last-child td{border-bottom:0}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}
tfoot td{font-weight:650;background:var(--soft)}
.legend{display:flex;gap:18px;font-size:12.5px;color:var(--mute);margin:14px 0 0;flex-wrap:wrap}
.legend i{width:11px;height:11px;border-radius:3px;display:inline-block;margin-right:6px;vertical-align:-1px}
svg{width:100%;height:auto;display:block}
.vl{font:600 13px -apple-system,sans-serif;fill:var(--ink);text-anchor:middle;font-variant-numeric:tabular-nums}
.cl{font:12px -apple-system,sans-serif;fill:var(--mute);text-anchor:middle}
.gl{stroke:var(--line);stroke-width:1}
.al{font:11px -apple-system,sans-serif;fill:var(--mute);text-anchor:end}
.note{font-size:12.5px;color:var(--mute);margin:14px 0 0;line-height:1.6}
ul{margin:10px 0 0;padding-left:18px}li{margin:6px 0;font-size:13px;color:var(--mute)}
li b{color:var(--ink)}
"""

def paired(cats, s1, s2, l1, l2, unit="", H=230):
    """парные столбики с сеткой"""
    mx=max(max(s1),max(s2)); step=10**(len(str(int(mx)))-1)
    top=(int(mx/step)+1)*step
    W=620; PAD_L=46; PAD_B=44; PAD_T=24
    ch=H-PAD_T-PAD_B
    n=len(cats); gw=(W-PAD_L-10)/n; bw=min(30,gw/2.7)
    o=[f'<svg viewBox="0 0 {W} {H}">']
    for i in range(5):
        y=PAD_T+ch*i/4; v=top*(1-i/4)
        o.append(f'<line x1="{PAD_L}" y1="{y:.1f}" x2="{W-8}" y2="{y:.1f}" class="gl"/>')
        o.append(f'<text x="{PAD_L-10}" y="{y+4:.1f}" class="al">{v:,.0f}</text>'.replace(","," "))
    for i,c in enumerate(cats):
        cx=PAD_L+gw*i+gw/2
        for j,(val,col) in enumerate([(s1[i],"var(--a)"),(s2[i],"var(--g)")]):
            bh=val/top*ch
            x=cx-bw-3+j*(bw+6); y=PAD_T+ch-bh
            o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="5" fill="{col}"/>')
            if val>0:
                o.append(f'<text x="{x+bw/2:.1f}" y="{y-8:.1f}" class="vl">{val:,.0f}{unit}</text>'.replace(","," "))
        for k,part in enumerate(c.split("\n")):
            o.append(f'<text x="{cx:.1f}" y="{PAD_T+ch+19+k*15:.1f}" class="cl">{e(part)}</text>')
    return "".join(o)+"</svg>"

def single(cats, vals, color="var(--a)", unit="", H=210, fmt=None):
    mx=max(vals); step=10**max(0,(len(str(int(mx)))-1)); top=(int(mx/step)+1)*step or 1
    W=620; PAD_L=46; PAD_B=40; PAD_T=22; ch=H-PAD_T-PAD_B
    n=len(cats); gw=(W-PAD_L-10)/n; bw=min(70,gw*0.5)
    o=[f'<svg viewBox="0 0 {W} {H}">']
    for i in range(5):
        y=PAD_T+ch*i/4; v=top*(1-i/4)
        o.append(f'<line x1="{PAD_L}" y1="{y:.1f}" x2="{W-8}" y2="{y:.1f}" class="gl"/>')
        o.append(f'<text x="{PAD_L-10}" y="{y+4:.1f}" class="al">{v:,.0f}</text>'.replace(","," "))
    for i,(c,v) in enumerate(zip(cats,vals)):
        cx=PAD_L+gw*i+gw/2; bh=v/top*ch; x=cx-bw/2; y=PAD_T+ch-bh
        col=color(v) if callable(color) else color
        o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="5" fill="{col}"/>')
        t=fmt(v) if fmt else f"{v:,.0f}{unit}".replace(","," ")
        o.append(f'<text x="{cx:.1f}" y="{y-7:.1f}" class="vl">{t}</text>')
        for k,part in enumerate(c.split("\n")):
            o.append(f'<text x="{cx:.1f}" y="{PAD_T+ch+18+k*15:.1f}" class="cl">{e(part)}</text>')
    return "".join(o)+"</svg>"

P=[]
P.append('<meta name="claude:viewport-fit-sides" content="cover">')
P.append("<title>ДАСТО — прогноз недели</title>")
P.append(f"<style>{CSS}</style><div class='w'>")
P.append("<h1>Прогноз на неделю</h1>")
P.append("<p class='sub'>ДАСТО — СТО · база: факт 17–23 октября · доезд и чек — твои вводные</p>")

P.append("<div class='kpis'>")
for v,l,d in [(f"{CA:.0f}","конверсий",None),(f"{LA:.0f}","клиентов доедет",None),
              (br(TA),"выручка",None),(br(SPEND),"расход на рекламу",None),
              (f"{SPEND/TA*100:.0f}%","реклама от выручки",None)]:
    P.append(f"<div class='k'><div class='v'>{v}</div><div class='l'>{l}</div></div>")
P.append("</div>")

P.append("<h2>Выручка по кампаниям</h2><div class='card'>")
P.append(paired([r["n"].replace(" — ","\n") for r in A],
                [r["rev"] for r in A],[r["rev"] for r in B],"сейчас","после правок"," Br"))
P.append("<div class='legend'><span><i style='background:var(--a)'></i>сейчас</span>"
         "<span><i style='background:var(--g)'></i>после правок: компьютеры, пустые ключи, вечер</span></div>")
P.append("</div>")

P.append("<h2>Расчёт</h2><div class='tw'><table><tr>"
 "<th>Кампания</th><th class='n'>Конверсий</th><th class='n'>Доезд</th>"
 "<th class='n'>Клиентов</th><th class='n'>Чек</th><th class='n'>Выручка</th></tr>")
for r in A:
    P.append(f"<tr><td>{e(r['n'])}</td><td class='n'>{r['conv']:.0f}</td>"
             f"<td class='n'>{r['dz']*100:.0f}%</td><td class='n'>{r['cl']:.1f}</td>"
             f"<td class='n'>{r['price']} Br</td><td class='n'>{br(r['rev'])}</td></tr>")
P.append(f"<tfoot><tr><td>Итого</td><td class='n'>{CA:.0f}</td><td class='n'>—</td>"
         f"<td class='n'>{LA:.1f}</td><td class='n'>—</td><td class='n'>{br(TA)}</td></tr></tfoot>")
P.append("</table></div>")

P.append("<h2>Что даст перенос денег</h2>")
P.append("<div class='kpis'>")
for v,l,d in [(f"{CB:.0f}","конверсий",f"+{CB-CA:.0f}"),(f"{LB:.0f}","клиентов",f"+{LB-LA:.0f}"),
              (br(TB),"выручка",f"+{br(TB-TA)}"),(br(SPEND),"расход",'без изменений'),
              (f"{SPEND/TB*100:.0f}%","реклама от выручки",f"−{SPEND/TA*100-SPEND/TB*100:.0f} п.п.")]:
    cls="up" if d and d.startswith("+") or (d and d.startswith("−")) else ""
    P.append(f"<div class='k'><div class='v'>{v}</div><div class='l'>{l}</div>"
             f"<div class='d {cls}'>{d}</div></div>")
P.append("</div>")

P.append("<h2>Выручка и расход за неделю</h2><div class='card'>")
P.append(single(["выручка\nсейчас","выручка\nпосле правок","расход\nна рекламу"],
                [TA,TB,SPEND],
                color=lambda v:"var(--r)" if v==SPEND else ("var(--g)" if v==TB else "var(--a)"),
                unit=" Br",H=230))
P.append("</div>")

P.append("<h2>На чём построено</h2><div class='card'><ul>"
 "<li><b>44 конверсии</b> — факт прошлой недели, 17–23 октября. Прогноз считается от него.</li>"
 "<li><b>Доезд и чек</b> — твои цифры: по маркам 55% и 125 Br, фары 95% и 40 Br, развал 80% и 60 Br.</li>"
 "<li><b>Конверсия ≠ звонок.</b> Считается клик по номеру на сайте. Часть кликов звонком не заканчивается — "
 "если таких 20%, все суммы ниже на пятую часть.</li>"
 "<li><b>Чек «от»</b> — с сайта, без запчастей. Реальный, скорее всего, выше.</li>"
 "<li><b>+16 конверсий</b> — перенос денег с компьютеров, 23 пустых ключей и часов после 17:00. Бюджет тот же.</li>"
 "<li>Курс 3,3 Br за доллар.</li>"
 "</ul></div>")
P.append("</div>")

body="\n".join(P)
os.makedirs(OUT,exist_ok=True)
open(os.path.join(OUT,"forecast_artifact.html"),"w",encoding="utf-8").write(body)
stand=('<!doctype html><html lang="ru"><head><meta charset="utf-8">'
 '<meta name="viewport" content="width=device-width,initial-scale=1">'
 + body.replace('<meta name="claude:viewport-fit-sides" content="cover">\n','',1)
       .replace("<div class='w'>","</head><body><div class='w'>",1)+"</body></html>")
open(os.path.join(OUT,"forecast.html"),"w",encoding="utf-8").write(stand)
print(f"сейчас: {CA:.0f} конв, {LA:.1f} клиентов, {br(TA)}")
print(f"после:  {CB:.0f} конв, {LB:.1f} клиентов, {br(TB)}")
print(f"расход {br(SPEND)} | реклама {SPEND/TA*100:.0f}% → {SPEND/TB*100:.0f}%")
print("файл:", os.path.join(OUT,"forecast.html"), len(body),"байт")
