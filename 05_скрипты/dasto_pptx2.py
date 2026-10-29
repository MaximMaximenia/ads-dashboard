# -*- coding: utf-8 -*-
import json, os
from collections import defaultdict, Counter
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

D=json.load(open(os.path.expanduser("~/Desktop/Реклама/01_google_ads/dasto_deep2.json")))
CH=json.load(open(os.path.expanduser("~/Desktop/Реклама/01_google_ads/changes.json")))
OUT=os.path.expanduser("~/Desktop/Реклама/03_анализ/ДАСТО_глубокий_29.10.2026.pptx")
SUB="ДАСТО — СТО · 20–28.10.2026 · в аккаунте ничего не менял"

INK=RGBColor(0x14,0x17,0x1C); MUTE=RGBColor(0x6B,0x72,0x80)
ACC=RGBColor(0x25,0x63,0xEB); BAD=RGBColor(0xDC,0x26,0x26)
GOOD=RGBColor(0x05,0x96,0x69); WARN=RGBColor(0xD9,0x77,0x06)
LINE=RGBColor(0xE5,0xE8,0xED); SOFT=RGBColor(0xF6,0xF8,0xFB); W=RGBColor(0xFF,0xFF,0xFF)

P=Presentation(); P.slide_width=Inches(13.333); P.slide_height=Inches(7.5)
BL=P.slide_layouts[6]
def tb(s,x,y,w,h,t,sz=13,b=False,c=INK,al=PP_ALIGN.LEFT):
    f=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)).text_frame
    f.word_wrap=True; f.margin_left=0;f.margin_right=0;f.margin_top=0;f.margin_bottom=0
    p=f.paragraphs[0]; p.alignment=al
    r=p.add_run(); r.text=t; r.font.size=Pt(sz); r.font.bold=b
    r.font.color.rgb=c; r.font.name="Arial"; return f
def bul(f,items,sz=11,c=INK):
    for i,t in enumerate(items):
        p=f.paragraphs[0] if i==0 else f.add_paragraph()
        p.space_after=Pt(6)
        r=p.add_run(); r.text="•  "+t; r.font.size=Pt(sz); r.font.color.rgb=c; r.font.name="Arial"
def rect(s,x,y,w,h,fill=W,ln=LINE):
    sh=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb=fill
    if ln: sh.line.color.rgb=ln; sh.line.width=Pt(0.75)
    else: sh.line.fill.background()
    sh.shadow.inherit=False; sh.adjustments[0]=0.05; return sh
def head(tag,title,sub=None):
    s=P.slides.add_slide(BL)
    s.background.fill.solid(); s.background.fill.fore_color.rgb=W
    tb(s,0.5,0.3,6,0.26,tag.upper(),9.5,True,ACC)
    tb(s,0.5,0.56,12.4,0.48,title,22,True,INK)
    tb(s,0.5,1.08,12.4,0.26,sub or SUB,9,False,MUTE)
    l=s.shapes.add_shape(1,Inches(0.5),Inches(1.38),Inches(12.33),Pt(1))
    l.fill.solid(); l.fill.fore_color.rgb=LINE; l.line.fill.background(); l.shadow.inherit=False
    return s
def kpis(s,items,y=1.6,h=0.95):
    n=len(items); g=0.14; w=(12.33-g*(n-1))/n
    for i,(v,lab,col) in enumerate(items):
        x=0.5+i*(w+g); rect(s,x,y,w,h,SOFT)
        tb(s,x+0.16,y+0.13,w-0.3,0.4,v,19,True,col or INK)
        tb(s,x+0.16,y+0.58,w-0.3,0.28,lab,8.5,False,MUTE)
def table(s,x,y,w,rows,colw=None,fs=9,hfs=8,rh=0.26):
    nr,nc=len(rows),len(rows[0])
    t=s.shapes.add_table(nr,nc,Inches(x),Inches(y),Inches(w),Inches(rh*nr)).table
    if colw:
        tot=sum(colw)
        for i,cw in enumerate(colw): t.columns[i].width=Emu(int(Inches(w)*cw/tot))
    for ri,row in enumerate(rows):
        t.rows[ri].height=Inches(rh)
        for ci,val in enumerate(row):
            c=t.cell(ri,ci); c.text=""
            c.margin_left=Inches(0.06); c.margin_right=Inches(0.06)
            c.margin_top=0; c.margin_bottom=0; c.vertical_anchor=MSO_ANCHOR.MIDDLE
            c.fill.solid(); c.fill.fore_color.rgb=SOFT if ri==0 else W
            txt,col,bo=val,INK,(ri==0)
            if isinstance(val,tuple): txt,col=val[0],val[1]; bo=(ri==0) or (len(val)>2 and val[2])
            p=c.text_frame.paragraphs[0]
            p.alignment=PP_ALIGN.LEFT if ci==0 else PP_ALIGN.RIGHT
            r=p.add_run(); r.text=str(txt); r.font.size=Pt(hfs if ri==0 else fs)
            r.font.bold=bo; r.font.color.rgb=MUTE if ri==0 else col; r.font.name="Arial"
    return t
def chart(s,x,y,w,h,cats,series,cols=None,fmt='0.0',leg=False):
    cd=CategoryChartData(); cd.categories=cats
    for nm,v in series: cd.add_series(nm,v)
    ch=s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,Inches(x),Inches(y),Inches(w),Inches(h),cd).chart
    ch.has_title=False; ch.has_legend=leg
    if leg:
        ch.legend.position=XL_LEGEND_POSITION.BOTTOM; ch.legend.include_in_layout=False
        ch.legend.font.size=Pt(8.5); ch.legend.font.color.rgb=MUTE
    pl=ch.plots[0]; pl.gap_width=60; pl.overlap=-8; pl.has_data_labels=True
    dl=pl.data_labels; dl.font.size=Pt(8); dl.font.color.rgb=INK; dl.font.bold=True
    dl.number_format=fmt; dl.number_format_is_linked=False
    dl.position=XL_LABEL_POSITION.OUTSIDE_END
    for i,sr in enumerate(ch.series):
        sr.format.fill.solid(); sr.format.fill.fore_color.rgb=(cols[i] if cols else ACC)
    ca=ch.category_axis; ca.tick_labels.font.size=Pt(8); ca.tick_labels.font.color.rgb=MUTE
    ca.format.line.color.rgb=LINE
    ch.value_axis.visible=False; ch.value_axis.has_major_gridlines=False
    return ch
def box(s,x,y,w,h,title,lines,acc=ACC,fill=SOFT,sz=10):
    rect(s,x,y,w,h,fill)
    b=s.shapes.add_shape(1,Inches(x),Inches(y),Pt(3),Inches(h))
    b.fill.solid(); b.fill.fore_color.rgb=acc; b.line.fill.background(); b.shadow.inherit=False
    tb(s,x+0.2,y+0.11,w-0.4,0.28,title,11,True,INK)
    f=tb(s,x+0.2,y+0.42,w-0.4,h-0.55,"",sz); f.paragraphs[0].runs[0].text=""
    bul(f,lines,sz)
def M(x): return f"${x:,.2f}".replace(","," ")
def CPA(c,v): return M(c/v) if v else "—"

# ---- данные
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
ta,tb_=tot(A),tot(B)
daily=defaultdict(lambda:[0.0,0,0.0])
for r in D["daily"]:
    x=daily[r["d"]]; x[0]+=r["cost"]; x[1]+=r["clicks"]; x[2]+=r["conv"]
DAYS=sorted(daily)[-12:]
kw=D["kw"]; T=D["terms_cur"]
dead_kw=sorted([k for k in kw if k["conv"]==0 and k["cost"]>0],key=lambda x:-x["cost"])
DEADC=sum(k["cost"] for k in dead_kw)
lp_bad=[k for k in kw if k["lp"]=="BELOW_AVERAGE"]
LPC=sum(k["cost"] for k in lp_bad)
agg=defaultdict(lambda:[0.0,0,0.0,set()])
for t in T:
    x=agg[t["term"]]; x[0]+=t["cost"]; x[1]+=t["clicks"]; x[2]+=t["conv"]; x[3].add(t["camp"])
cand=sorted([(k,v) for k,v in agg.items() if v[2]==0 and v[0]>=0.5],key=lambda x:-x[1][0])
CANDC=sum(v[0] for _,v in cand)
bykw=defaultdict(lambda:[set(),0.0,0.0,0])
for t in T:
    if not t["kw"]: continue
    x=bykw[(t["camp"],t["kw"])]; x[0].add(t["term"]); x[1]+=t["cost"]; x[2]+=t["conv"]; x[3]+=t["clicks"]
cur={c["camp"]:c for c in D["camp_cur"]}

# 1 титул
s=P.slides.add_slide(BL)
s.background.fill.solid(); s.background.fill.fore_color.rgb=RGBColor(0x14,0x17,0x1C)
tb(s,0.85,2.2,11,0.35,"GOOGLE ADS / ДАСТО — СТО",11,True,RGBColor(0x93,0xB4,0xFD))
tb(s,0.85,2.6,11,0.85,"Глубокий разбор",38,True,W)
tb(s,0.85,3.5,11,0.4,"неделя к неделе · эффект правок · ключи и запросы",16,False,RGBColor(0x9A,0xA0,0xA6))
tb(s,0.85,4.3,11,0.3,"20–28 октября 2026",12,False,RGBColor(0x6B,0x72,0x80))
tb(s,0.85,6.5,11,0.28,"Подготовлено 29.10.2026 · в аккаунте ничего не менял",9.5,False,RGBColor(0x6B,0x72,0x80))

# 2 недели
s=head("НЕДЕЛИ","Конверсий столько же, но дешевле")
kpis(s,[(f"{tb_[3]/len(db):.1f}","конверсий в день, эта",None),
        (f"{ta[3]/len(da):.1f}","было на прошлой",MUTE),
        (CPA(tb_[0],tb_[3]),"цена конверсии",GOOD),
        (CPA(ta[0],ta[3]),"было",MUTE),
        (f"{tb_[3]/tb_[1]*100:.1f}%","конверсия из клика",GOOD),
        (f"{ta[3]/ta[1]*100:.1f}%","было",MUTE)])
table(s,0.5,2.75,12.33,[
 ["Период","Дней","Расход","Клики","Конверсии","В день","Цена конв.","Конверсия из клика"],
 [f"Прошлая {W1[0][5:]}–{W1[1][5:]}",str(len(da)),M(ta[0]),str(ta[1]),f"{ta[3]:.0f}",
  f"{ta[3]/len(da):.1f}",CPA(ta[0],ta[3]),f"{ta[3]/ta[1]*100:.1f}%"],
 [f"Эта {W2[0][5:]}–{W2[1][5:]}",str(len(db)),M(tb_[0]),str(tb_[1]),f"{tb_[3]:.0f}",
  (f"{tb_[3]/len(db):.1f}",INK),(CPA(tb_[0],tb_[3]),GOOD,True),(f"{tb_[3]/tb_[1]*100:.1f}%",GOOD,True)],
],colw=[2.6,0.8,1.2,1,1.2,1,1.3,1.8],rh=0.34)
box(s,0.5,4.3,12.33,2.3,"Что это значит",[
 f"Объём держится: {ta[3]/len(da):.1f} против {tb_[3]/len(db):.1f} конверсий в день — разница в пределах дневного разброса.",
 f"Цена упала с {CPA(ta[0],ta[3])} до {CPA(tb_[0],tb_[3])}, конверсия из клика выросла с {ta[3]/ta[1]*100:.1f}% до {tb_[3]/tb_[1]*100:.1f}%.",
 "То есть кликов стало меньше, но они стали лучше. Это работа «Максимума конверсий»: система отсекает слабые аукционы.",
 "Оговорка: в этой неделе два дня, 27 и 28. Данных за 29-е ещё нет. Выводы предварительные.",
],GOOD,RGBColor(0xF0,0xFA,0xF5))

# 3 по дням
s=head("ПО ДНЯМ","Конверсии и расход")
chart(s,0.5,1.55,12.33,2.5,[d[8:10]+"."+d[5:7] for d in DAYS],
      [("Конверсии",[daily[d][2] for d in DAYS])],[ACC],'0')
rows=[["Дата","Конверсии","Расход","Цена конв.","Клики","Конверсия из клика"]]
for d in DAYS:
    c,k,v=daily[d]
    rows.append([d[8:10]+"."+d[5:7],f"{v:.0f}",M(c),CPA(c,v),str(k),
                 f"{v/k*100:.1f}%" if k else "—"])
table(s,0.5,4.2,12.33,rows,colw=[1.6,1.3,1.3,1.4,1.1,1.8],rh=0.215,fs=8.5)
box(s,0.5,7.0,12.33,0.4,"",[],ACC,W)
tb(s,0.5,7.0,12.33,0.3,"23 и 27 октября — по 16 конверсий, это максимумы. 28-е неполное: расход $21 против обычных $30–35.",9,False,MUTE)

# 4 изменения
s=head("ПРАВКИ","Что менялось и что из этого вышло")
rows=[["Когда","Кампания","Что изменилось","Было → стало"]]
KEY=[("27.10 12:52","СТО - По маркам","дневной бюджет","$10 → $15"),
     ("27.10 10:53","Регулировка фар","целевая цена конверсии","$1,70 → $1,60"),
     ("26.10 15:04","Регулировка фар","целевая цена конверсии","$2,50 → $1,70"),
     ("26.10 08:37","Ремонт подвески","перевод на «Максимум конверсий»","— → $2,00"),
     ("26.10 08:36","Развал-схождение","целевая цена конверсии","$2,50 → $2,00"),
     ("23.10 16:05","Развал-схождение","перевод на «Максимум конверсий»","— → $2,50"),
     ("23.10 08:57","Регулировка фар","перевод на «Максимум конверсий»","— → $2,50"),
     ("23.10 14:48","СТО - По маркам","предельная цена клика","$0,40 → снята"),
     ("21.10 09:58","Развал-схождение","дневной бюджет","$5 → $10")]
for w_,c,f_,v in KEY: rows.append([w_,c,f_,v])
table(s,0.5,1.55,12.33,rows,colw=[1.6,2.4,3.4,2.2],rh=0.32,fs=9)
box(s,0.5,5.0,12.33,1.9,"Плюс ручной режим работы",[
 "Кампании включаются утром между 8:30 и 9:00 и выключаются вечером между 16:50 и 18:30 — каждый день вручную.",
 "За 20–28 октября это 42 переключения статуса. Для «Максимума конверсий» такие паузы — помеха: "
 "стратегия заново набирает данные после каждого включения.",
 "Если нужен показ только в рабочие часы, это делается расписанием показа, а не руками.",
],WARN,RGBColor(0xFD,0xF9,0xF0))

# 5 эффект правок
s=head("ЭФФЕКТ","Три правки: одна сработала, две нет")
def wnd(camp,a,b):
    r=[daily_c for d,daily_c in [(r2["d"],r2) for r2 in D["daily"] if r2["camp"]==camp] if a<=d<=b]
    if not r: return None
    days=len({x["d"] for x in r})
    c=sum(x["cost"] for x in r); v=sum(x["conv"] for x in r)
    return dict(n=days,cost=c,conv=v,vpd=v/days,cpd=c/days,cpa=c/v if v else None)
cases=[("Регулировка фар","целевая цена $2,50 → $1,70",("2026-10-23","2026-10-23"),("2026-10-26","2026-10-26")),
       ("Регулировка фар","затем $1,70 → $1,60",("2026-10-26","2026-10-26"),("2026-10-27","2026-10-28")),
       ("СТО - По маркам","бюджет $10 → $15",("2026-10-23","2026-10-26"),("2026-10-27","2026-10-28")),
       ("Развал-схождение","бюджет $5 → $10",("2026-10-13","2026-10-20"),("2026-10-21","2026-10-23"))]
rows=[["Кампания","Правка","Было, конв/день","Стало","Было, цена","Стало","Итог"]]
cats=[]; b4=[]; af=[]
for camp,what,pre,post in cases:
    a=wnd(camp,*pre); b=wnd(camp,*post)
    if not a or not b: continue
    good = b["vpd"]>=a["vpd"]*0.95
    rows.append([camp,what,f"{a['vpd']:.1f}",(f"{b['vpd']:.1f}",GOOD if good else BAD,True),
                 CPA(a["cost"],a["conv"]),CPA(b["cost"],b["conv"]),
                 ("сработало",GOOD,True) if good else ("хуже",BAD,True)])
    cats.append(what[:22]); b4.append(a["vpd"]); af.append(b["vpd"])
table(s,0.5,1.55,12.33,rows,colw=[2.2,2.8,1.5,1.2,1.3,1.2,1.3],rh=0.33)
chart(s,0.5,3.6,12.33,2.3,cats,[("До",b4),("После",af)],[MUTE,ACC],'0.0',leg=True)
box(s,0.5,6.1,12.33,1.1,"Читается так",[
 "Снижение целевой цены с $2,50 до $1,70 удвоило объём: 3,0 → 6,0 конверсий в день. Дальнейшее снижение до $1,60 откатило обратно к 2,0.",
 "Бюджет СТО — По маркам до $15 объёма не дал: 7,0 → 4,5 конверсии в день, цена выросла с $1,77 до $3,39. Каждая правка измерена на 1–2 днях.",
],WARN,RGBColor(0xFD,0xF9,0xF0))

# 6 кампании
s=head("КАМПАНИИ","Кто вырос, кто просел")
rows=[["Кампания","Конв/день прошлая","Эта","Изменение","Цена прошлая","Цена эта","Расход эта"]]
for c in sorted(set(A)|set(B), key=lambda x:-(B.get(x,[0,0,0,0])[3])):
    a=A.get(c,[0,0,0,0.0]); b=B.get(c,[0,0,0,0.0])
    va=a[3]/len(da); vb=b[3]/len(db)
    if va==0 and vb==0: continue
    ch=(vb/va*100-100) if va else None
    chs=(f"{ch:+.0f}%",GOOD if (ch or 0)>0 else BAD,True) if ch is not None else "—"
    rows.append([c,f"{va:.1f}",f"{vb:.1f}",chs,
                 CPA(a[0],a[3]),CPA(b[0],b[3]),M(b[0])])
table(s,0.5,1.55,12.33,rows,colw=[3,1.8,1,1.3,1.4,1.3,1.3],rh=0.36)
box(s,0.5,4.2,6,2.5,"Выросла",[
 "СТО — Общая: 1,0 → 3,5 конверсии в день, цена упала с $3,13 до $1,38.",
 "Это лучшая цена конверсии в аккаунте на этой неделе.",
 "При этом доля показов всего 25%, а 59% теряется из-за ранга — "
 "то есть кампания работает на четверти своего потенциала.",
],GOOD,RGBColor(0xF0,0xFA,0xF5))
box(s,6.83,4.2,6,2.5,"Просели",[
 "СТО — По маркам: 5,2 → 4,5, цена $2,52 → $3,39. Это после повышения бюджета.",
 "Регулировка фар: 3,6 → 2,0, цена $2,54 → $2,79. Это после снижения целевой цены до $1,60.",
 "Обе просадки совпали с правками, а не предшествовали им.",
],BAD,RGBColor(0xFD,0xF2,0xF2))

# 7 аукцион
s=head("АУКЦИОН","Где теряем показы")
act=sorted([c for c in cur.values() if c["cost"]>1],key=lambda x:-x["cost"])
chart(s,0.5,1.55,12.33,2.9,[c["camp"][:16] for c in act],
      [("Получено, %",[c["is"] for c in act]),
       ("Потеря: бюджет, %",[c["lb"] for c in act]),
       ("Потеря: ранг, %",[c["lr"] for c in act])],
      [GOOD,BAD,MUTE],'0',leg=True)
rows=[["Кампания","Доля показов","Потеря: бюджет","Потеря: ранг","Верх страницы","Самый верх"]]
for c in act:
    rows.append([c["camp"],f"{c['is']:.0f}%",
                 (f"{c['lb']:.0f}%",BAD if c["lb"]>15 else INK),
                 (f"{c['lr']:.0f}%",BAD if c["lr"]>35 else INK),
                 f"{c['top']:.0f}%",f"{c['abs']:.0f}%"])
table(s,0.5,4.65,12.33,rows,colw=[3,1.5,1.6,1.4,1.5,1.3],rh=0.33)
tb(s,0.5,7.0,12.33,0.3,"Ремонт подвески: доля 15%, потеря по рангу 74% — кампания почти не показывается. "
   "СТО — Общая: 59% по рангу при лучшей цене конверсии.",9,False,MUTE)

# 8 качество — главная находка
s=head("КАЧЕСТВО","Объявления сильные, посадочная тянет вниз")
cnt={}; money={}
for field in ("adrel","ctr_exp","lp"):
    c=Counter(k[field] or "нет данных" for k in kw); cnt[field]=c
    m=defaultdict(float)
    for k in kw: m[k[field] or "нет данных"]+=k["cost"]
    money[field]=m
RU={"ABOVE_AVERAGE":"выше среднего","AVERAGE":"средне","BELOW_AVERAGE":"ниже среднего","нет данных":"нет данных"}
ORD=["ABOVE_AVERAGE","AVERAGE","BELOW_AVERAGE","нет данных"]
kpis(s,[(f"{len(lp_bad)}","ключей с посадочной ниже среднего",BAD),
        (M(LPC),"расход на них",BAD),
        (f"{LPC/sum(k['cost'] for k in kw)*100:.0f}%","от расхода на ключи",BAD),
        (f"{sum(k['qs'] for k in kw if k['qs'])/len([k for k in kw if k['qs']]):.2f}","средний показатель качества",None),
        (f"{cnt['adrel'].get('ABOVE_AVERAGE',0)}","объявлений выше среднего",GOOD)])
chart(s,0.5,2.75,12.33,2.3,["объявление","ожидаемый CTR","посадочная"],
      [("выше среднего",[cnt[f].get("ABOVE_AVERAGE",0) for f in ("adrel","ctr_exp","lp")]),
       ("средне",[cnt[f].get("AVERAGE",0) for f in ("adrel","ctr_exp","lp")]),
       ("ниже среднего",[cnt[f].get("BELOW_AVERAGE",0) for f in ("adrel","ctr_exp","lp")])],
      [GOOD,WARN,BAD],'0',leg=True)
box(s,0.5,5.25,12.33,1.85,"Что показывает разбивка",[
 f"Объявления: выше среднего у {cnt['adrel'].get('ABOVE_AVERAGE',0)} ключей, ниже среднего всего у {cnt['adrel'].get('BELOW_AVERAGE',0)}. Тексты работают.",
 f"Ожидаемый CTR: выше среднего у {cnt['ctr_exp'].get('ABOVE_AVERAGE',0)} ключей. Люди кликают.",
 f"Посадочная: ниже среднего у {cnt['lp'].get('BELOW_AVERAGE',0)} ключей, выше среднего — ни у одного. На эти ключи ушло {M(LPC)}.",
 "Это и есть причина потерь по рангу. Поднять ставку можно, но за ту же позицию придётся платить больше, пока страница слабее конкурентов.",
],BAD,RGBColor(0xFD,0xF2,0xF2))

# 9 ключ → запрос
s=head("КЛЮЧ → ЗАПРОС","Какие ключи работают пылесосом")
rows=[["Ключ","Кампания","Запросов ловит","Клики","Расход","Конверсии","Цена конв."]]
for (camp,k),(terms,c,v,cl) in sorted(bykw.items(), key=lambda x:-len(x[1][0]))[:12]:
    wide=len(terms)>=15
    rows.append([k[:30],camp[:18],(str(len(terms)),BAD if wide else INK,wide),
                 str(cl),M(c),(f"{v:.0f}",BAD if v==0 else INK),CPA(c,v)])
table(s,0.5,1.55,12.33,rows,colw=[3,2.2,1.5,1,1.2,1.2,1.3],rh=0.32)
box(s,0.5,5.9,12.33,1.3,"Широкие ключи",[
 "«автосервис» в СТО — Общей собрал 109 разных запросов за $2,89 и дал 1 конверсию. "
 "«развал схождение» — 33 запроса, 1 конверсия. «сто peugeot» — 17 запросов, ноль.",
 "Это не ошибка: широкий ключ нужен, чтобы находить новые формулировки. Но раз в неделю его улов надо разбирать — "
 "удачные запросы выносить в отдельные ключи, неудачные в минус.",
])

# 10 каннибализация
s=head("ПЕРЕСЕЧЕНИЯ","Один запрос ловят две группы")
byterm=defaultdict(list)
for t in T: byterm[t["term"]].append(t)
dup=sorted([(k,v) for k,v in byterm.items() if len({(x["camp"],x["grp"]) for x in v})>1],
           key=lambda x:-sum(y["cost"] for y in x[1]))
kpis(s,[(str(len(dup)),"запросов ловят разные группы",None),
        (M(sum(sum(y['cost'] for y in v) for _,v in dup)),"их суммарный расход",None),
        ("2","группы в «Регулировке фар»",None)])
rows=[["Запрос","Группа","Ключ","Клики","Расход","Конверсии"]]
for term,v in dup[:9]:
    first=True
    for x in sorted(v,key=lambda y:-y["cost"])[:2]:
        rows.append([term[:30] if first else "",x["grp"][:18],(x["kw"] or "—")[:24],
                     str(x["clicks"]),M(x["cost"]),
                     (f"{x['conv']:.0f}",GOOD if x["conv"] else MUTE)])
        first=False
table(s,0.5,2.9,12.33,rows,colw=[2.8,1.8,2.4,1,1.1,1.2],rh=0.215,fs=8.5)
box(s,0.5,7.0,12.33,0.4,"",[],ACC,W)
tb(s,0.5,7.0,12.33,0.3,"Главный пример: «регулировка фар минск» ловится обеими группами. "
   "В «Регулировке фар» — 39 кликов и 8 конверсий, в «Настройке фар» — 2 клика и ноль.",9,False,MUTE)

# 11 ключи без заявок
s=head("КЛЮЧИ","68 ключей потратили и не дали ни одной заявки")
kpis(s,[(str(len(dead_kw)),"ключей без заявок",BAD),(M(DEADC),"их расход за 9 дней",BAD),
        (f"{DEADC/sum(k['cost'] for k in kw)*100:.0f}%","от расхода на ключи",BAD),
        (f"{len([k for k in dead_kw if k['clicks']>=4])}","из них с 4+ кликами",None)])
rows=[["Ключ","Кампания","Клики","Расход","Качество","Посадочная"]]
LPRU={"BELOW_AVERAGE":"ниже среднего","AVERAGE":"средне","ABOVE_AVERAGE":"выше среднего"}
for k in dead_kw[:14]:
    rows.append([k["kw"][:32],k["camp"][:20],str(k["clicks"]),M(k["cost"]),
                 (str(k["qs"]) if k["qs"] else "—", BAD if (k["qs"] or 9)<=4 else INK),
                 LPRU.get(k["lp"],"—")])
table(s,0.5,2.75,12.33,rows,colw=[3.2,2.4,1,1.2,1.3,1.6],rh=0.25,fs=8.5)
tb(s,0.5,6.5,12.33,0.5,"Порог — любой расход за 20–28 октября. Больше всех потратил «настройка фар»: "
   "$6,12 и 15 кликов без единой заявки, при том что соседний «регулировка фар минск» дал 8 заявок.",9,False,MUTE)

# 12 минус-слова
s=head("МИНУС-СЛОВА","Добавлять почти нечего — и это важно")
kpis(s,[(str(len(cand)),"запросов без заявок",None),(M(CANDC),"их расход",None),
        (f"{CANDC/sum(v[0] for v in agg.values())*100:.0f}%","от расхода на запросы",None),
        ("2","паттерна для минусовки",GOOD)])
rows=[["Запрос","Клики","Расход","Кампания"]]
for term,v in cand[:13]:
    rows.append([term[:42],str(v[1]),M(v[0]),list(v[3])[0][:20]])
table(s,0.5,2.75,6.0,rows,colw=[3.4,0.8,1,1.6],rh=0.25,fs=8.5)
box(s,6.83,2.75,6.0,2.1,"Что реально можно минусовать",[
 "«рядом» — 1 запрос, $0,88. Человек ищет ближайший сервис, не вас.",
 "«стоимость», «цена» — 2 запроса, $1,38. Спорно: в этих же формулировках есть и конверсии.",
 "Всё. Больше паттернов нет.",
],GOOD,RGBColor(0xF0,0xFA,0xF5))
box(s,6.83,5.0,6.0,2.1,"Почему это хорошая новость",[
 "Остальные 35 запросов — целевые: «ремонт тойота минск», «мерседес сервис минск», «3d развал схождение минск».",
 "Они не дали заявок не потому что мусорные, а потому что человек ушёл с сайта.",
 "Значит проблема не в трафике, а в том, что происходит после клика.",
],ACC,RGBColor(0xEF,0xF4,0xFE))

# 13 выводы
s=head("ВЫВОДЫ","Что показали данные")
box(s,0.5,1.55,12.33,2.3,"Три вещи, которые видно только в цифрах",[
 "Посадочная ниже среднего у 114 ключей из 120 с оценкой, выше среднего — ни у одного. "
 "При этом объявления выше среднего у 97 ключей. Разрыв между рекламой и сайтом — главный ограничитель.",
 "Минусовать нечего: из 38 запросов без заявок целевых 35. Трафик чистый, теряется он уже на сайте.",
 "Снижение целевой цены конверсии ниже $1,70 на Регулировке фар срезало объём вдвое. "
 "Повышение бюджета СТО — По маркам до $15 объёма не добавило, цена выросла.",
],ACC,RGBColor(0xEF,0xF4,0xFE))
box(s,0.5,4.1,4.0,2.9,"Что стоит проверить",[
 "Вернуть целевую цену Регулировки на $1,70.",
 "Вернуть бюджет По маркам на $10.",
 "Измерять неделю, не два дня.",
],WARN,RGBColor(0xFD,0xF9,0xF0))
box(s,4.66,4.1,4.0,2.9,"Что даст больше всего",[
 "Посадочные страницы.",
 "114 ключей с оценкой ниже среднего.",
 "Это снимет потери по рангу: сейчас от 25% до 74% по кампаниям.",
],ACC,RGBColor(0xEF,0xF4,0xFE))
box(s,8.83,4.1,4.0,2.9,"Чего не делать",[
 "Не включать и не выключать кампании руками: 42 переключения за 9 дней мешают стратегии.",
 "Не искать мусор в запросах — его там нет.",
],BAD,RGBColor(0xFD,0xF2,0xF2))

# 14 данные
s=head("ДАННЫЕ","Что учтено и чего в цифрах нет")
box(s,0.5,1.55,12.33,2.6,"Границы выборки",[
 "Период 20–28 октября. Данных за 29-е ещё нет. «Эта неделя» — это два дня, 27 и 28.",
 "28 октября неполное: расход $21 против обычных $30–35.",
 "Конверсия = клик по номеру или мессенджеру на сайте. Это не звонок: часть кликов звонком не заканчивается.",
 "Эффект каждой правки измерен на 1–2 днях. Это направление, а не доказательство.",
 "Показатель качества есть не у всех ключей: у 45 из 165 данных нет.",
])
box(s,0.5,4.35,12.33,2.4,"Чего в отчёте нет",[
 "Статистики аукциона по конкурентам — Google не отдаёт её через API, только в интерфейсе.",
 "Данных о доезде: сколько из заявок стали клиентами. Без этого цена конверсии — не цена клиента.",
 "Среднего чека по кампаниям. С ним можно было бы считать не цену заявки, а выручку на вложенный доллар.",
],WARN,RGBColor(0xFD,0xF9,0xF0))

P.save(OUT)
print("сохранено:", OUT, os.path.getsize(OUT), "байт")
