#!/usr/bin/env python3
"""Компактные отчёты: VTI, бухгалтерия, YouTube."""
import json
import collections
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION

BG = RGBColor(0xF7,0xF7,0xF5); DARK = RGBColor(0x17,0x18,0x1A); RED = RGBColor(0xD0,0x13,0x0D)
BLUE = RGBColor(0x2F,0x5F,0xB8); GRAY = RGBColor(0x6E,0x6E,0x73); LINE = RGBColor(0xE3,0xE3,0xDF)
WHITE = RGBColor(0xFF,0xFF,0xFF); SOFT = RGBColor(0xEF,0xEF,0xEC)
FONT = "Arial"


def new_pres():
    p = Presentation(); p.slide_width = Inches(13.333); p.slide_height = Inches(7.5); return p


def add_slide(p, kicker, title, footer="Подготовлено 22.10.2026 · без изменений"):
    s = p.slides.add_slide(p.slide_layouts[6])
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, p.slide_width, p.slide_height)
    bg.fill.solid(); bg.fill.fore_color.rgb = BG; bg.line.fill.background()
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.10), p.slide_height)
    bar.fill.solid(); bar.fill.fore_color.rgb = RED; bar.line.fill.background()
    t = s.shapes.add_textbox(Inches(0.55), Inches(0.30), Inches(11.8), Inches(0.25))
    r = t.text_frame.paragraphs[0].add_run(); r.text = kicker
    r.font.name = FONT; r.font.size = Pt(9); r.font.bold = True; r.font.color.rgb = RED
    t = s.shapes.add_textbox(Inches(0.55), Inches(0.56), Inches(12.2), Inches(0.60))
    r = t.text_frame.paragraphs[0].add_run(); r.text = title
    r.font.name = FONT; r.font.size = Pt(23); r.font.bold = True; r.font.color.rgb = DARK
    t = s.shapes.add_textbox(Inches(0.55), Inches(7.12), Inches(12.2), Inches(0.20))
    r = t.text_frame.paragraphs[0].add_run(); r.text = footer
    r.font.name = FONT; r.font.size = Pt(8); r.font.color.rgb = GRAY
    return s


def text(s, x, y, w, h, lines, size=12, bold=False, color=DARK, gap=0):
    box = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame; tf.word_wrap = True
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    for i, line in enumerate(lines if isinstance(lines, list) else lines.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        r = p.add_run(); r.text = line
        r.font.name = FONT; r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color
    return box


def bullets(s, x, y, w, h, items, size=10.5, gap=7):
    box = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame; tf.word_wrap = True
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap); p.line_spacing = 1.02
        r0 = p.add_run(); r0.text = "●  "; r0.font.name = FONT; r0.font.size = Pt(size-3); r0.font.color.rgb = RED
        r = p.add_run(); r.text = item; r.font.name = FONT; r.font.size = Pt(size); r.font.color.rgb = DARK


def kpi(s, x, y, w, value, label, dark=False):
    card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(1.0))
    card.adjustments[0] = 0.10; card.fill.solid(); card.fill.fore_color.rgb = DARK if dark else WHITE
    card.line.color.rgb = DARK if dark else LINE
    t = s.shapes.add_textbox(Inches(x+0.16), Inches(y+0.10), Inches(w-0.32), Inches(0.44))
    r = t.text_frame.paragraphs[0].add_run(); r.text = value
    r.font.name = FONT; r.font.size = Pt(25); r.font.bold = True; r.font.color.rgb = WHITE if dark else RED
    t = s.shapes.add_textbox(Inches(x+0.16), Inches(y+0.62), Inches(w-0.32), Inches(0.25))
    r = t.text_frame.paragraphs[0].add_run(); r.text = label
    r.font.name = FONT; r.font.size = Pt(9); r.font.color.rgb = RGBColor(0xD9,0xD9,0xD9) if dark else GRAY


def table(s, x, y, w, h, data, widths=None, font=8.5, header=8.0, row_h=0.35, hl=False):
    rows, cols = len(data), len(data[0])
    shape = s.shapes.add_table(rows, cols, Inches(x), Inches(y), Inches(w), Inches(h))
    tbl = shape.table
    if widths:
        for i, cw in enumerate(widths): tbl.columns[i].width = Inches(cw)
    for r in range(rows):
        tbl.rows[r].height = Inches(row_h)
        for c in range(cols):
            cell = tbl.cell(r, c)
            cell.margin_left = Inches(0.05); cell.margin_right = Inches(0.05)
            cell.margin_top = Inches(0.01); cell.margin_bottom = Inches(0.01)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE; cell.fill.solid()
            if r == 0: cell.fill.fore_color.rgb = DARK
            elif hl and r == 1: cell.fill.fore_color.rgb = RGBColor(0xFB,0xE9,0xE7)
            else: cell.fill.fore_color.rgb = WHITE if r % 2 else SOFT
            tf = cell.text_frame; tf.word_wrap = True
            p = tf.paragraphs[0]; p.alignment = PP_ALIGN.RIGHT if c > 0 else PP_ALIGN.LEFT
            if r == 0 and c > 0: p.alignment = PP_ALIGN.RIGHT
            rr = p.add_run(); rr.text = str(data[r][c])
            rr.font.name = FONT; rr.font.size = Pt(header if r == 0 else font)
            rr.font.bold = (r == 0) or (hl and r == 1)
            rr.font.color.rgb = WHITE if r == 0 else DARK


def chart(s, x, y, w, h, cats, series, title, ymax=None, fmt='0'):
    cd = CategoryChartData(); cd.categories = cats
    for name, vals in series.items(): cd.add_series(name, tuple(vals))
    ch = s.shapes.add_chart(XL_CHART_TYPE.LINE_MARKERS, Inches(x), Inches(y), Inches(w), Inches(h), cd).chart
    ch.has_legend = True; ch.legend.position = XL_LEGEND_POSITION.BOTTOM; ch.legend.include_in_layout = False
    ch.legend.font.size = Pt(7.5); ch.legend.font.name = FONT
    ch.font.name = FONT; ch.font.size = Pt(7.5)
    ch.has_title = True; ch.chart_title.text_frame.text = title
    for p in ch.chart_title.text_frame.paragraphs:
        for r in p.runs: r.font.size = Pt(9); r.font.bold = True; r.font.name = FONT; r.font.color.rgb = DARK
    if ymax: ch.value_axis.maximum_scale = ymax
    ch.value_axis.minimum_scale = 0
    ch.value_axis.tick_labels.font.size = Pt(7); ch.value_axis.tick_labels.number_format = fmt
    ch.value_axis.tick_labels.number_format_is_linked = False
    ch.category_axis.tick_labels.font.size = Pt(7)
    for i, ser in enumerate(ch.series):
        col = [RED, DARK, BLUE][i % 3]
        ser.format.line.color.rgb = col; ser.format.line.width = Pt(1.8)
        ser.marker.style = 8; ser.marker.size = 4
        ser.marker.format.fill.solid(); ser.marker.format.fill.fore_color.rgb = col
        ser.marker.format.line.color.rgb = col


def title_slide(p, kicker, title, subtitle, footer):
    s = p.slides.add_slide(p.slide_layouts[6])
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, p.slide_width, p.slide_height)
    bg.fill.solid(); bg.fill.fore_color.rgb = DARK; bg.line.fill.background()
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.70), Inches(1.25), Inches(0.12), Inches(3.95))
    bar.fill.solid(); bar.fill.fore_color.rgb = RED; bar.line.fill.background()
    text(s, 1.05, 1.20, 10.8, 0.30, kicker, 11, True, RED)
    text(s, 1.05, 1.65, 10.8, 1.0, title, 42, True, WHITE)
    text(s, 1.05, 3.35, 10.8, 0.70, subtitle, 18, False, RGBColor(0xE6,0xE6,0xE6))
    line = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.05), Inches(5.15), Inches(5.0), Inches(0.02))
    line.fill.solid(); line.fill.fore_color.rgb = RGBColor(0x3A,0x3A,0x3C); line.line.fill.background()
    text(s, 1.05, 5.33, 10.8, 0.30, footer, 10, False, RGBColor(0xB9,0xB9,0xB9))


# ───────── VTI ─────────
vti = json.load(open("/Users/maksim/Desktop/Реклама/05_скрипты/vti_daily.json"))
vd = collections.defaultdict(lambda: [0, 0, 0.0])
for r in vti:
    d = r["segments"]["date"]; m = r["metrics"]
    vd[d][0] += int(m.get("impressions", 0))
    vd[d][1] += int(m.get("clicks", 0))
    vd[d][2] += int(m.get("costMicros", 0)) / 1e6
vdates = [d for d in sorted(vd) if d <= "2026-10-21"]
vlabels = [d[8:10]+"."+d[5:7] for d in vdates]
vau = collections.defaultdict(lambda: [0,0,0,0,0,0])
for r in vti:
    d = r["segments"]["date"]; m = r["metrics"]; w = int(m.get("impressions",0))
    vau[d][0] += w
    vau[d][1] += float(m.get("searchImpressionShare",0)) * w
    vau[d][2] += float(m.get("searchBudgetLostImpressionShare",0)) * w
    vau[d][3] += float(m.get("searchRankLostImpressionShare",0)) * w
    vau[d][4] += float(m.get("searchTopImpressionShare",0)) * w
    vau[d][5] += float(m.get("searchAbsoluteTopImpressionShare",0)) * w

p = new_pres()
title_slide(p, "GOOGLE ADS / VTI", "VTI: клики, показы,\nаукцион", "4 кампании · 12–21 октября 2026\nконверсии не настроены — оцениваем клики и аукцион", "Подготовлено 22.10.2026 · без изменений")

s = add_slide(p, "ГЛАВНОЕ", "VTI: трафик есть, но его мало")
kpi(s, 0.55, 1.35, 2.85, "667", "показов за 30 дней")
kpi(s, 3.55, 1.35, 2.85, "86", "кликов за 30 дней")
kpi(s, 6.55, 1.35, 2.85, "$87", "расход за 30 дней")
kpi(s, 9.55, 1.35, 2.85, "0", "конверсий: не настроены", dark=True)
bullets(s, 0.55, 2.75, 6.1, 3.7, [
    "4 кампании, $5/день каждая: вентиляция, водопровод, тепловой узел, аварийные работы.",
    "За 30 дней 667 показов и 86 кликов — это мало. Средний CPC $1,01.",
    "Аукцион сильный: доля показов 67%, топ страницы 86,7%, абсолютный топ 43,3%.",
    "Проблема не в ранге, а в объёме: мало показов и кликов. Конверсии не настроены — CPA не считаем.",
], size=10.6, gap=8)
card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.0), Inches(2.75), Inches(5.75), Inches(3.4))
card.adjustments[0] = 0.05; card.fill.solid(); card.fill.fore_color.rgb = WHITE; card.line.color.rgb = LINE
text(s, 7.22, 2.95, 5.3, 0.25, "ЧТО ДЕЛАТЬ", 9.5, True, RED)
bullets(s, 7.22, 3.30, 5.3, 2.6, [
    "Не гнаться за абсолютным топом: 43% уже выше рынка.",
    "Расширять объём: больше ключей/гео, поднять бюджет на вентиляцию и водопровод.",
    "Добавить конверсии, когда будет задача считать CPA.",
], size=9.8, gap=7)

s = add_slide(p, "ДНИ", "VTI: клики и расход по дням")
chart(s, 0.55, 1.35, 2.9, 4.4, vlabels,
      {"Клики": [vd[d][1] for d in vdates]},
      "Клики", 20, '0')
chart(s, 3.55, 1.35, 2.9, 4.4, vlabels,
      {"Расход, $": [round(vd[d][2],1) for d in vdates]},
      "Расход, $", 20, '$0')
bullets(s, 6.95, 1.40, 5.8, 4.8, [
    "12–16.10: 7–15 кликов/день, расход $7,8–16,5.",
    "19–21.10: 8–14 кликов/день, расход $6,9–12,5.",
    "22.10 — 1 клик, $1 (неполный день).",
    "Вентиляция — главный источник: 50 кликов и $47 из $87.",
], size=10.0, gap=8)

s = add_slide(p, "ДНИ · АУКЦИОН", "VTI: доля показов и потери по дням")
def pv(d, i):
    return round(vau[d][i] / vau[d][0] * 100, 1) if vau[d][0] else None
chart(s, 0.55, 1.35, 6.0, 4.3, vlabels,
      {"Доля показов": [pv(d,1) for d in vdates], "Топ страницы": [pv(d,4) for d in vdates], "Абс. топ": [pv(d,5) for d in vdates]},
      "Аукцион: IS, топ, абс. топ", 100, '0"%"')
chart(s, 6.85, 1.35, 5.9, 4.3, vlabels,
      {"lostB": [pv(d,2) for d in vdates], "lostR": [pv(d,3) for d in vdates]},
      "Потери: бюджет и ранг", 100, '0"%"')
bullets(s, 0.55, 5.8, 12.2, 1.0, [
    "VTI держит 60–70% доли показов и 80–90% топа страницы; абсолютный топ 40–45% — выше конкурентов.",
    "Потеря по рангу 20–40%, по бюджету 0–10%. Это сильный аукцион, но мало объёма: 667 показов за 30 дней.",
], size=9.4, gap=5)

s = add_slide(p, "30 ДНЕЙ", "VTI: кампании, доля показов, потери")
data = [
    ["Кампания", "Бюджет", "Показы", "Клики", "Расход", "IS", "lostB", "lostR"],
    ["Монтаж вентиляции", "$5", "430", "50", "$47,18", "61,1%", "9,9%", "29,0%"],
    ["Монтаж водопровода", "$5", "189", "26", "$28,53", "81,8%", "2,0%", "16,2%"],
    ["Монтаж теплового узла", "$5", "18", "5", "$7,17", "52,2%", "0%", "47,8%"],
    ["Аварийные работы", "$5", "30", "5", "$4,23", "90,9%", "0%", "9,1%"],
    ["Итого", "—", "667", "86", "$87,11", "67,0%", "5,0%", "28,0%"],
]
table(s, 0.55, 1.35, 11.4, 2.65, data, widths=[2.9,0.9,1.0,0.9,1.0,0.9,0.9,0.9], font=9.2, row_h=0.38)
bullets(s, 0.55, 4.35, 6.0, 2.3, [
    "Вентиляция: 50 кликов, $47 — половина расхода.",
    "Водопровод: 26 кликов, $28,5 — второй драйвер.",
    "Тепловой узел: 5 кликов, lostR 47,8% — мало объёма, не бюджет.",
], size=9.8, gap=7)
text(s, 6.85, 4.35, 5.9, 2.3, "Бюджеты по $5/день — это не «масштаб», а тест.\nЕсли растёт клик, а конверсий нет, сначала проверяем\nпосадочную и форму, потом поднимаем бюджет.", 9.8, False, GRAY)

s = add_slide(p, "АУКЦИОН", "VTI: сильная доля показов, слабый объём")
data = [
    ["Конкурент", "Доля", "Пересеч.", "Выше", "Топ", "Абс. топ", "Выигрыши"],
    ["Вы", "67,0%", "—", "—", "86,7%", "43,3%", "—"],
    ["sandareal.by", "20,9%", "26,3%", "40,9%", "89,0%", "20,6%", "59,8%"],
    ["glavlab.by", "14,1%", "19,2%", "65,5%", "87,0%", "41,3%", "58,6%"],
    ["eleco.by", "12,0%", "14,4%", "55,6%", "94,9%", "38,5%", "61,7%"],
    ["m-100.by", "12,0%", "14,2%", "66,1%", "88,5%", "42,3%", "60,7%"],
]
table(s, 0.55, 1.35, 8.0, 3.3, data, widths=[2.2,0.85,0.9,0.85,0.8,0.9,1.0], font=8.6, row_h=0.40, hl=True)
bullets(s, 8.85, 1.40, 3.95, 4.9, [
    "Доля показов 67% — выше всех конкурентов.",
    "Топ страницы 86,7%, абсолютный топ 43,3% — уже сильнее рынка.",
    "Конкуренты обходят в 41–66% пересечений, но у них доля ниже.",
    "Вывод: не тратить деньги на абсолютный топ. Нужен объём: ключи, гео, бюджет.",
], size=9.6, gap=7)
text(s, 0.55, 5.05, 8.0, 0.5, "30 дней, UI. Выкуп = доля показов; выигрыши — процент побед в аукционе.", 7.6, False, GRAY)

s = add_slide(p, "ЗАПРОСЫ И ПЛАН", "VTI: запросы релевантные, минусовка сильная")
bullets(s, 0.55, 1.35, 6.0, 4.8, [
    "1 118 минус-слов на кампаниях — аккаунт хорошо зачищен.",
    "Запросы: монтаж воздуховодов, установка вытяжки, прокладка водопровода, монтаж ИТП, расценки на вентиляцию.",
    "Мусора мало; есть «монтаж кондиционера» и «бризер» — проверить, делаете ли.",
    "QS в основном без данных; «прокладка водопровода» QS 4 с LP ниже — точечно посадочная.",
], size=10.0, gap=8)
bullets(s, 6.85, 1.35, 5.9, 4.8, [
    "План: 1) конверсии — когда нужен CPA; 2) объём — ключи/гео/бюджет на вентиляцию и водопровод; 3) посадочные — H1/цены/формы уже есть, проверить мобильные.",
    "Не менять ставки до накопления 30+ кликов на кампанию.",
    "Цель: 150–200 кликов/мес, а не абсолютный топ.",
], size=10.0, gap=8)

p.save("/Users/maksim/Desktop/Реклама/03_анализ/VTI_анализ_22.10.2026.pptx")

# ───────── БУХГАЛТЕРИЯ ─────────
buh = json.load(open("/Users/maksim/Desktop/Реклама/05_скрипты/buh_daily.json"))
bd = {}
for r in buh:
    d = r["segments"]["date"]; m = r["metrics"]
    bd[d] = [int(m.get("impressions",0)), int(m.get("clicks",0)), int(m.get("costMicros",0))/1e6,
             float(m.get("conversions",0)), float(m.get("searchBudgetLostImpressionShare",0))*100,
             float(m.get("searchRankLostImpressionShare",0))*100]
bdates = [d for d in sorted(bd) if d <= "2026-10-21"]
blabels = [d[8:10]+"."+d[5:7] for d in bdates]

p = new_pres()
title_slide(p, "GOOGLE ADS / БУХГАЛТЕРИЯ", "Бухгалтерские услуги:\nгде ломается", "1 кампания · 13–21 октября 2026\nранг, посадочная и запросы", "Подготовлено 22.10.2026 · без изменений")

s = add_slide(p, "ГЛАВНОЕ", "Бухгалтерия: 2 заявки, CPA $34,7, но ранг — 51%")
kpi(s, 0.55, 1.35, 2.85, "1 004", "показов 13–21.10")
kpi(s, 3.55, 1.35, 2.85, "70", "кликов 13–21.10")
kpi(s, 6.55, 1.35, 2.85, "2", "заявки (форма)")
kpi(s, 9.55, 1.35, 2.85, "$34,7", "CPA по заявкам", dark=True)
bullets(s, 0.55, 2.75, 6.1, 3.8, [
    "1 кампания «Бухгалтерские услуги», $7/день. За 13–21: 1 004 показа, 70 кликов, $69, 2 заявки.",
    "Доля показов 30,9%, потеря по рангу 50,9%, по бюджету 16,7%. Бюджет — не главное.",
    "12 объявлений ведут на главную dtcc.by — это Tilda-одностраничник: 536 слов, 5 изображений, 2 формы, нет H1/H2 и цен.",
    "Конкуренты обходят в 62–90% пересечений. Сначала LP/QS, потом ставки.",
], size=10.2, gap=8)
card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.0), Inches(2.75), Inches(5.75), Inches(3.4))
card.adjustments[0] = 0.05; card.fill.solid(); card.fill.fore_color.rgb = WHITE; card.line.color.rgb = LINE
text(s, 7.22, 2.95, 5.3, 0.25, "ГДЕ ЛОМАЕТСЯ", 9.5, True, RED)
bullets(s, 7.22, 3.30, 5.3, 2.6, [
    "LP: нет H1, нет цен, мало контента — Google не видит релевантности.",
    "QS 3–7, у части ключей LP ниже среднего.",
    "Запросы: «питер», «репетитор», «элементы метода», «калькулятор» — мусор при 386 минусах.",
], size=9.6, gap=7)

s = add_slide(p, "ДНИ", "Бухгалтерия: клики, заявки и потери по дням")
chart(s, 0.55, 1.35, 6.0, 4.3, blabels,
      {"Клики": [bd[d][1] for d in bdates], "Заявки": [bd[d][3] for d in bdates]},
      "Клики и заявки", 16, '0')
chart(s, 6.85, 1.35, 5.9, 4.3, blabels,
      {"lostB": [round(bd[d][4],1) for d in bdates], "lostR": [round(bd[d][5],1) for d in bdates]},
      "Потери: бюджет и ранг, %", 100, '0"%"')
bullets(s, 0.55, 5.85, 12.2, 1.0, [
    "13–16.10: 4–12 кликов/день, 0 заявок. 19–20.10: по 1 заявке, клики 9 и 15. 21.10: 10 кликов, 0 заявок.",
    "19.10 — lostR 41%, 20.10 — 48%, 21.10 — 55%: ранг стабильно режет охват.",
], size=9.6, gap=5)

s = add_slide(p, "LP", "dtcc.by: одностраничник Tilda, а не посадочная под услуги")
data = [
    ["Параметр", "Сейчас", "Что должно быть"],
    ["Слов на странице", "536", "1 500+ под услуги/сегменты"],
    ["H1 / H2", "нет", "H1 «Бухгалтерские услуги в Минске» + блоки"],
    ["Цены", "нет", "пакеты: ИП, ООО, нулевая отчётность"],
    ["Формы", "2", "форма + телефон + мессенджеры"],
    ["Изображения", "5", "фото команды/офиса/кейсы"],
    ["Объявления", "12 → главная", "на отдельные страницы услуг"],
]
table(s, 0.55, 1.35, 6.4, 3.3, data, widths=[1.8,1.6,3.0], font=8.6, row_h=0.44)
bullets(s, 7.25, 1.35, 5.5, 4.8, [
    "Сейчас все 12 объявлений ведут на главную. Для запроса «ведение бухучета» это слабая посадочная.",
    "Сделать 2–3 страницы: «Бухгалтерские услуги», «Бухгалтер для ИП», «Нулевая отчётность».",
    "На странице: H1 с городом, пакеты и цены, что входит, сроки, кейсы, FAQ, форма.",
    "Это поднимет LP/QS и конверсию; без этого ставки не помогут.",
], size=9.8, gap=7)
text(s, 0.55, 4.95, 6.4, 0.8, "LP = landing page. Сейчас это Tilda-визитка, а не страница под платный трафик.", 8.2, False, GRAY)

s = add_slide(p, "АУКЦИОН И ЗАПРОСЫ", "Бухгалтерия: конкуренты обходят по рангу, а не по бюджету")
data = [
    ["Конкурент", "Доля", "Выше", "Топ", "Абс. топ", "Выигрыши"],
    ["Вы", "30,9%", "—", "75,5%", "21,2%", "—"],
    ["prof-account.by", "22,1%", "81,0%", "81,9%", "26,6%", "24,4%"],
    ["buxgalteria.by", "21,6%", "74,7%", "75,2%", "21,7%", "25,0%"],
    ["rcompany.by", "20,2%", "61,6%", "76,0%", "17,1%", "26,9%"],
    ["fingorizont.by", "17,6%", "84,1%", "87,9%", "36,2%", "24,8%"],
]
table(s, 0.55, 1.35, 6.9, 3.0, data, widths=[2.2,0.9,0.8,0.8,0.9,0.9], font=8.6, row_h=0.42, hl=True)
bullets(s, 7.75, 1.35, 5.0, 4.9, [
    "Наша доля 30,9% — ниже конкурентов; потеря по рангу 50,9%, по бюджету 16,7%.",
    "Конкуренты обходят в 62–90% пересечений: не хватает ставки/QS.",
    "Запросы-мусор: «бухгалтерские услуги питер», «репетитор», «элементы метода», «счета», «калькулятор».",
    "386 минусов есть, но дырки остались; чистить точечно.",
], size=9.4, gap=6)
text(s, 0.55, 5.0, 12.2, 0.8, "Ядро: «ведение бухучета» — 13 кликов, 0 заявок; «поиск бухгалтера» — 1 заявка, QS 3. Это сигнал по LP/офферу, а не по бюджету.", 9.2, False, GRAY)

s = add_slide(p, "ПЛАН", "Бухгалтерия: сначала LP, потом ставки")
bullets(s, 0.55, 1.35, 6.0, 4.9, [
    "1. Сделать 2–3 посадочные под услуги (ведение, ИП, нулевая) с H1, ценами, кейсами, FAQ и формой.",
    "2. Перевести 12 объявлений с главной на эти страницы.",
    "3. Почистить запросы: питер, репетитор, элементы метода, счета, калькулятор.",
    "4. Поднять ставки/QS на «ведение бухучета», «бухгалтер для ИП», «бухгалтерские услуги Минск».",
    "5. Бюджет $7 не трогать до роста QS/топа: lostB 16,7%, lostR 50,9%.",
], size=9.8, gap=7)
bullets(s, 6.85, 1.35, 5.9, 4.9, [
    "Цель: топ страницы 60–70%, CPA < $25–30.",
    "Если после LP CPA не падает — менять оффер/цены, а не ставки.",
    "Конверсии уже есть (форма), но 2 заявки — мало для выводов.",
], size=9.8, gap=7)

p.save("/Users/maksim/Desktop/Реклама/03_анализ/Бухгалтерия_анализ_22.10.2026.pptx")

# ───────── YOUTUBE ─────────
p = new_pres()
title_slide(p, "YOUTUBE / IN-FEED", "YouTube In-Feed\n25–34 BY", "Кампания 24386283079 · 21–22 октября 2026\n2 показа, 0 кликов, $0", "Подготовлено 22.10.2026 · без изменений")

s = add_slide(p, "СТАТУС", "Кампания включена и одобрена, но почти не показывается")
kpi(s, 0.55, 1.35, 2.85, "2", "показа за 2 дня")
kpi(s, 3.55, 1.35, 2.85, "0", "кликов")
kpi(s, 6.55, 1.35, 2.85, "$0", "расход")
kpi(s, 9.55, 1.35, 2.85, "$0,01", "ставка CPV", dark=True)
bullets(s, 0.55, 2.75, 6.1, 3.9, [
    "Кампания ENABLED, servingStatus = SERVING. Объявление APPROVED, reviewStatus = REVIEWED.",
    "Формат: Video Responsive, In-Feed, 25–34, BY/RU. Бюджет $5/день.",
    "2 показа и 0 кликов за 2 дня — кампания barely участвует в аукционе.",
    "Креатив не тестируется: данных слишком мало.",
], size=10.4, gap=8)
card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.0), Inches(2.75), Inches(5.75), Inches(3.4))
card.adjustments[0] = 0.05; card.fill.solid(); card.fill.fore_color.rgb = WHITE; card.line.color.rgb = LINE
text(s, 7.22, 2.95, 5.3, 0.25, "ПРИЧИНА", 9.5, True, RED)
bullets(s, 7.22, 3.30, 5.3, 2.6, [
    "Ставка CPV $0,01 (target CPV $0,02) — слишком низко для конкуренции.",
    "20 каналов + 10 ключей, возраст 20–35, только In-Feed — узкая аудитория.",
    "2 дня — мало; но 2 показа явно мало даже для старта.",
], size=9.8, gap=7)

s = add_slide(p, "ЧТО ДЕЛАТЬ", "Что поднять, чтобы YouTube начал откручиваться")
bullets(s, 0.55, 1.35, 6.0, 4.9, [
    "1. Поднять CPV-ставку до $0,03–0,05 (target CPV $0,05).",
    "2. Расширить каналы/ключи: сейчас 20 каналов и 10 ключей — добавить смежные темы.",
    "3. Проверить возраст/гео: 20–35, BY/RU. Если аудитория узкая — расширить до 18–44.",
    "4. Добавить 2–3 варианта объявлений/видео для теста.",
    "5. Дать 3–5 дней и 1 000+ показов, потом смотреть CPV/CTR.",
], size=9.8, gap=7)
bullets(s, 6.85, 1.35, 5.9, 4.9, [
    "Цель кампании — «Просмотры видео». Если нужны клики на сайт, цель надо менять на «Рассмотрение»/клики, иначе алгоритм оптимизирует просмотры.",
    "Не менять креатив, пока нет 1 000+ показов.",
    "Не включать Max Conversions: данных нет.",
], size=9.8, gap=7)

s = add_slide(p, "ДАННЫЕ", "Что учтено")
bullets(s, 0.55, 1.35, 6.0, 4.9, [
    "Кампания 24386283079, аккаунт 4434931076.",
    "Период 21–22.10.2026; 2 показа, 0 кликов, $0.",
    "Ставка CPV $0,01; target CPV $0,02; бюджет $5/день.",
    "20 каналов + 10 ключей; In-Feed; 25–34; BY/RU.",
], size=10.2, gap=8)
bullets(s, 6.85, 1.35, 5.9, 4.9, [
    "Статус: ENABLED/SERVING; объявление APPROVED/REVIEWED.",
    "Метрик video_views API не отдаёт — оцениваем показы/клики/расход.",
    "В аккаунте ничего не менял.",
], size=10.2, gap=8)

p.save("/Users/maksim/Desktop/Реклама/03_анализ/YouTube_анализ_22.10.2026.pptx")
print("saved 3 decks")
