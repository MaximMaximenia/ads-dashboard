# -*- coding: utf-8 -*-
"""План на неделю с учётом потолка трафика."""
import os, html, json
OUT=os.path.expanduser("~/Desktop/Реклама/dashboard"); RATE=3.3; e=html.escape
# факт недели 17–23.10: расход, конверсии, доля показов, потеря бюджет, потеря ранг, доезд, чек
C=[("СТО — По маркам",   63.34,24, 58.2, 3.0,38.8,0.55,125),
   ("Регулировка фар",   48.81,11, 64.1, 4.8,31.1,0.95, 40),
   ("Развал-схождение",  31.63, 5, 56.9,31.2,12.0,0.80, 60),
   ("СТО — Общая",       12.27, 3, 24.7,12.2,63.1,0.55,125),
   ("Ремонт подвески",    5.05, 1, 21.3,50.2,28.6,0.60, 80),
   ("Проточка дисков",    3.96, 0, 57.9, 1.4,40.7,0.70, 45)]
FREE={"Компьютеры":29.14,"23 пустых ключа":36.64,"Часы после 17:00":3.10}  # $/нед
rows=[]
for n,cost,conv,isv,lb,lr,dz,price in C:
    rev1=dz*price                      # выручка с одной конверсии
    cpa=cost/conv if conv else None
    per=rev1/cpa if cpa else 0         # Br на $1 расхода
    k=(isv+lb)/isv if isv else 1       # во сколько вырастет при закрытии потерь по бюджету
    rows.append({"n":n,"cost":cost,"conv":conv,"is":isv,"lb":lb,"lr":lr,"dz":dz,
                 "price":price,"cpa":cpa,"rev1":rev1,"per":per,"k":k,
                 "add_cost":cost*(k-1),"add_conv":conv*(k-1),
                 "rev":conv*rev1,"rev_new":conv*k*rev1})
rows.sort(key=lambda r:-r["per"])
TOT=sum(r["cost"] for r in C and rows); CONV=sum(r["conv"] for r in rows)
REV=sum(r["rev"] for r in rows); REV2=sum(r["rev_new"] for r in rows)
CONV2=sum(r["conv"]*r["k"] for r in rows); ADD=sum(r["add_cost"] for r in rows)
FREED=sum(FREE.values()); LEFT=FREED-ADD
def br(x): return f"{x:,.0f}".replace(","," ")+" Br"
def us(x): return f"${x:,.2f}".replace(","," ")

CSS=open(os.path.expanduser("~/Desktop/Реклама/05_скрипты/forecast.py")).read()
CSS=CSS[CSS.index('CSS="""')+7:CSS.index('"""\n\ndef paired')]
exec(open(os.path.expanduser("~/Desktop/Реклама/05_скрипты/forecast.py")).read().split('P=[]')[0].split('CSS="""')[0])

def single(cats, vals, color="var(--a)", unit="", H=215, fmt=None):
    mx=max(vals); step=10**max(0,(len(str(int(mx)))-1)); top=(int(mx/step)+1)*step or 1
    W=620; PAD_L=46; PAD_B=42; PAD_T=22; ch=H-PAD_T-PAD_B
    n=len(cats); gw=(W-PAD_L-10)/n; bw=min(62,gw*0.5)
    o=[f'<svg viewBox="0 0 {W} {H}">']
    for i in range(5):
        y=PAD_T+ch*i/4; v=top*(1-i/4)
        o.append(f'<line x1="{PAD_L}" y1="{y:.1f}" x2="{W-8}" y2="{y:.1f}" class="gl"/>')
        o.append(f'<text x="{PAD_L-9}" y="{y+4:.1f}" class="al">{v:,.0f}</text>'.replace(","," "))
    for i,(c,v) in enumerate(zip(cats,vals)):
        cx=PAD_L+gw*i+gw/2; bh=v/top*ch; x=cx-bw/2; y=PAD_T+ch-bh
        col=color(v,i) if callable(color) else color
        o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="5" fill="{col}"/>')
        t=fmt(v) if fmt else f"{v:,.0f}{unit}".replace(","," ")
        o.append(f'<text x="{cx:.1f}" y="{y-8:.1f}" class="vl">{t}</text>')
        for k2,part in enumerate(c.split("\n")):
            o.append(f'<text x="{cx:.1f}" y="{PAD_T+ch+18+k2*15:.1f}" class="cl">{e(part)}</text>')
    return "".join(o)+"</svg>"

P=[]; A=P.append
A('<meta name="claude:viewport-fit-sides" content="cover">')
A("<title>ДАСТО — план на неделю</title>")
A(f"<style>{CSS}</style><div class='w'>")
A("<h1>План на неделю</h1>")
A("<p class='sub'>ДАСТО — СТО · база: факт 17–23 октября · перераспределение бюджета с учётом доступного трафика</p>")

A("<div class='kpis'>")
for v,l,d in [(f"{CONV2:.0f}","конверсий",f"+{CONV2-CONV:.0f}"),
              (f"{sum(r['conv']*r['k']*r['dz'] for r in rows):.0f}","клиентов",None),
              (br(REV2),"выручка",f"+{br(REV2-REV)}"),
              (us(TOT),"расход — без изменений",None),
              (f"{TOT*RATE/REV2*100:.0f}%","реклама от выручки",f"−{TOT*RATE/REV*100-TOT*RATE/REV2*100:.0f} п.п.")]:
    A(f"<div class='k'><div class='v'>{v}</div><div class='l'>{l}</div>"
      + (f"<div class='d up'>{d}</div>" if d else "") + "</div>")
A("</div>")

A("<h2>Сколько рублей приносит доллар рекламы</h2><div class='card'>")
A(single([r["n"].replace(" — ","\n").replace("-схождение","\nсхождение").replace(" дисков","\nдисков") for r in rows],
         [r["per"] for r in rows],
         color=lambda v,i:"var(--g)" if v>15 else ("var(--r)" if v<8 else "var(--a)"),
         fmt=lambda v:f"{v:.1f}" if v else "—"))
A("<p class='note'>Выручка в рублях на каждый вложенный доллар. "
  "Считается как чек × доезд ÷ цена конверсии. Это и есть порядок приоритета для бюджета.</p></div>")

A("<h2>Потолок: сколько можно добрать деньгами</h2><div class='tw'><table><tr>"
  "<th>Кампания</th><th class='n'>Доля показов</th><th class='n'>Теряем: бюджет</th>"
  "<th class='n'>Теряем: ранг</th><th class='n'>Добавить</th><th class='n'>+конверсий</th></tr>")
for r in rows:
    cls="good" if r["lb"]>10 else ("bad" if r["lb"]<5 else "")
    A(f"<tr><td>{e(r['n'])}</td><td class='n'>{r['is']:.1f}%</td>"
      f"<td class='n {cls}'>{r['lb']:.1f}%</td><td class='n'>{r['lr']:.1f}%</td>"
      f"<td class='n'>{us(r['add_cost']) if r['add_cost']>0.5 else '—'}</td>"
      f"<td class='n'>{'+'+format(r['add_conv'],'.1f') if r['add_conv']>0.1 else '—'}</td></tr>")
A(f"<tfoot><tr><td>Итого</td><td class='n'>—</td><td class='n'>—</td><td class='n'>—</td>"
  f"<td class='n'>{us(ADD)}</td><td class='n'>+{CONV2-CONV:.1f}</td></tr></tfoot></table></div>")
A("<p class='note'><b>Потеря из-за бюджета</b> — показы, которые мы не взяли, потому что кончились деньги. "
  "Только их можно выкупить, долив бюджет. <b>Потеря из-за ранга</b> деньгами не лечится: "
  "там нужны объявления и посадочная, иначе платишь больше за ту же позицию.</p>")

A("<h2>Откуда берём деньги</h2><div class='tw'><table><tr>"
  "<th>Источник</th><th class='n'>Освобождается в неделю</th></tr>")
for k,v in FREE.items():
    A(f"<tr><td>{e(k)}</td><td class='n'>{us(v)}</td></tr>")
A(f"<tfoot><tr><td>Итого</td><td class='n'>{us(FREED)}</td></tr></tfoot></table></div>")
A(f"<p class='note'>На закрытие бюджетных потерь нужно {us(ADD)}. Остаётся {us(LEFT)} — "
  f"их деньгами уже не потратить: у всех кампаний потери из-за бюджета будут закрыты.</p>")

A("<h2>Что получится по кампаниям</h2><div class='tw'><table><tr>"
  "<th>Кампания</th><th class='n'>Расход</th><th class='n'>Конверсий</th>"
  "<th class='n'>Клиентов</th><th class='n'>Выручка</th><th class='n'>Было</th></tr>")
for r in rows:
    nc=r["conv"]*r["k"]
    A(f"<tr><td>{e(r['n'])}</td><td class='n'>{us(r['cost']+r['add_cost'])}</td>"
      f"<td class='n'>{nc:.1f}</td><td class='n'>{nc*r['dz']:.1f}</td>"
      f"<td class='n'>{br(r['rev_new'])}</td><td class='n' style='color:var(--mute)'>{br(r['rev'])}</td></tr>")
A(f"<tfoot><tr><td>Итого</td><td class='n'>{us(TOT+ADD)}</td><td class='n'>{CONV2:.1f}</td>"
  f"<td class='n'>{sum(r['conv']*r['k']*r['dz'] for r in rows):.1f}</td>"
  f"<td class='n'>{br(REV2)}</td><td class='n' style='color:var(--mute)'>{br(REV)}</td></tr></tfoot></table></div>")

A("<h2>Выручка: было и станет</h2><div class='card'>")
A(single(["сейчас","после\nперераспределения","расход\nна рекламу"],[REV,REV2,TOT*RATE],
  color=lambda v,i:"var(--r)" if i==2 else ("var(--g)" if i==1 else "var(--a)"),unit=" Br",H=225))
A("</div>")

A("<h2>Что важно понимать</h2><div class='card'><ul>"
 f"<li><b>Расход не растёт.</b> {us(ADD)} берутся из освободившихся {us(FREED)}, а не из новых денег.</li>"
 f"<li><b>Больше чем на {us(ADD)} долить нельзя.</b> После этого потери из-за бюджета у всех закрыты, "
 "и лишние деньги просто не потратятся — показов в поиске столько, сколько есть.</li>"
 "<li><b>Приоритет не по цене конверсии, а по выручке.</b> Регулировка фар даёт дешёвые конверсии, "
 "но при чеке 40 Br это 8,6 Br с доллара. СТО — По маркам даёт 26 Br с доллара.</li>"
 "<li><b>Дальше упираемся в ранг.</b> У По маркам теряется 38,8% показов из-за рейтинга, у СТО — Общей 63,1%. "
 "Это следующий рубеж, и он решается объявлениями и посадочной, а не бюджетом.</li>"
 "<li><b>Конверсия — это клик по номеру</b>, не звонок. Если пятая часть не звонит, выручка ниже на 20%.</li>"
 "<li><b>Проточка дисков:</b> за неделю ноль конверсий при почти нулевом расходе. Данных нет, в план не беру.</li>"
 "</ul></div>")
A("</div>")

body="\n".join(P)
os.makedirs(OUT,exist_ok=True)
open(os.path.join(OUT,"plan_artifact.html"),"w",encoding="utf-8").write(body)
stand=('<!doctype html><html lang="ru"><head><meta charset="utf-8">'
 '<meta name="viewport" content="width=device-width,initial-scale=1">'
 + body.replace('<meta name="claude:viewport-fit-sides" content="cover">\n','',1)
       .replace("<div class='w'>","</head><body><div class='w'>",1)+"</body></html>")
open(os.path.join(OUT,"plan.html"),"w",encoding="utf-8").write(stand)
print("Выручка на $1:")
for r in rows: print(f"  {r['n']:<20} {r['per']:>5.1f} Br/$   потолок +{r['add_cost']:>5.2f}$  +{r['add_conv']:>4.1f} конв")
print(f"\nбыло {CONV} конв / {br(REV)} → станет {CONV2:.1f} конв / {br(REV2)}")
print(f"долить {us(ADD)}, освобождается {us(FREED)}, остаток {us(LEFT)}")
