# -*- coding: utf-8 -*-
import json, os, html
from collections import defaultdict, Counter
D=json.load(open(os.path.expanduser("~/Desktop/Реклама/01_google_ads/dasto_deep2.json")))
OUT=os.path.expanduser("~/Desktop/Реклама/dashboard"); e=html.escape
def M(x): return f"${x:,.2f}".replace(","," ")
def CPA(c,v): return M(c/v) if v else "—"

W1=("2026-10-20","2026-10-26"); W2=("2026-10-27","2026-10-28")
def win(a,b):
    o=defaultdict(lambda:[0.0,0,0,0.0]); d=set()
    for r in D["daily"]:
        if a<=r["d"]<=b:
            d.add(r["d"]); x=o[r["camp"]]
            x[0]+=r["cost"]; x[1]+=r["clicks"]; x[2]+=r["impr"]; x[3]+=r["conv"]
    return o,sorted(d)
A,da=win(*W1); B,db=win(*W2)
def tot(o): return [sum(v[i] for v in o.values()) for i in range(4)]
ta,tb=tot(A),tot(B)
daily=defaultdict(lambda:[0.0,0,0.0])
for r in D["daily"]:
    x=daily[r["d"]]; x[0]+=r["cost"]; x[1]+=r["clicks"]; x[2]+=r["conv"]
DAYS=sorted(daily)[-12:]
kw=D["kw"]; T=D["terms_cur"]; cur={c["camp"]:c for c in D["camp_cur"]}
dead_kw=sorted([k for k in kw if k["conv"]==0 and k["cost"]>0],key=lambda x:-x["cost"])
DEADC=sum(k["cost"] for k in dead_kw); KWC=sum(k["cost"] for k in kw)
lp_bad=[k for k in kw if k["lp"]=="BELOW_AVERAGE"]; LPC=sum(k["cost"] for k in lp_bad)
cnt={f:Counter(k[f] or "нд" for k in kw) for f in ("adrel","ctr_exp","lp")}
agg=defaultdict(lambda:[0.0,0,0.0,set()])
for t in T:
    x=agg[t["term"]]; x[0]+=t["cost"]; x[1]+=t["clicks"]; x[2]+=t["conv"]; x[3].add(t["camp"])
cand=sorted([(k,v) for k,v in agg.items() if v[2]==0 and v[0]>=0.5],key=lambda x:-x[1][0])
CANDC=sum(v[0] for _,v in cand); TERMC=sum(v[0] for v in agg.values())
bykw=defaultdict(lambda:[set(),0.0,0.0,0])
for t in T:
    if not t["kw"]: continue
    x=bykw[(t["camp"],t["kw"])]; x[0].add(t["term"]); x[1]+=t["cost"]; x[2]+=t["conv"]; x[3]+=t["clicks"]
byterm=defaultdict(list)
for t in T: byterm[t["term"]].append(t)
dup=sorted([(k,v) for k,v in byterm.items() if len({(x["camp"],x["grp"]) for x in v})>1],
           key=lambda x:-sum(y["cost"] for y in x[1]))
QS=[k["qs"] for k in kw if k["qs"]]

CSS="""
:root{--bg:#eef0f4;--card:#fff;--ink:#14171c;--mute:#6b7280;--line:#e5e8ed;
--a:#2563eb;--g:#059669;--r:#dc2626;--w:#d97706;--soft:#f6f8fb;color-scheme:light}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;-webkit-font-smoothing:antialiased}
.deck{max-width:1120px;margin:0 auto;display:flex;flex-direction:column;gap:18px;
padding-block:20px 60px;
padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.s{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:24px 28px;position:relative}
.s.t{background:#14171c;border-color:#14171c;padding:56px 32px}
.tag{font:700 10.5px/1 -apple-system;letter-spacing:1.3px;color:var(--a);margin:0 0 7px}
h2{font-size:23px;margin:0 0 5px;letter-spacing:-.4px;line-height:1.2}
.sub{font-size:11px;color:var(--mute);margin:0 0 15px;padding-bottom:11px;border-bottom:1px solid var(--line)}
.n{position:absolute;right:20px;top:18px;font-size:11.5px;color:var(--mute)}
.k{display:grid;grid-template-columns:repeat(auto-fit,minmax(125px,1fr));gap:9px;margin:0 0 14px}
.kk{background:var(--soft);border-radius:10px;padding:11px 13px}
.kk .v{font-size:20px;font-weight:650;letter-spacing:-.5px;font-variant-numeric:tabular-nums}
.kk .l{font-size:10.5px;color:var(--mute);margin-top:3px;line-height:1.3}
.c2{display:grid;grid-template-columns:1fr 1fr;gap:13px}
.c3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:13px}
@media(max-width:780px){.c2,.c3{grid-template-columns:1fr}}
.b{background:var(--soft);border-left:3px solid var(--a);border-radius:9px;padding:13px 16px}
.b.g{border-color:var(--g);background:#f0faf5}.b.r{border-color:var(--r);background:#fdf2f2}
.b.w{border-color:var(--w);background:#fdf9f0}
.b h4{margin:0 0 7px;font-size:13px}
.b ul{margin:0;padding-left:16px}.b li{margin:5px 0;font-size:12px;line-height:1.45}
.tw{overflow-x:auto;border:1px solid var(--line);border-radius:10px;margin:8px 0}
table{border-collapse:collapse;width:100%;font-size:12.5px}
th,td{padding:7px 11px;border-bottom:1px solid var(--line);white-space:nowrap;text-align:left}
th{font-size:10px;text-transform:uppercase;letter-spacing:.5px;color:var(--mute);font-weight:600;background:var(--soft)}
tr:last-child td{border-bottom:0}
td.r,th.r{text-align:right;font-variant-numeric:tabular-nums}
.bad{color:var(--r)}.good{color:var(--g)}.mute{color:var(--mute)}
svg{width:100%;height:auto;display:block;margin:4px 0}
.vl{font:600 11px -apple-system;fill:var(--ink);text-anchor:middle}
.cl{font:10.5px -apple-system;fill:var(--mute);text-anchor:middle}
.al{font:10px -apple-system;fill:var(--mute);text-anchor:end}
.gl{stroke:var(--line);stroke-width:1}
.leg{display:flex;gap:16px;font-size:11.5px;color:var(--mute);margin-top:8px;flex-wrap:wrap}
.leg i{width:10px;height:10px;border-radius:2px;display:inline-block;margin-right:5px}
.note{font-size:11.5px;color:var(--mute);margin:9px 0 0;line-height:1.5}
"""
def bars(cats,series,H=200,fmt=None,unit=""):
    mx=max(max(v) for _,v,_ in series) or 1
    step=10**max(0,len(str(int(mx)))-1); top=(int(mx/step)+1)*step or 1
    W=640; PL=42; PB=38; PT=20; ch=H-PT-PB
    n=len(cats); k=len(series); gw=(W-PL-8)/n; bw=min(26,(gw-10)/k)
    o=[f'<svg viewBox="0 0 {W} {H}">']
    for i in range(5):
        y=PT+ch*i/4
        o.append(f'<line x1="{PL}" y1="{y:.1f}" x2="{W-6}" y2="{y:.1f}" class="gl"/>')
        o.append(f'<text x="{PL-7}" y="{y+3.5:.1f}" class="al">{top*(1-i/4):,.0f}</text>'.replace(","," "))
    for ci,c in enumerate(cats):
        cx=PL+gw*ci+gw/2
        for si,(nm,vals,col) in enumerate(series):
            v=vals[ci]; bh=max(1.5,v/top*ch)
            x=cx-(k*bw)/2+si*bw; y=PT+ch-bh
            o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw-2:.1f}" height="{bh:.1f}" rx="3" fill="{col}"/>')
            t=fmt(v) if fmt else (f"{v:.0f}" if v>=10 or v==int(v) else f"{v:.1f}")
            o.append(f'<text x="{x+(bw-2)/2:.1f}" y="{y-5:.1f}" class="vl">{t}{unit}</text>')
        for li,part in enumerate(c.split("\n")):
            o.append(f'<text x="{cx:.1f}" y="{PT+ch+15+li*13:.1f}" class="cl">{e(part)}</text>')
    return "".join(o)+"</svg>"
S=[]; N=[0]
def sl(tag,title,body,sub=None):
    N[0]+=1
    S.append(f"<section class='s'><div class='n'>{N[0]}</div><p class='tag'>{e(tag)}</p>"
             f"<h2>{e(title)}</h2><p class='sub'>{e(sub or 'ДАСТО — СТО · 20–28.10.2026 · в аккаунте ничего не менял')}</p>{body}</section>")
def K(items): return "<div class='k'>"+"".join(
    f"<div class='kk'><div class='v {c or ''}'>{v}</div><div class='l'>{e(l)}</div></div>" for v,l,c in items)+"</div>"
def BX(t,lines,cls=""): return (f"<div class='b {cls}'><h4>{e(t)}</h4><ul>"
    + "".join(f"<li>{l}</li>" for l in lines)+"</ul></div>")
def TB(rows,rightcols=()):
    o=["<div class='tw'><table>"]
    for ri,r in enumerate(rows):
        o.append("<tr>")
        for ci,c in enumerate(r):
            txt,cls=(c if isinstance(c,tuple) else (c,""))
            a="r" if ci in rightcols else ""
            tg="th" if ri==0 else "td"
            o.append(f"<{tg} class='{a} {cls}'>{txt}</{tg}>")
        o.append("</tr>")
    return "".join(o)+"</table></div>"

S.append("<section class='s t'><p class='tag' style='color:#93b4fd'>GOOGLE ADS / ДАСТО — СТО</p>"
 "<h2 style='font-size:36px;color:#fff;margin:4px 0 10px'>Глубокий разбор</h2>"
 "<p style='font-size:16px;color:#9aa0a6;margin:0 0 6px'>неделя к неделе · эффект правок · ключи и запросы</p>"
 "<p style='font-size:12.5px;color:#6b7280;margin:0 0 26px'>20–28 октября 2026</p>"
 "<p style='font-size:11px;color:#6b7280;margin:0'>Подготовлено 29.10.2026 · в аккаунте ничего не менял</p></section>")

sl("НЕДЕЛИ","Конверсий столько же, но дешевле",
 K([(f"{tb[3]/len(db):.1f}","конверсий в день, эта",None),(f"{ta[3]/len(da):.1f}","было на прошлой","mute"),
    (CPA(tb[0],tb[3]),"цена конверсии","good"),(CPA(ta[0],ta[3]),"было","mute"),
    (f"{tb[3]/tb[1]*100:.1f}%","конверсия из клика","good"),(f"{ta[3]/ta[1]*100:.1f}%","было","mute")])
 + TB([["Период","Дней","Расход","Клики","Конверсии","В день","Цена конв.","Конверсия из клика"],
   [f"Прошлая {W1[0][5:]}–{W1[1][5:]}",str(len(da)),M(ta[0]),str(ta[1]),f"{ta[3]:.0f}",
    f"{ta[3]/len(da):.1f}",CPA(ta[0],ta[3]),f"{ta[3]/ta[1]*100:.1f}%"],
   [f"Эта {W2[0][5:]}–{W2[1][5:]}",str(len(db)),M(tb[0]),str(tb[1]),f"{tb[3]:.0f}",
    f"{tb[3]/len(db):.1f}",(CPA(tb[0],tb[3]),"good"),(f"{tb[3]/tb[1]*100:.1f}%","good")]],{1,2,3,4,5,6,7})
 + BX("Что это значит",[
   f"Объём держится: {ta[3]/len(da):.1f} против {tb[3]/len(db):.1f} конверсий в день.",
   f"Цена упала с {CPA(ta[0],ta[3])} до {CPA(tb[0],tb[3])}, конверсия из клика выросла с {ta[3]/ta[1]*100:.1f}% до {tb[3]/tb[1]*100:.1f}%.",
   "Кликов меньше, но они лучше — «Максимум конверсий» отсекает слабые аукционы.",
   "<b>Оговорка:</b> «эта неделя» — два дня, 27 и 28. За 29-е данных нет."],"g"))

sl("ПО ДНЯМ","Конверсии по дням",
 bars([d[8:10]+"."+d[5:7] for d in DAYS],[("конв",[daily[d][2] for d in DAYS],"var(--a)")])
 + TB([["Дата","Конверсии","Расход","Цена конв.","Клики","Конверсия из клика"]]
   + [[d[8:10]+"."+d[5:7],f"{daily[d][2]:.0f}",M(daily[d][0]),CPA(daily[d][0],daily[d][2]),
       str(daily[d][1]),f"{daily[d][2]/daily[d][1]*100:.1f}%" if daily[d][1] else "—"] for d in DAYS],{1,2,3,4,5})
 + "<p class='note'>23 и 27 октября — по 16 конверсий, максимумы. 28-е неполное: расход $21 против обычных $30–35.</p>")

KEY=[("27.10 12:52","СТО - По маркам","дневной бюджет","$10 → $15"),
     ("27.10 10:53","Регулировка фар","целевая цена конверсии","$1,70 → $1,60"),
     ("26.10 15:04","Регулировка фар","целевая цена конверсии","$2,50 → $1,70"),
     ("26.10 08:37","Ремонт подвески","перевод на «Максимум конверсий»","— → $2,00"),
     ("26.10 08:36","Развал-схождение","целевая цена конверсии","$2,50 → $2,00"),
     ("23.10 16:05","Развал-схождение","перевод на «Максимум конверсий»","— → $2,50"),
     ("23.10 08:57","Регулировка фар","перевод на «Максимум конверсий»","— → $2,50"),
     ("23.10 14:48","СТО - По маркам","предельная цена клика","$0,40 → снята"),
     ("21.10 09:58","Развал-схождение","дневной бюджет","$5 → $10")]
sl("ПРАВКИ","Что менялось в аккаунте",
 TB([["Когда","Кампания","Что изменилось","Было → стало"]]+[list(x) for x in KEY])
 + BX("Плюс ручной режим",[
   "Кампании включаются утром в 8:30–9:00 и выключаются вечером в 16:50–18:30 — каждый день вручную.",
   "<b>42 переключения статуса за 9 дней.</b> «Максимум конверсий» после каждого включения заново набирает данные.",
   "Если нужен показ 9–19, это задаётся расписанием показа, а не руками."],"w"))

def wnd(camp,a,b):
    r=[x for x in D["daily"] if x["camp"]==camp and a<=x["d"]<=b]
    if not r: return None
    days=len({x["d"] for x in r})
    return dict(cost=sum(x["cost"] for x in r),conv=sum(x["conv"] for x in r),
                vpd=sum(x["conv"] for x in r)/days)
cases=[("Регулировка фар","цена $2,50 → $1,70",("2026-10-23","2026-10-23"),("2026-10-26","2026-10-26")),
       ("Регулировка фар","затем $1,70 → $1,60",("2026-10-26","2026-10-26"),("2026-10-27","2026-10-28")),
       ("СТО - По маркам","бюджет $10 → $15",("2026-10-23","2026-10-26"),("2026-10-27","2026-10-28")),
       ("Развал-схождение","бюджет $5 → $10",("2026-10-13","2026-10-20"),("2026-10-21","2026-10-23"))]
rows=[["Кампания","Правка","Было, конв/день","Стало","Цена было","Цена стало","Итог"]]
cats=[];b4=[];af=[]
for camp,what,pre,post in cases:
    a=wnd(camp,*pre); b=wnd(camp,*post)
    if not a or not b: continue
    ok=b["vpd"]>=a["vpd"]*0.95
    rows.append([camp,what,f"{a['vpd']:.1f}",(f"{b['vpd']:.1f}","good" if ok else "bad"),
                 CPA(a["cost"],a["conv"]),CPA(b["cost"],b["conv"]),
                 ("сработало","good") if ok else ("хуже","bad")])
    cats.append(what[:18]); b4.append(a["vpd"]); af.append(b["vpd"])
sl("ЭФФЕКТ","Три правки: одна сработала, две нет",
 TB(rows,{2,3,4,5})
 + bars(cats,[("до",b4,"#9aa0a6"),("после",af,"var(--a)")],fmt=lambda v:f"{v:.1f}")
 + "<div class='leg'><span><i style='background:#9aa0a6'></i>до</span><span><i style='background:var(--a)'></i>после</span></div>"
 + BX("Читается так",[
   "Снижение целевой цены с $2,50 до $1,70 удвоило объём: 3,0 → 6,0 конверсий в день.",
   "Дальнейшее снижение до $1,60 откатило к 2,0. <b>Десять центов срезали объём втрое.</b>",
   "Бюджет СТО — По маркам до $15 объёма не дал: 7,0 → 4,5, цена с $1,77 до $3,39.",
   "Каждая правка измерена на 1–2 днях — это направление, не доказательство."],"w"))

rows=[["Кампания","Конв/день прошлая","Эта","Изменение","Цена прошлая","Цена эта","Расход эта"]]
for c in sorted(set(A)|set(B), key=lambda x:-(B.get(x,[0,0,0,0])[3])):
    a=A.get(c,[0,0,0,0.0]); b=B.get(c,[0,0,0,0.0])
    va=a[3]/len(da); vb=b[3]/len(db)
    if va==0 and vb==0: continue
    ch=(vb/va*100-100) if va else None
    rows.append([c,f"{va:.1f}",f"{vb:.1f}",
                 (f"{ch:+.0f}%","good" if (ch or 0)>0 else "bad") if ch is not None else "—",
                 CPA(a[0],a[3]),CPA(b[0],b[3]),M(b[0])])
sl("КАМПАНИИ","Кто вырос, кто просел",
 TB(rows,{1,2,3,4,5,6})
 + "<div class='c2'>"
 + BX("Выросла",[
   "<b>СТО — Общая:</b> 1,0 → 3,5 конверсии в день, цена с $3,13 до $1,38 — лучшая в аккаунте.",
   "При этом доля показов 25%, а 59% теряется из-за ранга. Кампания работает на четверти потенциала."],"g")
 + BX("Просели",[
   "<b>СТО — По маркам:</b> 5,2 → 4,5, цена $2,52 → $3,39. После повышения бюджета.",
   "<b>Регулировка фар:</b> 3,6 → 2,0, цена $2,54 → $2,79. После снижения целевой цены до $1,60.",
   "Обе просадки совпали с правками, а не предшествовали им."],"r")
 + "</div>")

act=sorted([c for c in cur.values() if c["cost"]>1],key=lambda x:-x["cost"])
sl("АУКЦИОН","Где теряем показы",
 bars([c["camp"][:13] for c in act],
   [("получено",[c["is"] for c in act],"var(--g)"),
    ("бюджет",[c["lb"] for c in act],"var(--r)"),
    ("ранг",[c["lr"] for c in act],"#9aa0a6")],unit="%")
 + "<div class='leg'><span><i style='background:var(--g)'></i>получено показов</span>"
   "<span><i style='background:var(--r)'></i>потеря из-за бюджета</span>"
   "<span><i style='background:#9aa0a6'></i>потеря из-за ранга</span></div>"
 + TB([["Кампания","Доля показов","Потеря: бюджет","Потеря: ранг","Верх страницы","Самый верх"]]
   + [[c["camp"],f"{c['is']:.0f}%",(f"{c['lb']:.0f}%","bad" if c["lb"]>15 else ""),
       (f"{c['lr']:.0f}%","bad" if c["lr"]>35 else ""),f"{c['top']:.0f}%",f"{c['abs']:.0f}%"] for c in act],
   {1,2,3,4,5})
 + "<p class='note'>Ремонт подвески: доля 15%, потеря по рангу 74% — кампания почти не показывается.</p>")

sl("КАЧЕСТВО","Объявления сильные, посадочная тянет вниз",
 K([(str(len(lp_bad)),"ключей с посадочной ниже среднего","bad"),(M(LPC),"расход на них","bad"),
    (f"{LPC/KWC*100:.0f}%","от расхода на ключи","bad"),
    (f"{sum(QS)/len(QS):.2f}","средний показатель качества",None),
    (str(cnt['adrel'].get('ABOVE_AVERAGE',0)),"объявлений выше среднего","good")])
 + bars(["объявление","ожидаемый\nCTR","посадочная"],
   [("выше",[cnt[f].get("ABOVE_AVERAGE",0) for f in ("adrel","ctr_exp","lp")],"var(--g)"),
    ("средне",[cnt[f].get("AVERAGE",0) for f in ("adrel","ctr_exp","lp")],"var(--w)"),
    ("ниже",[cnt[f].get("BELOW_AVERAGE",0) for f in ("adrel","ctr_exp","lp")],"var(--r)")])
 + "<div class='leg'><span><i style='background:var(--g)'></i>выше среднего</span>"
   "<span><i style='background:var(--w)'></i>средне</span>"
   "<span><i style='background:var(--r)'></i>ниже среднего</span></div>"
 + BX("Что показывает разбивка",[
   f"<b>Объявления:</b> выше среднего у {cnt['adrel'].get('ABOVE_AVERAGE',0)} ключей, ниже — у {cnt['adrel'].get('BELOW_AVERAGE',0)}. Тексты работают.",
   f"<b>Ожидаемый CTR:</b> выше среднего у {cnt['ctr_exp'].get('ABOVE_AVERAGE',0)} ключей. Люди кликают.",
   f"<b>Посадочная:</b> ниже среднего у {cnt['lp'].get('BELOW_AVERAGE',0)}, выше среднего — <b>ни у одного</b>. На них ушло {M(LPC)}.",
   "Это и есть причина потерь по рангу. Ставку поднять можно, но платить придётся больше за ту же позицию."],"r"))

rows=[["Ключ","Кампания","Запросов ловит","Клики","Расход","Конверсии","Цена конв."]]
for (camp,k),(terms,c,v,cl) in sorted(bykw.items(), key=lambda x:-len(x[1][0]))[:12]:
    rows.append([k,camp,(str(len(terms)),"bad" if len(terms)>=15 else ""),str(cl),M(c),
                 (f"{v:.0f}","bad" if v==0 else ""),CPA(c,v)])
sl("КЛЮЧ → ЗАПРОС","Какие ключи работают пылесосом",
 TB(rows,{2,3,4,5,6})
 + BX("Широкие ключи",[
   "<b>«автосервис»</b> собрал 109 разных запросов за $2,89 и дал 1 конверсию.",
   "<b>«развал схождение»</b> — 33 запроса, 1 конверсия. <b>«сто peugeot»</b> — 17 запросов, ноль.",
   "Это не ошибка: широкий ключ находит новые формулировки. Но его улов надо разбирать раз в неделю — "
   "удачные запросы в отдельные ключи, неудачные в минус."]))

rows=[["Запрос","Группа","Ключ","Клики","Расход","Конверсии"]]
for term,v in dup[:9]:
    first=True
    for x in sorted(v,key=lambda y:-y["cost"])[:2]:
        rows.append([term if first else "",x["grp"],(x["kw"] or "—"),str(x["clicks"]),M(x["cost"]),
                     (f"{x['conv']:.0f}","good" if x["conv"] else "mute")])
        first=False
sl("ПЕРЕСЕЧЕНИЯ","Один запрос ловят две группы",
 K([(str(len(dup)),"запросов ловят разные группы",None),
    (M(sum(sum(y['cost'] for y in v) for _,v in dup)),"их суммарный расход",None)])
 + TB(rows,{3,4,5})
 + "<p class='note'>Главный пример: «регулировка фар минск» ловится обеими группами. "
   "В «Регулировке фар» — 39 кликов и 8 конверсий, в «Настройке фар» — 2 клика и ноль.</p>")

LPRU={"BELOW_AVERAGE":"ниже среднего","AVERAGE":"средне","ABOVE_AVERAGE":"выше среднего"}
sl("КЛЮЧИ","Ключи, которые потратили и не дали ни одной заявки",
 K([(str(len(dead_kw)),"ключей без заявок","bad"),(M(DEADC),"их расход за 9 дней","bad"),
    (f"{DEADC/KWC*100:.0f}%","от расхода на ключи","bad"),
    (str(len([k for k in dead_kw if k['clicks']>=4])),"из них с 4+ кликами",None)])
 + TB([["Ключ","Кампания","Клики","Расход","Качество","Посадочная"]]
   + [[k["kw"],k["camp"],str(k["clicks"]),M(k["cost"]),
       (str(k["qs"]) if k["qs"] else "—","bad" if (k["qs"] or 9)<=4 else ""),
       LPRU.get(k["lp"],"—")] for k in dead_kw[:15]],{2,3,4})
 + "<p class='note'>Больше всех потратил <b>«настройка фар»</b>: $6,12 и 15 кликов без единой заявки — "
   "при том что соседний «регулировка фар минск» дал 8.</p>")

sl("МИНУС-СЛОВА","Добавлять почти нечего — и это важно",
 K([(str(len(cand)),"запросов без заявок",None),(M(CANDC),"их расход",None),
    (f"{CANDC/TERMC*100:.0f}%","от расхода на запросы",None),("2","паттерна для минусовки","good")])
 + "<div class='c2'>"
 + TB([["Запрос","Клики","Расход"]]+[[t,str(v[1]),M(v[0])] for t,v in cand[:13]],{1,2})
 + ("<div>" + BX("Что реально можно минусовать",[
     "<b>«рядом»</b> — 1 запрос, $0,88. Человек ищет ближайший сервис, не вас.",
     "<b>«стоимость», «цена»</b> — 2 запроса, $1,38. Спорно: в тех же формулировках есть и конверсии.",
     "Всё. Больше паттернов нет."],"g")
   + BX("Почему это хорошая новость",[
     "Остальные 35 запросов целевые: «ремонт тойота минск», «мерседес сервис минск», «3d развал схождение минск».",
     "Они не дали заявок не потому что мусорные, а потому что человек ушёл с сайта.",
     "<b>Проблема не в трафике, а в том, что после клика.</b>"]) + "</div>")
 + "</div>")

sl("ВЫВОДЫ","Что показали данные",
 BX("Три вещи, которые видно только в цифрах",[
   f"<b>Посадочная ниже среднего у {len(lp_bad)} ключей, выше среднего — ни у одного.</b> "
   f"При этом объявления выше среднего у {cnt['adrel'].get('ABOVE_AVERAGE',0)}. Разрыв между рекламой и сайтом — главный ограничитель.",
   "<b>Минусовать нечего:</b> из 38 запросов без заявок целевых 35. Трафик чистый, теряется на сайте.",
   "<b>Снижение целевой цены ниже $1,70</b> на Регулировке срезало объём втрое. "
   "<b>Повышение бюджета</b> СТО — По маркам до $15 объёма не добавило, цена выросла."])
 + "<div class='c3' style='margin-top:13px'>"
 + BX("Проверить",["Вернуть целевую цену Регулировки на $1,70.","Вернуть бюджет По маркам на $10.",
     "Мерить неделю, а не два дня."],"w")
 + BX("Даст больше всего",["Посадочные страницы.",f"{len(lp_bad)} ключей с оценкой ниже среднего.",
     "Это снимет потери по рангу — сейчас от 25% до 74%."])
 + BX("Не делать",["Не включать и не выключать кампании руками: 42 переключения за 9 дней мешают стратегии.",
     "Не искать мусор в запросах — его там нет."],"r")
 + "</div>")

sl("ДАННЫЕ","Что учтено и чего в цифрах нет",
 BX("Границы выборки",[
   "Период 20–28 октября. Данных за 29-е ещё нет. «Эта неделя» — два дня, 27 и 28.",
   "28 октября неполное: расход $21 против обычных $30–35.",
   "Конверсия = клик по номеру или мессенджеру. Это не звонок: часть кликов звонком не заканчивается.",
   "Эффект каждой правки измерен на 1–2 днях.",
   f"Показатель качества есть не у всех: у {cnt['lp'].get('нд',0)} ключей из {len(kw)} данных нет."])
 + BX("Чего здесь нет",[
   "Статистики аукциона по конкурентам — Google не отдаёт её через API, только в интерфейсе.",
   "Данных о доезде: сколько заявок стали клиентами.",
   "Среднего чека по кампаниям — с ним считалась бы выручка на доллар, а не цена заявки."],"w"))

body=('<meta name="claude:viewport-fit-sides" content="cover">\n'
 "<title>ДАСТО — глубокий разбор</title>\n"
 f"<style>{CSS}</style>\n<div class='deck'>"+"".join(S)+"</div>")
os.makedirs(OUT,exist_ok=True)
open(os.path.join(OUT,"dasto2_artifact.html"),"w",encoding="utf-8").write(body)
stand=('<!doctype html><html lang="ru"><head><meta charset="utf-8">'
 '<meta name="viewport" content="width=device-width,initial-scale=1">'
 + body.replace('<meta name="claude:viewport-fit-sides" content="cover">\n','',1)
       .replace("<div class='deck'>","</head><body><div class='deck'>",1)+"</body></html>")
open(os.path.join(OUT,"dasto2.html"),"w",encoding="utf-8").write(stand)
print("слайдов:",len(S),"| байт:",len(body))
