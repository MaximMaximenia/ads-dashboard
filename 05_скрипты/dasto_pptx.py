# -*- coding: utf-8 -*-
"""Презентация по ДАСТО. Только чтение данных."""
import json, os
from collections import defaultdict
import statistics as st
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

SRC=os.path.expanduser("~/Desktop/Реклама/01_google_ads/dasto_clean.json")
OUT=os.path.expanduser("~/Desktop/Реклама/03_анализ/ДАСТО_разбор_24.10.2026.pptx")
D=json.load(open(SRC))
DAYS=14; SUB="ДАСТО — СТО · 6–23.10.2026 · 14 рабочих дней · в аккаунте ничего не менял"

INK=RGBColor(0x16,0x18,0x1D); MUTE=RGBColor(0x6B,0x72,0x80)
ACC=RGBColor(0x1A,0x73,0xE8); BAD=RGBColor(0xC5,0x22,0x1F)
GOOD=RGBColor(0x13,0x73,0x33); WARN=RGBColor(0xB0,0x60,0x00)
LINE=RGBColor(0xE3,0xE6,0xEA); SOFT=RGBColor(0xF4,0xF6,0xF8); WHITE=RGBColor(0xFF,0xFF,0xFF)

P=Presentation(); P.slide_width=Inches(13.333); P.slide_height=Inches(7.5)
BLANK=P.slide_layouts[6]

def tb(s,x,y,w,h,txt,size=14,bold=False,color=INK,align=PP_ALIGN.LEFT,space=0):
    t=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)); f=t.text_frame
    f.word_wrap=True; f.margin_left=0; f.margin_right=0; f.margin_top=0; f.margin_bottom=0
    p=f.paragraphs[0]; p.alignment=align
    r=p.add_run(); r.text=txt; r.font.size=Pt(size); r.font.bold=bold
    r.font.color.rgb=color; r.font.name="Arial"
    if space: p.space_after=Pt(space)
    return f

def bullets(f,items,size=12,color=INK):
    for i,it in enumerate(items):
        p=f.paragraphs[0] if i==0 else f.add_paragraph()
        p.space_after=Pt(7)
        r=p.add_run(); r.text="•  "+it
        r.font.size=Pt(size); r.font.color.rgb=color; r.font.name="Arial"

def rect(s,x,y,w,h,fill=WHITE,line=LINE):
    from pptx.enum.shapes import MSO_SHAPE
    sh=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb=fill
    if line: sh.line.color.rgb=line; sh.line.width=Pt(0.75)
    else: sh.line.fill.background()
    sh.shadow.inherit=False
    sh.adjustments[0]=0.06
    return sh

def head(tag,title,note=None):
    s=P.slides.add_slide(BLANK)
    s.background.fill.solid(); s.background.fill.fore_color.rgb=WHITE
    tb(s,0.55,0.34,6,0.3,tag.upper(),10,True,ACC)
    tb(s,0.55,0.62,12.3,0.5,title,23,True,INK)
    tb(s,0.55,1.16,12.3,0.3,note or SUB,9.5,False,MUTE)
    ln=s.shapes.add_shape(1,Inches(0.55),Inches(1.46),Inches(12.23),Pt(1))
    ln.fill.solid(); ln.fill.fore_color.rgb=LINE; ln.line.fill.background(); ln.shadow.inherit=False
    return s

def kpis(s,items,y=1.68,h=1.0):
    n=len(items); gap=0.16; w=(12.23-gap*(n-1))/n
    for i,(v,l,col) in enumerate(items):
        x=0.55+i*(w+gap); rect(s,x,y,w,h,SOFT)
        tb(s,x+0.18,y+0.14,w-0.3,0.42,v,21,True,col or INK)
        tb(s,x+0.18,y+0.62,w-0.3,0.3,l,9.5,False,MUTE)

def table(s,x,y,w,rows,colw=None,fs=9.5,hfs=8.5,rh=0.26):
    nr,nc=len(rows),len(rows[0])
    gf=s.shapes.add_table(nr,nc,Inches(x),Inches(y),Inches(w),Inches(rh*nr))
    t=gf.table
    if colw:
        tot=sum(colw)
        for i,cw in enumerate(colw): t.columns[i].width=Emu(int(Inches(w)*cw/tot))
    for ri,row in enumerate(rows):
        t.rows[ri].height=Inches(rh)
        for ci,val in enumerate(row):
            c=t.cell(ri,ci); c.text=""
            c.margin_left=Inches(0.07); c.margin_right=Inches(0.07)
            c.margin_top=0; c.margin_bottom=0
            c.vertical_anchor=MSO_ANCHOR.MIDDLE
            c.fill.solid(); c.fill.fore_color.rgb=SOFT if ri==0 else WHITE
            txt=val; col=INK; bold=(ri==0)
            if isinstance(val,tuple): txt,col=val[0],val[1]; bold=(ri==0) or (len(val)>2 and val[2])
            p=c.text_frame.paragraphs[0]
            p.alignment=PP_ALIGN.LEFT if ci==0 else PP_ALIGN.RIGHT
            r=p.add_run(); r.text=str(txt)
            r.font.size=Pt(hfs if ri==0 else fs); r.font.bold=bold
            r.font.color.rgb=MUTE if ri==0 else col; r.font.name="Arial"
    return t

def chart(s,x,y,w,h,cats,series,colors=None,fmt='0.0',labels=True,legend=False):
    cd=CategoryChartData(); cd.categories=cats
    for nm,vals in series: cd.add_series(nm,vals)
    gf=s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,Inches(x),Inches(y),Inches(w),Inches(h),cd)
    ch=gf.chart; ch.has_title=False
    ch.has_legend=legend
    if legend:
        ch.legend.position=XL_LEGEND_POSITION.BOTTOM; ch.legend.include_in_layout=False
        ch.legend.font.size=Pt(9); ch.legend.font.color.rgb=MUTE
    pl=ch.plots[0]; pl.gap_width=55; pl.overlap=-10
    pl.has_data_labels=labels
    if labels:
        dl=pl.data_labels; dl.font.size=Pt(8.5); dl.font.color.rgb=INK; dl.font.bold=True
        dl.number_format=fmt; dl.number_format_is_linked=False
        dl.position=XL_LABEL_POSITION.OUTSIDE_END
    for i,sr in enumerate(ch.series):
        sr.format.fill.solid()
        sr.format.fill.fore_color.rgb=(colors[i] if colors else ACC)
    ca=ch.category_axis; ca.tick_labels.font.size=Pt(8.5); ca.tick_labels.font.color.rgb=MUTE
    ca.format.line.color.rgb=LINE
    va=ch.value_axis; va.visible=False; va.has_major_gridlines=False
    return ch

def note(s,x,y,w,txt,size=9.5,color=MUTE):
    tb(s,x,y,w,0.4,txt,size,False,color)

def box(s,x,y,w,h,title,lines,accent=ACC,fill=SOFT):
    rect(s,x,y,w,h,fill)
    bar=s.shapes.add_shape(1,Inches(x),Inches(y),Pt(3),Inches(h))
    bar.fill.solid(); bar.fill.fore_color.rgb=accent; bar.line.fill.background(); bar.shadow.inherit=False
    tb(s,x+0.22,y+0.13,w-0.4,0.3,title,11.5,True,INK)
    f=tb(s,x+0.22,y+0.46,w-0.4,h-0.6,"",10)
    f.paragraphs[0].runs[0].text=""
    bullets(f,lines,10)

# ---------- данные ----------
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
MOB_CPA=dev["MOBILE"]["cost"]/dev["MOBILE"]["conv"]
byh=defaultdict(lambda:[0,0,0.0])
for r in D["hour"]:
    x=byh[r["k"]]; x[0]+=r["cost"]; x[1]+=r["clicks"]; x[2]+=r["conv"]
byd=defaultdict(list)
for r in D["dow_daily"]: byd[r["dow"]].append(r)
dead=[k for k in D["keywords"] if k["conv"]==0 and k["cost"]>=2]
dead.sort(key=lambda x:-x["cost"]); DEADC=sum(k["cost"] for k in dead)
lp_bad=[k for k in D["keywords"] if k.get("lp")=="BELOW_AVERAGE" and k["cost"]>0]
LPC=sum(k["cost"] for k in lp_bad)
def M(x): return f"${x:,.2f}".replace(","," ")
def CPA(c,v): return M(c/v) if v else "—"

# ---------- 1 титул ----------
s=P.slides.add_slide(BLANK)
s.background.fill.solid(); s.background.fill.fore_color.rgb=RGBColor(0x14,0x16,0x1A)
tb(s,0.9,2.3,11,0.4,"GOOGLE ADS / ДАСТО — СТО",12,True,RGBColor(0x8A,0xB4,0xF8))
tb(s,0.9,2.75,11,0.9,"Разбор рекламы",40,True,WHITE)
tb(s,0.9,3.7,11,0.5,"6–23 октября 2026 · 14 рабочих дней",17,False,RGBColor(0x9A,0xA0,0xA6))
tb(s,0.9,4.5,11,0.3,"аукцион · устройства · часы · ключи · качество · расчёт прироста",12,False,RGBColor(0x6B,0x72,0x80))
tb(s,0.9,6.4,11,0.3,"Подготовлено 24.10.2026 · в аккаунте ничего не менял",10,False,RGBColor(0x6B,0x72,0x80))

# ---------- 2 ограничения ----------
s=head("ДАННЫЕ","Почему окно — с 6 октября, а не за месяц")
box(s,0.55,1.7,12.23,2.0,"Учёт конверсий менялся — периоды несравнимы",[
 "До 1 октября конверсией считались page_view и scroll_75 из GA4: 24.09 было 53,7 «конверсии» на 45 кликов.",
 "С 6 октября остались только осмысленные действия: «Исходящий клик» (клик по номеру), инстаграм, вайбер, телеграм.",
 "За 24.09–23.10 суммарно: page_view 230,3 · Исходящий клик 88,0 · scroll_75 17,1 · остальное 24,0.",
 "Поэтому всё ниже считается с 6 по 23 октября. Сравнения с сентябрём в отчёте нет — они были бы ложными.",
],BAD,RGBColor(0xFD,0xF3,0xF2))
box(s,0.55,3.9,12.23,1.7,"Что ещё учтено",[
 "14 рабочих дней: 6–9, 12–16, 19–23 октября. Реклама идёт только по будням с 9 до 19.",
 "Конверсия = клик по номеру или мессенджеру на сайте. Это не звонок: часть кликов звонком не заканчивается.",
 "Расчёты прироста — оценка при сохранении текущих CTR, конверсии и цены клика. Не гарантия.",
 "Доля показов и потери — из API, по дням. Имена конкурентов API не отдаёт.",
])
note(s,0.55,5.8,12.23,"Все цифры в отчёте перепроверены на этом окне. Там, где наблюдений мало, это написано прямо.")

# ---------- 3 главное ----------
s=head("ГЛАВНОЕ","Что показали 14 дней")
kpis(s,[(f"{TOTV:.0f}","конверсий",None),(M(TOTC),"расход",None),
        (CPA(TOTC,TOTV),"цена конверсии",None),(f"{TOTK}","кликов",None),
        (M(TOTC/TOTK),"цена клика",None)])
box(s,0.55,2.95,6.0,3.6,"Подтвердилось данными",[
 f"Компьютеры: 186 кликов за 14 дней дали 3 конверсии. Конверсия 1,61% против 10,21% на телефонах.",
 f"Часы 13–16 дают конверсию 11–13%, часы 9–10 и 17–18 — 4–7%. Разброс устойчив все 14 дней.",
 f"Развал-схождение теряет 43,9% показов из-за бюджета при потере по рангу всего 4,5%.",
 f"110 ключей из 256 имеют посадочную ниже среднего, на них ушло {M(LPC)} из {M(TOTC)}.",
 f"{len(dead)} ключа потратили {M(DEADC)} и не дали ни одной конверсии.",
],GOOD,RGBColor(0xF1,0xF8,0xF3))
box(s,6.78,2.95,6.0,3.6,"Не подтвердилось — проверял, снимаю",[
 "«Настройка фар дублирует Регулировку фар» — неверно. Это разные формулировки: регулировка / настройка / коррекция. Пересечений в ключах нет.",
 "«Ключи без слова минск конвертят хуже» — на всей выборке разницы нет: 8,87% против 8,54%. Внутри одной группы выглядело убедительно, на 256 ключах — шум.",
 "«Понедельник проваливается» — наблюдений всего 2. Вынесено в гипотезы, вывода здесь нет.",
],WARN,RGBColor(0xFD,0xF8,0xF0))

# ---------- 4 по дням ----------
s=head("ПО ДНЯМ","Конверсии и расход по дням")
chart(s,0.55,1.65,12.23,2.5,[d[8:10]+"."+d[5:7] for d in DATES],
      [("Конверсии",[daily[d][2] for d in DATES])],[ACC],'0')
rows=[["Дата","Конверсии","Расход","Цена конв.","Клики","Цена клика"]]
for d in DATES:
    c,k,v=daily[d]
    rows.append([d[8:10]+"."+d[5:7],f"{v:.0f}",M(c),CPA(c,v),str(k),M(c/k) if k else "—"])
table(s,0.55,4.3,12.23,rows,colw=[2,1.4,1.4,1.5,1.2,1.4],rh=0.17,fs=8.5)
note(s,0.55,6.95,12.23,"6–9 октября в среднем 3 конверсии в день, 13–23 октября — 8,8. Рост совпал с накоплением данных у стратегий.")

# ---------- 5 кампании ----------
s=head("КАМПАНИИ","Все кампании за 14 дней")
rows=[["Кампания","Расход","Клики","Конв.","Цена конв.","Доля показов","Потеря: бюджет","Потеря: ранг"]]
for c in sorted(camps.values(), key=lambda x:-x["cost"]):
    cl=BAD if c["conv"]==0 else INK
    rows.append([c["camp"],M(c["cost"]),str(c["clicks"]),(f"{c['conv']:.0f}",cl),
                 (CPA(c["cost"],c["conv"]),cl),f"{c['is']:.1f}%",
                 (f"{c['lost_b']:.1f}%",BAD if c["lost_b"]>25 else INK),
                 (f"{c['lost_r']:.1f}%",BAD if c["lost_r"]>35 else INK)])
table(s,0.55,1.7,12.23,rows,colw=[3,1.3,1,1,1.4,1.5,1.6,1.4],rh=0.31)
box(s,0.55,5.0,12.23,1.6,"Что читается",[
 "Ремонт ДВС и Ремонт глушителя: 59 кликов, 0 конверсий, $51,21. Обе уже остановлены.",
 "СТО — По маркам: лучшая цена конверсии $2,74, при этом теряет 18,8% показов из-за бюджета и 37,3% из-за ранга.",
 "Развал-схождение: потеря по рангу всего 4,5% — объявления и ставка в порядке, упирается только в деньги.",
])

# ---------- 6 аукцион ----------
s=head("АУКЦИОН","Где теряем показы: бюджет против ранга")
act=[c for c in camps.values() if c["conv"]>0 or c["cost"]>20]
act.sort(key=lambda x:-x["lost_b"])
chart(s,0.55,1.65,12.23,3.1,[c["camp"][:18] for c in act],
      [("Получено, %",[c["is"] for c in act]),
       ("Потеря: бюджет, %",[c["lost_b"] for c in act]),
       ("Потеря: ранг, %",[c["lost_r"] for c in act])],
      [GOOD,BAD,MUTE],'0',legend=True)
box(s,0.55,4.95,6.0,1.9,"Лечится деньгами",[
 "Развал-схождение — 43,9% потерь по бюджету, по рангу 4,5%.",
 "СТО — По маркам — 18,8% по бюджету при лучшей цене конверсии в аккаунте.",
],BAD,RGBColor(0xFD,0xF3,0xF2))
box(s,6.78,4.95,6.0,1.9,"Лечится качеством",[
 "СТО — Общая: 63,1% потерь по рангу, доля показов 24,7%.",
 "Ремонт подвески: 37,9% по рангу, цена конверсии $7,24 — худшая среди работающих.",
],WARN,RGBColor(0xFD,0xF8,0xF0))

# ---------- 7 устройства ----------
s=head("УСТРОЙСТВА","Компьютеры: 186 кликов, 3 конверсии")
pc,mb=dev["DESKTOP"],dev["MOBILE"]
kpis(s,[(f"{pc['clicks']}","кликов с компьютеров",None),
        (f"{pc['conv']:.0f}","конверсии",BAD),
        (f"{pc['conv']/pc['clicks']*100:.2f}%","конверсия",BAD),
        (M(pc['cost']/pc['conv']),"цена конверсии",BAD),
        (M(pc['cost']),"потрачено",None)])
chart(s,0.55,2.95,5.9,2.4,["Телефоны","Компьютеры"],
      [("Конверсия из клика, %",[mb["conv"]/mb["clicks"]*100, pc["conv"]/pc["clicks"]*100])],
      [GOOD],'0.00')
rows=[["Устройство","Расход","Клики","Конв.","Конверсия","Цена конв."]]
RUD={"MOBILE":"Телефоны","DESKTOP":"Компьютеры","TABLET":"Планшеты"}
for k,v in sorted(dev.items(), key=lambda x:-x[1]["cost"]):
    cr=v["conv"]/v["clicks"]*100 if v["clicks"] else 0
    cl=BAD if k=="DESKTOP" else INK
    rows.append([RUD.get(k,k),M(v["cost"]),str(v["clicks"]),(f"{v['conv']:.0f}",cl),
                 (f"{cr:.2f}%",cl),(CPA(v["cost"],v["conv"]),cl)])
table(s,6.78,3.0,6.0,rows,colw=[2,1.3,1,1,1.3,1.4],rh=0.3)
box(s,0.55,5.6,12.23,1.3,"Расчёт",[
 f"За 14 дней на компьютеры ушло {M(pc['cost'])} и получено {pc['conv']:.0f} конверсии. "
 f"Те же деньги на телефонах по цене {M(MOB_CPA)} дали бы {pc['cost']/MOB_CPA:.1f} конверсий.",
 f"Чистый прирост при переносе: +{pc['cost']/MOB_CPA-pc['conv']:.1f} конверсий за 14 дней, "
 f"то есть +{(pc['cost']/MOB_CPA-pc['conv'])/DAYS*5:.1f} в неделю. Выборка — 14 дней, паттерн устойчив.",
],GOOD,RGBColor(0xF1,0xF8,0xF3))

# ---------- 8 часы ----------
s=head("ЧАСЫ","Конверсия по часам: провал утром и после 17")
hs=[h for h in sorted(byh) if byh[h][1]>0]
chart(s,0.55,1.65,12.23,2.6,[f"{h}:00" for h in hs],
      [("Конверсия из клика, %",[byh[h][2]/byh[h][1]*100 for h in hs])],
      [ACC],'0.0')
rows=[["Час","Клики","Конверсии","Конверсия","Расход","Цена конв."]]
for h in hs:
    c,cl_,v=byh[h]; cr=v/cl_*100
    col=GOOD if cr>=10 else (BAD if cr<5 else INK)
    rows.append([f"{h}:00",str(cl_),(f"{v:.0f}",col),(f"{cr:.2f}%",col),M(c),CPA(c,v)])
table(s,0.55,4.45,12.23,rows,colw=[1.2,1.2,1.4,1.4,1.4,1.5],rh=0.225,fs=9.5)
note(s,0.55,7.02,12.23,
 f"13–16 часов: конверсия 11–13%. 9–10 и 17–18 часов: 4–7%. "
 f"18:00 — 24 клика и ноль конверсий за все 14 дней, расход {M(byh[18][0])}.")

# ---------- 9 дни недели ----------
s=head("ДНИ НЕДЕЛИ","Наблюдение, а не вывод: данных мало")
ORD=["MONDAY","TUESDAY","WEDNESDAY","THURSDAY","FRIDAY"]
RUW={"MONDAY":"Пн","TUESDAY":"Вт","WEDNESDAY":"Ср","THURSDAY":"Чт","FRIDAY":"Пт"}
present=[k for k in ORD if k in byd]
chart(s,0.55,1.65,7.5,2.6,[RUW[k] for k in present],
      [("Конверсий в день, среднее",[st.mean([x["conv"] for x in byd[k]]) for k in present])],
      [ACC],'0.0')
rows=[["День","Наблюдений","Всего конв.","Среднее/день","Разброс","Цена конв."]]
for k in present:
    v=byd[k]; cs=[x["conv"] for x in v]; cost=sum(x["cost"] for x in v)
    col=BAD if len(v)<3 else INK
    rows.append([RUW[k],(str(len(v)),col),f"{sum(cs):.0f}",f"{st.mean(cs):.1f}",
                 f"{min(cs):.0f}–{max(cs):.0f}",CPA(cost,sum(cs))])
table(s,8.3,1.75,4.48,rows,colw=[1,1.4,1.3,1.4,1.2,1.3],rh=0.33,fs=9)
box(s,0.55,4.6,12.23,2.0,"Почему здесь нет вывода",[
 "Понедельников в выборке всего два: 12 и 19 октября. Оба дали по 3 конверсии при среднем 7,4 по остальным дням.",
 "Два наблюдения — это совпадение ровно настолько же, насколько закономерность. Менять ставки на основании двух дней нельзя.",
 "У остальных дней по 3 наблюдения и разброс внутри дня больше, чем разница между днями: у пятницы 1–15, у вторника 3–11.",
 "Что делать: ничего не трогать и вернуться к этому через 3–4 недели, когда наблюдений станет 6–8 на день.",
],WARN,RGBColor(0xFD,0xF8,0xF0))

# ---------- 10 пустые ключи ----------
s=head("КЛЮЧИ","Ключи, которые потратили и не дали ничего")
kpis(s,[(str(len(dead)),"ключей без конверсий",BAD),(M(DEADC),"потрачено за 14 дней",BAD),
        (M(DEADC/DAYS*5),"в неделю",None),
        (f"+{DEADC/MOB_CPA/DAYS*5:.1f}","конверсий/нед при переносе",GOOD)])
rows=[["Ключ","Кампания","Расход","Клики","QS"]]
for k in dead[:15]:
    rows.append([k["kw"][:42],k["camp"][:22],M(k["cost"]),str(k["clicks"]),
                 (str(k["qs"]) if k["qs"] else "—", BAD if k["qs"] and k["qs"]<=4 else INK)])
table(s,0.55,2.95,12.23,rows,colw=[4.2,2.6,1.2,1,0.8],rh=0.235,fs=9)
note(s,0.55,6.9,12.23,
 "Порог — расход от $2 за 14 дней. Перенос этих денег в работающие ключи считается по текущей цене конверсии на телефонах.")

# ---------- 11 качество ----------
s=head("КАЧЕСТВО","Посадочная ниже среднего у 110 ключей из 256")
bycamp=defaultdict(lambda:[0,0])
for k in lp_bad: bycamp[k["camp"]][0]+=k["cost"]; bycamp[k["camp"]][1]+=1
items=sorted(bycamp.items(), key=lambda x:-x[1][0])
kpis(s,[(f"{len(lp_bad)}","ключей с LP ниже среднего",BAD),(M(LPC),"расход на них",BAD),
        (f"{LPC/TOTC*100:.0f}%","от всего расхода",BAD),
        (f"{st.mean([k['qs'] for k in D['keywords'] if k['qs']]):.2f}","средний QS",None)])
chart(s,0.55,2.95,12.23,2.3,[c[:18] for c,_ in items],
      [("Расход на слабые ключи, $",[v[0] for _,v in items])],[BAD],'0')
box(s,0.55,5.45,12.23,1.6,"Что это значит",[
 "LP ниже среднего — оценка Google: страница, на которую ведёт ключ, слабее, чем у конкурентов по этому же запросу.",
 "Это главная причина потерь по рангу. Поднять ставку можно, но платить придётся больше за ту же позицию.",
 "Хуже всего у Регулировки фар ($85,45 на 12 ключей) и Развала ($83,98 на 13 ключей) — при том что сами кампании рабочие.",
],WARN,RGBColor(0xFD,0xF8,0xF0))

# ---------- 12 группы по фарам ----------
s=head("ФАРЫ","Разбор групп: дублирования нет, проблема в одном ключе")
FG=["Регулировка фар","Настройка фар","ПТФ и линзы"]
kw_by={g:[k for k in D["keywords"] if k["group"]==g] for g in FG}
rows=[["Группа","Ключей","Расход","Клики","Конв.","Цена конв."]]
for g in FG:
    ks=kw_by[g]; c=sum(x["cost"] for x in ks); v=sum(x["conv"] for x in ks); cl=sum(x["clicks"] for x in ks)
    rows.append([g,str(len(ks)),M(c),str(cl),f"{v:.1f}",CPA(c,v)])
table(s,0.55,1.7,6.0,rows,colw=[2.2,1,1.3,1,1,1.3],rh=0.32)
rows=[["Ключ","Группа","Расход","Клики","Конв."]]
allk=sorted([k for g in FG for k in kw_by[g]], key=lambda x:-x["cost"])[:12]
for k in allk:
    col=BAD if k["conv"]==0 and k["cost"]>3 else INK
    rows.append([k["kw"][:32],k["group"][:16],M(k["cost"]),str(k["clicks"]),(f"{k['conv']:.1f}",col)])
table(s,6.78,1.7,6.0,rows,colw=[2.6,1.5,1.1,0.9,0.9],rh=0.255,fs=8.5)
box(s,0.55,4.6,12.23,2.2,"Что я сказал в прошлый раз и почему это было неверно",[
 "Говорил: «Настройка фар дублирует Регулировку фар, слить в одну». Посмотрел ключи — пересечений нет. "
 "В Регулировке — регулировка фар, регулировка света фар, отрегулировать фары. В Настройке — настройка фар, корректировка, коррекция.",
 "Это разные формулировки одного запроса, и разделение сделано правильно: так видно, какая формулировка работает.",
 "Реальная проблема точечная: ключ «корректировка фар» — $10,02, 18 кликов, ноль конверсий. Это 28% расхода группы.",
 "Рядом «коррекция фар минск» за $9,23 дал 3,3 конверсии. Разница в одном слове, а не в группе.",
],GOOD,RGBColor(0xF1,0xF8,0xF3))

# ---------- 13 прирост ----------
s=head("ПРИРОСТ","Сколько даст бюджет и сколько — перенос денег")
def gain(name,target):
    c=camps[name]; new=min(99.0,c["is"]+(c["lost_b"]-target)); k=new/c["is"]
    return (c["clicks"]*(k-1), c["conv"]*(k-1), c["cost"]*(k-1), new)
rows=[["Что делаем","Сейчас","Станет","+клики/14дн","+конв/нед","+расход/день"]]
for nm,t in [("Развал-схождение",20),("Развал-схождение",0),("СТО — По маркам",0)]:
    key="СТО - По маркам" if "По маркам" in nm else nm
    ac,av,acost,new=gain(key,t)
    rows.append([f"{nm}: потеря по бюджету → {t}%",f"доля {camps[key]['is']:.1f}%",f"доля {new:.1f}%",
                 f"+{ac:.0f}",(f"+{av/DAYS*5:.1f}",GOOD),f"+{M(acost/DAYS)}"])
pcg=pc["cost"]/MOB_CPA-pc["conv"]
rows.append(["Отключить компьютеры",f"{pc['conv']:.0f} конв за {M(pc['cost'])}",
             f"{pc['cost']/MOB_CPA:.1f} конв",   "—",(f"+{pcg/DAYS*5:.1f}",GOOD),"0"])
rows.append(["Убрать 23 пустых ключа",f"{M(DEADC)} в никуда",f"{DEADC/MOB_CPA:.1f} конв","—",
             (f"+{DEADC/MOB_CPA/DAYS*5:.1f}",GOOD),"0"])
rows.append(["Отключить показы с 18:00",f"{M(byh[18][0])}, 0 конв",f"{byh[18][0]/MOB_CPA:.1f} конв","—",
             (f"+{byh[18][0]/MOB_CPA/DAYS*5:.1f}",GOOD),f"-{M(byh[18][0]/DAYS)}"])
table(s,0.55,1.7,12.23,rows,colw=[3.6,2.1,1.7,1.4,1.4,1.5],rh=0.36)
nowk=TOTV/DAYS*5
addk=pcg/DAYS*5+DEADC/MOB_CPA/DAYS*5+byh[18][0]/MOB_CPA/DAYS*5
box(s,0.55,4.5,12.23,2.3,"Итог без роста бюджета",[
 f"Сейчас: {nowk:.1f} конверсий в неделю при расходе {M(TOTC/DAYS*5)}.",
 f"Перенос денег с компьютеров, пустых ключей и вечерних часов: +{addk:.1f} конверсий в неделю на тех же деньгах.",
 f"Это {addk/nowk*100:.0f}% прироста. Цена конверсии уйдёт примерно с {CPA(TOTC,TOTV)} к {M(TOTC/(TOTV+addk/5*DAYS))}.",
 f"Бюджет на Развал-схождение — отдельно: +4,9 конверсий в неделю при +$5,38 в день. Окупается, но это уже новые деньги.",
 "Все цифры — оценка при сохранении текущих показателей. Проверять по одному изменению за раз.",
],GOOD,RGBColor(0xF1,0xF8,0xF3))

# ---------- 14 план ----------
s=head("ПЛАН","По шагам, по одному изменению за раз")
box(s,0.55,1.7,3.95,2.6,"ШАГ 1 · на этой неделе",[
 "Компьютеры: ставка -80% или отключить.",
 "Показы с 18:00 выключить.",
 "23 пустых ключа в минус-слова.",
 "Ждать неделю, не трогать остальное.",
],BAD,RGBColor(0xFD,0xF3,0xF2))
box(s,4.69,1.7,3.95,2.6,"ШАГ 2 · после замера",[
 "Развал-схождение: бюджет +30%.",
 "Цель — потеря по бюджету ниже 20%.",
 "Следить за ценой конверсии: не выше $6.",
 "Ещё неделя на замер.",
],WARN,RGBColor(0xFD,0xF8,0xF0))
box(s,8.83,1.7,3.95,2.6,"ШАГ 3 · дольше",[
 "Посадочные под Регулировку и Развал.",
 "110 ключей с LP ниже среднего.",
 "Это снимет потери по рангу.",
 "Эффект через 3–4 недели.",
],ACC,RGBColor(0xEF,0xF4,0xFE))
box(s,0.55,4.5,12.23,2.3,"Чего делать не нужно",[
 "Не менять ставки по дням недели: два понедельника — не основание.",
 "Не сливать группы по фарам: они разделены правильно, проблема в одном ключе.",
 "Не доливать бюджет в СТО — Общая и Ремонт подвески: там потери по рангу, деньги уйдут в ту же стену.",
 "Не менять больше одной вещи за раз — иначе не поймём, что сработало.",
])

# ---------- 15 закономерности ----------
s=head("ЗАКОНОМЕРНОСТИ","Что видно в данных и насколько этому можно верить")
rows=[["Наблюдение","Доказательство","Наблюдений","Статус"]]
rows+=[
 ["Компьютеры не конвертят","186 кликов → 3 конв, CR 1,61% против 10,21%","14 дней",("подтверждено",GOOD,True)],
 ["Дневной пик 13–16 часов","CR 11–13% против 4–7% утром и вечером","14 дней",("подтверждено",GOOD,True)],
 ["18:00 — мёртвый час","24 клика, 0 конверсий за весь период","14 дней",("подтверждено",GOOD,True)],
 ["Развал упирается в бюджет","потеря по бюджету 43,9%, по рангу 4,5%","14 дней",("подтверждено",GOOD,True)],
 ["Посадочные слабые","110 из 256 ключей с LP ниже среднего","весь период",("подтверждено",GOOD,True)],
 ["Понедельник слабее","2 наблюдения: 3 и 3 конверсии против 7,4","2 дня",("мало данных",WARN,True)],
 ["Группы фар дублируются","пересечений в ключах нет","—",("опровергнуто",BAD,True)],
 ["Ключи без «минск» хуже","CR 8,54% против 8,87% — разницы нет","256 ключей",("опровергнуто",BAD,True)],
]
table(s,0.55,1.7,12.23,rows,colw=[3.2,4.6,1.5,1.8],rh=0.4)
note(s,0.55,5.6,12.23,
 "«Подтверждено» — паттерн держится все 14 дней и разница больше внутридневного разброса. "
 "«Мало данных» — наблюдений меньше трёх, решение откладывается. "
 "«Опровергнуто» — проверил и не нашёл основания, вывод снят.")

P.save(OUT)
print("Готово:", OUT, os.path.getsize(OUT), "байт, слайдов:", len(P.slides.__iter__.__self__._sldIdLst))
