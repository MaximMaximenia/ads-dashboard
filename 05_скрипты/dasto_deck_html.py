# -*- coding: utf-8 -*-
"""Та же презентация, но HTML-слайдами. Только чтение."""
import json, os, html, statistics as st
from collections import defaultdict
SRC=os.path.expanduser("~/Desktop/Реклама/01_google_ads/dasto_clean.json")
OUT=os.path.expanduser("~/Desktop/Реклама/dashboard")
D=json.load(open(SRC)); e=html.escape; DAYS=14
def M(x): return f"${x:,.2f}".replace(","," ")
def CPA(c,v): return M(c/v) if v else "—"

camps={c["camp"]:c for c in D["camp"] if c["cost"]>0}
TOTC=sum(c["cost"] for c in camps.values()); TOTK=sum(c["clicks"] for c in camps.values())
TOTV=sum(c["conv"] for c in camps.values())
daily=defaultdict(lambda:[0,0,0.0])
for r in D["camp_daily"]:
    x=daily[r["date"]]; x[0]+=r["cost"]; x[1]+=r["clicks"]; x[2]+=r["conv"]
DATES=sorted(daily)
dev=defaultdict(lambda:{"cost":0,"clicks":0,"conv":0.0})
for r in D["dev_daily"]:
    x=dev[r["dev"]]; x["cost"]+=r["cost"]; x["clicks"]+=r["clicks"]; x["conv"]+=r["conv"]
pc,mb=dev["DESKTOP"],dev["MOBILE"]; MOB=mb["cost"]/mb["conv"]
byh=defaultdict(lambda:[0,0,0.0])
for r in D["hour"]:
    x=byh[r["k"]]; x[0]+=r["cost"]; x[1]+=r["clicks"]; x[2]+=r["conv"]
byd=defaultdict(list)
for r in D["dow_daily"]: byd[r["dow"]].append(r)
dead=sorted([k for k in D["keywords"] if k["conv"]==0 and k["cost"]>=2],key=lambda x:-x["cost"])
DEADC=sum(k["cost"] for k in dead)
lp_bad=[k for k in D["keywords"] if k.get("lp")=="BELOW_AVERAGE" and k["cost"]>0]
LPC=sum(k["cost"] for k in lp_bad)
QS=st.mean([k["qs"] for k in D["keywords"] if k["qs"]])

CSS="""
:root{--bg:#eceef1;--card:#fff;--ink:#16181d;--mute:#6b7280;--line:#e3e6ea;
--acc:#1a73e8;--good:#137333;--bad:#c5221f;--warn:#b06000;--soft:#f4f6f8}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){
--bg:#0f1114;--card:#1b1e24;--ink:#e8eaed;--mute:#9aa0a6;--line:#2c3038;
--acc:#8ab4f8;--good:#81c995;--bad:#f28b82;--warn:#fdd663;--soft:#232730;color-scheme:dark}}
:root[data-theme=dark]{--bg:#0f1114;--card:#1b1e24;--ink:#e8eaed;--mute:#9aa0a6;--line:#2c3038;
--acc:#8ab4f8;--good:#81c995;--bad:#f28b82;--warn:#fdd663;--soft:#232730;color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
.deck{max-width:1180px;margin:0 auto;
padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));
padding-block:20px 60px;display:flex;flex-direction:column;gap:20px}
.s{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:26px 30px;
min-height:580px;display:flex;flex-direction:column;position:relative}
.s.title{background:#14161a;border-color:#14161a;justify-content:center;min-height:460px}
.tag{font-size:11px;font-weight:700;letter-spacing:1.2px;color:var(--acc);margin:0 0 6px}
h2{font-size:25px;margin:0 0 6px;letter-spacing:-.4px;line-height:1.2}
.sub{font-size:11.5px;color:var(--mute);margin:0 0 16px;padding-bottom:12px;border-bottom:1px solid var(--line)}
.num{position:absolute;right:22px;top:20px;font-size:12px;color:var(--mute)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin:0 0 16px}
.kpi{background:var(--soft);border-radius:10px;padding:12px 14px}
.kpi .v{font-size:21px;font-weight:650;letter-spacing:-.5px}
.kpi .l{font-size:11px;color:var(--mute);margin-top:3px}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.cols3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px}
@media(max-width:760px){.cols,.cols3{grid-template-columns:1fr}}
.box{background:var(--soft);border-left:3px solid var(--acc);border-radius:9px;padding:13px 16px}
.box.g{border-color:var(--good)}.box.b{border-color:var(--bad)}.box.w{border-color:var(--warn)}
.box h4{margin:0 0 7px;font-size:13.5px}
.box ul{margin:0;padding-left:17px}.box li{margin:5px 0;font-size:12.5px;line-height:1.45}
.tw{overflow-x:auto;border:1px solid var(--line);border-radius:10px;margin:8px 0}
table{border-collapse:collapse;width:100%;font-size:12.5px}
th,td{padding:7px 10px;border-bottom:1px solid var(--line);white-space:nowrap;text-align:left}
th{font-size:10.5px;text-transform:uppercase;letter-spacing:.4px;color:var(--mute);font-weight:500;background:var(--soft)}
tr:last-child td{border-bottom:0}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}
.bad{color:var(--bad)}.good{color:var(--good)}.warn{color:var(--warn)}
.chart{width:100%;height:auto;display:block;margin:4px 0}
.bv{font-size:10.5px;fill:var(--ink);text-anchor:middle;font-weight:600}
.bl{font-size:10px;fill:var(--mute);text-anchor:middle}
.note{font-size:11.5px;color:var(--mute);margin:8px 0 0}
.leg{display:flex;gap:16px;font-size:11.5px;color:var(--mute);margin:4px 0 0}
.leg i{width:10px;height:10px;border-radius:2px;display:inline-block;margin-right:5px}
.sp{flex:1}
"""
def bars(items,h=140,color="var(--acc)",fmt=None,unit=""):
    if not items: return ""
    mx=max(v for _,v,_ in items) or 1
    n=len(items); w=max(26,min(72,int(900/n))); gap=9
    W=n*(w+gap); H=h+50
    o=[f'<svg viewBox="0 0 {W} {H}" class="chart">']
    for i,(lab,val,sub) in enumerate(items):
        bh=max(2,val/mx*h); x=i*(w+gap); y=h-bh
        col=color(val) if callable(color) else color
        o.append(f'<rect x="{x}" y="{y:.1f}" width="{w}" height="{bh:.1f}" rx="3" fill="{col}"/>')
        t=fmt(val) if fmt else (f"{val:.0f}" if val>=10 else f"{val:.1f}")
        o.append(f'<text x="{x+w/2}" y="{y-5:.1f}" class="bv">{t}{unit}</text>')
        o.append(f'<text x="{x+w/2}" y="{h+16}" class="bl">{e(lab)}</text>')
        if sub: o.append(f'<text x="{x+w/2}" y="{h+31}" class="bl">{e(sub)}</text>')
    return "".join(o)+"</svg>"
def grouped(cats,series,h=150):
    mx=max(max(v) for _,v,_ in series) or 1
    n=len(cats); k=len(series); bw=16; gw=k*bw+16
    W=n*gw; H=h+46
    o=[f'<svg viewBox="0 0 {W} {H}" class="chart">']
    for ci,c in enumerate(cats):
        for si,(nm,vals,col) in enumerate(series):
            v=vals[ci]; bh=max(1.5,v/mx*h); x=ci*gw+si*bw+8; y=h-bh
            o.append(f'<rect x="{x}" y="{y:.1f}" width="{bw-3}" height="{bh:.1f}" rx="2" fill="{col}"/>')
            o.append(f'<text x="{x+(bw-3)/2}" y="{y-4:.1f}" class="bv" style="font-size:9px">{v:.0f}</text>')
        o.append(f'<text x="{ci*gw+gw/2}" y="{h+17}" class="bl">{e(c)}</text>')
    return "".join(o)+"</svg>"
S=[]; N=[0]
def slide(tag,title,body,sub=None):
    N[0]+=1
    S.append(f"<section class='s'><div class='num'>{N[0]}</div>"
             f"<p class='tag'>{e(tag)}</p><h2>{e(title)}</h2>"
             f"<p class='sub'>{e(sub or 'ДАСТО — СТО · 6–23.10.2026 · 14 рабочих дней · в аккаунте ничего не менял')}</p>"
             f"{body}</section>")
def kpi(items):
    return "<div class='kpis'>"+"".join(
        f"<div class='kpi'><div class='v {c or ''}'>{v}</div><div class='l'>{e(l)}</div></div>"
        for v,l,c in items)+"</div>"
def box(t,lines,cls=""):
    return (f"<div class='box {cls}'><h4>{e(t)}</h4><ul>"
            + "".join(f"<li>{l}</li>" for l in lines)+"</ul></div>")
def tbl(rows,align=None):
    o=["<div class='tw'><table>"]
    for ri,r in enumerate(rows):
        o.append("<tr>")
        for ci,c in enumerate(r):
            cls=""; txt=c
            if isinstance(c,tuple): txt,cls=c
            a="n" if (align and ci in align) else ""
            tag="th" if ri==0 else "td"
            o.append(f"<{tag} class='{a} {cls}'>{txt}</{tag}>")
        o.append("</tr>")
    return "".join(o)+"</table></div>"

S.append("<section class='s title'>"
 "<p class='tag' style='color:#8ab4f8'>GOOGLE ADS / ДАСТО — СТО</p>"
 "<h2 style='font-size:40px;color:#fff;margin:6px 0 10px'>Разбор рекламы</h2>"
 "<p style='font-size:17px;color:#9aa0a6;margin:0 0 6px'>6–23 октября 2026 · 14 рабочих дней</p>"
 "<p style='font-size:12.5px;color:#6b7280;margin:0'>аукцион · устройства · часы · ключи · качество · расчёт прироста</p>"
 "<div class='sp'></div>"
 "<p style='font-size:11px;color:#6b7280;margin:0'>Подготовлено 24.10.2026 · в аккаунте ничего не менял</p></section>")

slide("ДАННЫЕ","Почему окно — с 6 октября, а не за месяц",
 box("Учёт конверсий менялся — периоды несравнимы",[
  "До 1 октября конверсией считались <b>page_view</b> и <b>scroll_75</b> из GA4: 24 сентября было <b>53,7 «конверсии» на 45 кликов</b>.",
  "С 6 октября остались только осмысленные действия: «Исходящий клик» (клик по номеру), инстаграм, вайбер, телеграм.",
  "За 24.09–23.10 суммарно: page_view 230,3 · Исходящий клик 88,0 · scroll_75 17,1 · остальное 24,0.",
  "Поэтому всё ниже считается с 6 по 23 октября. Сравнений с сентябрём в отчёте нет — они были бы ложными."],"b")
 + box("Что ещё учтено",[
  "14 рабочих дней: 6–9, 12–16, 19–23 октября. Реклама идёт только по будням с 9 до 19.",
  "Конверсия = клик по номеру или мессенджеру. Это не звонок: часть кликов звонком не заканчивается.",
  "Расчёты прироста — оценка при сохранении текущих CTR, конверсии и цены клика. Не гарантия.",
  "Доля показов и потери — из API по дням. Имена конкурентов API не отдаёт."])
 + "<p class='note'>Там, где наблюдений мало, это написано прямо.</p>")

slide("ГЛАВНОЕ","Что показали 14 дней",
 kpi([(f"{TOTV:.0f}","конверсий",None),(M(TOTC),"расход",None),(CPA(TOTC,TOTV),"цена конверсии",None),
      (f"{TOTK}","кликов",None),(M(TOTC/TOTK),"цена клика",None)])
 + "<div class='cols'>"
 + box("Подтвердилось данными",[
   "<b>Компьютеры:</b> 186 кликов за 14 дней дали 3 конверсии. Конверсия 1,61% против 10,21% на телефонах.",
   "<b>Часы 13–16</b> дают конверсию 11–13%, часы 9–10 и 17–18 — 4–7%.",
   "<b>Развал-схождение</b> теряет 43,9% показов из-за бюджета при потере по рангу 4,5%.",
   f"<b>110 ключей из 256</b> с посадочной ниже среднего, на них {M(LPC)} из {M(TOTC)}.",
   f"<b>{len(dead)} ключа</b> потратили {M(DEADC)} и не дали ни одной конверсии."],"g")
 + box("Не подтвердилось — проверял, снимаю",[
   "«Настройка фар дублирует Регулировку фар» — <b>неверно</b>. Разные формулировки: регулировка / настройка / коррекция. Пересечений в ключах нет.",
   "«Ключи без слова минск конвертят хуже» — на всей выборке разницы нет: <b>8,87% против 8,54%</b>. Внутри одной группы выглядело убедительно, на 256 ключах — шум.",
   "«Понедельник проваливается» — наблюдений <b>всего два</b>. Вынесено в гипотезы, вывода здесь нет."],"w")
 + "</div>")

slide("ПО ДНЯМ","Конверсии по дням",
 bars([(d[8:10]+"."+d[5:7], daily[d][2], CPA(daily[d][0],daily[d][2])) for d in DATES],
      color=lambda v:"var(--good)" if v>=10 else "var(--acc)")
 + tbl([["Дата","Конверсии","Расход","Цена конв.","Клики","Цена клика"]]
   + [[d[8:10]+"."+d[5:7],f"{daily[d][2]:.0f}",M(daily[d][0]),CPA(daily[d][0],daily[d][2]),
       str(daily[d][1]),M(daily[d][0]/daily[d][1]) if daily[d][1] else "—"] for d in DATES],
   align={1,2,3,4,5})
 + "<p class='note'>6–9 октября в среднем 3 конверсии в день, 13–23 октября — 8,8. Рост совпал с накоплением данных у стратегий.</p>")

rows=[["Кампания","Расход","Клики","Конв.","Цена конв.","Доля","Потеря: бюджет","Потеря: ранг"]]
for c in sorted(camps.values(), key=lambda x:-x["cost"]):
    z="bad" if c["conv"]==0 else ""
    rows.append([e(c["camp"]),M(c["cost"]),str(c["clicks"]),(f"{c['conv']:.0f}",z),
                 (CPA(c["cost"],c["conv"]),z),f"{c['is']:.1f}%",
                 (f"{c['lost_b']:.1f}%","bad" if c["lost_b"]>25 else ""),
                 (f"{c['lost_r']:.1f}%","bad" if c["lost_r"]>35 else "")])
slide("КАМПАНИИ","Все кампании за 14 дней",
 tbl(rows,align={1,2,3,4,5,6,7})
 + box("Что читается",[
   "<b>Ремонт ДВС и Ремонт глушителя:</b> 59 кликов, 0 конверсий, $51,21. Обе уже остановлены.",
   "<b>СТО — По маркам:</b> лучшая цена конверсии $2,74, при этом теряет 18,8% по бюджету и 37,3% по рангу.",
   "<b>Развал-схождение:</b> потеря по рангу всего 4,5% — объявления и ставка в порядке, упирается только в деньги."]))

act=sorted([c for c in camps.values() if c["conv"]>0 or c["cost"]>20], key=lambda x:-x["lost_b"])
slide("АУКЦИОН","Где теряем показы: бюджет против ранга",
 grouped([c["camp"][:15] for c in act],
   [("Получено",[c["is"] for c in act],"var(--good)"),
    ("Бюджет",[c["lost_b"] for c in act],"var(--bad)"),
    ("Ранг",[c["lost_r"] for c in act],"var(--mute)")])
 + "<div class='leg'><span><i style='background:var(--good)'></i>получено показов</span>"
   "<span><i style='background:var(--bad)'></i>потеря из-за бюджета</span>"
   "<span><i style='background:var(--mute)'></i>потеря из-за ранга</span></div>"
 + "<div class='cols' style='margin-top:14px'>"
 + box("Лечится деньгами",[
   "<b>Развал-схождение</b> — 43,9% потерь по бюджету, по рангу 4,5%.",
   "<b>СТО — По маркам</b> — 18,8% по бюджету при лучшей цене конверсии в аккаунте."],"b")
 + box("Лечится качеством",[
   "<b>СТО — Общая:</b> 63,1% потерь по рангу, доля показов 24,7%.",
   "<b>Ремонт подвески:</b> 37,9% по рангу, цена конверсии $7,24 — худшая среди работающих."],"w")
 + "</div>")

RUD={"MOBILE":"Телефоны","DESKTOP":"Компьютеры","TABLET":"Планшеты"}
slide("УСТРОЙСТВА","Компьютеры: 186 кликов, 3 конверсии",
 kpi([(f"{pc['clicks']}","кликов с компьютеров",None),(f"{pc['conv']:.0f}","конверсии","bad"),
      (f"{pc['conv']/pc['clicks']*100:.2f}%","конверсия","bad"),
      (M(pc['cost']/pc['conv']),"цена конверсии","bad"),(M(pc['cost']),"потрачено",None)])
 + "<div class='cols'>"
 + ("<div>"+bars([("Телефоны",mb["conv"]/mb["clicks"]*100,None),
                  ("Компьютеры",pc["conv"]/pc["clicks"]*100,None)],
                 color=lambda v:"var(--good)" if v>5 else "var(--bad)",
                 fmt=lambda v:f"{v:.2f}",unit="%")
    +"<p class='note'>Конверсия из клика, %</p></div>")
 + tbl([["Устройство","Расход","Клики","Конв.","Конверсия","Цена конв."]]
   + [[RUD.get(k,k),M(v["cost"]),str(v["clicks"]),
       (f"{v['conv']:.0f}","bad" if k=="DESKTOP" else ""),
       (f"{v['conv']/v['clicks']*100:.2f}%" if v["clicks"] else "—","bad" if k=="DESKTOP" else ""),
       (CPA(v["cost"],v["conv"]),"bad" if k=="DESKTOP" else "")]
      for k,v in sorted(dev.items(),key=lambda x:-x[1]["cost"])],align={1,2,3,4,5})
 + "</div>"
 + box("Расчёт",[
   f"За 14 дней на компьютеры ушло <b>{M(pc['cost'])}</b> и получено <b>{pc['conv']:.0f} конверсии</b>. "
   f"Те же деньги на телефонах по цене {M(MOB)} дали бы <b>{pc['cost']/MOB:.1f} конверсий</b>.",
   f"Чистый прирост при переносе: <b>+{pc['cost']/MOB-pc['conv']:.1f} конверсий за 14 дней</b>, "
   f"то есть <b>+{(pc['cost']/MOB-pc['conv'])/DAYS*5:.1f} в неделю</b>. Выборка 14 дней, паттерн устойчив."],"g"))

hs=[h for h in sorted(byh) if byh[h][1]>0]
slide("ЧАСЫ","Конверсия по часам: провал утром и после 17",
 bars([(f"{h}", byh[h][2]/byh[h][1]*100, CPA(byh[h][0],byh[h][2])) for h in hs],
      color=lambda v:"var(--good)" if v>=10 else ("var(--bad)" if v<5 else "var(--acc)"),
      fmt=lambda v:f"{v:.1f}",unit="%")
 + tbl([["Час","Клики","Конверсии","Конверсия","Расход","Цена конв."]]
   + [[f"{h}:00",str(byh[h][1]),
       (f"{byh[h][2]:.0f}","good" if byh[h][2]/byh[h][1]*100>=10 else ("bad" if byh[h][2]/byh[h][1]*100<5 else "")),
       (f"{byh[h][2]/byh[h][1]*100:.2f}%","good" if byh[h][2]/byh[h][1]*100>=10 else ("bad" if byh[h][2]/byh[h][1]*100<5 else "")),
       M(byh[h][0]),CPA(byh[h][0],byh[h][2])] for h in hs],align={1,2,3,4,5})
 + f"<p class='note'>13–16 часов: конверсия 11–13%. 9–10 и 17–18: 4–7%. "
   f"18:00 — 24 клика и ноль конверсий за все 14 дней, расход {M(byh[18][0])}.</p>")

ORD=["MONDAY","TUESDAY","WEDNESDAY","THURSDAY","FRIDAY"]
RUW={"MONDAY":"Пн","TUESDAY":"Вт","WEDNESDAY":"Ср","THURSDAY":"Чт","FRIDAY":"Пт"}
pres=[k for k in ORD if k in byd]
slide("ДНИ НЕДЕЛИ","Наблюдение, а не вывод: данных мало",
 "<div class='cols'>"
 + ("<div>"+bars([(RUW[k], st.mean([x["conv"] for x in byd[k]]), f"набл. {len(byd[k])}") for k in pres],
                 color=lambda v:"var(--bad)" if v<5 else "var(--acc)",fmt=lambda v:f"{v:.1f}")
   +"<p class='note'>Среднее конверсий в день</p></div>")
 + tbl([["День","Набл.","Всего","Среднее","Разброс","Цена конв."]]
   + [[RUW[k],(str(len(byd[k])),"bad" if len(byd[k])<3 else ""),
       f"{sum(x['conv'] for x in byd[k]):.0f}",
       f"{st.mean([x['conv'] for x in byd[k]]):.1f}",
       f"{min(x['conv'] for x in byd[k]):.0f}–{max(x['conv'] for x in byd[k]):.0f}",
       CPA(sum(x['cost'] for x in byd[k]),sum(x['conv'] for x in byd[k]))] for k in pres],
   align={1,2,3,4,5})
 + "</div>"
 + box("Почему здесь нет вывода",[
   "Понедельников в выборке <b>всего два</b>: 12 и 19 октября. Оба дали по 3 конверсии при среднем 7,4 по остальным дням.",
   "Два наблюдения — это совпадение ровно настолько же, насколько закономерность. Менять ставки на основании двух дней нельзя.",
   "У остальных дней по 3 наблюдения, и разброс внутри дня больше разницы между днями: у пятницы 1–15, у вторника 3–11.",
   "Вернуться к этому через 3–4 недели, когда наблюдений станет 6–8 на день."],"w"))

slide("КЛЮЧИ","Ключи, которые потратили и не дали ничего",
 kpi([(str(len(dead)),"ключей без конверсий","bad"),(M(DEADC),"потрачено за 14 дней","bad"),
      (M(DEADC/DAYS*5),"в неделю",None),
      (f"+{DEADC/MOB/DAYS*5:.1f}","конверсий/нед при переносе","good")])
 + tbl([["Ключ","Кампания","Расход","Клики","QS"]]
   + [[e(k["kw"]),e(k["camp"]),M(k["cost"]),str(k["clicks"]),
       (str(k["qs"]) if k["qs"] else "—","bad" if k["qs"] and k["qs"]<=4 else "")] for k in dead[:16]],
   align={2,3,4})
 + "<p class='note'>Порог — расход от $2 за 14 дней. Перенос считается по текущей цене конверсии на телефонах.</p>")

bycamp=defaultdict(lambda:[0,0])
for k in lp_bad: bycamp[k["camp"]][0]+=k["cost"]; bycamp[k["camp"]][1]+=1
items=sorted(bycamp.items(), key=lambda x:-x[1][0])
slide("КАЧЕСТВО","Посадочная ниже среднего у 110 ключей из 256",
 kpi([(f"{len(lp_bad)}","ключей с LP ниже среднего","bad"),(M(LPC),"расход на них","bad"),
      (f"{LPC/TOTC*100:.0f}%","от всего расхода","bad"),(f"{QS:.2f}","средний QS",None)])
 + bars([(c[:14], v[0], f"{v[1]} ключ.") for c,v in items],
        color="var(--bad)",fmt=lambda v:f"${v:.0f}")
 + box("Что это значит",[
   "<b>LP ниже среднего</b> — оценка Google: страница, на которую ведёт ключ, слабее, чем у конкурентов по этому же запросу.",
   "Это главная причина потерь по рангу. Поднять ставку можно, но платить придётся больше за ту же позицию.",
   "Хуже всего у <b>Регулировки фар</b> ($85,45 на 12 ключей) и <b>Развала</b> ($83,98 на 13 ключей) — при том что кампании рабочие."],"w"))

FG=["Регулировка фар","Настройка фар","ПТФ и линзы"]
kwb={g:[k for k in D["keywords"] if k["group"]==g] for g in FG}
allk=sorted([k for g in FG for k in kwb[g]], key=lambda x:-x["cost"])[:12]
slide("ФАРЫ","Разбор групп: дублирования нет, проблема в одном ключе",
 "<div class='cols'>"
 + tbl([["Группа","Ключей","Расход","Клики","Конв.","Цена конв."]]
   + [[g,str(len(kwb[g])),M(sum(x["cost"] for x in kwb[g])),
       str(sum(x["clicks"] for x in kwb[g])),f"{sum(x['conv'] for x in kwb[g]):.1f}",
       CPA(sum(x["cost"] for x in kwb[g]),sum(x["conv"] for x in kwb[g]))] for g in FG],
   align={1,2,3,4,5})
 + tbl([["Ключ","Группа","Расход","Клики","Конв."]]
   + [[e(k["kw"]),e(k["group"]),M(k["cost"]),str(k["clicks"]),
       (f"{k['conv']:.1f}","bad" if k["conv"]==0 and k["cost"]>3 else "")] for k in allk],
   align={2,3,4})
 + "</div>"
 + box("Что я сказал в прошлый раз и почему это было неверно",[
   "Говорил: «Настройка фар дублирует Регулировку фар, слить в одну». Посмотрел ключи — <b>пересечений нет</b>. "
   "В Регулировке: регулировка фар, регулировка света фар, отрегулировать фары. В Настройке: настройка фар, корректировка, коррекция.",
   "Это разные формулировки одного запроса, и разделение сделано правильно: так видно, какая формулировка работает.",
   "Реальная проблема точечная: ключ <b>«корректировка фар» — $10,02, 18 кликов, ноль конверсий</b>. Это 28% расхода группы.",
   "Рядом <b>«коррекция фар минск»</b> за $9,23 дал 3,3 конверсии. Разница в одном слове, а не в группе."],"g"))

def gain(name,target):
    c=camps[name]; new=min(99.0,c["is"]+(c["lost_b"]-target)); k=new/c["is"]
    return c["clicks"]*(k-1), c["conv"]*(k-1), c["cost"]*(k-1), new
rows=[["Что делаем","Сейчас","Станет","+клики/14дн","+конв/нед","+расход/день"]]
for nm,t in [("Развал-схождение",20),("Развал-схождение",0),("СТО - По маркам",0)]:
    ac,av,acost,new=gain(nm,t)
    rows.append([f"{e(nm)}: потеря по бюджету → {t}%",f"доля {camps[nm]['is']:.1f}%",f"доля {new:.1f}%",
                 f"+{ac:.0f}",(f"+{av/DAYS*5:.1f}","good"),f"+{M(acost/DAYS)}"])
pcg=pc["cost"]/MOB-pc["conv"]
rows.append(["Отключить компьютеры",f"{pc['conv']:.0f} конв за {M(pc['cost'])}",
             f"{pc['cost']/MOB:.1f} конв","—",(f"+{pcg/DAYS*5:.1f}","good"),"0"])
rows.append([f"Убрать {len(dead)} пустых ключа",f"{M(DEADC)} в никуда",f"{DEADC/MOB:.1f} конв","—",
             (f"+{DEADC/MOB/DAYS*5:.1f}","good"),"0"])
rows.append(["Отключить показы с 18:00",f"{M(byh[18][0])}, 0 конв",f"{byh[18][0]/MOB:.1f} конв","—",
             (f"+{byh[18][0]/MOB/DAYS*5:.1f}","good"),f"−{M(byh[18][0]/DAYS)}"])
nowk=TOTV/DAYS*5
addk=pcg/DAYS*5+DEADC/MOB/DAYS*5+byh[18][0]/MOB/DAYS*5
slide("ПРИРОСТ","Сколько даст бюджет и сколько — перенос денег",
 tbl(rows,align={1,2,3,4,5})
 + box("Итог без роста бюджета",[
   f"Сейчас: <b>{nowk:.1f} конверсий в неделю</b> при расходе {M(TOTC/DAYS*5)}.",
   f"Перенос с компьютеров, пустых ключей и вечерних часов: <b>+{addk:.1f} конверсий в неделю</b> на тех же деньгах.",
   f"Это <b>{addk/nowk*100:.0f}% прироста</b>. Цена конверсии уйдёт примерно с {CPA(TOTC,TOTV)} к {M(TOTC/(TOTV+addk/5*DAYS))}.",
   "Бюджет на Развал-схождение — отдельно: +4,9 конверсий в неделю при +$5,38 в день. Это уже новые деньги.",
   "Все цифры — оценка при сохранении текущих показателей. Проверять по одному изменению за раз."],"g"))

slide("ПЛАН","По шагам, по одному изменению за раз",
 "<div class='cols3'>"
 + box("ШАГ 1 · на этой неделе",["Компьютеры: ставка −80% или отключить.","Показы с 18:00 выключить.",
     f"{len(dead)} пустых ключа в минус-слова.","Ждать неделю, остальное не трогать."],"b")
 + box("ШАГ 2 · после замера",["Развал-схождение: бюджет +30%.","Цель — потеря по бюджету ниже 20%.",
     "Следить за ценой конверсии: не выше $6.","Ещё неделя на замер."],"w")
 + box("ШАГ 3 · дольше",["Посадочные под Регулировку и Развал.","110 ключей с LP ниже среднего.",
     "Это снимет потери по рангу.","Эффект через 3–4 недели."],"")
 + "</div>"
 + box("Чего делать не нужно",[
   "Не менять ставки по дням недели: два понедельника — не основание.",
   "Не сливать группы по фарам: они разделены правильно, проблема в одном ключе.",
   "Не доливать бюджет в СТО — Общая и Ремонт подвески: там потери по рангу, деньги уйдут в ту же стену.",
   "Не менять больше одной вещи за раз — иначе не поймём, что сработало."]))

rows=[["Наблюдение","Доказательство","Наблюдений","Статус"]]
for a,b,c,st_,cl in [
 ("Компьютеры не конвертят","186 кликов → 3 конверсии, CR 1,61% против 10,21%","14 дней","подтверждено","good"),
 ("Дневной пик 13–16 часов","CR 11–13% против 4–7% утром и вечером","14 дней","подтверждено","good"),
 ("18:00 — мёртвый час","24 клика, 0 конверсий за весь период","14 дней","подтверждено","good"),
 ("Развал упирается в бюджет","потеря по бюджету 43,9%, по рангу 4,5%","14 дней","подтверждено","good"),
 ("Посадочные слабые","110 из 256 ключей с LP ниже среднего","весь период","подтверждено","good"),
 ("Понедельник слабее","2 наблюдения: 3 и 3 конверсии против 7,4","2 дня","мало данных","warn"),
 ("Группы фар дублируются","пересечений в ключах нет","—","опровергнуто","bad"),
 ("Ключи без «минск» хуже","CR 8,54% против 8,87% — разницы нет","256 ключей","опровергнуто","bad")]:
    rows.append([a,b,c,(st_,cl)])
slide("ЗАКОНОМЕРНОСТИ","Что видно в данных и насколько этому можно верить",
 tbl(rows,align={2,3})
 + "<p class='note'><b>Подтверждено</b> — паттерн держится все 14 дней и разница больше внутридневного разброса. "
   "<b>Мало данных</b> — наблюдений меньше трёх, решение откладывается. "
   "<b>Опровергнуто</b> — проверил и не нашёл основания, вывод снят.</p>")

body=('<meta name="claude:viewport-fit-sides" content="cover">\n'
      "<title>ДАСТО — разбор рекламы</title>\n"
      f"<style>{CSS}</style>\n<div class='deck'>"+ "".join(S) + "</div>")
os.makedirs(OUT,exist_ok=True)
open(os.path.join(OUT,"dasto_deck_artifact.html"),"w",encoding="utf-8").write(body)
stand=('<!doctype html><html lang="ru"><head><meta charset="utf-8">'
  '<meta name="viewport" content="width=device-width,initial-scale=1">'
  + body.replace('<meta name="claude:viewport-fit-sides" content="cover">\n','',1)
        .replace("<div class='deck'>","</head><body><div class='deck'>",1) + "</body></html>")
open(os.path.join(OUT,"dasto_deck.html"),"w",encoding="utf-8").write(stand)
print("слайдов:", len(S), "| размер:", len(body), "байт")
