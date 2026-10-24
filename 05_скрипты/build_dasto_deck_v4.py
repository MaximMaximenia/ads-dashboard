#!/usr/bin/env python3
"""ДАСТО v3: по одной кампании на слайд, столбики по дням."""
import json
import datetime
import math
import os
from PIL import Image, ImageDraw, ImageFont
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
hourly = json.load(open("/Users/maksim/Desktop/Реклама/05_скрипты/dasto_hourly.json"))
ads_raw = json.load(open("/Users/maksim/Desktop/Реклама/05_скрипты/dasto_ads.json"))
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

def kpi_strip(s, vals, y=1.25, h=0.82):
    # vals: list of (value,label)
    n=len(vals); w=1.62; gap=0.10; x0=(13.333-(n*w+(n-1)*gap))/2
    for i,(v,l) in enumerate(vals):
        x=x0+i*(w+gap)
        card=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
        card.adjustments[0]=0.10; card.fill.solid(); card.fill.fore_color.rgb=WHITE; card.line.color.rgb=LINE
        t=s.shapes.add_textbox(Inches(x+0.08),Inches(y+0.05),Inches(w-0.16),Inches(0.30))
        r=t.text_frame.paragraphs[0].add_run(); r.text=v
        r.font.name=FONT; r.font.size=Pt(15); r.font.bold=True; r.font.color.rgb=RED
        t=s.shapes.add_textbox(Inches(x+0.08),Inches(y+h-0.25),Inches(w-0.16),Inches(0.22))
        r=t.text_frame.paragraphs[0].add_run(); r.text=l
        r.font.name=FONT; r.font.size=Pt(6.6); r.font.color.rgb=RGBColor(0x6E,0x6E,0x73)

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
    ch=s.shapes.add_chart(XL_CHART_TYPE.COLUMN_STACKED,Inches(0.55),Inches(2.55),Inches(12.2),Inches(1.55),cd).chart
    chart_base(ch,"Аукцион по дням: что получили и что потеряли",105,'0"%"' )
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
    ch=s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,Inches(0.55),Inches(4.17),Inches(12.2),Inches(1.02),cd).chart
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
    ch.has_legend=False
    ch.series[0].format.fill.solid(); ch.series[0].format.fill.fore_color.rgb=color
    ch.series[0].format.line.fill.background()
    ch.plots[0].gap_width=45
    ch.plots[0].has_data_labels=True
    dl=ch.plots[0].data_labels; dl.font.size=Pt(5.7); dl.font.name=FONT
    dl.number_format=('$0.00' if key=="cpa" else '0.0'); dl.number_format_is_linked=False
    dl.position=XL_LABEL_POSITION.OUTSIDE_END

def period_stats(c):
    ds=[d for d in sorted(by[c]) if "2026-10-13"<=d<="2026-10-21"]
    impr=sum(by[c][d]["impr"] for d in ds); cl=sum(by[c][d]["cl"] for d in ds)
    cost=sum(by[c][d]["cost"] for d in ds); conv=sum(by[c][d]["conv"] for d in ds)
    def w(k): return sum(by[c][d][k]*by[c][d]["impr"] for d in ds)/impr if impr else 0
    return dict(impr=impr,cl=cl,cost=cost,conv=conv,cpa=cost/conv if conv else 0,
                is_=w("is"),lostb=w("lostb"),lostr=w("lostr"),top=w("top"),abs=w("abs"))


CHART_DIR="/Users/maksim/Desktop/Реклама/05_скрипты/charts"
os.makedirs(CHART_DIR, exist_ok=True)
FONT_REG="/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BOLD="/System/Library/Fonts/Supplemental/Arial Bold.ttf"

def _font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)

def _combo(path, labels, calls, prices, left_max, right_max, price_fmt, legend_price, final=False, avg=None, axis_fmt=None):
    w,h=(2400,900) if final else (2400,550)
    im=Image.new("RGBA",(w,h),(0,0,0,0)); d=ImageDraw.Draw(im)
    ml,mr,mt,mb=(170,190,80,90) if final else (150,180,60,80)
    pw=w-ml-mr; ph=h-mt-mb
    left=ml; right=w-mr; top=mt; bottom=h-mb
    grid=(227,227,223,255); axis=(120,120,124,255); dark=(23,24,26,255); red=(208,19,13,255); blue=(47,95,184,255); gray=(110,110,114,255)
    # grid + axes
    steps=4
    for i in range(steps+1):
        y=top+ph*i/steps
        d.line([(left,y),(right,y)],fill=grid,width=2)
        lv=left_max*(steps-i)/steps
        rv=right_max*(steps-i)/steps
        d.text((left-18,y),f"{lv:.0f}",font=_font(22 if final else 20),fill=gray,anchor="rm")
        d.text((right+18,y),(axis_fmt or price_fmt)(rv),font=_font(22 if final else 20),fill=gray,anchor="lm")
    d.line([(left,top),(left,bottom)],fill=axis,width=2)
    d.line([(right,top),(right,bottom)],fill=axis,width=2)
    d.line([(left,bottom),(right,bottom)],fill=axis,width=2)
    n=len(labels); step=pw/max(n,1); bw=step*0.34
    for i,(lab,c,p) in enumerate(zip(labels,calls,prices)):
        x=left+step*(i+0.5)
        bh=ph*min(c/left_max,1)
        if bh>0:
            d.rectangle([x-bw/2,bottom-bh,x+bw/2,bottom],fill=red)
            d.text((x,bottom-bh-8),f"{c:.0f}" if abs(c-round(c))<0.05 else f"{c:.1f}",font=_font(22 if final else 20),fill=dark,anchor="mb")
        d.text((x,bottom+16),lab,font=_font(24 if final else 21),fill=dark,anchor="ma")
    pts=[]
    for i,p in enumerate(prices):
        if p is None: pts.append(None); continue
        x=left+step*(i+0.5); y=top+ph*(1-min(p/right_max,1)); pts.append((x,y))
    for i in range(1,len(pts)):
        if pts[i-1] and pts[i]:
            d.line([pts[i-1],pts[i]],fill=blue,width=5 if final else 4)
    for i,p in enumerate(pts):
        if not p: continue
        x,y=p; r=8 if final else 6
        d.ellipse([x-r,y-r,x+r,y+r],fill=blue)
        txt=price_fmt(prices[i]); fnt=_font(19 if final else 17)
        if i%2==0:
            tx,ty,anc=x,y-14,"mb"
        else:
            tx,ty,anc=x,y+14,"mt"
        bb=d.textbbox((tx,ty),txt,font=fnt,anchor=anc)
        d.rounded_rectangle([bb[0]-4,bb[1]-2,bb[2]+4,bb[3]+2],radius=3,fill=(255,255,255,240))
        d.text((tx,ty),txt,font=fnt,fill=blue,anchor=anc)
    if avg is not None:
        y=top+ph*(1-min(avg/right_max,1))
        # dashed line
        for xx in range(left,right,22):
            d.line([(xx,y),(min(xx+12,right),y)],fill=(110,110,114,180),width=2)
        txt=f"средняя {price_fmt(avg)}"; fnt=_font(20 if final else 18)
        bb=d.textbbox((left+12,y-8),txt,font=fnt,anchor="lb")
        d.rounded_rectangle([bb[0]-4,bb[1]-2,bb[2]+4,bb[3]+2],radius=3,fill=(255,255,255,240))
        d.text((left+12,y-8),txt,font=fnt,fill=gray,anchor="lb")
    # legend
    lx,ly=left+6,top+6
    d.rectangle([lx,ly+8,lx+22,ly+26],fill=red)
    d.text((lx+32,ly+16),"Звонки",font=_font(22 if final else 20),fill=dark,anchor="lm")
    d.line([(lx,ly+48),(lx+28,ly+48)],fill=blue,width=5)
    d.text((lx+38,ly+48),legend_price,font=_font(22 if final else 20),fill=dark,anchor="lm")
    im.save(path)

def make_campaign_image(c):
    dates=sorted(by[c]); labels=[d[8:10]+"."+d[5:7] for d in dates]
    calls=[by[c][d]["conv"] for d in dates]
    prices=[(by[c][d]["cost"]/by[c][d]["conv"] if by[c][d]["conv"]>0 else None) for d in dates]
    maxp=max([p for p in prices if p],default=1)
    left=max(4,math.ceil(max(calls))+1)
    right=max(2,math.ceil(maxp*1.25))
    path=os.path.join(CHART_DIR,"camp_"+str(CAMP.index(c))+".png")
    _combo(path,labels,calls,prices,left,right,lambda v:f"${v:.2f}".replace(".",","),"Цена звонка",False,axis_fmt=lambda v:f"${v:.0f}")
    return path

def make_final_image():
    dates=[f"2026-10-{x:02d}" for x in range(13,22)]
    labels=[d[8:10]+"."+d[5:7] for d in dates]
    calls=[ACCT[d]["conv"] if d in ACCT else 0 for d in dates]
    prices=[(ACCT[d]["cost"]/ACCT[d]["cl"] if d in ACCT and ACCT[d]["cl"] else None) for d in dates]
    avg=sum(ACCT[d]["cost"] for d in dates if d in ACCT)/sum(ACCT[d]["cl"] for d in dates if d in ACCT)
    path=os.path.join(CHART_DIR,"final.png")
    _combo(path,labels,calls,prices,12,0.6,lambda v:f"${v:.2f}".replace(".",","),"Цена клика",True,avg,axis_fmt=lambda v:f"${v:.2f}".replace(".",","))
    return path

def heat_table(s,c):
    dates=sorted(by[c]); rows=[["Дата","Получено","Бюджет","Ранг","Топ","Абс."]]
    for d in dates:
        v=by[c][d]
        rows.append([d[8:10]+"."+d[5:7],f"{v['is']:.0f}%",f"{v['lostb']:.0f}%",f"{v['lostr']:.0f}%",f"{v['top']:.0f}%",f"{v['abs']:.0f}%"])
    cols=6; shape=s.shapes.add_table(len(rows),cols,Inches(0.55),Inches(5.10),Inches(12.2),Inches(1.95)); tbl=shape.table
    widths=[1.15,2.20,2.20,2.20,2.20,2.20]
    for i,w in enumerate(widths): tbl.columns[i].width=Inches(w)
    for r in range(len(rows)):
        tbl.rows[r].height=Inches(0.22 if r==0 else 0.165)
        for cix in range(cols):
            cell=tbl.cell(r,cix); cell.margin_left=Inches(0.05); cell.margin_right=Inches(0.05)
            cell.margin_top=0; cell.margin_bottom=0; cell.vertical_anchor=MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            if r==0:
                cell.fill.fore_color.rgb=DARK
            else:
                val=float(rows[r][cix].replace('%','')) if cix>0 else None
                if cix==0:
                    fill=WHITE if r%2 else SOFT
                elif cix==1: fill=RGBColor(0xF8,0xD7,0xD3) if val<35 else (RGBColor(0xFC,0xE8,0xC8) if val<50 else RGBColor(0xDD,0xF0,0xDD))
                elif cix in (2,3): fill=RGBColor(0xF8,0xD7,0xD3) if val>40 else (RGBColor(0xFC,0xE8,0xC8) if val>20 else RGBColor(0xDD,0xF0,0xDD))
                elif cix==4: fill=RGBColor(0xF8,0xD7,0xD3) if val<35 else (RGBColor(0xFC,0xE8,0xC8) if val<50 else RGBColor(0xDD,0xF0,0xDD))
                else: fill=RGBColor(0xF8,0xD7,0xD3) if val<15 else (RGBColor(0xFC,0xE8,0xC8) if val<25 else RGBColor(0xDD,0xF0,0xDD))
                cell.fill.fore_color.rgb=fill
            p=cell.text_frame.paragraphs[0]; p.alignment=PP_ALIGN.LEFT if cix==0 else PP_ALIGN.CENTER
            rr=p.add_run(); rr.text=str(rows[r][cix]); rr.font.name=FONT
            rr.font.size=Pt(6.6 if r else 6.4); rr.font.bold=(r==0); rr.font.color.rgb=WHITE if r==0 else DARK

def campaign_slide(c,kicker,title,fix):
    s=add_slide(kicker,title)
    p=period_stats(c)
    kpi_strip(s,[(f"{p['conv']:.0f}","звонков 13–21"),(f"${p['cpa']:.2f}" if p['cpa'] else "—","цена звонка"),
                 (f"${p['cost']:.0f}","расход"),(f"{p['is_']:.0f}%","доля показов"),
                 (f"{p['lostb']:.0f}%","потеря по бюджету"),(f"{p['lostr']:.0f}%","потеря по рангу"),
                 (f"{p['top']:.0f}% / {p['abs']:.0f}%","топ / абс. топ")], y=1.10, h=0.68)
    text(s,0.55,1.90,1.95,0.22,"ЧТО ЧИНИТЬ:",7.6,True,RED)
    text(s,2.25,1.90,10.5,0.34,fix,7.4,False,RGBColor(0x4A,0x4A,0x4E))
    img=make_campaign_image(c)
    s.shapes.add_picture(img,Inches(0.55),Inches(2.30),width=Inches(12.2),height=Inches(2.72))
    heat_table(s,c)


def table(s,x,y,w,h,data,widths=None,font=8.4,header_font=8.0,row_h=0.36):
    rows,cols=len(data),len(data[0])
    shape=s.shapes.add_table(rows,cols,Inches(x),Inches(y),Inches(w),Inches(h)); tbl=shape.table
    if widths:
        for i,cw in enumerate(widths): tbl.columns[i].width=Inches(cw)
    for r in range(rows):
        tbl.rows[r].height=Inches(row_h)
        for c in range(cols):
            cell=tbl.cell(r,c); cell.margin_left=Inches(0.05); cell.margin_right=Inches(0.04)
            cell.margin_top=Inches(0.01); cell.margin_bottom=Inches(0.01); cell.vertical_anchor=MSO_ANCHOR.MIDDLE
            cell.fill.solid(); cell.fill.fore_color.rgb=DARK if r==0 else (WHITE if r%2 else SOFT)
            p=cell.text_frame.paragraphs[0]; p.alignment=PP_ALIGN.RIGHT if c>0 else PP_ALIGN.LEFT
            rr=p.add_run(); rr.text=str(data[r][c]); rr.font.name=FONT
            rr.font.size=Pt(header_font if r==0 else font); rr.font.bold=(r==0)
            rr.font.color.rgb=WHITE if r==0 else DARK

# ───────── account aggregate + new dashboard ─────────
ACCT = {}
for d in sorted({d for c in CAMP for d in by[c]}):
    rs = [by[c][d] for c in CAMP if d in by[c]]
    if not rs: continue
    impr = sum(x["impr"] for x in rs)
    if not impr: continue
    ACCT[d] = {
        "impr": impr,
        "cl": sum(x["cl"] for x in rs),
        "cost": sum(x["cost"] for x in rs),
        "conv": sum(x["conv"] for x in rs),
        "is": sum(x["is"]*x["impr"] for x in rs)/impr,
        "lostb": sum(x["lostb"]*x["impr"] for x in rs)/impr,
        "lostr": sum(x["lostr"]*x["impr"] for x in rs)/impr,
        "top": sum(x["top"]*x["impr"] for x in rs)/impr,
        "abs": sum(x["abs"]*x["impr"] for x in rs)/impr,
    }
ADATES = sorted(ACCT)
ALABELS = [d[8:10]+"."+d[5:7] for d in ADATES]

def acct_chart_stacked(s):
    cd=CategoryChartData(); cd.categories=ALABELS
    cd.add_series("Получено (IS)",tuple(round(ACCT[d]["is"],1) for d in ADATES))
    cd.add_series("Потеряно по бюджету",tuple(round(ACCT[d]["lostb"],1) for d in ADATES))
    cd.add_series("Потеряно по рангу",tuple(round(ACCT[d]["lostr"],1) for d in ADATES))
    ch=s.shapes.add_chart(XL_CHART_TYPE.COLUMN_STACKED,Inches(0.55),Inches(1.30),Inches(12.2),Inches(2.45),cd).chart
    chart_base(ch,"Аукцион по дням: что получили и что потеряли",105,'0"%"' )
    for i,ser in enumerate(ch.series):
        ser.format.fill.solid(); ser.format.fill.fore_color.rgb=[DARK,RED,GRAY][i]; ser.format.line.fill.background()
    ch.plots[0].gap_width=50
    ch.plots[0].has_data_labels=True
    dl=ch.plots[0].data_labels; dl.font.size=Pt(5.6); dl.font.name=FONT
    dl.number_format='0"%"'; dl.number_format_is_linked=False; dl.position=XL_LABEL_POSITION.CENTER

def acct_chart_top(s,x,y,w,h):
    cd=CategoryChartData(); cd.categories=ALABELS
    cd.add_series("Топ страницы",tuple(round(ACCT[d]["top"],1) for d in ADATES))
    cd.add_series("Абс. топ",tuple(round(ACCT[d]["abs"],1) for d in ADATES))
    ch=s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,Inches(x),Inches(y),Inches(w),Inches(h),cd).chart
    chart_base(ch,"Где показываемся: топ / абс. топ",100,'0"%"')
    for i,ser in enumerate(ch.series):
        ser.format.fill.solid(); ser.format.fill.fore_color.rgb=[BLUE,DARK][i]; ser.format.line.fill.background()
    ch.plots[0].gap_width=55; ch.plots[0].has_data_labels=True
    dl=ch.plots[0].data_labels; dl.font.size=Pt(6.0); dl.number_format='0"%"'; dl.number_format_is_linked=False; dl.position=XL_LABEL_POSITION.OUTSIDE_END

def acct_chart_single(s,x,y,w,h,key,title,ymax,fmt,color):
    vals=[]
    for d in ADATES:
        if key=="conv": vals.append(round(ACCT[d]["conv"],1))
        elif key=="cpa": vals.append(round(ACCT[d]["cost"]/ACCT[d]["conv"],2) if ACCT[d]["conv"]>0 else None)
    cd=CategoryChartData(); cd.categories=ALABELS; cd.add_series(title,tuple(vals))
    ch=s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,Inches(x),Inches(y),Inches(w),Inches(h),cd).chart
    chart_base(ch,title,ymax,fmt)
    ch.has_legend=False
    ch.series[0].format.fill.solid(); ch.series[0].format.fill.fore_color.rgb=color; ch.series[0].format.line.fill.background()
    ch.plots[0].gap_width=45; ch.plots[0].has_data_labels=True
    dl=ch.plots[0].data_labels; dl.font.size=Pt(6.2); dl.number_format=('$0.00' if key=="cpa" else '0.0')
    dl.number_format_is_linked=False; dl.position=XL_LABEL_POSITION.OUTSIDE_END

def dashboard_slide():
    s=add_slide("ДАШБОРД","Вся картина: аукцион → звонки → CPA")
    acct_chart_stacked(s)
    acct_chart_single(s,0.55,4.05,3.95,2.45,"conv","Звонки по дням",max(4,max(ACCT[d]["conv"] for d in ADATES)+1),'0.0',RED)
    maxcpa=max((ACCT[d]["cost"]/ACCT[d]["conv"] for d in ADATES if ACCT[d]["conv"]>0),default=1)
    acct_chart_single(s,4.65,4.05,3.95,2.45,"cpa","CPA по дням",max(2,round(maxcpa*1.25,0)),'$0.00',BLUE)
    acct_chart_top(s,8.75,4.05,3.95,2.45)
    text(s,0.55,6.65,12.2,0.35,"Верх — аукцион: чёрный получено, красный бюджет, серый ранг. Низ — звонки, CPA и где показываемся. Один столбик = день.",7.2,False,RGBColor(0x6E,0x6E,0x73))

# ───────── hours ─────────
HD = collections.defaultdict(lambda: collections.defaultdict(lambda: [0.0,0,0.0]))
for r in hourly:
    h=int(r["segments"]["hour"]); c=r["campaign"]["name"]; m=r["metrics"]
    HD[h][c][0]+=float(m.get("conversions",0)); HD[h][c][1]+=int(m.get("clicks",0)); HD[h][c][2]+=int(m.get("costMicros",0))/1e6
HOURS=[9,10,11,12,13,14,15,16,17,18]
HLAB=[f"{h:02d}" for h in HOURS]

def hours_slide():
    s=add_slide("ЧАСЫ","Когда звонят: разбивка по времени")
    cd=CategoryChartData(); cd.categories=HLAB
    for c in CAMP:
        cd.add_series(SHORT[c],tuple(round(HD[h][c][0],1) for h in HOURS))
    ch=s.shapes.add_chart(XL_CHART_TYPE.COLUMN_STACKED,Inches(0.55),Inches(1.30),Inches(7.15),Inches(4.55),cd).chart
    chart_base(ch,"Звонки по часам, стек по кампаниям",12,'0.0')
    for i,ser in enumerate(ch.series):
        ser.format.fill.solid(); ser.format.fill.fore_color.rgb=[RED,DARK,BLUE,GRAY][i]; ser.format.line.fill.background()
    ch.plots[0].gap_width=40
    data=[["Час","Звонки","Клики","CR"]]
    for h in HOURS:
        calls=sum(HD[h][c][0] for c in CAMP); clicks=sum(HD[h][c][1] for c in CAMP)
        data.append([f"{h:02d}:00",f"{calls:.1f}",str(clicks),f"{calls/clicks*100 if clicks else 0:.1f}%"])
    table(s,7.95,1.30,4.80,4.15,data,widths=[1.0,1.1,0.9,0.9],font=8.4,header_font=8.0,row_h=0.36)
    text(s,0.55,6.05,7.15,0.55,"Пик 11:00 — 10,3 звонка, CR 14,4%. 9–14 — 39 из 47 звонков (83%). 18:00 — 0. Данных 9 дней: это наблюдение, не вывод.",7.2,False,RGBColor(0x6E,0x6E,0x73))
    text(s,7.95,5.65,4.8,0.55,"После 16:00 спад. 17:00 — 1 звонок, 18:00 — 0.",7.2,False,RGBColor(0x6E,0x6E,0x73))

# ───────── ads CTR ─────────
ADROWS=[]
for r in ads_raw:
    m=r["metrics"]; a=r["adGroupAd"]["ad"]
    impr=int(m.get("impressions",0))
    if impr<50: continue
    heads=[h["text"] for h in a.get("responsiveSearchAd",{}).get("headlines",[])]
    ADROWS.append({"camp":r["campaign"]["name"],"impr":impr,"cl":int(m.get("clicks",0)),
                   "ctr":float(m.get("ctr",0))*100,"conv":float(m.get("conversions",0)),
                   "head":heads[0] if heads else ""})
ADROWS=sorted(ADROWS,key=lambda x:-x["ctr"])

def ads_slide():
    s=add_slide("ОБЪЯВЛЕНИЯ","CTR по объявлениям: где попали в боль, где просели")
    strong=ADROWS[:5]; weak=ADROWS[-5:]
    for side,rows,x,title,color in [("strong",strong,0.55,"СИЛЬНЫЕ: CTR 14–27%",RED),("weak",weak,6.80,"СЛАБЫЕ: CTR 7–10%",GRAY)]:
        text(s,x,1.30,5.9,0.25,title,9.0,True,color)
        data=[["Объявление","CTR","Клики","Звонки"]]
        for a in rows:
            h=a["head"]
            if h.startswith("{KeyWord:") and h.endswith("}"):
                h=h[len("{KeyWord:"):-1]
            if a["camp"]=="СТО - По маркам":
                brand=h.split("Ремонт ")[-1].split(" в")[0].split(" —")[0]
                label="СТО-По маркам · "+brand
            else:
                label=SHORT[a["camp"]]+" · "+h
            if len(label)>40:
                label=label[:37].rsplit(" ",1)[0]+"…"
            data.append([label,f"{a['ctr']:.1f}%",str(a["cl"]),f"{a['conv']:.1f}"])
        table(s,x,1.62,5.9,2.55,data,widths=[3.55,0.75,0.65,0.65],font=8.4,header_font=7.8,row_h=0.40)
    text(s,0.55,4.45,12.2,0.30,"ЧТО ВИДНО",9.0,True,RED)
    bullets(s,0.55,4.78,6.0,2.2,[
        "Opel 27,1% (5 звонков), Ford 18,7%, Hyundai 18,2% — бренд + «диагностика 0 BYN» работают.",
        "Mercedes 7,5% (0 звонков), BMW 9,5%, Проточка 8,4% — CTR просел.",
        "Peugeot 17,6% и Renault 14,0%, но 0 звонков: клик есть, звонка нет.",
    ],size=8.8,gap=6)
    bullets(s,6.75,4.78,6.0,2.2,[
        "Цена в заголовке ≠ цена в описании: Проточка «от 45 BYN» / «от 35 BYN»; Развал «от 60» / «от 40–80». Это режет доверие.",
        "Проточка: 368 показов, 31 клик, 1 звонок. Свести цену к одной и проверить оффер.",
        "Peugeot/Renault: высокий CTR, 0 звонков — проблема в посадочной, не в объявлении.",
    ],size=8.8,gap=6)

# ───────── brand page ─────────
def brand_page_slide():
    s=add_slide("СТО ПО МАРКАМ","Страница под марки: что именно править")
    frame=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(0.55),Inches(1.30),Inches(6.25),Inches(4.95))
    frame.adjustments[0]=0.03; frame.fill.solid(); frame.fill.fore_color.rgb=WHITE; frame.line.color.rgb=LINE
    head=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(0.55),Inches(1.30),Inches(6.25),Inches(0.40))
    head.fill.solid(); head.fill.fore_color.rgb=DARK; head.line.fill.background()
    text(s,0.72,1.36,5.9,0.27,"СТО ПО МАРКАМ В МИНСКЕ",8.8,True,WHITE)
    text(s,0.72,1.84,5.9,0.28,"Renault · Peugeot · Citroen · Opel · Ford",9.2,True,RED)
    text(s,0.72,2.14,5.9,0.55,"Ремонт и диагностика по маркам. Цены известны до начала. Гарантия.",7.8,False,RGBColor(0x4A,0x4A,0x4E))
    # tabs
    for i,b in enumerate(["Renault","Peugeot","Citroen","Opel","Ford"]):
        x=0.72+i*1.10
        tab=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(x),Inches(2.80),Inches(1.00),Inches(0.32))
        tab.fill.solid(); tab.fill.fore_color.rgb=RGBColor(0xEF,0xEF,0xEC); tab.line.color.rgb=LINE
        text(s,x+0.04,2.86,0.92,0.20,b,6.6,True,DARK)
    # brand cards
    for i,b in enumerate(["Renault","Peugeot","Citroen"]):
        x=0.72+i*1.92
        card=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(x),Inches(3.28),Inches(1.78),Inches(1.45))
        card.fill.solid(); card.fill.fore_color.rgb=RGBColor(0xF7,0xF7,0xF5); card.line.color.rgb=LINE
        text(s,x+0.08,3.36,1.62,0.22,b,7.4,True,RED)
        text(s,x+0.08,3.60,1.62,0.95,"Модели\n3 услуги + цены\nотзыв\nфото",6.3,False,RGBColor(0x4A,0x4A,0x4E))
    # bottom blocks
    text(s,0.72,4.88,2.8,0.30,"Цены и пакеты",7.2,True,DARK)
    text(s,0.72,5.13,2.8,0.55,"Диагностика 0 BYN\nТО / тормоза / подвеска",6.4,False,RGBColor(0x4A,0x4A,0x4E))
    text(s,3.70,4.88,2.9,0.30,"Отзывы и FAQ",7.2,True,DARK)
    text(s,3.70,5.13,2.9,0.55,"2–3 отзыва по марке\n5 вопросов",6.4,False,RGBColor(0x4A,0x4A,0x4E))
    text(s,0.72,5.78,5.8,0.30,"Форма + телефон в первом экране",7.2,True,RED)
    # right checklist
    bullets(s,7.05,1.30,5.7,5.0,[
        "H1: «СТО по маркам в Минске» + подзаголовок с 5 брендами. Сейчас H1 общий, брендов нет.",
        "Табы/блоки по топ-5: Renault, Peugeot, Citroen, Opel, Ford. В каждом — модели, 3 услуги с ценами, отзыв, фото.",
        "Цены и пакеты: диагностика 0 BYN, ТО, тормоза, подвеска. Не прятать цену.",
        "Отзывы по марке + FAQ: 5 вопросов, schema FAQ.",
        "Форма и телефон в первом экране; кнопка «Позвонить» на мобиле.",
        "Не делать 19 страниц. Одна страница с 5 блоками; тест 2 недели, потом остальные марки.",
    ],size=8.8,gap=7)
    text(s,7.05,6.12,5.7,0.30,"Сейчас: 19 объявлений на главную, 77 ключей с LP ниже среднего.",7.4,False,RGBColor(0x6E,0x6E,0x73))


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

dashboard_slide()

# 3-6 campaigns
campaign_slide(CAMP[0],"РАЗВАЛ","Развал-схождение: бюджет — главный рычаг",
    "Бюджет +20–30% → +3 звонка/нед; QS «развал схождение» 3 — усилить страницу и заголовки.")
campaign_slide(CAMP[1],"СТО - ПО МАРКАМ","СТО-По маркам: ранг, а не бюджет",
    "Ранг 39%: страница/блоки топ-5 марок + ставки на брендовые ключи; бюджет — после LP/QS.")
campaign_slide(CAMP[2],"РЕГУЛИРОВКА","Регулировка фар: ранг, бюджет не трогать",
    "Бюджет 0; QS/LP «регулировка фар»; цель CPA < $4,5 и топ страницы 60–70%.")
campaign_slide(CAMP[3],"ПРОТОЧКА","Проточка: мало объёма, не бюджет",
    "Объём: расширить ключи/объявления и поднять ставку/IS; бюджет не трогать; CPA < $6.")

hours_slide()
ads_slide()
brand_page_slide()

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
text(s,0.55,1.16,12.2,0.28,"По данным 13–21.10 (47 звонков) + внешний ориентир. Это гипотезы, а не приговор; проверять по одному изменению.",8.4,False,RGBColor(0x6E,0x6E,0x73))
cards = [
    ("46 из 47","звонков — с телефона","Desktop: 85 кликов → 1 звонок, CR 1,2%. Мобайл: 442 клика → 46 звонков, CR 10,4%.","Мобайл в приоритет. Десктоп -50% на тест; проверить скорость мобильной."),
    ("83%","звонков с 9 до 14","11:00 — CR 14,4%; 13–14 — 12–13%; 18:00 — 0 звонков. После 16:00 спад.","Dayparting: +20–30% 9–14, -20% после 17. Данных 9 дней — наблюдение."),
    ("0,34 $ / 3,82 $","клик и звонок — дешевле рынка","Ориентир auto repair: клик ~3,5 $, заявка ~44 $ (CA, 2024–25). У нас 0,34 $ и 3,82 $.","Экономика сильная; масштабировать шагами, не бояться."),
    ("45 vs 35","цена в заголовке и описании","Проточка: «от 45 BYN» в заголовке, «от 35 BYN» в описании. CTR 8,4%, 1 звонок.","Свести цену к одной; проверить оффер и доверие."),
    ("14–18% / 0","CTR есть, звонков нет","Peugeot 17,6% — 29 кликов, 0 звонков. Renault 14,0% — 16 кликов, 0.","Клик есть, звонка нет: LP/оффер/брендовая страница."),
    ("+47% / +39%","масштаб → CPA; пауза → ramp","Расход/день +47%, CPA +39%. После паузы 2→6→8 звонков.","Шагами; первые 2 дня после паузы не оценивать."),
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

# 17. simple
s = add_slide("ПРОСТЫМИ СЛОВАМИ", "Что происходит: коротко и по-человечески")
kpi_strip(s,[("47","звонков за 9 дней"),("$3,82","средняя цена звонка"),("530","кликов"),("$0,34","средняя цена клика"),("$179","расход")])
data=[["Кампания","Звонки","Расход","Цена звонка","Клики","Цена клика"],
      ["Развал","12","$45","$3,78","138","$0,33"],
      ["СТО - По маркам","19","$62","$3,24","217","$0,28"],
      ["Регулировка фар","15","$57","$3,83","142","$0,40"],
      ["Проточка","1","$15","$14,95","33","$0,45"],
      ["Всего","47","$179","$3,82","530","$0,34"]]
table(s,0.55,2.25,7.0,2.75,data,widths=[2.2,0.75,0.85,1.0,0.75,0.95],font=8.8,header_font=8.0,row_h=0.40)
bullets(s,7.85,2.25,4.9,3.0,[
    "8,9 из 100 кликов заканчиваются звонком — хороший уровень.",
    "46 из 47 звонков — с телефона.",
    "Лучше всего звонят с 9 до 14; после 16 почти нет.",
    "Развал + СТО = 31 из 47 звонков.",
    "Самый дешёвый звонок — СТО: 3,24 $.",
    "Проточка: 1 звонок — это мало данных, не вывод.",
],size=9.0,gap=6)
text(s,0.55,5.20,12.2,0.28,"КУДА ДВИГАЕМСЯ",9.0,True,RED)
moves=[("РАЗВАЛ","Добавить бюджет"),("СТО - ПО МАРКАМ","Сделать страницу по маркам"),("РЕГУЛИРОВКА","Не поднимать бюджет, чинить страницу"),("ПРОТОЧКА","Набрать объём")]
for i,(name,action) in enumerate(moves):
    x=0.55+i*3.12
    box=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(x),Inches(5.52),Inches(2.95),Inches(0.92))
    box.adjustments[0]=0.06; box.fill.solid(); box.fill.fore_color.rgb=WHITE; box.line.color.rgb=LINE
    text(s,x+0.14,5.62,2.65,0.22,name,8.4,True,DARK)
    text(s,x+0.14,5.88,2.65,0.45,action,8.0,False,RGBColor(0x4A,0x4A,0x4E))
text(s,0.55,6.60,12.2,0.40,"Хорошая новость: клик 0,34 $ и звонок 3,82 $ — это очень дёшево. Ориентир auto repair (CA, 2024–25): клик ~3,5 $, заявка ~44 $. Рынок другой, но запас большой.",7.0,False,RGBColor(0x6E,0x6E,0x73))

# 18. daily total table
s = add_slide("ПО ДНЯМ", "Заявки и деньги по дням — без разбивки по кампаниям")
text(s,0.55,1.16,12.2,0.25,"13–21 октября. 17–18 — пауза, 19 — провал, 20–21 — восстановление.",8.4,False,RGBColor(0x6E,0x6E,0x73))
dates=["2026-10-13","2026-10-14","2026-10-15","2026-10-16","2026-10-17","2026-10-18","2026-10-19","2026-10-20","2026-10-21"]
wd={0:"Пн",1:"Вт",2:"Ср",3:"Чт",4:"Пт",5:"Сб",6:"Вс"}
rows=[["Дата","День","Звонки","Накопительно","Расход","Цена звонка","Клики","Цена клика"]]
cum=0
for d in dates:
    dt=datetime.date.fromisoformat(d); a=ACCT.get(d)
    if a:
        calls=a["conv"]; cum+=calls
        rows.append([f"{d[8:10]}.10",wd[dt.weekday()],f"{calls:.0f}",f"{cum:.0f}",f"${a['cost']:.2f}".replace(".", ","),
                     f"${a['cost']/calls:.2f}".replace(".", ",") if calls else "—",f"{a['cl']:.0f}",f"${a['cost']/a['cl']:.2f}".replace(".", ",") if a['cl'] else "—"])
    else:
        rows.append([f"{d[8:10]}.10",wd[dt.weekday()],"0",f"{cum:.0f}","$0","—","0","—"])
rows.append(["Итого","—","47","47","$179,38","$3,82","530","$0,34"])
table(s,0.55,1.52,7.55,4.35,rows,widths=[0.75,0.60,0.75,1.05,1.05,1.05,0.75,1.05],font=8.3,header_font=7.6,row_h=0.35)
# simple calls chart
cd=CategoryChartData(); cd.categories=[r[0] for r in rows[1:10]]; cd.add_series("Звонки",tuple(int(r[2]) for r in rows[1:10]))
ch=s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,Inches(8.35),Inches(1.52),Inches(4.45),Inches(4.0),cd).chart
chart_base(ch,"Звонки по дням",12,'0')
ch.series[0].format.fill.solid(); ch.series[0].format.fill.fore_color.rgb=RED; ch.series[0].format.line.fill.background()
ch.has_legend=False
ch.plots[0].gap_width=45; ch.plots[0].has_data_labels=True
dl=ch.plots[0].data_labels; dl.font.size=Pt(7.0); dl.font.name=FONT; dl.number_format='0'; dl.number_format_is_linked=False
dl.position=XL_LABEL_POSITION.OUTSIDE_END
text(s,0.55,6.02,7.55,0.75,"19.10: 2 звонка, цена звонка $10,64 — день после паузы. 20–21: 6 и 8 звонков, цена $5,38 и $4,27. Выходные 17–18 не работали.",7.4,False,RGBColor(0x6E,0x6E,0x73))
text(s,8.35,5.65,4.45,0.55,"Цена звонка = расход / звонки.\nЦена клика = расход / клики.",7.2,False,RGBColor(0x6E,0x6E,0x73))

# 19. weeks
s = add_slide("НЕДЕЛИ", "Недели: конверсии, цена клика, стоимость конверсии и расход")
text(s,0.55,1.14,12.2,0.25,"По 4 текущим кампаниям. 05.10 данных нет. Неделя 19–25 — неполная (19–22).",8.2,False,RGBColor(0x6E,0x6E,0x73))
wdata=[["Неделя","Конверсии","Клики","Средняя цена клика","Коэф. конверсии","Стоимость конверсии","Расход"],
       ["05–11.10 (06–09)","9","149","$0,46","6,0%","$7,68","$69,16"],
       ["12–18.10  · лучшая","33","338","$0,33","9,8%","$3,37","$111,18"],
       ["19–25.10 (19–22)","17","274","$0,36","6,2%","$5,73","$97,46"],
       ["Итого 06–22.10","59","761","$0,37","7,8%","$4,71","$277,80"]]
table(s,0.55,1.45,12.2,2.05,wdata,widths=[2.65,1.45,0.95,1.75,1.75,2.20,1.45],font=8.8,header_font=8.0,row_h=0.38)
text(s,0.55,3.72,7.8,0.25,"ПОНЕДЕЛЬНИКИ",9.0,True,RED)
mdata=[["Понедельник","Конверсии","Клики","Цена клика","Конв.","Цена конв.","Расход"],
       ["05.10","—","—","—","—","—","—"],
       ["12.10","2","58","$0,34","3,4%","$9,74","$19,47"],
       ["19.10","2","65","$0,33","3,1%","$10,64","$21,27"]]
table(s,0.55,4.02,7.55,1.65,mdata,widths=[1.35,1.05,0.90,1.05,0.95,1.05,1.20],font=8.6,header_font=7.8,row_h=0.36)
bullets(s,8.45,4.02,4.3,2.4,[
    "05.10 данных нет — сравнивать не с чем.",
    "12.10 vs 19.10: звонки 2 и 2, клики 58→65, CPA $9,74→$10,64.",
    "19-е — первый день после паузы, поэтому не показатель.",
    "Лучшая неделя — 12–18.10: 33 звонка, CPA $3,37, CVR 9,8%.",
],size=8.8,gap=6)
text(s,0.55,5.95,12.2,0.35,"05–11 — только 06–09 (4 дня), 9 звонков. Итог 06–22 — 59 звонков, $277,80, CPA $4,71.",7.4,False,RGBColor(0x6E,0x6E,0x73))

# 19. final clean chart
s = add_slide("ИТОГ", "Заявки и цена клика: как двигалось")
kpi_strip(s,[("47","звонков за 9 дней"),("$0,34","средняя цена клика"),("$3,82","средняя цена звонка")], y=1.10, h=0.68)
s.shapes.add_picture(make_final_image(),Inches(0.55),Inches(2.02),width=Inches(12.2),height=Inches(4.58))
text(s,0.55,6.72,12.2,0.30,"17–18 — пауза, 19 — провал, 20–21 — восстановление. Средняя цена клика $0,34; средняя цена звонка $3,82.",7.8,False,RGBColor(0x6E,0x6E,0x73))

out="/Users/maksim/Desktop/Реклама/03_анализ/ДАСТО_столбики_22.10.2026.pptx"
prs.save(out); print("saved",out,"slides",len(prs.slides))
