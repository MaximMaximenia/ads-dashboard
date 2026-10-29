#!/usr/bin/env python3
import json, os, collections
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION

BG=RGBColor(0xF7,0xF7,0xF5); DARK=RGBColor(0x17,0x18,0x1A); RED=RGBColor(0xD0,0x13,0x0D)
BLUE=RGBColor(0x2F,0x5F,0xB8); GRAY=RGBColor(0x6E,0x6E,0x73); LINE=RGBColor(0xE3,0xE3,0xDF)
WHITE=RGBColor(0xFF,0xFF,0xFF); SOFT=RGBColor(0xEF,0xEF,0xEC); GREEN=RGBColor(0x1F,0x8A,0x4C)
FONT="Arial"

def new(): p=Presentation(); p.slide_width=Inches(13.333); p.slide_height=Inches(7.5); return p
def add(p,kicker,title,footer="Подготовлено 27.10.2026 · без изменений в аккаунте"):
 s=p.slides.add_slide(p.slide_layouts[6]); bg=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,0,0,p.slide_width,p.slide_height)
 bg.fill.solid(); bg.fill.fore_color.rgb=BG; bg.line.fill.background(); bar=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,0,0,Inches(0.10),p.slide_height)
 bar.fill.solid(); bar.fill.fore_color.rgb=RED; bar.line.fill.background()
 t=s.shapes.add_textbox(Inches(0.55),Inches(0.30),Inches(11.8),Inches(0.25)); r=t.text_frame.paragraphs[0].add_run(); r.text=kicker
 r.font.name=FONT; r.font.size=Pt(9); r.font.bold=True; r.font.color.rgb=RED
 t=s.shapes.add_textbox(Inches(0.55),Inches(0.56),Inches(12.2),Inches(0.60)); r=t.text_frame.paragraphs[0].add_run(); r.text=title
 r.font.name=FONT; r.font.size=Pt(23); r.font.bold=True; r.font.color.rgb=DARK
 t=s.shapes.add_textbox(Inches(0.55),Inches(7.12),Inches(12.2),Inches(0.20)); r=t.text_frame.paragraphs[0].add_run(); r.text=footer
 r.font.name=FONT; r.font.size=Pt(8); r.font.color.rgb=GRAY
 return s

def text(s,x,y,w,h,lines,size=11,bold=False,color=DARK,gap=0):
 box=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)); tf=box.text_frame; tf.word_wrap=True
 tf.margin_left=0; tf.margin_right=0; tf.margin_top=0; tf.margin_bottom=0
 for i,line in enumerate(lines if isinstance(lines,list) else lines.split("\n")):
  para=tf.paragraphs[0] if i==0 else tf.add_paragraph(); para.space_after=Pt(gap)
  r=para.add_run(); r.text=line; r.font.name=FONT; r.font.size=Pt(size); r.font.bold=bold; r.font.color.rgb=color

def bullets(s,x,y,w,h,items,size=10,gap=7):
 box=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)); tf=box.text_frame; tf.word_wrap=True
 tf.margin_left=0; tf.margin_right=0; tf.margin_top=0; tf.margin_bottom=0
 for i,item in enumerate(items):
  para=tf.paragraphs[0] if i==0 else tf.add_paragraph(); para.space_after=Pt(gap); para.line_spacing=1.02
  r0=para.add_run(); r0.text="●  "; r0.font.name=FONT; r0.font.size=Pt(size-3); r0.font.color.rgb=RED
  r=para.add_run(); r.text=item; r.font.name=FONT; r.font.size=Pt(size); r.font.color.rgb=DARK

def kpi(s,x,y,w,val,label,dark=False):
 card=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(1.0)); card.adjustments[0]=0.10
 card.fill.solid(); card.fill.fore_color.rgb=DARK if dark else WHITE; card.line.color.rgb=DARK if dark else LINE
 t=s.shapes.add_textbox(Inches(x+0.16),Inches(y+0.10),Inches(w-0.32),Inches(0.44)); r=t.text_frame.paragraphs[0].add_run(); r.text=val
 r.font.name=FONT; r.font.size=Pt(25); r.font.bold=True; r.font.color.rgb=WHITE if dark else RED
 t=s.shapes.add_textbox(Inches(x+0.16),Inches(y+0.62),Inches(w-0.32),Inches(0.25)); r=t.text_frame.paragraphs[0].add_run(); r.text=label
 r.font.name=FONT; r.font.size=Pt(9); r.font.color.rgb=RGBColor(0xD9,0xD9,0xD9) if dark else GRAY

def table(s,x,y,w,h,data,widths=None,font=8.5,header_font=8.0,row_h=0.35,hl=None):
 rows,cols=len(data),len(data[0]); shape=s.shapes.add_table(rows,cols,Inches(x),Inches(y),Inches(w),Inches(h)); tbl=shape.table
 if widths:
  for i,cw in enumerate(widths): tbl.columns[i].width=Inches(cw)
 for r in range(rows):
  tbl.rows[r].height=Inches(row_h)
  for c in range(cols):
   cell=tbl.cell(r,c); cell.margin_left=Inches(0.05); cell.margin_right=Inches(0.05)
   cell.margin_top=Inches(0.01); cell.margin_bottom=Inches(0.01); cell.vertical_anchor=MSO_ANCHOR.MIDDLE; cell.fill.solid()
   if r==0: cell.fill.fore_color.rgb=DARK
   elif hl and r==hl: cell.fill.fore_color.rgb=RGBColor(0xE3,0xF2,0xE6)
   else: cell.fill.fore_color.rgb=WHITE if r%2 else SOFT
   p=cell.text_frame.paragraphs[0]; p.alignment=PP_ALIGN.RIGHT if c>0 else PP_ALIGN.LEFT
   rr=p.add_run(); rr.text=str(data[r][c]); rr.font.name=FONT; rr.font.size=Pt(header_font if r==0 else font); rr.font.bold=(r==0)
   rr.font.color.rgb=WHITE if r==0 else DARK

def chart(s,x,y,w,h,cats,vals,title,ymax=20):
 cd=CategoryChartData(); cd.categories=cats; cd.add_series("Звонки",tuple(vals))
 ch=s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,Inches(x),Inches(y),Inches(w),Inches(h),cd).chart
 ch.has_legend=False; ch.font.name=FONT; ch.font.size=Pt(8); ch.has_title=True; ch.chart_title.text_frame.text=title
 for p in ch.chart_title.text_frame.paragraphs:
  for r in p.runs: r.font.size=Pt(9); r.font.bold=True; r.font.name=FONT; r.font.color.rgb=DARK
 ch.value_axis.maximum_scale=ymax; ch.value_axis.minimum_scale=0; ch.value_axis.has_major_gridlines=True
 ch.value_axis.major_gridlines.format.line.color.rgb=RGBColor(0xE8,0xE8,0xE4)
 ch.value_axis.tick_labels.font.size=Pt(7); ch.category_axis.tick_labels.font.size=Pt(7)
 ch.series[0].format.fill.solid(); ch.series[0].format.fill.fore_color.rgb=RED; ch.series[0].format.line.fill.background()
 ch.plots[0].gap_width=45; ch.plots[0].has_data_labels=True
 dl=ch.plots[0].data_labels; dl.font.size=Pt(7); dl.font.name=FONT; dl.number_format='0'; dl.number_format_is_linked=False

def title_slide(p,kicker,title,sub,footer):
 s=p.slides.add_slide(p.slide_layouts[6]); bg=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,0,0,p.slide_width,p.slide_height)
 bg.fill.solid(); bg.fill.fore_color.rgb=DARK; bg.line.fill.background()
 bar=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(0.70),Inches(1.25),Inches(0.12),Inches(3.95)); bar.fill.solid(); bar.fill.fore_color.rgb=RED; bar.line.fill.background()
 text(s,1.05,1.20,10.8,0.30,kicker,11,True,RED); text(s,1.05,1.65,10.8,1.0,title,42,True,WHITE)
 text(s,1.05,3.35,10.8,0.75,sub,18,False,RGBColor(0xE6,0xE6,0xE6))
 line=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(1.05),Inches(5.15),Inches(5.0),Inches(0.02)); line.fill.solid(); line.fill.fore_color.rgb=RGBColor(0x3A,0x3A,0x3C); line.line.fill.background()
 text(s,1.05,5.33,10.8,0.30,footer,10,False,RGBColor(0xB9,0xB9,0xB9))

# ---------------- DASTO ----------------
p=new(); title_slide(p,"GOOGLE ADS / ДАСТО - СТО","ДАСТО: неделя\nпосле Max Conversions","13–26 октября 2026\n5 кампаний · понедельник 26.10 · рост к 20 заявкам","Подготовлено 27.10.2026 · без изменений в аккаунте")

s=add(p,"ГЛАВНОЕ","Что изменилось: заявки вверх, CPA вниз")
kpi(s,0.55,1.35,2.8,"45","заявок 19–25.10",False)
kpi(s,3.50,1.35,2.8,"$3,67","CPA 19–25.10",True)
kpi(s,6.45,1.35,2.8,"10,2%","конверсия 19–25.10")
kpi(s,9.40,1.35,3.0,"13","заявок в пн 26.10")
bullets(s,0.55,2.72,6.0,3.9,[
 "13–19.10: 40 заявок, CPA $4,02, конверсия 9,2%.",
 "19–25.10: 45 заявок, CPA $3,67, конверсия 10,2%. Расход почти тот же: $161 → $165.",
 "20–23.10 (Вт–Пт): 42 заявки, CPA $3,17, конверсия 12,0% — вот эффект после смены стратегии.",
 "26.10: 13 заявок, CPA $2,32, конверсия 17,1% — лучший понедельник.",
],size=9.8,gap=8)
text(s,6.85,2.72,5.9,0.30,"ЧТО ЭТО ЗНАЧИТ",9.2,True,RED)
bullets(s,6.85,3.05,5.9,3.5,[
 "Max Conversions не сломал экономику: 45 против 40 заявок, CPA $4,02 → $3,67.",
 "20–23.10 без плохого понедельника: CPA $3,17, конверсия 12,0% — сильнее.",
 "В конверсиях 20–26 есть 5 кликов Instagram; для обучения Max Conversions это шум.",
],size=9.5,gap=7)

s=add(p,"НЕДЕЛИ","Недели: заявки, цена клика, CPA, расход")
w=[["Неделя","Заявки","Клики","Цена клика","Конверсия","CPA","Расход"],
   ["05–11.10 (06–09)","9","149","$0,46","6,0%","$7,68","$69,16"],
   ["12–18.10","33","338","$0,33","9,8%","$3,37","$111,18"],
   ["19–25.10","45","442","$0,37","10,2%","$3,67","$165,07"],
   ["Итого 06–25.10","87","929","$0,37","9,4%","$3,97","$345,41"]]
table(s,0.55,1.35,12.2,2.3,w,widths=[2.6,1.1,1.0,1.6,1.7,1.5,1.7],font=9.5,header_font=8.5,row_h=0.40,hl=3)
bullets(s,0.55,4.0,12.2,2.5,[
 "Лучшая неделя — 12–18.10: 33 заявки, CPA $3,37, конверсия 9,8%.",
 "19–25.10: 45 заявок, CPA $3,67 — объём вырос, но CPA выше из-за понедельника 19.10.",
 "05–11 — только 4 дня (06–09), 9 заявок; 26.10 — отдельный понедельник: 13 заявок.",
],size=10.5,gap=8)
chart(s,8.45,4.0,4.3,2.4,["13","14","15","16","19","20","21","22","23","26","27"],[11,10,7,9,3,7,10,9,16,13,2],"Заявки по дням",18)

s=add(p,"ПН–ПТ И ПОНЕДЕЛЬНИКИ","Понедельник 26.10 — сильнее, чем 19.10")
m=[["Период","Заявки","Клики","Цена клика","Конверсия","CPA","Расход"],
   ["13–17.10, Пн–Пт","37","344","$0,38","10,8%","$3,49","$128,99"],
   ["19–23.10, Пн–Пт","45","442","$0,37","10,2%","$3,67","$165,07"],
   ["20–23.10, Вт–Пт","42","349","$0,38","12,0%","$3,17","$133,29"],
   ["19.10, понедельник","3","93","$0,34","3,2%","$10,59","$31,78"],
   ["26.10, понедельник","13","76","$0,40","17,1%","$2,32","$30,11"]]
table(s,0.55,1.35,12.2,2.55,m,widths=[2.7,1.1,1.0,1.55,1.55,1.5,1.6],font=9.4,header_font=8.4,row_h=0.40,hl=5)
bullets(s,0.55,4.22,12.2,2.5,[
 "Пн–Пт 19–23 хуже 13–17 по CPA ($3,67 vs $3,49) — потому что в понедельник 19 было 3 заявки.",
 "Вт–Пт 20–23: 42 заявки, CPA $3,17, конверсия 12,0% — вот эффект после смены стратегии.",
 "26.10: 13 заявок, CPA $2,32. 19.10: 3 заявки, CPA $10,59. Разница огромная, но 19-е — после паузы.",
],size=9.8,gap=8)

s=add(p,"КАМПАНИИ","Что сейчас работает и где узкие места")
c=[["Кампания","Ставки","Бюджет","Заявки","Расход","CPA","Конв.","lostB","lostR"],
   ["СТО - По маркам","Max Conv","$10","26","$65,58","$2,52","14,9%","14%","31%"],
   ["Регулировка фар","Max Conv","$10","17","$45,73","$2,69","14,9%","0%","36%"],
   ["СТО - Общая","Max Clicks","$5","5","$15,67","$3,13","11,1%","12%","63%"],
   ["Развал-схождение","Max Conv","$10","7","$31,71","$4,53","8,6%","18%","27%"],
   ["Ремонт подвески","Max Conv","$6","0","$1,21","—","0%","0%","88%"]]
table(s,0.55,1.35,12.2,2.65,c,widths=[2.5,1.2,0.95,0.9,1.0,0.9,0.9,0.9,0.9],font=8.8,header_font=8.0,row_h=0.40,hl=1)
bullets(s,0.55,4.25,6.0,2.5,[
 "СТО-По маркам — главный драйвер: 26 заявок, CPA $2,52; есть потеря по бюджету 14%.",
 "Регулировка: 17 заявок, CPA $2,69, потеря только по рангу 36% — можно поднимать ставки/QS.",
 "Развал: CPA $4,53, потеря по бюджету 18% — дороже, но ещё есть объём.",
],size=9.2,gap=7)
bullets(s,6.85,4.25,5.9,2.5,[
 "СТО-Общая: 5 заявок, CPA $3,13, но потеря по рангу 63% — слабая видимость.",
 "Подвеска: 10 показов, 3 клика, 0 заявок, потеря по рангу 88% — кампания фактически не работает.",
 "Что чинить: Подвеска — LP/ставки или пауза; СТО-Общая — ранг/объявления.",
],size=9.2,gap=7)

s=add(p,"РОСТ","Как дойти до 20 заявок в день")
kpi(s,0.55,1.35,2.8,"9–13","сейчас в день")
kpi(s,3.50,1.35,2.8,"20","цель в день",True)
kpi(s,6.45,1.35,2.8,"+$30–40","нужно в день")
kpi(s,9.40,1.35,3.0,"+90–120%","кликов")
bullets(s,0.55,2.75,6.0,3.8,[
 "19–25.10: 45 заявок за 5 рабочих дней = 9/день; 20–23.10 — 10,5/день; 26.10 — 13.",
 "Цель 20/день: +7–11 заявок в день (+54–122%).",
 "При CPA $3,17–3,67: 20 заявок = $63–73/день. Сейчас $33/день. Нужно +$30–40/день.",
 "По кликам: 20 / 10–12% = 167–196 кликов/день. Сейчас 85–88. Нужно +90–120%.",
],size=9.6,gap=8)
bullets(s,6.85,2.75,5.9,3.8,[
 "Бюджеты сейчас $41/день, фактически $33. Поднять СТО-По маркам и Регулировку — там лучший CPA.",
 "Подвеска не даст роста: 10 показов, потеря по рангу 88%. Сначала починить или выключить.",
 "План: 15 → 18 → 20 заявок. На каждом шаге смотреть CPA; если CPA > $4 — стоп/откат.",
 "Без роста конверсии 20/день потребуют почти вдвое больше кликов.",
],size=9.6,gap=8)

s=add(p,"ЭКОНОМИКА","Экономика по услугам: где считаем, где нет")
e=[["Кампания / услуга","Заявки","CPA","Конверсия","Средний чек","Маржа","Что нужно"],
   ["СТО - По маркам","26","$2,52","14,9%","—","—","цена/маржа по маркам"],
   ["Регулировка фар","17","$2,69","14,9%","—","—","цена регулировки"],
   ["СТО - Общая","5","$3,13","11,1%","—","—","что входит в СТО"],
   ["Развал-схождение","7","$4,53","8,6%","—","—","цена развала"],
   ["Полировка фар","—","—","—","—","—","нет отдельной кампании/ключей"]]
table(s,0.55,1.35,12.2,2.7,e,widths=[2.6,1.0,0.9,1.1,1.3,1.0,2.4],font=9.0,header_font=8.2,row_h=0.42)
bullets(s,0.55,4.25,6.0,2.5,[
 "CPA по услугам уже разный: от $2,52 до $4,53. Это не значит, что Развал хуже — зависит от чека и маржи.",
 "Полировка фар в запросах и кампаниях не выделена. Если это отдельная услуга — нужна отдельная группа/кампания, иначе экономику не посчитать.",
 "Формула: допустимый CPA = прибыль с заявки × конверсия в визит/сделку.",
],size=9.2,gap=7)
bullets(s,6.85,4.25,5.9,2.5,[
 "Пришли цены/маржу по услугам — соберу таблицу «заявка → выручка → прибыль → допустимый CPA».",
 "Пока видно: СТО-По маркам и Регулировка дешевле всех по заявке; их можно масштабировать первыми.",
 "Развал дороже, но может быть выгоднее по чеку — нужна экономика, не только CPA.",
],size=9.2,gap=7)

s=add(p,"ЧТО УЛУЧШИТЬ","Max Conversions: что не сломать дальше")
bullets(s,0.55,1.35,6.0,4.9,[
 "4 из 5 кампаний на Max Conversions. 19–25: заявки 40 → 45, CPA $4,02 → $3,67, конверсия 9,2% → 10,2%.",
 "20–23.10 без понедельника 19: 42 заявки, CPA $3,17, конверсия 12,0% — лучший отрезок.",
 "В конверсиях 20–26 есть 5 кликов Instagram; если это не заявки — перевести в наблюдаемые.",
 "Подвеска: 10 показов, 3 клика, 0 заявок, потеря по рангу 88%. Починить LP/ставки или выключить.",
 "СТО-Общая: 5 заявок, потеря по рангу 63% — слабая видимость; нужно качество/ставки.",
],size=9.5,gap=8)
bullets(s,6.85,1.35,5.9,4.9,[
 "Проверить, что Max Conversions не режет лучшие кампании: у СТО-По маркам потеря по бюджету 14% — есть куда расти.",
 "Не масштабировать всё сразу: сначала СТО-По маркам и Регулировка, потом Развал.",
 "Добавить цель «заявка» с ценностью; иначе Max Conversions оптимизирует клики.",
 "Считать экономику по услугам, а не только CPA.",
],size=9.5,gap=8)

p.save("/Users/maksim/Desktop/Реклама/03_анализ/ДАСТО_27.10.2026.pptx")

# ---------------- YOUTUBE ----------------
p=new(); title_slide(p,"YOUTUBE / IN-FEED","YouTube: первая заявка\nи что это значит","21–27 октября 2026\n12 880 показов · 42 клика · $21,53","Подготовлено 27.10.2026")

s=add(p,"ИТОГ","Первая заявка есть, но в Google Ads её нет")
kpi(s,0.55,1.35,2.8,"12 880","показов 21–27.10")
kpi(s,3.50,1.35,2.8,"42","клика",False)
kpi(s,6.45,1.35,2.8,"$21,53","расход",True)
kpi(s,9.40,1.35,3.0,"1","заявка (Метрика/CRM)")
bullets(s,0.55,2.75,6.0,3.8,[
 "Кампания разогналась: 22.10 — 208 показов, 26.10 — 5 789, 27.10 — 2 614.",
 "42 клика, CTR 0,33%, средняя цена клика $0,51.",
 "В Google Ads конверсий 0: заявка не привязана к кампании.",
 "Если заявка одна и расход $21,53 — CPL около $21,53, но это не подтверждённая атрибуция.",
],size=9.6,gap=8)
bullets(s,6.85,2.75,5.9,3.8,[
 "Цель кампании — «Просмотры видео», а не заявки. Алгоритм не знает о лиде.",
 "UTM: utm_source=youtube, utm_medium=video, utm_campaign=infeed_test.",
 "В Метрике за 21–27: 236 визитов, 212 — переходы по рекламе.",
 "Чтобы найти заявку: смотреть цель «форма/звонок» и UTM в Метрике/CRM.",
],size=9.6,gap=8)

s=add(p,"ДНИ","YouTube: как разгонялась кампания")
d=[["Дата","Показы","Клики","Расход","Заявки"],
   ["21.10","2","0","$0,00","0"],
   ["22.10","208","0","$0,19","0"],
   ["23.10","561","1","$0,35","0"],
   ["24.10","901","2","$0,99","0"],
   ["25.10","2 807","6","$4,16","0"],
   ["26.10","5 789","22","$10,12","1?"],
   ["27.10","2 614","11","$5,72","—"]]
table(s,0.55,1.35,6.4,3.2,d,widths=[1.0,1.2,0.9,1.1,1.2],font=9.2,header_font=8.2,row_h=0.38)
bullets(s,7.25,1.35,5.5,4.8,[
 "До 25.10 кампания почти не откручивалась: 2–900 показов.",
 "26.10 — скачок: 5 789 показов, 22 клика, $10,12.",
 "27.10 — ещё 2 614 показов, 11 кликов, $5,72.",
 "Заявка, вероятно, 26–27.10; в Ads она не отражена.",
 "Кампания остаётся на Target CPV $0,05; фактическая ставка $0,01.",
],size=9.4,gap=8)

s=add(p,"МЕТРИКА","Откуда заявка: что проверить в Метрике")
bullets(s,0.55,1.35,6.0,4.9,[
 "Счётчик: 113657567 (coordinat.pro). За 21–27: 236 визитов, 212 — по рекламе, 19 — прямые, 5 — ссылки.",
 "В Google Ads по YouTube 0 конверсий — заявка не привязана. Это не значит, что её не было.",
 "UTM: youtube / video / infeed_test. В Метрике смотреть «Источники» → UTM Source / UTM Campaign.",
 "Цель: «Отправка формы» или «Клик по телефону». Если цели нет — заявку не увидим.",
],size=9.4,gap=8)
bullets(s,6.85,1.35,5.9,4.9,[
 "Найди в Метрике визит с utm_source=youtube и целью «форма/звонок» — это и будет доказательство.",
 "Если заявка пришла с формы, проверь, передаёт ли форма UTM в CRM/Telegram.",
 "Без этого нельзя сказать, YouTube это или другой источник; в Ads атрибуции нет.",
 "Скинь текст заявки/скрин из Метрики — сверю источник и время.",
],size=9.4,gap=8)
text(s,0.55,6.15,12.2,0.35,"Метрика доступна, но API-токена нет — смотрел интерфейс. Точную заявку по UTM нужно открыть в отчёте.",7.2,False,GRAY)

s=add(p,"ЧТО ДЕЛАТЬ","YouTube: как превратить первую заявку в систему")
bullets(s,0.55,1.35,6.0,4.9,[
 "1. Добавить конверсию: отправка формы и клик по телефону на coordinat.pro. Без неё Max Conversions/оптимизация невозможны.",
 "2. Поставить цель «Заявка», а не «Просмотры видео»; иначе алгоритм покупает просмотры.",
 "3. Оставить Target CPV $0,05; при необходимости поднять до $0,07–0,10.",
 "4. Расширить 20 каналов/10 ключей, если после 10 000 показов мало кликов.",
],size=9.5,gap=8)
bullets(s,6.85,1.35,5.9,4.9,[
 "5. Не масштабировать бюджет, пока нет 3–5 заявок и понятной CPL.",
 "6. Смотреть не клики, а заявки/CPL; сейчас 42 клика и 1 заявка — выборка мала.",
 "7. Проверить, что форма на coordinat.pro передаёт UTM и источник в CRM/Telegram.",
 "8. После 10–15 заявок — решить, масштабировать или менять креатив/аудиторию.",
],size=9.5,gap=8)

p.save("/Users/maksim/Desktop/Реклама/03_анализ/YouTube_27.10.2026.pptx")
print("saved both")
