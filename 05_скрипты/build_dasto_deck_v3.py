#!/usr/bin/env python3
"""ДАСТО v3: по одной кампании на слайд, столбики по дням."""
import json
import collections
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION

BG = RGBColor(0xF7,0xF7,0xF5); DARK = RGBColor(0x17,0x18,0x1A); RED = RGBColor(0xD0,0x13,0x0D)
BLUE = RGBColor(0x2F,0x5F,0xB8); GRAY = RGBColor(0x9A,0x9A,0x9E); LINE = RGBColor(0xE3,0xE3,0xDF)
WHITE = RGBColor(0xFF,0xFF,0xFF); SOFT = RGBColor(0xEF,0xEF,0xEC)
FONT = "Arial"
prs = Presentation(); prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)

CAMP = ["Развал-схождение", "СТО - По маркам", "Регулировка фар", "Проточка тормозных дисков"]
SHORT = {"Развал-схождение":"Развал", "СТО - По маркам":"СТО-По маркам",
         "Регулировка фар":"Регулировка", "Проточка тормозных дисков":"Проточка"}

raw = json.load(open("/Users/maksim/Desktop/Реклама/05_скрипты/dasto_daily.json"))
by = {c:{} for c in CAMP}
for r in raw:
    n=r["campaign"]["name"]; d=r["segments"]["date"]; m=r["metrics"]
    if n not in by: continue
    by[n][d]={"impr":int(m.get("impressions",0)),"cl":int(m.get("clicks",0)),
              "cost":int(m.get("costMicros",0))/1e6,"conv":float(m.get("conversions",0)),
              "is":float(m.get("searchImpressionShare",0))*100,
              "lostb":float(m.get("searchBudgetLostImpressionShare",0))*100,
              "lostr":float(m.get("searchRankLostImpressionShare",0))*100,
              "top":float(m.get("searchTopImpressionShare",0))*100,
              "abs":float(m.get("searchAbsoluteTopImpressionShare",0))*100}

def add_slide(kicker, title, footer="ДАСТО — СТО · 13–21.10.2026 · только 4 активные кампании · без изменений"):
    s=prs.slides.add_slide(prs.slide_layouts[6])
    bg=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,0,0,prs.slide_width,prs.slide_height)
    bg.fill.solid(); bg.fill.fore_color.rgb=BG; bg.line.fill.background()
    bar=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,0,0,Inches(0.10),prs.slide_height)
    bar.fill.solid(); bar.fill.fore_color.rgb=RED; bar.line.fill.background()
    t=s.shapes.add_textbox(Inches(0.55),Inches(0.30),Inches(11.8),Inches(0.25))
    r=t.text_frame.paragraphs[0].add_run(); r.text=kicker
    r.font.name=FONT; r.font.size=Pt(9); r.font.bold=True; r.font.color.rgb=RED
    t=s.shapes.add_textbox(Inches(0.55),Inches(0.56),Inches(12.2),Inches(0.55))
    r=t.text_frame.paragraphs[0].add_run(); r.text=title
    r.font.name=FONT; r.font.size=Pt(22); r.font.bold=True; r.font.color.rgb=DARK
    t=s.shapes.add_textbox(Inches(0.55),Inches(7.13),Inches(12.2),Inches(0.20))
    r=t.text_frame.paragraphs[0].add_run(); r.text=footer
    r.font.name=FONT; r.font.size=Pt(8); r.font.color.rgb=RGBColor(0x6E,0x6E,0x73)
    return s

def text(s,x,y,w,h,lines,size=11,bold=False,color=DARK,gap=0):
    box=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)); tf=box.text_frame; tf.word_wrap=True
    tf.margin_left=0; tf.margin_right=0; tf.margin_top=0; tf.margin_bottom=0
    for i,line in enumerate(lines if isinstance(lines,list) else lines.split("\n")):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph(); p.space_after=Pt(gap)
        r=p.add_run(); r.text=line; r.font.name=FONT; r.font.size=Pt(size); r.font.bold=bold; r.font.color.rgb=color
    return box

def bullets(s,x,y,w,h,items,size=9,gap=5):
    box=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)); tf=box.text_frame; tf.word_wrap=True
    tf.margin_left=0; tf.margin_right=0; tf.margin_top=0; tf.margin_bottom=0
    for i,item in enumerate(items):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph(); p.space_after=Pt(gap); p.line_spacing=1.0
        r0=p.add_run(); r0.text="●  "; r0.font.name=FONT; r0.font.size=Pt(size-2); r0.font.color.rgb=RED
        r=p.add_run(); r.text=item; r.font.name=FONT; r.font.size=Pt(size); r.font.color.rgb=DARK

def kpi_strip(s, vals):
    # vals: list of (value,label)
    n=len(vals); w=1.62; gap=0.10; x0=(13.333-(n*w+(n-1)*gap))/2
    for i,(v,l) in enumerate(vals):
        x=x0+i*(w+gap)
        card=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(x),Inches(1.25),Inches(w),Inches(0.82))
        card.adjustments[0]=0.10; card.fill.solid(); card.fill.fore_color.rgb=WHITE; card.line.color.rgb=LINE
        t=s.shapes.add_textbox(Inches(x+0.08),Inches(1.31),Inches(w-0.16),Inches(0.32))
        r=t.text_frame.paragraphs[0].add_run(); r.text=v
        r.font.name=FONT; r.font.size=Pt(15); r.font.bold=True; r.font.color.rgb=RED
        t=s.shapes.add_textbox(Inches(x+0.08),Inches(1.64),Inches(w-0.16),Inches(0.25))
        r=t.text_frame.paragraphs[0].add_run(); r.text=l
        r.font.name=FONT; r.font.size=Pt(6.8); r.font.color.rgb=RGBColor(0x6E,0x6E,0x73)

def chart_base(ch, title, ymax=None, fmt='0'):
    ch.has_legend=True; ch.legend.position=XL_LEGEND_POSITION.BOTTOM; ch.legend.include_in_layout=False
    ch.legend.font.size=Pt(6.5); ch.legend.font.name=FONT
    ch.font.name=FONT; ch.font.size=Pt(6.5)
    ch.has_title=True; ch.chart_title.text_frame.text=title
    for p in ch.chart_title.text_frame.paragraphs:
        for r in p.runs: r.font.size=Pt(8.5); r.font.bold=True; r.font.name=FONT; r.font.color.rgb=DARK
    if ymax: ch.value_axis.maximum_scale=ymax
    ch.value_axis.minimum_scale=0
    ch.value_axis.has_major_gridlines=True
    ch.value_axis.major_gridlines.format.line.color.rgb=RGBColor(0xE8,0xE8,0xE4)
    ch.value_axis.tick_labels.font.size=Pt(6.3); ch.value_axis.tick_labels.number_format=fmt
    ch.value_axis.tick_labels.number_format_is_linked=False
    ch.category_axis.tick_labels.font.size=Pt(6.2)

def stacked_auction(s,c):
    dates=sorted(by[c]); labels=[d[8:10]+"."+d[5:7] for d in dates]
    cd=CategoryChartData(); cd.categories=labels
    cd.add_series("Получено (IS)",tuple(round(by[c][d]["is"],1) for d in dates))
    cd.add_series("Потеряно по бюджету",tuple(round(by[c][d]["lostb"],1) for d in dates))
    cd.add_series("Потеряно по рангу",tuple(round(by[c][d]["lostr"],1) for d in dates))
    ch=s.shapes.add_chart(XL_CHART_TYPE.COLUMN_STACKED,Inches(0.55),Inches(2.40),Inches(6.35),Inches(2.58),cd).chart
    chart_base(ch,"Аукцион по дням: что получили и что потеряли",100,'0"%"')
    colors=[DARK,RED,GRAY]
    for i,ser in enumerate(ch.series):
        ser.format.fill.solid(); ser.format.fill.fore_color.rgb=colors[i]
        ser.format.line.fill.background()
    ch.plots[0].gap_width=45
    ch.plots[0].has_data_labels=True
    dl=ch.plots[0].data_labels; dl.font.size=Pt(5.8); dl.font.name=FONT
    dl.number_format='0"%"'; dl.number_format_is_linked=False
    dl.position=XL_LABEL_POSITION.CENTER

def clustered_top(s,c):
    dates=sorted(by[c]); labels=[d[8:10]+"."+d[5:7] for d in dates]
    cd=CategoryChartData(); cd.categories=labels
    cd.add_series("Топ страницы",tuple(round(by[c][d]["top"],1) for d in dates))
    cd.add_series("Абс. топ",tuple(round(by[c][d]["abs"],1) for d in dates))
    ch=s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,Inches(7.05),Inches(2.40),Inches(5.75),Inches(2.58),cd).chart
    chart_base(ch,"Где показываемся: топ страницы и абсолютный топ",100,'0"%"')
    for i,ser in enumerate(ch.series):
        ser.format.fill.solid(); ser.format.fill.fore_color.rgb=[BLUE,DARK][i]
        ser.format.line.fill.background()
    ch.plots[0].gap_width=55
    ch.plots[0].has_data_labels=True
    dl=ch.plots[0].data_labels; dl.font.size=Pt(6.2); dl.font.name=FONT
    dl.number_format='0"%"'; dl.number_format_is_linked=False
    dl.position=XL_LABEL_POSITION.OUTSIDE_END

def single_chart(s,c,key,title,ymax,fmt,x,y,w,h,color=RED):
    dates=sorted(by[c]); labels=[d[8:10]+"."+d[5:7] for d in dates]
    vals=[]
    for d in dates:
        v=by[c][d]
        if key=="conv": vals.append(round(v["conv"],1))
        elif key=="cpa": vals.append(round(v["cost"]/v["conv"],2) if v["conv"]>0 else None)
        else: vals.append(None)
    cd=CategoryChartData(); cd.categories=labels; cd.add_series(title,tuple(vals))
    ch=s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,Inches(x),Inches(y),Inches(w),Inches(h),cd).chart
    chart_base(ch,title,ymax,fmt)
    ch.series[0].format.fill.solid(); ch.series[0].format.fill.fore_color.rgb=color
    ch.series[0].format.line.fill.background()
    ch.plots[0].gap_width=45
    ch.plots[0].has_data_labels=True
    dl=ch.plots[0].data_labels; dl.font.size=Pt(6.3); dl.font.name=FONT
    dl.number_format=('$0.00' if key=="cpa" else '0.0'); dl.number_format_is_linked=False
    dl.position=XL_LABEL_POSITION.OUTSIDE_END

def period_stats(c):
    ds=[d for d in sorted(by[c]) if "2026-10-13"<=d<="2026-10-21"]
    impr=sum(by[c][d]["impr"] for d in ds); cl=sum(by[c][d]["cl"] for d in ds)
    cost=sum(by[c][d]["cost"] for d in ds); conv=sum(by[c][d]["conv"] for d in ds)
    def w(k): return sum(by[c][d][k]*by[c][d]["impr"] for d in ds)/impr if impr else 0
    return dict(impr=impr,cl=cl,cost=cost,conv=conv,cpa=cost/conv if conv else 0,
                is_=w("is"),lostb=w("lostb"),lostr=w("lostr"),top=w("top"),abs=w("abs"))

def campaign_slide(c,kicker,title,fixes):
    s=add_slide(kicker,title)
    p=period_stats(c)
    kpi_strip(s,[(f"{p['conv']:.0f}","звонков 13–21"),(f"${p['cpa']:.2f}" if p['cpa'] else "—","CPA"),
                 (f"${p['cost']:.0f}","расход"),(f"{p['is_']:.0f}%","доля показов"),
                 (f"{p['lostb']:.0f}%","потеря по бюджету"),(f"{p['lostr']:.0f}%","потеря по рангу"),
                 (f"{p['top']:.0f}% / {p['abs']:.0f}%","топ / абс. топ")])
    stacked_auction(s,c); clustered_top(s,c)
    single_chart(s,c,"conv","Звонки по дням",max(4,max(by[c][d]["conv"] for d in by[c])+1),'0.0',0.55,5.20,3.95,1.75,RED)
    maxcpa=max((by[c][d]["cost"]/by[c][d]["conv"] for d in by[c] if by[c][d]["conv"]>0),default=1)
    single_chart(s,c,"cpa","CPA по дням",max(2,round(maxcpa*1.25,0)),'$0.00',4.65,5.20,3.95,1.75,BLUE)
    box=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(8.80),Inches(5.10),Inches(4.00),Inches(1.95))
    box.adjustments[0]=0.05; box.fill.solid(); box.fill.fore_color.rgb=WHITE; box.line.color.rgb=LINE
    text(s,8.97,5.18,3.7,0.22,"ЧТО ЧИНИТЬ",7.8,True,RED)
    bullets(s,8.97,5.44,3.7,1.55,fixes,size=7.6,gap=4)

# 1. title
s=prs.slides.add_slide(prs.slide_layouts[6])
bg=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,0,0,prs.slide_width,prs.slide_height)
bg.fill.solid(); bg.fill.fore_color.rgb=DARK; bg.line.fill.background()
bar=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(0.70),Inches(1.25),Inches(0.12),Inches(3.95))
bar.fill.solid(); bar.fill.fore_color.rgb=RED; bar.line.fill.background()
text(s,1.05,1.20,10.8,0.30,"GOOGLE ADS / ДАСТО - СТО",11,True,RED)
text(s,1.05,1.65,10.8,1.0,"ДАСТО: столбики\nпо каждой кампании",40,True,WHITE)
text(s,1.05,3.45,10.8,0.65,"4 кампании · 8–21 октября 2026\nаукцион, потери, звонки, CPA",17,False,RGBColor(0xE6,0xE6,0xE6))
line=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(1.05),Inches(5.15),Inches(5.0),Inches(0.02))
line.fill.solid(); line.fill.fore_color.rgb=RGBColor(0x3A,0x3A,0x3C); line.line.fill.background()
text(s,1.05,5.33,10.8,0.30,"Подготовлено 22.10.2026 · в аккаунте ничего не менял",10,False,RGBColor(0xB9,0xB9,0xB9))

# 2. summary
s=add_slide("ГЛАВНОЕ","Что видно по столбикам")
kpi_strip(s,[("47","звонков 13–21"),("$3,82","CPA"),("$179","расход"),("530","кликов"),("58","звонков 30 дн."),("$4,62","CPA 30 дн."),("$0,01→$33","рост расхода/день")])
bullets(s,0.55,2.35,6.0,4.3,[
    "Каждый слайд ниже — одна кампания: по дням видно, где теряем бюджет, где ранг, где мы в топе.",
    "Развал: бюджет — главный ограничитель, 30–52% потерь по бюджету. Поднять бюджет — первый шаг.",
    "СТО: главный ограничитель — ранг, 37–39%. Бюджет уже почти не режет. Сначала LP/QS и ставки.",
    "Регулировка: бюджет 0%, ранг 33%. Только качество/ставка.",
    "Проточка: ранг 33–40%, но мало объёма: 7 кликов за неделю.",
],size=10.0,gap=8)
box=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(6.85),Inches(2.35),Inches(5.95),Inches(3.9))
box.adjustments[0]=0.05; box.fill.solid(); box.fill.fore_color.rgb=WHITE; box.line.color.rgb=LINE
text(s,7.07,2.55,5.5,0.25,"КАК ЧИТАТЬ",8.5,True,RED)
bullets(s,7.07,2.88,5.5,3.1,[
    "Аукцион: чёрный столбик — доля показов (выкуп), красный — потеря по бюджету, серый — потеря по рангу. В сумме 100%.",
    "Топ страницы — показ в верхнем блоке; абсолютный топ — самая первая позиция. Вам нужен топ страницы 70–80%, не абсолютный топ.",
    "Звонки — «исходящий клик» по номеру. CPA — расход / звонки; в дни без звонков CPA нет.",
],size=8.8,gap=7)

# 3-6 campaigns
campaign_slide(CAMP[0],"РАЗВАЛ","Развал-схождение: бюджет — главный рычаг",[
    "Бюджет: потеря 42,6% (13–21), 30% на этой неделе. Поднять на 20–30%.",
    "Ожидание: +3 звонка/нед; CPA держать < $5,5.",
    "Ранг: потеря 6,4% — не главное; топ страницы 39,8%, абс. 11,8%.",
    "LP/QS: QS 4,89, топ-ключ «развал схождение» QS 3 — усилить страницу и заголовки.",
])
campaign_slide(CAMP[1],"СТО - ПО МАРКАМ","СТО-По маркам: ранг, а не бюджет",[
    "Ранг: потеря 39,2% (36,6% на этой неделе) — главный ограничитель.",
    "Бюджет: 14,4% (6,2% сейчас) — второй приоритет, не первый.",
    "LP: 19 объявлений на главную; на главной нет Renault/Peugeot/Citroen. Сделать страницу/блоки топ-5 марок.",
    "Ставки/QS: QS 6,42, 77 ключей с LP ниже; поднять ставки на брендовые ключи.",
])
campaign_slide(CAMP[2],"РЕГУЛИРОВКА","Регулировка фар: ранг, бюджет не трогать",[
    "Бюджет: потеря 7% (0% сейчас) — поднимать бессмысленно.",
    "Ранг: потеря 32,7% — QS 5,38, 13 ключей с LP ниже.",
    "Усилить страницу/заголовки под «регулировка фар»; CPA держать < $4,5.",
    "Топ страницы 49,5%, абс. 27,2% — цель топ 60–70%.",
])
campaign_slide(CAMP[3],"ПРОТОЧКА","Проточка: мало объёма, не бюджет",[
    "Бюджет: 0% — не трогать.",
    "Ранг: 32,7%, на этой неделе 39,9% — расширить ключи/объявления.",
    "7 кликов за неделю — это мало; поднять ставку/IS, дать объём.",
    "QS 6,43, топ-ключи QS 8; CPA $5,26 — держать < $6.",
])

# 7 growth
s=add_slide("ПРИРОСТ","Сколько может дать бюджет, а сколько — ранг")
data=[["Кампания","Рычаг","Сейчас/день","Сценарий","+клики/день","+звонки/день","+звонки/нед","+расход/день"],
      ["Развал","Бюджет","1,71 звонка","lostB 42,6% → 30%","+4,9","+0,42","+3,0","+$1,60"],
      ["Развал","Бюджет","1,71 звонка","lostB 42,6% → 0%","+16,5","+1,43","+10,0","+$5,41"],
      ["СТО - По маркам","Бюджет","2,71 звонка","lostB 14,4% → 0%","+9,6","+0,84","+5,9","+$2,73"],
      ["СТО - По маркам","Ранг","2,71 звонка","lostR 39,2% → 25%","+9,5","+0,83","+5,8","+$2,70"],
      ["Регулировка","Ранг","2,14 звонка","lostR 32,7% → 20%","+4,3","+0,45","+3,2","+$1,74"],
      ["Проточка","Ранг","0,14 звонка","lostR 32,7% → 25%","+0,5","+0,02","+0,1","+$0,25"]]
rows,cols=len(data),len(data[0])
shape=s.shapes.add_table(rows,cols,Inches(0.55),Inches(1.30),Inches(12.2),Inches(2.9)); tbl=shape.table
widths=[1.8,0.95,1.15,1.85,1.2,1.25,1.25,1.25]
for i,w in enumerate(widths): tbl.columns[i].width=Inches(w)
for r in range(rows):
    tbl.rows[r].height=Inches(0.36)
    for c in range(cols):
        cell=tbl.cell(r,c); cell.margin_left=Inches(0.05); cell.margin_right=Inches(0.05)
        cell.margin_top=Inches(0.01); cell.margin_bottom=Inches(0.01); cell.vertical_anchor=MSO_ANCHOR.MIDDLE
        cell.fill.solid(); cell.fill.fore_color.rgb=DARK if r==0 else (WHITE if r%2 else SOFT)
        p=cell.text_frame.paragraphs[0]; p.alignment=PP_ALIGN.RIGHT if c>0 else PP_ALIGN.LEFT
        rr=p.add_run(); rr.text=data[r][c]; rr.font.name=FONT; rr.font.size=Pt(7.6); rr.font.bold=(r==0)
        rr.font.color.rgb=WHITE if r==0 else DARK
bullets(s,0.55,4.45,12.2,2.2,[
    "Развал: бюджет — реальный рычаг. +3 звонка/нед при lostB до 30%; +10/нед только при снятии лимита (нереалистично).",
    "СТО: за 13–21 бюджет и ранг дают ~по +6/нед; но сейчас бюджет 6,2% → подъём бюджета даст ~2–3/нед, ранг 36,6% → ~6/нед. Сначала LP/QS.",
    "Регулировка: бюджет 0, только ранг: +2–3/нед. Проточка: ранг +0,1/нед — сначала объём.",
    "Оценка при сохранении CTR/CR/CPC; не гарантия.",
],size=9.2,gap=7)

# 8 rank + LP
s=add_slide("РАНГ И LP","Почему теряем ранг и что чинить на страницах")
bullets(s,0.55,1.30,6.0,5.5,[
    "Ранг = Ad Rank: ставка × Quality Score + активы. «Потеря по рангу» — вас обошли по ставке/качеству, а не по бюджету.",
    "СТО: QS 6,42, но 77 ключей с LP ниже среднего; 19 объявлений на главную; на главной нет Renault, Peugeot, Citroen — только VW/BMW. Человек ищет «СТО Renault», а видит общую страницу.",
    "Конкуренты: tonymotors обходит в 84,3% пересечений, nv-service — 45,9%. Ставка $0,28 низкая для брендовых аукционов.",
    "Регулировка: QS 5,38, 13 ключей с LP ниже; страница сильная (1000 слов, цены, отзывы, FAQ, 3 формы), но ad relevance/ставка слабее. Бюджет 0 — поднимать бессмысленно.",
],size=9.2,gap=8)
bullets(s,6.85,1.30,5.9,5.5,[
    "LP = landing page. Сервисные страницы сильные: H1, цена, процесс, отзывы, FAQ, 3 формы, 19 изображений, ~1000 слов. Переделывать с нуля не надо.",
    "Главная: 1603 слова, 74 изображения, 4 формы — но бренды только VW/BMW. Для 19 брендовых запросов это нерелевантно.",
    "Что сделать: страница «СТО по маркам» или брендовые блоки для топ-5 (Renault, Peugeot, Citroen, Opel, Ford): модели, услуги, цены, мастера, отзывы, фото. Одна страница — тест, не 19 сразу.",
    "Для сервисных страниц: H1 с точной фразой, цена выше, schema FAQ, мобильная скорость, форма в первом экране. Цель — топ страницы 70–80%, не абсолютный топ.",
],size=9.2,gap=8)

# 9 auction aggregate
s=add_slide("АУКЦИОН","Аукцион за 30 дней: мы первые по доле, но не по абсолютному топу")
data1=[["Конкурент","Доля","Пересеч.","Выше","Топ","Абс. топ","Выигрыши"],
       ["Вы","45,3%","—","—","83,2%","29,0%","—"],
       ["развал-схождение.бел","14,9%","17,0%","52,7%","77,5%","29,3%","41,2%"],
       ["carlife.by","14,8%","21,7%","21,2%","61,2%","5,0%","43,2%"],
       ["autoprofi.by","13,3%","13,9%","57,2%","83,8%","34,3%","41,7%"],
       ["venimotors.by","12,7%","13,5%","67,7%","90,1%","40,3%","41,1%"],
       ["vsesto.by","10,4%","15,3%","17,9%","73,1%","3,2%","44,0%"]]
rows,cols=len(data1),len(data1[0]); shape=s.shapes.add_table(rows,cols,Inches(0.55),Inches(1.30),Inches(7.55),Inches(3.4)); tbl=shape.table
widths=[2.35,0.8,0.85,0.8,0.8,0.9,0.95]
for i,w in enumerate(widths): tbl.columns[i].width=Inches(w)
for r in range(rows):
    tbl.rows[r].height=Inches(0.40)
    for c in range(cols):
        cell=tbl.cell(r,c); cell.margin_left=Inches(0.05); cell.margin_right=Inches(0.04)
        cell.margin_top=Inches(0.01); cell.margin_bottom=Inches(0.01); cell.vertical_anchor=MSO_ANCHOR.MIDDLE
        cell.fill.solid(); cell.fill.fore_color.rgb=DARK if r==0 else (RGBColor(0xFB,0xE9,0xE7) if r==1 else (WHITE if r%2 else SOFT))
        p=cell.text_frame.paragraphs[0]; p.alignment=PP_ALIGN.RIGHT if c>0 else PP_ALIGN.LEFT
        rr=p.add_run(); rr.text=data1[r][c]; rr.font.name=FONT; rr.font.size=Pt(8.0); rr.font.bold=(r==0 or r==1)
        rr.font.color.rgb=WHITE if r==0 else DARK
data2=[["СТО-По маркам","Доля","Выше","Абс. топ"],
       ["Вы","42,1%","—","14,8%"],
       ["tonymotors.by","21,6%","84,3%","30,8%"],
       ["nv-service.by","17,8%","45,9%","10,8%"],
       ["vsesto.by","13,9%","26,8%","2,2%"]]
rows,cols=len(data2),len(data2[0]); shape=s.shapes.add_table(rows,cols,Inches(8.30),Inches(1.30),Inches(4.40),Inches(2.2)); tbl=shape.table
widths=[1.7,0.75,0.9,0.9]
for i,w in enumerate(widths): tbl.columns[i].width=Inches(w)
for r in range(rows):
    tbl.rows[r].height=Inches(0.36)
    for c in range(cols):
        cell=tbl.cell(r,c); cell.margin_left=Inches(0.05); cell.margin_right=Inches(0.04)
        cell.margin_top=Inches(0.01); cell.margin_bottom=Inches(0.01); cell.vertical_anchor=MSO_ANCHOR.MIDDLE
        cell.fill.solid(); cell.fill.fore_color.rgb=DARK if r==0 else (RGBColor(0xFB,0xE9,0xE7) if r==1 else (WHITE if r%2 else SOFT))
        p=cell.text_frame.paragraphs[0]; p.alignment=PP_ALIGN.RIGHT if c>0 else PP_ALIGN.LEFT
        rr=p.add_run(); rr.text=data2[r][c]; rr.font.name=FONT; rr.font.size=Pt(8.2); rr.font.bold=(r==0 or r==1)
        rr.font.color.rgb=WHITE if r==0 else DARK
bullets(s,0.55,5.0,12.2,1.7,[
    "У нас 45,3% показов, но абсолютный топ 29,0% против 40,3% у venimotors и 34,3% у autoprofi.",
    "Конкуренты обходят в 52–68% пересечений: мы на странице, но не выше них. Это и есть потеря по рангу.",
    "Абсолютный топ не цель: цель — топ страницы 70–80%. Рост — через QS/ставку на «развал» и «регулировку», не через бюджет.",
],size=9.2,gap=6)
text(s,0.55,6.75,12.2,0.22,"30 дней, UI. Дневные имена конкурентов API не отдаёт; дневные столбики выше — наши IS/top/abs.",7.4,False,RGBColor(0x6E,0x6E,0x73))

# 10 plan
s=add_slide("ПЛАН","Что делать: по одной кампании, без «всё сразу»")
cards=[("РАЗВАЛ","бюджет",["+20–30% бюджета: lostB 42,6% → 30%.","+3 звонка/нед, +$1,6/день.","LP/QS — вторым шагом; цель CPA < $5,5."]),
       ("СТО - ПО МАРКАМ","ранг + LP",["Страница/блоки топ-5 марок: Renault, Peugeot, Citroen, Opel, Ford.","Поднять ставки на брендовые ключи.","Бюджет — после LP/QS; цель CPA < $4,5."]),
       ("РЕГУЛИРОВКА","ранг",["Бюджет не трогать: lostB 0%.","LP/заголовки: QS 5,38, 13 LP ниже.","Цель +2–3 звонка/нед, CPA < $4,5."]),
       ("ПРОТОЧКА","объём",["Бюджет не трогать: lostB 0%.","Расширить ключи/объявления.","Цель 15–20 кликов/нед, CPA < $6."])]
for i,(name,lever,items) in enumerate(cards):
    x=0.55+i*3.12
    box=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(x),Inches(1.40),Inches(2.95),Inches(4.25))
    box.adjustments[0]=0.04; box.fill.solid(); box.fill.fore_color.rgb=WHITE; box.line.color.rgb=LINE
    head=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(1.40),Inches(2.95),Inches(0.08))
    head.fill.solid(); head.fill.fore_color.rgb=RED; head.line.fill.background()
    text(s,x+0.14,1.58,2.65,0.25,name,8.8,True,DARK)
    text(s,x+0.14,1.86,2.65,0.22,lever.upper(),7.4,True,RED)
    bullets(s,x+0.14,2.20,2.65,3.2,items,size=8.0,gap=6)
text(s,0.55,5.95,12.2,0.55,"Абсолютный топ не цель. Цель — топ страницы 70–80% и CPA по звонку.",9.5,True,RED)

# 11 data
s=add_slide("ДАННЫЕ","Что учтено и ограничения")
bullets(s,0.55,1.35,6.0,4.9,[
    "8–21 октября; 17–18 кампании не работали, 22 октября без расхода.",
    "4 активные кампании: Развал, СТО-По маркам, Регулировка, Проточка.",
    "Звонки = «Исходящий клик» (клик по номеру). 13–21: 47; 30 дней: 58.",
    "CPA = расход / звонки; в дни без звонков CPA нет.",
    "Качество — по ключам с данными; у части ключей QS нет.",
],size=9.8,gap=8)
bullets(s,6.85,1.35,5.9,4.9,[
    "Дневные IS/top/abs — API. Имена конкурентов и «процент выигрышей» — UI за 30 дней.",
    "Прирост — оценка при сохранении CTR/CR/CPC; не гарантия.",
    "LP-аудит: 4 страницы, H1/H2, объём, формы, бренды. Сервисные страницы сильные, главная — нет.",
    "19 объявлений на главную — только СТО-По маркам; 31 — все, включая паузу.",
    "В аккаунте ничего не менял.",
],size=9.8,gap=8)

# 12. patterns
s = add_slide("ЗАКОНОМЕРНОСТИ", "6 паттернов, которые не видны в лоб")
text(s,0.55,1.16,12.2,0.28,"По данным 13–21.10 (47 звонков). Это гипотезы, а не приговор; проверять по одному изменению.",8.4,False,RGBColor(0x6E,0x6E,0x73))
cards = [
    ("46 из 47","звонков — с телефона","Desktop: 85 кликов → 1 звонок, CR 1,2%. Мобайл: 442 клика → 46 звонков, CR 10,4%.","Мобайл в приоритет. Десктоп -50% на тест; проверить скорость мобильной."),
    ("83%","звонков с 9 до 14","11:00 — CR 14,4%; 13–14 — 12–13%; 18:00 — 0 звонков. После 16:00 спад.","Dayparting: +20–30% 9–14, -20% после 17. Не судить по целому дню."),
    ("8 / 8","звонков в вторник и среду","Пн — 2 (после паузы), Пт — 6. Вторник/среда — по 8/день.","Усилить Tue/Wed; понедельник не оценивать по первому дню."),
    ("+47% / +39%","расход/день → CPA","СТО: $6,2→$15,4/день, CR 9,8→7,4%. Масштаб даёт CPA выше.","Масштабировать шагами; не включать всё сразу."),
    ("QS 8 / CR 3%","Проточка: качество есть, звонков нет","1 звонок на 33 клика. QS 6,4, топ-ключи QS 8.","Цена/гарантия/оффер, а не бюджет."),
    ("2 → 6 → 8","звонки после паузы","19.10 — 2, 20.10 — 6, 21.10 — 8. Выходные 17–18 выключены.","Ramp 2 дня; тест субботы 9–15, если СТО открыто."),
]
for i,(stat,label,evidence,action) in enumerate(cards):
    x=0.55+(i%3)*4.10; y=1.55+(i//3)*2.35
    box=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(x),Inches(y),Inches(4.00),Inches(2.15))
    box.adjustments[0]=0.04; box.fill.solid(); box.fill.fore_color.rgb=WHITE; box.line.color.rgb=LINE
    text(s,x+0.16,y+0.12,1.55,0.35,stat,17,True,RED)
    text(s,x+0.16,y+0.50,3.65,0.22,label,7.8,True,DARK)
    text(s,x+0.16,y+0.78,3.65,0.62,evidence,7.4,False,RGBColor(0x4A,0x4A,0x4E))
    text(s,x+0.16,y+1.48,3.65,0.55,"→ "+action,7.2,True,RGBColor(0x6E,0x6E,0x73))
text(s,0.55,6.28,12.2,0.55,"Проверять по одному изменению: день/ставка/бюджет/LP. Если менять всё сразу — снова не поймём, что сработало.",9.2,True,RED)

out="/Users/maksim/Desktop/Реклама/03_анализ/ДАСТО_столбики_22.10.2026.pptx"
prs.save(out); print("saved",out,"slides",len(prs.slides))
