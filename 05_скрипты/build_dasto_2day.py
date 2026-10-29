from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION

BG=RGBColor(0xF7,0xF7,0xF5); DARK=RGBColor(0x17,0x18,0x1A); RED=RGBColor(0xD0,0x13,0x0D)
GRAY=RGBColor(0x6E,0x6E,0x73); LINE=RGBColor(0xE3,0xE3,0xDF); WHITE=RGBColor(0xFF,0xFF,0xFF); SOFT=RGBColor(0xEF,0xEF,0xEC)
FONT="Arial"
p=Presentation(); p.slide_width=Inches(13.333); p.slide_height=Inches(7.5)

def add_slide(kicker,title,footer="ДАСТО — СТО · 26–27.10.2026 · без изменений в аккаунте"):
 s=p.slides.add_slide(p.slide_layouts[6]); bg=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,0,0,p.slide_width,p.slide_height)
 bg.fill.solid(); bg.fill.fore_color.rgb=BG; bg.line.fill.background()
 bar=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,0,0,Inches(0.10),p.slide_height); bar.fill.solid(); bar.fill.fore_color.rgb=RED; bar.line.fill.background()
 t=s.shapes.add_textbox(Inches(0.55),Inches(0.30),Inches(12),Inches(0.25)); r=t.text_frame.paragraphs[0].add_run(); r.text=kicker; r.font.name=FONT; r.font.size=Pt(9); r.font.bold=True; r.font.color.rgb=RED
 t=s.shapes.add_textbox(Inches(0.55),Inches(0.56),Inches(12.2),Inches(0.6)); r=t.text_frame.paragraphs[0].add_run(); r.text=title; r.font.name=FONT; r.font.size=Pt(23); r.font.bold=True; r.font.color.rgb=DARK
 t=s.shapes.add_textbox(Inches(0.55),Inches(7.12),Inches(12.2),Inches(0.2)); r=t.text_frame.paragraphs[0].add_run(); r.text=footer; r.font.name=FONT; r.font.size=Pt(8); r.font.color.rgb=GRAY
 return s

def text(s,x,y,w,h,txt,size=11,bold=False,color=DARK):
 box=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)); tf=box.text_frame; tf.word_wrap=True
 tf.margin_left=0; tf.margin_right=0; tf.margin_top=0; tf.margin_bottom=0
 for i,line in enumerate(txt if isinstance(txt,list) else [txt]):
  para=tf.paragraphs[0] if i==0 else tf.add_paragraph(); para.space_after=Pt(4)
  r=para.add_run(); r.text=line; r.font.name=FONT; r.font.size=Pt(size); r.font.bold=bold; r.font.color.rgb=color

def bullets(s,x,y,w,h,items,size=9.6,gap=8):
 box=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)); tf=box.text_frame; tf.word_wrap=True
 tf.margin_left=0; tf.margin_right=0; tf.margin_top=0; tf.margin_bottom=0
 for i,item in enumerate(items):
  para=tf.paragraphs[0] if i==0 else tf.add_paragraph(); para.space_after=Pt(gap); para.line_spacing=1.02
  r0=para.add_run(); r0.text="●  "; r0.font.name=FONT; r0.font.size=Pt(size-3); r0.font.color.rgb=RED
  r=para.add_run(); r.text=item; r.font.name=FONT; r.font.size=Pt(size); r.font.color.rgb=DARK

def kpi(s,x,y,w,val,label,dark=False):
 card=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(1.0)); card.adjustments[0]=0.10
 card.fill.solid(); card.fill.fore_color.rgb=DARK if dark else WHITE; card.line.color.rgb=DARK if dark else LINE
 t=s.shapes.add_textbox(Inches(x+0.15),Inches(y+0.10),Inches(w-0.30),Inches(0.42)); r=t.text_frame.paragraphs[0].add_run(); r.text=val
 r.font.name=FONT; r.font.size=Pt(24); r.font.bold=True; r.font.color.rgb=WHITE if dark else RED
 t=s.shapes.add_textbox(Inches(x+0.15),Inches(y+0.60),Inches(w-0.30),Inches(0.28)); r=t.text_frame.paragraphs[0].add_run(); r.text=label
 r.font.name=FONT; r.font.size=Pt(8.5); r.font.color.rgb=RGBColor(0xD9,0xD9,0xD9) if dark else GRAY

def table(s,x,y,w,h,data,widths,font=8.4,header_font=7.7,row_h=0.34):
 rows,cols=len(data),len(data[0]); shp=s.shapes.add_table(rows,cols,Inches(x),Inches(y),Inches(w),Inches(h)); tbl=shp.table
 for i,cw in enumerate(widths): tbl.columns[i].width=Inches(cw)
 for r in range(rows):
  tbl.rows[r].height=Inches(row_h)
  for c in range(cols):
   cell=tbl.cell(r,c); cell.margin_left=Inches(0.04); cell.margin_right=Inches(0.04); cell.margin_top=Inches(0.01); cell.margin_bottom=Inches(0.01)
   cell.vertical_anchor=MSO_ANCHOR.MIDDLE; cell.fill.solid(); cell.fill.fore_color.rgb=DARK if r==0 else (WHITE if r%2 else SOFT)
   para=cell.text_frame.paragraphs[0]; para.alignment=PP_ALIGN.RIGHT if c>0 else PP_ALIGN.LEFT
   run=para.add_run(); run.text=str(data[r][c]); run.font.name=FONT; run.font.size=Pt(header_font if r==0 else font); run.font.bold=(r==0)
   run.font.color.rgb=WHITE if r==0 else DARK

def chart(s,x,y,w,h):
 cd=CategoryChartData(); cats=['20','21','22','23','24','25','26','27','29','30','31']; cd.categories=cats
 cd.add_series('Факт',(7,10,9,16,0,0,13,16,0,0,0))
 cd.add_series('Прогноз',(0,0,0,0,0,0,0,0,14,14,14))
 ch=s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,Inches(x),Inches(y),Inches(w),Inches(h),cd).chart
 ch.has_legend=True; ch.legend.position=XL_LEGEND_POSITION.BOTTOM; ch.legend.include_in_layout=False; ch.font.name=FONT; ch.font.size=Pt(8)
 ch.has_title=True; ch.chart_title.text_frame.text='Заявки по дням: факт + прогноз 29–31.10'
 for para in ch.chart_title.text_frame.paragraphs:
  for r in para.runs: r.font.size=Pt(10); r.font.bold=True; r.font.name=FONT
 ch.value_axis.maximum_scale=20; ch.value_axis.minimum_scale=0; ch.value_axis.has_major_gridlines=True
 ch.value_axis.major_gridlines.format.line.color.rgb=RGBColor(0xE8,0xE8,0xE4); ch.value_axis.tick_labels.font.size=Pt(7)
 ch.category_axis.tick_labels.font.size=Pt(7); ch.plots[0].gap_width=40; ch.plots[0].overlap=-10
 ch.series[0].format.fill.solid(); ch.series[0].format.fill.fore_color.rgb=RED; ch.series[0].format.line.fill.background()
 ch.series[1].format.fill.solid(); ch.series[1].format.fill.fore_color.rgb=RGBColor(0x9A,0x9A,0x9A); ch.series[1].format.line.fill.background()

def title_slide():
 s=p.slides.add_slide(p.slide_layouts[6]); bg=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,0,0,p.slide_width,p.slide_height)
 bg.fill.solid(); bg.fill.fore_color.rgb=DARK; bg.line.fill.background()
 bar=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(0.70),Inches(1.25),Inches(0.12),Inches(4.0)); bar.fill.solid(); bar.fill.fore_color.rgb=RED; bar.line.fill.background()
 text(s,1.05,1.20,10.8,0.3,"GOOGLE ADS / ДАСТО · 2 ДНЯ",11,True,RED)
 text(s,1.05,1.65,10.8,1.0,"ДАСТО: 26–27 октября\nи прогноз",42,True,WHITE)
 text(s,1.05,3.35,10.8,0.75,"29 заявок · $64,51 · CPA $2,23\nчто растёт, где потери и куда двигаемся",18,False,RGBColor(0xE6,0xE6,0xE6))
 line=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(1.05),Inches(5.15),Inches(5.0),Inches(0.02)); line.fill.solid(); line.fill.fore_color.rgb=RGBColor(0x3A,0x3A,0x3C); line.line.fill.background()
 text(s,1.05,5.33,10.8,0.3,"Подготовлено 28.10.2026 · без изменений в аккаунте",10,False,RGBColor(0xB9,0xB9,0xB9))

# 1
title_slide()
# 2 summary
s=add_slide("ГЛАВНОЕ","29 заявок за 2 дня, CPA $2,23")
kpi(s,0.55,1.35,2.8,"29","заявок 26–27.10",False)
kpi(s,3.50,1.35,2.8,"$64,51","расход",True)
kpi(s,6.45,1.35,2.8,"$2,23","CPA")
kpi(s,9.40,1.35,3.0,"18,9%","конверсия клика")
bullets(s,0.55,2.72,6.0,3.8,[
 "26.10: 13 заявок, $30,11, CPA $2,32.",
 "27.10: 16 заявок, $34,40, CPA $2,15.",
 "Клики: 76 и 77; конверсия 17,1% и 20,8%.",
 "Телефонные звонки: 14 и 12 подтверждённых; вручную по 27-му — 14.",
 "Расход почти ровный, заявки выросли на 23%.",
],size=9.4,gap=7)
text(s,6.85,2.72,5.9,0.3,"КУДА ДВИЖЕМСЯ",9.2,True,RED)
bullets(s,6.85,3.05,5.9,3.6,[
 "Два дня подряд 13–16 заявок — это новый уровень против 10–12 ранее.",
 "CPA $2,23 — ниже прошлой недели ($2,97).",
 "Но 27-е дало 16 заявок при том же расходе — качество выросло.",
 "Главный риск — не деньги, а потеря ранга: 40–69% по кампаниям.",
],size=9.4,gap=7)

# 3 chart
s=add_slide("ДИНАМИКА","Факт 20–27.10 и прогноз 29–31.10")
chart(s,0.55,1.30,8.2,5.35)
bullets(s,9.05,1.40,3.85,4.8,[
 "Факт: 20–27.10, без выходных 24–25.",
 "23-е — 16 заявок, 26-е — 13, 27-е — 16.",
 "Прогноз 29–31.10: 14 в день (база).",
 "Сценарии: 11 / 14 / 17 в день.",
 "Прогноз — по последним активным дням, не ML.",
],size=8.9,gap=6)

# 4 daily table
s=add_slide("ДНИ","26 и 27 октября: все основные метрики")
d=[["День","Показы","Клики","Расход","Заявки","CTR","CPC","CVR","CPA"],
   ["26.10","744","76","$30,11","13","10,2%","$0,396","17,1%","$2,32"],
   ["27.10","598","77","$34,40","16","12,9%","$0,447","20,8%","$2,15"],
   ["Итого","1 342","153","$64,51","29","11,4%","$0,422","18,9%","$2,23"]]
table(s,0.55,1.35,12.2,2.05,d,[1.5,1.3,1.1,1.3,1.2,1.2,1.2,1.2,1.2],font=9.3,header_font=8.0,row_h=0.40)
bullets(s,0.55,3.8,12.2,2.6,[
 "26-е: 13 заявок, CPA $2,32; 27-е: 16 заявок, CPA $2,15.",
 "CTR вырос с 10,2% до 12,9%; CVR — с 17,1% до 20,8%.",
 "Расход +$4,29, заявки +3 — рост не за счёт пропорционального бюджета.",
 "27-е — лучший день по заявкам и CPA за последние 7 дней.",
],size=9.6,gap=8)

# 5 campaigns
s=add_slide("КАМПАНИИ","Кто даёт заявки и кто тормозит")
c=[["Кампания","Заявки","Расход","CPA","CVR","IS","lostB","lostR","Top","Abs top"],
   ["СТО - По маркам","10,0","$24,86","$2,49","21,7%","41%","59%","0%","36%","12%"],
   ["Регулировка фар","10,0","$17,28","$1,73","20,8%","60%","0%","40%","53%","18%"],
   ["СТО - Общая","6,0","$14,09","$2,35","15,0%","28%","14%","57%","21%","10%"],
   ["Развал-схождение","3,0","$7,08","$2,36","18,8%","31%","0%","69%","22%","10%"]]
table(s,0.55,1.35,12.2,2.35,c,[2.3,1.0,1.1,1.1,1.1,0.9,0.9,0.9,0.9,1.0],font=8.6,header_font=7.4,row_h=0.40)
bullets(s,0.55,4.0,6.0,2.5,[
 "СТО-По маркам — лидер по заявкам, но 59% потеряно по бюджету: можно масштабировать.",
 "Регулировка — лучший CPA $1,73; потеря 40% по рангу — есть куда расти.",
 "СТО-Общая — 6 заявок, CPA $2,35, но 57% потеряно по рангу.",
],size=8.9,gap=6)
bullets(s,6.85,4.0,5.9,2.5,[
 "Развал — CPA $2,36, но 69% потеряно по рангу: денег не хватает не из-за бюджета.",
 "Ремонт подвески — 0 заявок, $1,21, 10 показов; фактически не работает.",
 "Главный вывод: масштабировать СТО и Регулировку, чинить ранг Развала/Общей.",
],size=8.9,gap=6)

# 6 losses
s=add_slide("ПОТЕРИ","Деньги или ранг?")
kpi(s,0.55,1.35,2.8,"59%","lostB у СТО-По маркам")
kpi(s,3.50,1.35,2.8,"69%","lostR у Развала",True)
kpi(s,6.45,1.35,2.8,"57%","lostR у СТО-Общей")
kpi(s,9.40,1.35,3.0,"40%","lostR у Регулировки")
bullets(s,0.55,2.75,6.0,3.8,[
 "Бюджет режет только СТО-По маркам: 59% lostB за 2 дня, 48% 27-го.",
 "Развал: 69% потеряно по рангу, бюджет 0 — деньги не помогут.",
 "СТО-Общая: 57% по рангу, 14% по бюджету — сначала ранг/качество.",
],size=9.3,gap=8)
text(s,6.85,2.75,5.9,0.3,"ЧТО ЭТО ЗНАЧИТ",9.2,True,RED)
bullets(s,6.85,3.08,5.9,3.5,[
 "Не размазывать бюджет по всем: СТО-По маркам — первый кандидат на +$5–10/день.",
 "Развал/Общая — не бюджет, а ставки/QS/объявления.",
 "Подвеска — 0 заявок; чинить или выключать.",
 "Рост до 17–20/день требует двух рычагов: бюджет + ранг.",
],size=9.3,gap=7)

# 7 forecast
s=add_slide("ПРОГНОЗ","29–31 октября: три сценария")
f=[["Сценарий","Заявок/день","Заявок за 3 дня","Расход","CPA"],
   ["Осторожный","11","33","$90","$2,73"],
   ["Базовый","14","42","$96","$2,29"],
   ["Оптимистичный","17","51","$112","$2,20"]]
table(s,0.55,1.35,12.2,2.0,f,[2.4,1.8,2.0,1.8,1.5],font=10.0,header_font=8.5,row_h=0.42)
bullets(s,0.55,3.7,6.0,3.0,[
 "База: 14/день = 42 заявки, $96, CPA $2,29.",
 "Осторожный: 11/день = 33, $90, CPA $2,73.",
 "Оптимистичный: 17/день = 51, $112, CPA $2,20.",
 "Прогноз построен по последним активным дням, не гарантия.",
],size=9.6,gap=8)
text(s,6.85,3.7,5.9,0.3,"ЧТО ДОЛЖНО СБЫТЬСЯ",9.2,True,RED)
bullets(s,6.85,4.03,5.9,2.6,[
 "СТО-По маркам: +$5/день и снятие бюджетного потолка.",
 "Регулировка: удержать CPA $1,7–2,0.",
 "Развал/Общая: поднять ранг, иначе прогноз не сбудется.",
 "Контроль: заявки/день, CPA, lostB/lostR.",
],size=9.4,gap=7)

# 8 conclusion
s=add_slide("ВЫВОД","Куда двигаемся дальше")
bullets(s,0.55,1.35,12.2,4.8,[
 "26–27.10: 29 заявок, $64,51, CPA $2,23, CVR 18,9% — это хороший уровень.",
 "Рост 27-го: 16 заявок при $34,40; CPA $2,15 — лучше 26-го.",
 "Первый рычаг: СТО-По маркам — 59% lostB; +$5–10/день, цель 12–14 заявок/день.",
 "Второй рычаг: Регулировка — CPA $1,73, 40% lostR; поднимать ранг, не резать CPA.",
 "Развал и СТО-Общая — ранг/качество; Подвеска — чинить или выключать.",
 "Прогноз 29–31.10: база 42 заявки, $96, CPA $2,29; оптимистично 51, $112, CPA $2,20.",
],size=10.5,gap=10)

p.save("/Users/maksim/Desktop/Реклама/03_анализ/ДАСТО_26-27.10.2026.pptx")
print("saved")
