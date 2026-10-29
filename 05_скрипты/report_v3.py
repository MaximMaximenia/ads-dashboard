# -*- coding: utf-8 -*-
import json, os, html
from collections import defaultdict
D=json.load(open(os.path.expanduser("~/Desktop/Реклама/01_google_ads/weekly.json")))
OUT=os.path.expanduser("~/Desktop/Реклама/dashboard"); e=html.escape
def M(x): return f"${x:,.2f}".replace(","," ")
def M0(x): return f"${x:,.0f}".replace(","," ")

WEEKS=[("Неделя 1","06–12.10","2026-10-06","2026-10-12"),
       ("Неделя 2","13–19.10","2026-10-13","2026-10-19"),
       ("Неделя 3","20–26.10","2026-10-20","2026-10-26"),
       ("Неделя 4","27–28.10","2026-10-27","2026-10-28")]
Wd=[]
for nm,lab,a,b in WEEKS:
    rs=[r for r in D["daily"] if a<=r["d"]<=b]
    days=len({r["d"] for r in rs})
    c=sum(r["cost"] for r in rs); k=sum(r["clicks"] for r in rs); v=sum(r["conv"] for r in rs)
    Wd.append(dict(nm=nm,lab=lab,days=days,cost=c,clicks=k,conv=v,
                   cpa=c/v if v else 0,cvr=v/k*100 if k else 0,vpd=v/days,cpd=c/days))
daily=defaultdict(lambda:[0.0,0,0.0])
for r in D["daily"]:
    x=daily[r["d"]]; x[0]+=r["cost"]; x[1]+=r["clicks"]; x[2]+=r["conv"]
DAYS=sorted(daily)
dev=defaultdict(lambda:[0.0,0.0])
for r in D["dev"]:
    x=dev[r["dev"]]; x[0]+=r["cost"]; x[1]+=r["conv"]
PCW=0.0
for nm,lab,a,b in WEEKS:
    pc=[r for r in D["dev"] if a<=r["d"]<=b and r["dev"]=="DESKTOP"]
    mo=[r for r in D["dev"] if a<=r["d"]<=b and r["dev"]=="MOBILE"]
    pcc=sum(r["cost"] for r in pc); pcv=sum(r["conv"] for r in pc)
    mc=sum(r["cost"] for r in mo); mv=sum(r["conv"] for r in mo)
    PCW += pcc - pcv*(mc/mv if mv else 0)
ca=defaultdict(lambda:[0.0,0.0])
for r in D["daily"]:
    x=ca[r["camp"]]; x[0]+=r["cost"]; x[1]+=r["conv"]
EMPTY=sum(v[0] for v in ca.values() if v[1]==0)
TOTAL=sum(v[0] for v in ca.values())
MINUS=15.22
SAFE=[("цена",71,8.00),("сколько стоит",22,4.85),("поблизости",2,1.45),
      ("автоэлектрик",3,0.69),("шиномонтаж",2,0.23),("отзыв",2,0.00)]
RISKY=[("стоимость",1),("рядом",2),("бесплатно",1)]
MARKS={"2026-10-21":("бюджет Развала $5→$10",0),
       "2026-10-23":("переход на «Максимум конверсий»",1),
       "2026-10-26":("целевая цена $2,50→$1,70",2),
       "2026-10-27":("бюджет По маркам $10→$15",3)}
B=Wd[-1]
SC=[("Осторожный",10,B["cpa"]*1.05),("Базовый",12,B["cpa"]),("С правками",14,B["cpa"]*0.95)]

CSS="""
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@500;600&family=Fira+Sans:wght@400;500;600;700&display=swap');
:root{
--bg:#F8FAFC;--card:#FFFFFF;--fg:#1E3A8A;--ink:#0F172A;--muted:#E9EEF6;--mfg:#475569;
--border:#DBEAFE;--primary:#1E40AF;--secondary:#3B82F6;--accent:#D97706;--bad:#DC2626;
--good:#059669;color-scheme:light}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.55 'Fira Sans',-apple-system,sans-serif;-webkit-font-smoothing:antialiased}
.w{max-width:960px;margin:0 auto;padding-block:32px 80px;
padding-left:max(18px,env(safe-area-inset-left,0px));padding-right:max(18px,env(safe-area-inset-right,0px))}
h1{font-size:30px;margin:0 0 6px;letter-spacing:-.8px;font-weight:700;color:var(--ink)}
.lead{color:var(--mfg);font-size:14px;margin:0 0 30px}
h2{font-size:13px;letter-spacing:1.4px;text-transform:uppercase;color:var(--primary);
font-weight:700;margin:40px 0 14px}
.card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:22px 24px}
.kpi{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px}
.kc{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:16px 18px}
.kc .v{font:600 27px/1.1 'Fira Code',monospace;letter-spacing:-1px;color:var(--ink)}
.kc .l{font-size:12.5px;color:var(--mfg);margin-top:6px}
.kc .d{font:600 12.5px 'Fira Sans';margin-top:7px}
.up{color:var(--good)}.dn{color:var(--bad)}
svg{width:100%;height:auto;display:block}
.vl{font:600 12px 'Fira Code',monospace;fill:var(--ink);text-anchor:middle}
.vs{font:600 11px 'Fira Code',monospace;fill:var(--accent);text-anchor:middle}
.cl{font:500 12px 'Fira Sans';fill:var(--mfg);text-anchor:middle}
.al{font:11px 'Fira Code',monospace;fill:var(--mfg);text-anchor:end}
.mk{font:500 9.5px 'Fira Sans';fill:var(--accent);text-anchor:middle}
.gl{stroke:var(--border);stroke-width:1}
.leg{display:flex;gap:20px;flex-wrap:wrap;font-size:13px;color:var(--mfg);margin-top:14px}
.leg i{width:12px;height:12px;border-radius:3px;display:inline-block;margin-right:7px;vertical-align:-1px}
table{border-collapse:collapse;width:100%;font-size:14px}
.tw{overflow-x:auto;background:var(--card);border:1px solid var(--border);border-radius:14px}
th,td{padding:12px 16px;text-align:left;border-bottom:1px solid var(--border);white-space:nowrap}
th{font-size:11px;text-transform:uppercase;letter-spacing:.7px;color:var(--mfg);font-weight:600;background:#FBFCFE}
tr:last-child td{border-bottom:0}
td.n,th.n{text-align:right;font-family:'Fira Code',monospace;font-size:13.5px}
.big{font:600 15px 'Fira Code',monospace}
pre{background:var(--card);border:1px solid var(--border);border-radius:14px;
padding:18px 20px;overflow-x:auto;font:500 14px/1.9 'Fira Code',monospace;
color:var(--ink);margin:0;white-space:pre-wrap;word-break:break-word}
.note{font-size:13px;color:var(--mfg);margin:12px 2px 0;line-height:1.6}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media(max-width:720px){.grid2{grid-template-columns:1fr}}
.tag{display:inline-block;font:600 11px 'Fira Sans';padding:4px 10px;border-radius:20px;
background:var(--muted);color:var(--mfg)}
.tag.g{background:#D1FAE5;color:#065F46}.tag.r{background:#FEE2E2;color:#991B1B}
"""
P=[];A=P.append

def combo(W,H=300):
    """столбики конверсий/день + линия CPA"""
    PL,PR,PT,PB=52,54,30,56; cw=W-PL-PR; chh=H-PT-PB
    vmax=max(w["vpd"] for w in Wd); vtop=((int(vmax/2)+1)*2) or 1
    cmax=max(w["cpa"] for w in Wd); ctop=((int(cmax/2)+1)*2) or 1
    n=len(Wd); gw=cw/n; bw=min(62,gw*0.44)
    o=[f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Конверсии в день и цена конверсии по неделям">']
    for i in range(5):
        y=PT+chh*i/4
        o.append(f'<line x1="{PL}" y1="{y:.1f}" x2="{W-PR}" y2="{y:.1f}" class="gl"/>')
        o.append(f'<text x="{PL-9}" y="{y+4:.1f}" class="al">{vtop*(1-i/4):.0f}</text>')
        o.append(f'<text x="{W-PR+9}" y="{y+4:.1f}" class="al" style="text-anchor:start;fill:var(--accent)">${ctop*(1-i/4):.0f}</text>')
    pts=[]
    for i,w in enumerate(Wd):
        cx=PL+gw*i+gw/2
        bh=w["vpd"]/vtop*chh; x=cx-bw/2; y=PT+chh-bh
        o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="6" fill="var(--secondary)"/>')
        o.append(f'<text x="{cx:.1f}" y="{y-9:.1f}" class="vl">{w["vpd"]:.1f}</text>')
        o.append(f'<text x="{cx:.1f}" y="{PT+chh+20:.1f}" class="cl">{w["nm"]}</text>')
        o.append(f'<text x="{cx:.1f}" y="{PT+chh+36:.1f}" class="cl" style="font-size:11px">{w["lab"]}</text>')
        pts.append((cx, PT+chh-w["cpa"]/ctop*chh))
    o.append('<polyline fill="none" stroke="var(--accent)" stroke-width="2.5" stroke-linejoin="round" points="'
             + " ".join(f"{x:.1f},{y:.1f}" for x,y in pts)+'"/>')
    for (x,y),w in zip(pts,Wd):
        lbl=f'${w["cpa"]:.2f}'; tw=len(lbl)*7.2+12
        ly=y-15
        o.append(f'<rect x="{x-tw/2:.1f}" y="{ly-12:.1f}" width="{tw:.1f}" height="17" rx="5" '
                 f'fill="#fff" stroke="var(--border)"/>')
        o.append(f'<text x="{x:.1f}" y="{ly:.1f}" class="vs">{lbl}</text>')
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#fff" stroke="var(--accent)" stroke-width="2.5"/>')
    return "".join(o)+"</svg>"

def timeline(W,H=386):
    PL,PR,PT,PB=46,16,132,46; cw=W-PL-PR; chh=H-PT-PB
    top=max(daily[d][2] for d in DAYS); top=(int(top/4)+1)*4
    n=len(DAYS); gw=cw/n; bw=min(26,gw*0.62)
    o=[f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Конверсии по дням с отметками изменений">']
    for i in range(5):
        y=PT+chh*i/4
        o.append(f'<line x1="{PL}" y1="{y:.1f}" x2="{W-PR}" y2="{y:.1f}" class="gl"/>')
        o.append(f'<text x="{PL-8}" y="{y+4:.1f}" class="al">{top*(1-i/4):.0f}</text>')
    for i,d in enumerate(DAYS):
        cx=PL+gw*i+gw/2; v=daily[d][2]
        bh=max(2,v/top*chh); y=PT+chh-bh
        col="var(--primary)" if d in MARKS else "var(--secondary)"
        o.append(f'<rect x="{cx-bw/2:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="4" fill="{col}"/>')
        o.append(f'<text x="{cx:.1f}" y="{y-7:.1f}" class="vl" style="font-size:10.5px">{v:.0f}</text>')
        o.append(f'<text x="{cx:.1f}" y="{PT+chh+18:.1f}" class="cl" style="font-size:10.5px">{d[8:10]}</text>')
        if d in MARKS:
            txt,lvl=MARKS[d]; ly=PT-108+lvl*25
            o.append(f'<line x1="{cx:.1f}" y1="{ly+8:.1f}" x2="{cx:.1f}" y2="{y-16:.1f}" '
                     f'stroke="var(--accent)" stroke-width="1.5" stroke-dasharray="3 3"/>')
            tw=len(txt)*5.4+16
            lx=min(max(cx, PL+tw/2), W-PR-tw/2)
            o.append(f'<rect x="{lx-tw/2:.1f}" y="{ly-11:.1f}" width="{tw:.1f}" height="19" rx="9" '
                     f'fill="#FEF3E2" stroke="var(--accent)" stroke-width="1"/>')
            o.append(f'<text x="{lx:.1f}" y="{ly+2:.1f}" class="mk">{e(txt)}</text>')
            o.append(f'<circle cx="{cx:.1f}" cy="{y-16:.1f}" r="3.5" fill="var(--accent)"/>')
    return "".join(o)+"</svg>"

def hbars(items,W,unit="$",H=None):
    n=len(items); rh=44; H=H or n*rh+16
    mx=max(v for _,v,_ in items) or 1
    LW=190; o=[f'<svg viewBox="0 0 {W} {H}">']
    for i,(lab,v,col) in enumerate(items):
        y=10+i*rh
        o.append(f'<text x="0" y="{y+17:.0f}" style="font:500 13px \'Fira Sans\';fill:var(--ink)">{e(lab)}</text>')
        bw=v/mx*(W-LW-80)
        o.append(f'<rect x="{LW}" y="{y+2:.0f}" width="{max(3,bw):.1f}" height="22" rx="5" fill="{col}"/>')
        o.append(f'<text x="{LW+max(3,bw)+10:.1f}" y="{y+18:.0f}" '
                 f'style="font:600 13px \'Fira Code\';fill:var(--ink)">{unit}{v:,.0f}</text>'.replace(","," "))
    return "".join(o)+"</svg>"

A('<meta name="claude:viewport-fit-sides" content="cover">')
A("<title>ДАСТО — отчёт по рекламе</title>")
A(f"<style>{CSS}</style><div class='w'>")
A("<h1>ДАСТО — куда движемся</h1>")
A("<p class='lead'>6–28 октября 2026 · четыре недели · в аккаунте ничего не менял</p>")

w1,w4=Wd[0],Wd[-1]
A("<div class='kpi'>")
for v,l,d,cls in [(f"{w4['vpd']:.1f}","заявок в день",f"было {w1['vpd']:.1f}","up"),
                  (M(w4['cpa']),"цена заявки",f"было {M(w1['cpa'])}","up"),
                  (f"{w4['cvr']:.1f}%","конверсия из клика",f"было {w1['cvr']:.1f}%","up"),
                  (M0(w4['cpd']),"расход в день","почти не менялся","")]:
    A(f"<div class='kc'><div class='v'>{v}</div><div class='l'>{l}</div>"
      f"<div class='d {cls}'>{d}</div></div>")
A("</div>")

A("<h2>Четыре недели</h2><div class='card'>")
A(combo(880))
A("<div class='leg'><span><i style='background:var(--secondary)'></i>заявок в день</span>"
  "<span><i style='background:var(--accent)'></i>цена заявки</span></div>")
A("</div>")
A("<div class='tw' style='margin-top:14px'><table><tr><th>Неделя</th><th class='n'>Расход</th>"
  "<th class='n'>Клики</th><th class='n'>Заявки</th><th class='n'>В день</th>"
  "<th class='n'>Цена заявки</th><th class='n'>Конверсия</th></tr>")
for w in Wd:
    last = w is Wd[-1]
    A(f"<tr><td>{w['nm']} · {w['lab']}</td><td class='n'>{M0(w['cost'])}</td>"
      f"<td class='n'>{w['clicks']}</td><td class='n'>{w['conv']:.0f}</td>"
      f"<td class='n big'>{w['vpd']:.1f}</td><td class='n big'>{M(w['cpa'])}</td>"
      f"<td class='n'>{w['cvr']:.1f}%</td></tr>")
A("</table></div>")
A(f"<p class='note'>Расход держится около {M0(Wd[1]['cost'])} в неделю, а заявок стало в "
  f"{w4['vpd']/w1['vpd']:.1f} раза больше. Неделя 4 — это два дня, 27 и 28 октября.</p>")

A("<h2>Что меняли и когда</h2><div class='card'>")
A(timeline(880))
A("<p class='note' style='margin-top:16px'>Синим отмечены дни, когда менялись настройки. "
  "21 октября — бюджет Развала. 23 октября — переход на «Максимум конверсий». "
  "26 октября — снижение целевой цены. 27 октября — бюджет По маркам.</p>")
A("</div>")
A("<div class='tw' style='margin-top:14px'><table><tr><th>Дата</th><th>Кампания</th>"
  "<th>Что сделали</th><th class='n'>Было → стало</th><th>Результат</th></tr>")
for d,c,wha,val,res,cls in [
 ("21.10","Развал-схождение","дневной бюджет","$5 → $10","объём не вырос","r"),
 ("23.10","Регулировка, Развал, Проточка","перевод на «Максимум конверсий»","— → $2,50","+60% заявок за неделю","g"),
 ("26.10","Регулировка фар","целевая цена заявки","$2,50 → $1,70","3,0 → 6,0 в день","g"),
 ("27.10","Регулировка фар","целевая цена заявки","$1,70 → $1,60","6,0 → 2,0 в день","r"),
 ("27.10","СТО — По маркам","дневной бюджет","$10 → $15","7,0 → 4,5 в день","r")]:
    A(f"<tr><td>{d}</td><td>{e(c)}</td><td>{e(wha)}</td><td class='n'>{val}</td>"
      f"<td><span class='tag {cls}'>{res}</span></td></tr>")
A("</table></div>")

A("<h2>Куда ушли деньги впустую</h2>")
A("<div class='card'>")
A(hbars([("Кампании без заявок",EMPTY,"var(--bad)"),
         ("Переплата за компьютеры",PCW,"var(--bad)"),
         ("Запросы под минус-слова",MINUS,"var(--accent)")],880))
A("</div>")
A("<div class='kpi' style='margin-top:14px'>")
for v,l in [(M0(EMPTY+PCW+MINUS),"впустую за 4 недели"),
            (f"{(EMPTY+PCW+MINUS)/TOTAL*100:.0f}%","от всего расхода"),
            (M0(TOTAL),"потрачено всего"),
            (f"{(EMPTY+PCW+MINUS)/w4['cpa']:.0f}","заявок можно было купить")]:
    A(f"<div class='kc'><div class='v'>{v}</div><div class='l'>{l}</div></div>")
A("</div>")
A("<p class='note'>Кампании «Ремонт ДВС» и «Ремонт глушителя» — "
  f"{M0(EMPTY)} и ноль заявок, уже остановлены. Компьютеры: переплата считается как разница "
  "между их ценой заявки и мобильной.</p>")

A("<h2>Прогноз на следующую неделю</h2><div class='card'>")
mx=max(s[1] for s in SC)
PLn,W2n,PTn,PBn=52,880,26,54; chn=250-PTn-PBn
o=[f'<svg viewBox="0 0 {W2n} 250">']
top=((int(mx*5/10)+1)*10)
cw=W2n-PLn-20; gw=cw/len(SC); bw=min(90,gw*0.5)
for i in range(5):
    y=PTn+chn*i/4
    o.append(f'<line x1="{PLn}" y1="{y:.1f}" x2="{W2n-20}" y2="{y:.1f}" class="gl"/>')
    o.append(f'<text x="{PLn-9}" y="{y+4:.1f}" class="al">{top*(1-i/4):.0f}</text>')
COLS=["#93C5FD","var(--secondary)","var(--primary)"]
for i,(nm,vpd,cpa) in enumerate(SC):
    tot=vpd*5; cx=PLn+gw*i+gw/2; bh=tot/top*chn; y=PTn+chn-bh
    o.append(f'<rect x="{cx-bw/2:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="7" fill="{COLS[i]}"/>')
    o.append(f'<text x="{cx:.1f}" y="{y-10:.1f}" class="vl" style="font-size:15px">{tot:.0f}</text>')
    o.append(f'<text x="{cx:.1f}" y="{PTn+chn+20:.1f}" class="cl">{e(nm)}</text>')
    o.append(f'<text x="{cx:.1f}" y="{PTn+chn+37:.1f}" class="cl" style="font-size:11px">'
             f'{vpd} в день · {M(cpa)}</text>')
A("".join(o)+"</svg>")
A("</div>")
A("<div class='tw' style='margin-top:14px'><table><tr><th>Сценарий</th>"
  "<th class='n'>Заявок в день</th><th class='n'>За 5 дней</th><th class='n'>Цена заявки</th>"
  "<th class='n'>Расход</th><th>На чём основан</th></tr>")
BASES=["ниже текущего темпа, если правки 27-го не откатить",
       "текущий темп недели 4 без изменений",
       "вернуть целевую цену $1,70 и бюджет $10, убрать компьютеры"]
for (nm,vpd,cpa),b in zip(SC,BASES):
    A(f"<tr><td>{e(nm)}</td><td class='n big'>{vpd}</td><td class='n big'>{vpd*5}</td>"
      f"<td class='n'>{M(cpa)}</td><td class='n'>{M0(vpd*5*cpa)}</td><td>{e(b)}</td></tr>")
A("</table></div>")
A("<p class='note'>Прогноз строится от недели 4: 11 заявок в день при цене $2,53. "
  "Это два дня наблюдений, поэтому разброс сценариев широкий.</p>")

A("<h2>Минус-слова — скопировать и вставить</h2>")
A("<p class='note' style='margin-top:0;margin-bottom:12px'>Проверил каждое на заявки за 4 недели. "
  "Эти шесть ничего не убьют — по ним ноль заявок за весь период.</p>")
A("<pre>" + "\n".join(s[0] for s in SAFE) + "</pre>")
A("<div class='tw' style='margin-top:14px'><table><tr><th>Слово</th>"
  "<th class='n'>Запросов</th><th class='n'>Расход за 4 недели</th><th class='n'>Заявок</th></tr>")
for nm,cnt,c in SAFE:
    A(f"<tr><td>{e(nm)}</td><td class='n'>{cnt}</td><td class='n'>{M(c)}</td>"
      f"<td class='n' style='color:var(--good)'>0</td></tr>")
A(f"<tr><td><b>Итого</b></td><td class='n'><b>{sum(s[1] for s in SAFE)}</b></td>"
  f"<td class='n'><b>{M(sum(s[2] for s in SAFE))}</b></td><td class='n'><b>0</b></td></tr>")
A("</table></div>")
A("<h2 style='font-size:12px;margin-top:26px'>А эти минусовать нельзя</h2>")
A("<div class='tw'><table><tr><th>Слово</th><th class='n'>Заявок по нему</th><th>Почему</th></tr>")
for nm,cv in RISKY:
    why={"стоимость":"«стоимость диагностики подвески» — 1 заявка",
         "рядом":"«развал схождение рядом» — 2 заявки",
         "бесплатно":"«диагностика подвески минск бесплатно» — 1 заявка"}[nm]
    A(f"<tr><td>{e(nm)}</td><td class='n' style='color:var(--bad)'>{cv}</td><td>{e(why)}</td></tr>")
A("</table></div>")

A("<h2>Что делать на этой неделе</h2>")
A("<div class='grid2'>")
A("<div class='card'><div style='font:600 15px \"Fira Sans\";margin-bottom:10px'>Откатить</div>"
  "<table style='font-size:14px'>"
  "<tr><td style='border:0;padding:6px 0'>Регулировка фар</td>"
  "<td class='n' style='border:0;padding:6px 0'>$1,60 → $1,70</td></tr>"
  "<tr><td style='border:0;padding:6px 0'>СТО — По маркам</td>"
  "<td class='n' style='border:0;padding:6px 0'>$15 → $10</td></tr></table>"
  "<p class='note'>Обе правки 27 октября совпали с просадкой.</p></div>")
A("<div class='card'><div style='font:600 15px \"Fira Sans\";margin-bottom:10px'>Отключить</div>"
  "<table style='font-size:14px'>"
  "<tr><td style='border:0;padding:6px 0'>Компьютеры</td>"
  f"<td class='n' style='border:0;padding:6px 0'>−{M0(PCW/4)}/нед</td></tr>"
  "<tr><td style='border:0;padding:6px 0'>6 минус-слов</td>"
  f"<td class='n' style='border:0;padding:6px 0'>−{M0(MINUS/4)}/нед</td></tr></table>"
  "<p class='note'>Освободится около $22 в неделю — это 9 заявок по текущей цене.</p></div>")
A("</div>")
A("<p class='note'>Менять по одной вещи за раз и мерить неделю. "
  "Правка 27 октября показала, что десять центов целевой цены меняют объём втрое.</p>")
A("</div>")

body="\n".join(P)
os.makedirs(OUT,exist_ok=True)
open(os.path.join(OUT,"report3_artifact.html"),"w",encoding="utf-8").write(body)
stand=('<!doctype html><html lang="ru"><head><meta charset="utf-8">'
 '<meta name="viewport" content="width=device-width,initial-scale=1">'
 + body.replace('<meta name="claude:viewport-fit-sides" content="cover">\n','',1)
       .replace("<div class='w'>","</head><body><div class='w'>",1)+"</body></html>")
open(os.path.join(OUT,"report3.html"),"w",encoding="utf-8").write(stand)
print("байт:",len(body))
print(f"слив: пустые кампании {EMPTY:.2f} + ПК {PCW:.2f} + минус {MINUS:.2f} = {EMPTY+PCW+MINUS:.2f} из {TOTAL:.2f}")
