"""Отчёт по ДАСТО в HTML. Только чтение."""
import json, os, html, datetime
SNAP=os.path.expanduser("~/Desktop/Реклама/01_google_ads/dasto_deep.json")
OUTDIR=os.path.expanduser("~/Desktop/Реклама/dashboard")
D=json.load(open(SNAP)); e=html.escape
RATE=3.3  # BYN за 1 USD, ориентир

def money(x): return f"${x:,.2f}".replace(","," ")
def byn(x): return f"{x*RATE:,.0f} Br".replace(","," ")
def pct(x): return f"{x:.1f}%"
def cv(x): return f"{x:.0f}" if abs(x-round(x))<0.01 else f"{x:.1f}"
def cpa(c,v): return money(c/v) if v else "—"

def bars(items, unit="", h=150, color="var(--accent)", fmt=None):
    """items: [(label, value, подпись|None)]"""
    if not items: return ""
    mx=max(v for _,v,_ in items) or 1
    w=max(34, min(70, int(760/len(items))))
    gap=8; W=len(items)*(w+gap); H=h+54
    p=[f'<svg viewBox="0 0 {W} {H}" class="chart" role="img">']
    for i,(lab,val,sub) in enumerate(items):
        bh=max(2, val/mx*h); x=i*(w+gap); y=h-bh
        col=color(val) if callable(color) else color
        p.append(f'<rect x="{x}" y="{y:.1f}" width="{w}" height="{bh:.1f}" rx="3" fill="{col}"/>')
        txt=fmt(val) if fmt else (f"{val:.0f}" if val>=10 else f"{val:.1f}")
        p.append(f'<text x="{x+w/2}" y="{y-5:.1f}" class="bv">{txt}{unit}</text>')
        p.append(f'<text x="{x+w/2}" y="{h+16}" class="bl">{e(lab)}</text>')
        if sub: p.append(f'<text x="{x+w/2}" y="{h+32}" class="bs">{e(sub)}</text>')
    p.append("</svg>")
    return "".join(p)

CSS="""
:root{--bg:#f6f7f9;--card:#fff;--ink:#16181d;--mute:#6b7280;--line:#e3e6ea;
--accent:#1a73e8;--good:#137333;--bad:#c5221f;--warn:#b06000;--soft:#e8f0fe}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){
--bg:#14161a;--card:#1c1f25;--ink:#e8eaed;--mute:#9aa0a6;--line:#2c3038;
--accent:#8ab4f8;--good:#81c995;--bad:#f28b82;--warn:#fdd663;--soft:#243043;color-scheme:dark}}
:root[data-theme=dark]{--bg:#14161a;--card:#1c1f25;--ink:#e8eaed;--mute:#9aa0a6;--line:#2c3038;
--accent:#8ab4f8;--good:#81c995;--bad:#f28b82;--warn:#fdd663;--soft:#243043;color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:1000px;margin:0 auto;padding-block:28px 72px;
padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
h1{font-size:26px;margin:0 0 4px;letter-spacing:-.4px}
h2{font-size:19px;margin:38px 0 12px;padding-top:18px;border-top:1px solid var(--line)}
h3{font-size:15px;margin:22px 0 8px}
.sub{color:var(--mute);font-size:13px;margin:0 0 22px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:0 0 8px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:13px 15px}
.kpi .v{font-size:22px;font-weight:600;letter-spacing:-.4px}
.kpi .l{color:var(--mute);font-size:12px;margin-top:3px}
.kpi .d{font-size:12px;margin-top:4px}
.up{color:var(--good)}.down{color:var(--bad)}
.tw{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:12px;margin:10px 0}
table{border-collapse:collapse;width:100%;font-size:13.5px}
th,td{padding:9px 12px;text-align:left;border-bottom:1px solid var(--line);white-space:nowrap}
th{color:var(--mute);font-weight:500;font-size:11.5px;text-transform:uppercase;letter-spacing:.4px}
tr:last-child td{border-bottom:0}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}
.chart{width:100%;height:auto;display:block;margin:6px 0 2px}
.bv{font-size:11px;fill:var(--ink);text-anchor:middle;font-weight:600}
.bl{font-size:10.5px;fill:var(--mute);text-anchor:middle}
.bs{font-size:9.5px;fill:var(--mute);text-anchor:middle}
.box{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin:10px 0}
.box.hl{border-left:3px solid var(--accent);background:var(--soft)}
.box.warn{border-left:3px solid var(--warn)}
.box.bad{border-left:3px solid var(--bad)}
.box p{margin:6px 0}
.box h4{margin:0 0 6px;font-size:14.5px}
.note{color:var(--mute);font-size:12.5px;margin:6px 2px}
ul{margin:8px 0;padding-left:20px}li{margin:4px 0}
.pill{font-size:11px;padding:2px 8px;border-radius:999px;background:var(--line);color:var(--mute)}
.pill.g{background:rgba(19,115,51,.15);color:var(--good)}
.pill.r{background:rgba(197,34,31,.13);color:var(--bad)}
footer{color:var(--mute);font-size:12.5px;margin-top:44px;border-top:1px solid var(--line);padding-top:14px}
"""

def esc(s): return e(str(s))
P=[]
A=P.append
A('<meta name="claude:viewport-fit-sides" content="cover">')
A("<title>ДАСТО — разбор недели</title>")
A(f"<style>{CSS}</style><div class='wrap'>")
A("<h1>ДАСТО — разбор недели</h1>")
A(f"<p class='sub'>17–23 октября 2026, отдельно пятница 23-го · собрано {datetime.datetime.now():%d.%m.%Y в %H:%M}</p>")

# --- агрегаты
def T(rows):
    return (sum(r["cost"] for r in rows), sum(r["clicks"] for r in rows),
            sum(r["conv"] for r in rows))
cw,kw,vw=T(D["camp_week"]); cp,kp,vp=T(D["camp_prev_week"]); cf,kf,vf=T(D["camp_friday"])
dv=lambda a,b:(a-b)/b*100 if b else 0

A("<h2>Итог недели</h2>")
A("<div class='kpis'>")
for v,l,d_ in [(money(cw),"расход",f"{dv(cw,cp):+.0f}% к прошлой"),
               (cv(vw),"обращений",f"{dv(vw,vp):+.0f}% к прошлой"),
               (cpa(cw,vw),"цена обращения",f"{dv(cw/vw if vw else 0, cp/vp if vp else 1):+.0f}%"),
               (str(kw),"кликов",f"{dv(kw,kp):+.0f}%")]:
    cls="up" if d_.startswith("+") else "down"
    if "цена" in l: cls="down" if d_.startswith("+") else "up"
    A(f"<div class='kpi'><div class='v'>{v}</div><div class='l'>{l}</div>"
      f"<div class='d {cls}'>{d_}</div></div>")
A("</div>")
A(f"<p class='note'>Прошлая неделя 10–16 октября: {money(cp)}, {cv(vp)} обращений, "
  f"цена обращения {cpa(cp,vp)}. Реклама идёт только по будням с 9 до 19.</p>")

# --- пятница
A("<h2>Пятница 23 октября — лучший день за всё время</h2>")
A("<div class='kpis'>")
for v,l in [(money(cf),"расход за день"),(cv(vf),"обращений"),(cpa(cf,vf),"цена обращения"),(str(kf),"кликов")]:
    A(f"<div class='kpi'><div class='v'>{v}</div><div class='l'>{l}</div></div>")
A("</div>")
A("<div class='box hl'><h4>Что произошло</h4>"
  "<p>В пятницу четыре кампании переведены на «Максимум конверсий» с целевой ценой, "
  "двум другим выставлен предельный клик. Результат: расход упал на четверть, "
  "а обращений стало вдвое больше обычного.</p>"
  f"<p><b>Цена обращения {cpa(cf,vf)}</b> против {cpa(cw,vw)} в среднем за неделю — "
  "почти вдвое дешевле.</p></div>")

# --- по дням
A("<h3>Обращения по дням</h3>")
daily={}
for r in D["camp_daily"]:
    x=daily.setdefault(r["date"],[0,0,0.0]); x[0]+=r["cost"]; x[1]+=r["clicks"]; x[2]+=r["conv"]
days=sorted(daily)[-10:]
A(bars([(d[8:10]+"."+d[5:7], daily[d][2], money(daily[d][0]/daily[d][2]) if daily[d][2] else "—")
        for d in days], color=lambda v: "var(--good)" if v>=12 else "var(--accent)"))
A("<p class='note'>Снизу — цена обращения за день. Выходных нет: реклама по будням.</p>")
A("<h3>Расход по дням</h3>")
A(bars([(d[8:10]+"."+d[5:7], daily[d][0], None) for d in days],
       color="var(--mute)", fmt=lambda v:f"${v:.0f}"))

# --- кампании
A("<h2>Кампании</h2>")
BID={"MAXIMIZE_CONVERSIONS":"Максимум конверсий","TARGET_SPEND":"Максимум кликов",
     "MAXIMIZE_CONVERSION_VALUE":"Максимум ценности","MANUAL_CPC":"Ручной CPC"}
A("<h3>Неделя 17–23 октября</h3><div class='tw'><table><tr>"
  "<th>Кампания</th><th>Стратегия</th><th class='n'>Бюджет</th><th class='n'>Расход</th>"
  "<th class='n'>Клики</th><th class='n'>Обращ.</th><th class='n'>Цена обращ.</th>"
  "<th class='n'>Доля показов</th></tr>")
for c in sorted(D["camp_week"], key=lambda x:-x["cost"]):
    if c["cost"]==0 and c["status"]!="ENABLED": continue
    A(f"<tr><td>{esc(c['name'])}</td><td><span class='pill'>{BID.get(c['bid'],c['bid'])}</span></td>"
      f"<td class='n'>{money(c['budget'])}</td><td class='n'>{money(c['cost'])}</td>"
      f"<td class='n'>{c['clicks']}</td><td class='n'>{cv(c['conv'])}</td>"
      f"<td class='n'>{cpa(c['cost'],c['conv'])}</td><td class='n'>{pct(c['is'])}</td></tr>")
A("</table></div>")

A("<h3>Пятница 23 октября</h3><div class='tw'><table><tr>"
  "<th>Кампания</th><th class='n'>Расход</th><th class='n'>Клики</th>"
  "<th class='n'>Обращ.</th><th class='n'>Цена обращ.</th><th class='n'>Доля показов</th></tr>")
for c in sorted(D["camp_friday"], key=lambda x:-x["cost"]):
    if c["cost"]==0: continue
    A(f"<tr><td>{esc(c['name'])}</td><td class='n'>{money(c['cost'])}</td>"
      f"<td class='n'>{c['clicks']}</td><td class='n'>{cv(c['conv'])}</td>"
      f"<td class='n'>{cpa(c['cost'],c['conv'])}</td><td class='n'>{pct(c['is'])}</td></tr>")
A("</table></div>")

# --- потери
paused=[c for c in D["camp_week"] if c["cost"]>0 and c["status"]!="ENABLED"]
if paused:
    A("<div class='box bad'><h4>Внимание: реклама сейчас выключена</h4>"
      f"<p>На момент сбора данных все {len(paused)} работавших кампаний стоят на паузе — "
      "их выключили в пятницу вечером, между 18:22 и 18:33. "
      "Суббота и воскресенье всё равно выходные по расписанию, но "
      "<b>в понедельник утром их надо включить обратно</b>, иначе день пропадёт.</p></div>")
A("<h2>Статистика аукциона: где теряем показы</h2>")
camps=[c for c in D["camp_week"] if c["cost"]>0]
A("<h3>Потери из-за бюджета — лечатся деньгами</h3>")
A(bars([(c["name"][:14], c["lost_b"], None) for c in sorted(camps,key=lambda x:-x["lost_b"])],
       unit="%", color=lambda v:"var(--bad)" if v>25 else ("var(--warn)" if v>10 else "var(--mute)"),
       fmt=lambda v:f"{v:.0f}"))
A("<h3>Потери из-за рейтинга — лечатся качеством и ставкой</h3>")
A(bars([(c["name"][:14], c["lost_r"], None) for c in sorted(camps,key=lambda x:-x["lost_r"])],
       unit="%", color=lambda v:"var(--bad)" if v>45 else ("var(--warn)" if v>30 else "var(--mute)"),
       fmt=lambda v:f"{v:.0f}"))
A("<div class='box warn'><h4>Читается так</h4>"
  "<p><b>Развал-схождение</b> теряет 31% показов из-за бюджета — единственная кампания, "
  "которой реально не хватает денег.</p>"
  "<p><b>СТО — Общая</b> теряет 63% из-за рейтинга. Это не про деньги: объявления и "
  "посадочная слабее конкурентов, Google ставит ниже.</p>"
  "<p>В пятницу потери из-за бюджета у всех упали до нуля — «Максимум конверсий» "
  "сам снизил охват и стал выбирать.</p></div>")

# --- группы
A("<h2>Группы объявлений</h2>")
gw=[g for g in D["group_week"] if g["cost"]>0]
A("<div class='tw'><table><tr><th>Кампания</th><th>Группа</th><th class='n'>Расход</th>"
  "<th class='n'>Клики</th><th class='n'>Обращ.</th><th class='n'>Цена обращ.</th>"
  "<th class='n'>Доля</th><th class='n'>Потеря: ранг</th><th class='n'>Верх страницы</th></tr>")
for g in sorted(gw, key=lambda x:-x["cost"]):
    bad=" style='color:var(--bad)'" if g["conv"]==0 and g["cost"]>2 else ""
    A(f"<tr><td>{esc(g['camp'])}</td><td{bad}>{esc(g['group'])}</td>"
      f"<td class='n'>{money(g['cost'])}</td><td class='n'>{g['clicks']}</td>"
      f"<td class='n'>{cv(g['conv'])}</td><td class='n'>{cpa(g['cost'],g['conv'])}</td>"
      f"<td class='n'>{pct(g['is'])}</td><td class='n'>{pct(g['lost_r'])}</td>"
      f"<td class='n'>{pct(g['top_is'])}</td></tr>")
A("</table></div>")
dead=[g for g in gw if g["conv"]==0 and g["cost"]>2]
A(f"<p class='note'>Красным — группы с расходом выше $2 и без единого обращения. "
  f"Их {len(dead)}, суммарно {money(sum(g['cost'] for g in dead))} за неделю.</p>")

# --- устройства
A("<h2>Находка недели: компьютеры</h2>")
dev=sorted(D["dev"], key=lambda x:-x["cost"])
A(bars([(d["dev"], d["cost"]/d["conv"] if d["conv"] else 0, f"{cv(d['conv'])} обращ.") for d in dev if d["cost"]>1],
       color=lambda v:"var(--bad)" if v>10 else "var(--good)", fmt=lambda v:f"${v:.2f}" if v else "—"))
A("<div class='box bad'><h4>Компьютеры съедают деньги впустую</h4>")
pc=next((d for d in dev if d["dev"]=="Компьютеры"), None)
mob=next((d for d in dev if d["dev"]=="Телефоны"), None)
if pc and mob:
    A(f"<p>С компьютеров: <b>{money(pc['cost'])}</b> за 11 дней, {pc['clicks']} кликов, "
      f"<b>{cv(pc['conv'])} обращения</b>. Цена обращения <b>{cpa(pc['cost'],pc['conv'])}</b>.</p>"
      f"<p>С телефонов: {money(mob['cost'])}, {mob['clicks']} кликов, {cv(mob['conv'])} обращений, "
      f"цена обращения {cpa(mob['cost'],mob['conv'])}.</p>"
      f"<p><b>Разница в {pc['cost']/pc['conv']/(mob['cost']/mob['conv']):.0f} раз.</b> "
      f"В пересчёте на месяц с компьютеров уходит около {money(pc['cost']/11*30)} "
      f"и приносит 5–6 обращений.</p>")
A("</div>")

# --- часы и дни
A("<h2>Когда звонят</h2>")
A("<h3>По часам</h3>")
hrs=[h for h in D["hours"] if h["clicks"]>0]
A(bars([(f"{h['hour']}", h["conv"], cpa(h["cost"],h["conv"])) for h in hrs],
       color=lambda v:"var(--good)" if v>=11 else ("var(--bad)" if v<3 else "var(--accent)")))
A("<p class='note'>Снизу — цена обращения в этот час.</p>")
A("<h3>По дням недели</h3>")
dow=sorted(D["dow"], key=lambda x:-x["conv"])
A(bars([(d["day"][:3], d["conv"], cpa(d["cost"],d["conv"])) for d in dow],
       color=lambda v:"var(--good)" if v>=18 else ("var(--bad)" if v<5 else "var(--accent)")))
A("<div class='box warn'><h4>Два провала</h4>"
  "<p><b>Понедельник</b> — 3 обращения на $31,78, цена $10,56. Худший день недели "
  "с четырёхкратным отрывом. При этом расход как в обычный день.</p>"
  "<p><b>После 17:00</b> — с 17 до 19 часов уходит $24 и приходит 2 обращения. "
  "Сервис закрывается в 19, последний час работает вхолостую.</p></div>")


# --- ЭКОНОМИКА
A("<h2>Экономика: сколько реклама съедает от чека</h2>")
PRICES=[("Регулировка света фар",40,0.5,"Регулировка фар",4.44),
        ("3D развал-схождение, 1 ось",60,1.0,"Развал-схождение",6.33),
        ("Проточка тормозных дисков",45,1.0,"Проточка тормозных дисков",None),
        ("Замена амортизаторов",86,1.5,None,None),
        ("Сайлентблоки передних рычагов",120,2.0,None,None),
        ("Замена комплекта ГРМ",240,3.0,None,None)]
A("<h3>Выручка на час работы поста</h3>")
A(bars([(n[:16], p/t, f"{p:.0f} Br") for n,p,t,_,_ in PRICES],
       color=lambda v:"var(--good)" if v>=75 else "var(--accent)", fmt=lambda v:f"{v:.0f}"))
A("<p class='note'>В рублях за час. Время работ — оценка, точных норм у меня нет. "
  "Цены с сайта, «от», без запчастей.</p>")

A("<h3>Что остаётся от чека после рекламы</h3>")
A("<div class='tw'><table><tr><th>Услуга</th><th class='n'>Чек</th>"
  "<th class='n'>Цена обращения</th><th class='n'>Цена клиента</th>"
  "<th class='n'>Реклама от чека</th><th class='n'>Остаётся</th></tr>")
for name,price,hrs_,camp,cpa_usd in PRICES:
    if not cpa_usd: continue
    c_byn=cpa_usd*RATE; client=c_byn*2   # доезд 50%
    share=client/price*100
    cls=" style='color:var(--bad)'" if share>60 else (" style='color:var(--warn)'" if share>40 else "")
    A(f"<tr><td>{esc(name)}</td><td class='n'>{price} Br</td>"
      f"<td class='n'>{c_byn:.0f} Br</td><td class='n'>{client:.0f} Br</td>"
      f"<td class='n'{cls}>{share:.0f}%</td><td class='n'>{price-client:.0f} Br</td></tr>")
A("</table></div>")
A("<div class='box bad'><h4>Главная цифра всего отчёта</h4>"
  "<p>При чеке 40–60 рублей реклама съедает <b>две трети выручки за работу</b>. "
  "Это если из двух обращений доезжает один — реального коэффициента у нас нет, "
  "и это первое, что надо посчитать.</p>"
  "<p>Вывод неприятный, но важный: <b>снижать цену клика дальше почти некуда</b>. "
  "Рычаг не в рекламе, а в среднем чеке.</p></div>")

A("<div class='box hl'><h4>Где искать прибыль</h4>"
  "<p><b>1. Допродажа на посту.</b> Человек приехал на регулировку фар за 40 рублей — "
  "это 40 минут и всё. Если тут же предложить развал-схождение, чек становится 100, "
  "а реклама из 73% превращается в 29%. Привлечение уже оплачено, вторая работа "
  "достаётся бесплатно.</p>"
  "<p><b>2. Бесплатная диагностика подвески — это не расход, а воронка.</b> "
  "На сайте она указана как акция. Значит кампания «Ремонт подвески» ведёт людей "
  "на бесплатную услугу, и вся экономика там решается тем, сколько из них "
  "остаются на ремонт. Если конверсия в ремонт выше 30% — кампанию надо не резать, "
  "а наращивать.</p>"
  "<p><b>3. Марки — самая выгодная история.</b> У «СТО — По маркам» обращение стоит "
  "8,7 рубля, а работы там дорогие: ГРМ 240, ГБЦ 600, подвеска от 120. "
  "Это кампания с лучшей экономикой в аккаунте, и она упирается не в бюджет, "
  "а в рейтинг.</p></div>")

# --- ВЫВОДЫ
A("<h2>Что делать</h2>")
A("<div class='box'><h4>Сразу, без обсуждений</h4><ul>"
  "<li><b>Компьютеры — понизить ставку на 80–90% или отключить.</b> "
  "Экономия около 130 долларов в месяц при потере 5–6 обращений, "
  "каждое из которых стоит 24 доллара.</li>"
  "<li><b>Отключить показы с 18:00.</b> Последний час даёт ноль обращений "
  "и забирает деньги.</li>"
  "<li><b>Группа «Настройка фар» — 15,46 доллара за неделю, цена обращения 11,59.</b> "
  "Рядом «Регулировка фар» с ценой 3,65. Группы по сути об одном. "
  "Слить в одну или урезать слабую.</li></ul></div>")

A("<div class='box'><h4>Наращивать</h4><ul>"
  "<li><b>СТО — По маркам.</b> Лучшая цена обращения и самые дорогие работы. "
  "Потери из-за бюджета всего 3%, из-за рейтинга 39% — значит добавлять надо "
  "не деньги, а качество: объявления под конкретные марки. "
  "Самые слабые: Toyota (доля 30%), Audi (38%), Volkswagen (42%).</li>"
  "<li><b>Развал-схождение.</b> Единственная кампания с реальным бюджетным голодом — "
  "теряет 31% показов из-за денег. Здесь прибавка бюджета даст рост сразу.</li></ul></div>")

A("<div class='box'><h4>Проверить</h4><ul>"
  "<li><b>Понедельник.</b> Три обращения на 31,78 доллара при обычном расходе. "
  "Либо совпадение, либо что-то системное — нужны ещё две недели наблюдений.</li>"
  "<li><b>Коэффициент доезда.</b> Сколько обращений превращается в заезд на пост. "
  "Без этой цифры вся экономика выше построена на допущении 50%.</li>"
  "<li><b>Средний чек по кампаниям.</b> Если «По маркам» даёт чек 150–200, "
  "а «Регулировка фар» 40, то бюджеты надо перераспределять в пользу марок, "
  "даже при одинаковой цене обращения.</li></ul></div>")

A("<div class='box warn'><h4>Про «Максимум конверсий»</h4>"
  "<p>Пятничный результат отличный, но <b>один день — не доказательство</b>. "
  "В пятницу кампании включались и выключались несколько раз, работали не весь день. "
  "Плюс обычный эффект новизны: первые дни после смены стратегии система "
  "часто показывает лучший результат, чем потом.</p>"
  "<p>Смотреть надо на следующей неделе целиком. Если цена обращения удержится "
  "ниже трёх долларов — переводить остальные кампании. "
  "Если вернётся к четырём — значит это была случайность.</p></div>")

A(f"</div><footer>Данные из Google Ads API, аккаунт ДАСТО — СТО (400-166-4019). "
  f"Цены услуг — с сайта dasto.by. Пересчёт в рубли по курсу {RATE} Br за доллар, "
  f"это ориентир, а не точный курс дня.</footer>")

os.makedirs(OUTDIR, exist_ok=True)
body="\n".join(P)

# автономная версия — открывается файлом и в гите
stand = ('<!doctype html><html lang="ru"><head><meta charset="utf-8">'
         '<meta name="viewport" content="width=device-width,initial-scale=1">'
         + body.replace('<meta name="claude:viewport-fit-sides" content="cover">\n','',1)
               .replace("<div class='wrap'>","</head><body><div class='wrap'>",1)
         + "</body></html>")
f1=os.path.join(OUTDIR,"dasto.html"); open(f1,"w",encoding="utf-8").write(stand)
# версия для публикации по ссылке — оболочку добавляет платформа
f2=os.path.join(OUTDIR,"dasto_artifact.html"); open(f2,"w",encoding="utf-8").write(body)
print("Готово:", f1, len(stand), "байт")
print("Готово:", f2, len(body), "байт")
