#!/usr/bin/env python3
"""ДАСТО v2: дневные графики, потери, аукцион, прирост, посадочные."""
import json
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION

BG = RGBColor(0xF7, 0xF7, 0xF5)
DARK = RGBColor(0x17, 0x18, 0x1A)
RED = RGBColor(0xD0, 0x13, 0x0D)
BLUE = RGBColor(0x2F, 0x5F, 0xB8)
GRAY = RGBColor(0x6E, 0x6E, 0x73)
LGRAY = RGBColor(0xB9, 0xB9, 0xB6)
LINE = RGBColor(0xE3, 0xE3, 0xDF)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
SOFT = RGBColor(0xEF, 0xEF, 0xEC)
FONT = "Arial"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

CAMP = ["Развал-схождение", "СТО - По маркам", "Регулировка фар", "Проточка тормозных дисков"]
COLORS = [RED, DARK, BLUE, GRAY]
SHORT = {"Развал-схождение": "Развал", "СТО - По маркам": "СТО-По маркам",
         "Регулировка фар": "Регулировка", "Проточка тормозных дисков": "Проточка"}

raw = json.load(open("/Users/maksim/Desktop/Реклама/05_скрипты/dasto_daily.json"))
by = {c: {} for c in CAMP}
for r in raw:
    n = r["campaign"]["name"]; d = r["segments"]["date"]
    if n not in by: continue
    m = r["metrics"]
    by[n][d] = {
        "impr": int(m.get("impressions", 0)), "clicks": int(m.get("clicks", 0)),
        "cost": int(m.get("costMicros", 0)) / 1e6, "conv": float(m.get("conversions", 0)),
        "is": float(m.get("searchImpressionShare", 0)) * 100,
        "lostb": float(m.get("searchBudgetLostImpressionShare", 0)) * 100,
        "lostr": float(m.get("searchRankLostImpressionShare", 0)) * 100,
        "top": float(m.get("searchTopImpressionShare", 0)) * 100,
        "abs": float(m.get("searchAbsoluteTopImpressionShare", 0)) * 100,
    }

DATES = [f"2026-10-{d:02d}" for d in [8,9,12,13,14,15,16,19,20,21]]
LABELS = [d[8:10] + "." + d[5:7] for d in DATES]


def add_slide(kicker=None, title=None, footer="ДАСТО — СТО · 13–21.10.2026 · только 4 активные кампании · без изменений"):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid(); bg.fill.fore_color.rgb = BG; bg.line.fill.background()
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.10), prs.slide_height)
    bar.fill.solid(); bar.fill.fore_color.rgb = RED; bar.line.fill.background()
    if kicker:
        t = s.shapes.add_textbox(Inches(0.55), Inches(0.30), Inches(11.8), Inches(0.25))
        p = t.text_frame.paragraphs[0]; r = p.add_run(); r.text = kicker
        r.font.name = FONT; r.font.size = Pt(9); r.font.bold = True; r.font.color.rgb = RED
    if title:
        t = s.shapes.add_textbox(Inches(0.55), Inches(0.56), Inches(12.2), Inches(0.60))
        p = t.text_frame.paragraphs[0]; r = p.add_run(); r.text = title
        r.font.name = FONT; r.font.size = Pt(23); r.font.bold = True; r.font.color.rgb = DARK
    if footer:
        t = s.shapes.add_textbox(Inches(0.55), Inches(7.12), Inches(12.2), Inches(0.20))
        p = t.text_frame.paragraphs[0]; r = p.add_run(); r.text = footer
        r.font.name = FONT; r.font.size = Pt(8); r.font.color.rgb = GRAY
    return s


def textbox(s, x, y, w, h, text, size=12, bold=False, color=DARK, align=PP_ALIGN.LEFT, gap=0):
    box = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame; tf.word_wrap = True
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    for i, line in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align; p.space_after = Pt(gap)
        r = p.add_run(); r.text = line
        r.font.name = FONT; r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color
    return box


def bullets(s, x, y, w, h, items, size=11, color=DARK, gap=7):
    box = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame; tf.word_wrap = True
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap); p.line_spacing = 1.02
        r0 = p.add_run(); r0.text = "●  "; r0.font.name = FONT; r0.font.size = Pt(size-3); r0.font.color.rgb = RED
        r = p.add_run(); r.text = item; r.font.name = FONT; r.font.size = Pt(size); r.font.color.rgb = color
    return box


def kpi(s, x, y, w, value, label, dark=False):
    card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(1.02))
    card.adjustments[0] = 0.10
    card.fill.solid(); card.fill.fore_color.rgb = DARK if dark else WHITE
    card.line.color.rgb = DARK if dark else LINE
    tb = s.shapes.add_textbox(Inches(x+0.16), Inches(y+0.10), Inches(w-0.32), Inches(0.46))
    p = tb.text_frame.paragraphs[0]; r = p.add_run(); r.text = value
    r.font.name = FONT; r.font.size = Pt(25); r.font.bold = True; r.font.color.rgb = WHITE if dark else RED
    tb2 = s.shapes.add_textbox(Inches(x+0.16), Inches(y+0.64), Inches(w-0.32), Inches(0.25))
    p2 = tb2.text_frame.paragraphs[0]; r2 = p2.add_run(); r2.text = label
    r2.font.name = FONT; r2.font.size = Pt(9); r2.font.color.rgb = RGBColor(0xD9,0xD9,0xD9) if dark else GRAY


def table(s, x, y, w, h, data, col_widths=None, font=8.2, header_font=7.8, row_h=0.25,
          align_right_from=1, highlight_first=False):
    rows, cols = len(data), len(data[0])
    shape = s.shapes.add_table(rows, cols, Inches(x), Inches(y), Inches(w), Inches(h))
    tbl = shape.table
    if col_widths:
        for i, cw in enumerate(col_widths):
            tbl.columns[i].width = Inches(cw)
    for r in range(rows):
        tbl.rows[r].height = Inches(row_h)
        for c in range(cols):
            cell = tbl.cell(r, c)
            cell.margin_left = Inches(0.05); cell.margin_right = Inches(0.04)
            cell.margin_top = Inches(0.01); cell.margin_bottom = Inches(0.01)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            if r == 0:
                cell.fill.fore_color.rgb = DARK
            elif highlight_first and r == 1:
                cell.fill.fore_color.rgb = RGBColor(0xFB,0xE9,0xE7)
            else:
                cell.fill.fore_color.rgb = WHITE if r % 2 else SOFT
            tf = cell.text_frame; tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.RIGHT if (c >= align_right_from) else PP_ALIGN.LEFT
            rr = p.add_run(); rr.text = str(data[r][c])
            rr.font.name = FONT; rr.font.size = Pt(header_font if r == 0 else font)
            rr.font.bold = (r == 0) or (highlight_first and r == 1)
            rr.font.color.rgb = WHITE if r == 0 else DARK
    return tbl


def line_chart(s, x, y, w, h, series, y_max, title, number_format='0"%"', legend=True):
    cd = CategoryChartData()
    cd.categories = LABELS
    for name, vals in series.items():
        cd.add_series(name, tuple(vals))
    ch = s.shapes.add_chart(XL_CHART_TYPE.LINE_MARKERS, Inches(x), Inches(y), Inches(w), Inches(h), cd).chart
    ch.has_legend = legend
    if legend:
        ch.legend.position = XL_LEGEND_POSITION.BOTTOM
        ch.legend.include_in_layout = False
        ch.legend.font.size = Pt(7.5); ch.legend.font.name = FONT
    ch.font.name = FONT; ch.font.size = Pt(7.5)
    ch.has_title = True
    ch.chart_title.text_frame.text = title
    for p in ch.chart_title.text_frame.paragraphs:
        for r in p.runs:
            r.font.size = Pt(9); r.font.bold = True; r.font.name = FONT; r.font.color.rgb = DARK
    ch.value_axis.maximum_scale = y_max
    ch.value_axis.minimum_scale = 0
    ch.value_axis.has_major_gridlines = True
    ch.value_axis.major_gridlines.format.line.color.rgb = RGBColor(0xE6,0xE6,0xE2)
    ch.value_axis.tick_labels.font.size = Pt(7); ch.value_axis.tick_labels.font.name = FONT
    ch.value_axis.tick_labels.number_format = number_format
    ch.value_axis.tick_labels.number_format_is_linked = False
    ch.category_axis.tick_labels.font.size = Pt(6.8); ch.category_axis.tick_labels.font.name = FONT
    for i, ser in enumerate(ch.series):
        ser.format.line.color.rgb = COLORS[i]
        ser.format.line.width = Pt(1.8)
        ser.marker.style = 8
        ser.marker.size = 4
        ser.marker.format.fill.solid(); ser.marker.format.fill.fore_color.rgb = COLORS[i]
        ser.marker.format.line.color.rgb = COLORS[i]
    return ch


def val(c, d, key):
    v = by[c].get(d)
    if not v: return None
    return v[key]


def conv_val(c, d):
    v = by[c].get(d)
    if not v: return None
    return round(v["conv"], 1)


def cpa_val(c, d):
    v = by[c].get(d)
    if not v or v["conv"] <= 0: return None
    return round(v["cost"] / v["conv"], 2)


def pct_val(c, d, key):
    v = by[c].get(d)
    if not v: return None
    return round(v[key], 1)


# ───────── 1. Титул ─────────
s = prs.slides.add_slide(prs.slide_layouts[6])
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg.fill.solid(); bg.fill.fore_color.rgb = DARK; bg.line.fill.background()
bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.70), Inches(1.25), Inches(0.12), Inches(3.95))
bar.fill.solid(); bar.fill.fore_color.rgb = RED; bar.line.fill.background()
textbox(s, 1.05, 1.20, 10.8, 0.30, "GOOGLE ADS  /  ДАСТО - СТО", 11, True, RED)
textbox(s, 1.05, 1.65, 10.8, 1.0, "Дневная динамика\nи где теряем трафик", 42, True, WHITE)
textbox(s, 1.05, 3.35, 10.8, 0.60, "4 активные кампании · 8–21 октября 2026", 20, False, RGBColor(0xE6,0xE6,0xE6))
textbox(s, 1.05, 4.05, 10.8, 0.35, "звонки · CPA · потеря по бюджету · потеря по рангу · аукцион · прирост", 11, False, RGBColor(0xB9,0xB9,0xB9))
line = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.05), Inches(5.15), Inches(5.0), Inches(0.02))
line.fill.solid(); line.fill.fore_color.rgb = RGBColor(0x3A,0x3A,0x3C); line.line.fill.background()
textbox(s, 1.05, 5.33, 10.8, 0.30, "Подготовлено 22.10.2026 · в аккаунте ничего не менял", 10, False, RGBColor(0xB9,0xB9,0xB9))

# ───────── 2. Главное ─────────
s = add_slide("ГЛАВНОЕ", "Что показывают дни: рост объёма и рост CPA")
kpi(s, 0.55, 1.35, 2.85, "47", "звонков 13–21.10")
kpi(s, 3.55, 1.35, 2.85, "$3,82", "CPA 13–21.10")
kpi(s, 6.55, 1.35, 2.85, "$179", "расход 13–21.10")
kpi(s, 9.55, 1.35, 2.85, "58", "звонков за 30 дней", dark=True)
bullets(s, 0.55, 2.70, 6.15, 3.85, [
    "13–21 октября: 47 звонков, $179, CPA $3,82. За 30 дней — 58 звонков, CPA $4,62.",
    "17–18 октября кампании не работали; 19-е — провал (2 звонка), 20–21-е восстановление (6 и 8).",
    "Рост бюджета дал объём, но CPA вырос: $3,42 → $4,74. Причина — масштабирование СТО и Регулировки, а не общий рост качества.",
    "Развал теряет по бюджету (42,6% за 13–21), СТО и Регулировка — по рангу (39,2% и 32,7%). Это разные рычаги.",
], size=10.8, gap=8)
card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.0), Inches(2.70), Inches(5.8), Inches(3.55))
card.adjustments[0] = 0.05; card.fill.solid(); card.fill.fore_color.rgb = WHITE; card.line.color.rgb = LINE
textbox(s, 7.22, 2.90, 5.35, 0.25, "ГЛАВНЫЙ ВЫВОД", 9.5, True, RED)
bullets(s, 7.22, 3.25, 5.35, 2.8, [
    "Развал: бюджет — главный рычаг. +20–30% бюджета может дать ~3 звонка/нед.",
    "СТО: бюджет и ранг примерно равны за 13–21, но сейчас ранг 36,6% против бюджета 6,2%. Сначала LP/QS, потом бюджет.",
    "Регулировка: бюджет 0, только ранг. Проточка: ранг, но мало объёма.",
], size=10.0, gap=8)

# ───────── 3. Звонки по дням ─────────
s = add_slide("ДНИ · ЗВОНКИ", "Звонки по дням: 19-е провал, 20–21-е восстановление")
line_chart(s, 0.55, 1.35, 8.35, 4.45,
           {SHORT[c]: [conv_val(c, d) for d in DATES] for c in CAMP},
           4.5, "Звонки в день", '0.0')
bullets(s, 9.15, 1.40, 3.75, 5.0, [
    "13–16.10: 6–10 звонков/день по всем кампаниям.",
    "19.10: 2 звонка — провал после паузы 17–18.10.",
    "20–21.10: 6 и 8 звонков, но CPA выше: $5,38 и $4,27.",
    "Проточка: после 14.10 — 0 звонков, 1–4 клика/день. Это не приговор, это мало данных.",
], size=9.2, gap=7)

# ───────── 4. CPA по дням ─────────
s = add_slide("ДНИ · CPA", "CPA по дням: цифры скачут из-за малых чисел")
line_chart(s, 0.55, 1.35, 8.35, 4.45,
           {SHORT[c]: [cpa_val(c, d) for d in DATES] for c in CAMP},
           12, "CPA в день, $", '$0.00')
textbox(s, 9.15, 1.35, 3.75, 0.55, "Точки есть только там, где были звонки.\n0 — это «нет данных», а не бесплатно.", 8.2, False, GRAY)
bullets(s, 9.15, 2.05, 3.75, 4.4, [
    "Развал: $1,61–$7,67; 19.10 — 0 звонков.",
    "СТО: $2,32–$6,83; 20.10 — $4,33.",
    "Регулировка: $1,12–$9,59; 21.10 — $3,33.",
    "Один день ничего не решает: смотреть 3–7-дневное среднее.",
], size=9.2, gap=7)

# ───────── 5. Потеря по бюджету ─────────
s = add_slide("ДНИ · БЮДЖЕТ", "Потеря по бюджету: где деньги реально режут охват")
line_chart(s, 0.55, 1.35, 8.35, 4.45,
           {SHORT[c]: [pct_val(c, d, "lostb") for d in DATES] for c in CAMP},
           70, "Потеряно по бюджету, %", '0"%"')
bullets(s, 9.15, 1.40, 3.75, 5.0, [
    "Развал: 35–65% почти каждый день, пик 16.10 — 64,7%. Это главный ограничитель.",
    "СТО: 63,5% 13.10 → 0% 15–20.10 → 10,9% 21.10. Бюджет перестал быть главным.",
    "Регулировка: 0–28%, с 20.10 — 0%. Бюджет не режет.",
    "Проточка: 0% почти всегда. Бюджет не режет.",
], size=9.2, gap=7)
textbox(s, 0.55, 6.05, 8.35, 0.35, "Потеря по бюджету = доля показов, которые не получили из-за дневного лимита.", 8.2, False, GRAY)

# ───────── 6. Потеря по рангу ─────────
s = add_slide("ДНИ · РАНГ", "Потеря по рангу: не хватает ставки/качества, а не денег")
line_chart(s, 0.55, 1.35, 8.35, 4.45,
           {SHORT[c]: [pct_val(c, d, "lostr") for d in DATES] for c in CAMP},
           60, "Потеряно по рангу, %", '0"%"')
bullets(s, 9.15, 1.40, 3.75, 5.0, [
    "Ранг — это Ad Rank: ставка × Quality Score + активы. Это не «рейтинг» и не бюджет.",
    "СТО: 27–55%, пик 15.10 — 54,7%. Конкуренты tonymotors и nv-service обходят по ставке/качеству.",
    "Регулировка: 0–44%, 15.10 — 44,4%. Тоже ранг, не бюджет.",
    "Проточка: 0–42%, растёт к 21.10. Развал: 0–21%, но в основном бюджет.",
], size=8.9, gap=6)
textbox(s, 0.55, 6.05, 8.35, 0.35, "Потеря по рангу = доля показов, которые не получили, потому что Ad Rank ниже конкурентов.", 8.2, False, GRAY)

# ───────── 7. Аукцион по дням ─────────
s = add_slide("ДНИ · АУКЦИОН", "Доля показов, топ страницы и абсолютный топ — по дням")
line_chart(s, 0.45, 1.30, 4.15, 3.95,
           {SHORT[c]: [pct_val(c, d, "is") for d in DATES] for c in CAMP},
           100, "Доля показов (выкуп), %", '0"%"')
line_chart(s, 4.60, 1.30, 4.15, 3.95,
           {SHORT[c]: [pct_val(c, d, "top") for d in DATES] for c in CAMP},
           100, "Топ страницы, %", '0"%"', legend=False)
line_chart(s, 8.75, 1.30, 4.15, 3.95,
           {SHORT[c]: [pct_val(c, d, "abs") for d in DATES] for c in CAMP},
           50, "Абсолютный топ, %", '0"%"', legend=False)
bullets(s, 0.55, 5.45, 12.2, 1.55, [
    "Выкуп (доля показов) — сколько аукционов вы выиграли. Топ страницы — показ в верхнем блоке. Абсолютный топ — самая первая позиция.",
    "Абсолютный топ вам не нужен: цель — топ страницы 70–80%, а не первая строка. Сейчас топ страницы 38–61%, абсолютный топ 11–27%.",
], size=9.6, gap=6)
textbox(s, 0.55, 6.85, 12.2, 0.22, "Процент выигрышей (outranking share) API по дням не отдаёт; он есть в UI за период — см. слайд «Аукцион»", 7.6, False, GRAY)

# ───────── 8. Дневные таблицы: Развал + СТО ─────────
def daily_rows(c):
    out = []
    for d in DATES:
        v = by[c].get(d)
        if not v: continue
        cpa = f"${v['cost']/v['conv']:.2f}" if v["conv"] > 0 else "—"
        out.append([d[8:10]+"."+d[5:7], f"{v['impr']:,}".replace(",", " "), str(v["clicks"]),
                    f"${v['cost']:.2f}", f"{v['conv']:.1f}", cpa,
                    f"{v['is']:.0f}%", f"{v['lostb']:.0f}%", f"{v['lostr']:.0f}%",
                    f"{v['top']:.0f}%", f"{v['abs']:.0f}%"])
    return out

HEAD = ["Дата", "Показы", "Клики", "Расход", "Звонки", "CPA", "IS", "lostB", "lostR", "Top", "Abs"]
CW = [0.85, 1.05, 0.85, 1.05, 0.90, 0.95, 0.80, 0.90, 0.90, 0.85, 0.85]

s = add_slide("ДНИ · ТАБЛИЦЫ 1/2", "Развал и СТО-По маркам: все дни, все цифры")
textbox(s, 0.55, 1.30, 6.0, 0.25, "РАЗВАЛ-СХОЖДЕНИЕ", 9.5, True, RED)
table(s, 0.55, 1.58, 10.0, 2.55, [HEAD] + daily_rows(CAMP[0]), col_widths=CW, font=7.0, header_font=6.8, row_h=0.215)
textbox(s, 0.55, 4.20, 6.0, 0.25, "СТО - ПО МАРКАМ", 9.5, True, RED)
table(s, 0.55, 4.48, 10.0, 2.45, [HEAD] + daily_rows(CAMP[1]), col_widths=CW, font=7.0, header_font=6.8, row_h=0.215)
textbox(s, 10.75, 1.35, 2.1, 5.3, "18–19.10\nданных нет:\nкампании\nне работали.\n\n22.10\nбез расхода.\n\nЗвонки —\nклики по\nномеру.", 8.0, False, GRAY)

# ───────── 9. Дневные таблицы: Регулировка + Проточка ─────────
s = add_slide("ДНИ · ТАБЛИЦЫ 2/2", "Регулировка и Проточка: все дни, все цифры")
textbox(s, 0.55, 1.30, 6.0, 0.25, "РЕГУЛИРОВКА ФАР", 9.5, True, RED)
table(s, 0.55, 1.58, 10.0, 2.55, [HEAD] + daily_rows(CAMP[2]), col_widths=CW, font=7.0, header_font=6.8, row_h=0.215)
textbox(s, 0.55, 4.20, 6.0, 0.25, "ПРОТОЧКА ТОРМОЗНЫХ ДИСКОВ", 9.5, True, RED)
table(s, 0.55, 4.48, 10.0, 2.45, [HEAD] + daily_rows(CAMP[3]), col_widths=CW, font=7.0, header_font=6.8, row_h=0.215)
textbox(s, 10.75, 1.35, 2.1, 5.3, "Регулировка:\n15 звонков\nза 13–21.\n\nПроточка:\n1 звонок\nза 13–21,\n0 после 13.10.\n\nЭто малая\nвыборка.", 8.0, False, GRAY)

# ───────── 10. Прирост ─────────
s = add_slide("ПРИРОСТ", "Сколько может дать бюджет, а сколько — ранг")
data = [
    ["Кампания", "Рычаг", "Сейчас/день", "Сценарий", "+клики/день", "+звонки/день", "+звонки/нед", "+расход/день"],
    ["Развал", "Бюджет", "1,71 звонка", "lostB 42,6% → 30%", "+4,9", "+0,42", "+3,0", "+$1,60"],
    ["Развал", "Бюджет", "1,71 звонка", "lostB 42,6% → 0%", "+16,5", "+1,43", "+10,0", "+$5,41"],
    ["СТО - По маркам", "Бюджет", "2,71 звонка", "lostB 14,4% → 0%", "+9,6", "+0,84", "+5,9", "+$2,73"],
    ["СТО - По маркам", "Ранг", "2,71 звонка", "lostR 39,2% → 25%", "+9,5", "+0,83", "+5,8", "+$2,70"],
    ["Регулировка", "Ранг", "2,14 звонка", "lostR 32,7% → 20%", "+4,3", "+0,45", "+3,2", "+$1,74"],
    ["Проточка", "Ранг", "0,14 звонка", "lostR 32,7% → 25%", "+0,5", "+0,02", "+0,1", "+$0,25"],
]
table(s, 0.55, 1.35, 12.2, 2.95, data, col_widths=[1.80,0.95,1.15,1.85,1.20,1.25,1.25,1.25], font=7.7, header_font=7.2, row_h=0.38)
bullets(s, 0.55, 4.55, 12.2, 2.2, [
    "Развал: бюджет — реальный рычаг. +3 звонка/нед при снижении lostB до 30%; +10/нед — только если снять лимит полностью (нереалистично).",
    "СТО: за 13–21 бюджет и ранг дают примерно по +6 звонков/нед; но сейчас бюджет уже 6,2%, а ранг 36,6%. Сначала LP/QS, потом бюджет.",
    "Регулировка: бюджет 0, только ранг: +2–3 звонка/нед. Проточка: ранг даёт +0,1/нед — сначала объём/ключи.",
    "Оценка при сохранении CTR, CR и CPC. Это не гарантия, а порядок цифр.",
], size=9.4, gap=7)

# ───────── 11. Почему ранг + LP ─────────
s = add_slide("РАНГ И LP", "Почему СТО и Регулировка теряют ранг и что чинить на LP")
bullets(s, 0.55, 1.35, 5.85, 5.4, [
    "Ранг (Ad Rank) = ставка × Quality Score + активы. «Потеря по рангу» значит: вас обошли по ставке/качеству, а не по бюджету.",
    "СТО: QS 6,42, но 77 ключей с LP ниже среднего; 19 брендовых объявлений ведут на главную. В главной есть только Volkswagen и BMW — нет Renault, Peugeot, Citroen. Человек ищет «СТО Renault», а попадает на общую страницу.",
    "Конкуренты: tonymotors обходит в 84,3% пересечений, nv-service — в 45,9%. CPC $0,28 — ставка низкая для брендовых аукционов.",
    "Регулировка: QS 5,38, 13 ключей с LP ниже; страница сильная (1000 слов, цены, отзывы, FAQ, 3 формы), но ad relevance/ставка слабее. Бюджет 0 — поднимать его бессмысленно.",
], size=9.4, gap=7)
bullets(s, 6.75, 1.35, 6.0, 5.4, [
    "LP = landing page. Сервисные страницы DАСТО сильные: H1, цена, процесс, отзывы, FAQ, 3 формы, 19 изображений, ~1000 слов. Их не надо переделывать с нуля.",
    "Главная: 1603 слова, 74 изображения, 4 формы — но бренды только VW/BMW. Для 19 брендовых запросов это нерелевантно.",
    "Что сделать: страница «СТО по маркам» или брендовые блоки для топ-5 (Renault, Peugeot, Citroen, Opel, Ford): модели, услуги, цены, мастера, отзывы, фото. Одна страница — тест, не 19 сразу.",
    "Для сервисных страниц: H1 с точной фразой, цена выше, schema FAQ, скорость мобильной, кнопка/форма в первом экране. Не абсолютный топ — цель топ страницы 70–80%.",
], size=9.4, gap=7)

# ───────── 12. Аукцион: агрегат ─────────
s = add_slide("АУКЦИОН", "Аукцион за 30 дней: мы первые по доле, но не по абсолютному топу")
data1 = [
    ["Конкурент", "Доля", "Пересеч.", "Выше", "Топ", "Абс. топ", "Выигрыши"],
    ["Вы", "45,3%", "—", "—", "83,2%", "29,0%", "—"],
    ["развал-схождение.бел", "14,9%", "17,0%", "52,7%", "77,5%", "29,3%", "41,2%"],
    ["carlife.by", "14,8%", "21,7%", "21,2%", "61,2%", "5,0%", "43,2%"],
    ["autoprofi.by", "13,3%", "13,9%", "57,2%", "83,8%", "34,3%", "41,7%"],
    ["venimotors.by", "12,7%", "13,5%", "67,7%", "90,1%", "40,3%", "41,1%"],
    ["vsesto.by", "10,4%", "15,3%", "17,9%", "73,1%", "3,2%", "44,0%"],
]
table(s, 0.55, 1.35, 7.55, 3.55, data1, col_widths=[2.35,0.80,0.85,0.80,0.80,0.90,0.95], font=8.0, header_font=7.4, row_h=0.42, highlight_first=True)
data2 = [
    ["СТО-По маркам", "Доля", "Выше", "Абс. топ"],
    ["Вы", "42,1%", "—", "14,8%"],
    ["tonymotors.by", "21,6%", "84,3%", "30,8%"],
    ["nv-service.by", "17,8%", "45,9%", "10,8%"],
    ["vsesto.by", "13,9%", "26,8%", "2,2%"],
]
table(s, 8.30, 1.35, 4.40, 2.70, data2, col_widths=[1.70,0.75,0.90,0.90], font=8.2, header_font=7.6, row_h=0.40, highlight_first=True)
bullets(s, 0.55, 5.15, 12.2, 1.65, [
    "Мы берём 45,3% показов, но абсолютный топ — 29,0% против 40,3% у venimotors и 34,3% у autoprofi.",
    "Конкуренты обходят нас в 52–68% пересечений. Это и есть «потеря по рангу»: мы на странице, но не выше них.",
    "Абсолютный топ не цель: цель — топ страницы 70–80%. Рост — через QS/ставку на «развал» и «регулировку», не через бюджет.",
], size=9.6, gap=6)
textbox(s, 0.55, 6.80, 12.2, 0.22, "30 дней, UI. Дневных имён конкурентов API не отдаёт; дневные графики выше — наши IS/top/abs.", 7.5, False, GRAY)

# ───────── 13. План ─────────
s = add_slide("ПЛАН", "Что делать: сначала рычаг, потом деньги")
cards = [
    ("РАЗВАЛ", "бюджет", [
        "Поднять бюджет на 20–30%: lostB 42,6% → 30%.",
        "Ожидание: +3 звонка/нед, +$1,6/день.",
        "LP/QS — вторым шагом: QS 4,89, топ-ключ QS 3.",
        "Цель: CPA < $5,5, топ страницы 55–60%.",
    ]),
    ("СТО - ПО МАРКАМ", "ранг + LP", [
        "Страница/блоки под топ-5 марок: Renault, Peugeot, Citroen, Opel, Ford.",
        "Поднять ставки на брендовые ключи; QS 6,42, 77 LP ниже.",
        "Бюджет — после LP/QS: сейчас lostB 6,2%, lostR 36,6%.",
        "Цель: топ страницы 60–70%, CPA < $4,5.",
    ]),
    ("РЕГУЛИРОВКА", "ранг", [
        "Бюджет не трогать: lostB 0%.",
        "LP/объявления: QS 5,38, 13 LP ниже.",
        "Ставка/QS: lostR 32,7% → 20%.",
        "Цель: +2–3 звонка/нед, CPA < $4,5.",
    ]),
    ("ПРОТОЧКА", "объём", [
        "Бюджет не трогать: lostB 0%.",
        "Расширить ключи/объявления: 7 кликов за неделю — мало.",
        "Ставка/IS: lostR 32,7% → 25%.",
        "Цель: 15–20 кликов/нед, CPA < $6.",
    ]),
]
for i, (name, lever, items) in enumerate(cards):
    x = 0.55 + i * 3.12
    card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(1.40), Inches(2.95), Inches(4.55))
    card.adjustments[0] = 0.04; card.fill.solid(); card.fill.fore_color.rgb = WHITE; card.line.color.rgb = LINE
    head = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(1.40), Inches(2.95), Inches(0.08))
    head.fill.solid(); head.fill.fore_color.rgb = RED; head.line.fill.background()
    textbox(s, x+0.14, 1.58, 2.65, 0.25, name, 8.8, True, DARK)
    textbox(s, x+0.14, 1.86, 2.65, 0.22, lever.upper(), 7.4, True, RED)
    bullets(s, x+0.14, 2.20, 2.65, 3.5, items, size=8.1, gap=6)
textbox(s, 0.55, 6.15, 12.2, 0.55, "Абсолютный топ не цель. Цель — топ страницы 70–80% и CPA по звонку, а не по клику.", 9.5, True, RED)

# ───────── 14. Данные ─────────
s = add_slide("ДАННЫЕ", "Что учтено и какие ограничения")
bullets(s, 0.55, 1.35, 6.0, 4.9, [
    "8–21 октября; 17–18 кампании не работали, 22 октября без расхода.",
    "4 активные кампании: Развал, СТО-По маркам, Регулировка, Проточка.",
    "Звонки = «Исходящий клик» (клик по номеру). 13–21: 47; 30 дней: 58.",
    "CPA = расход / звонки; в дни без звонков CPA нет.",
    "Качество — по ключам с данными; у части ключей QS нет.",
], size=10.0, gap=8)
bullets(s, 6.85, 1.35, 5.95, 4.9, [
    "Дневные IS/top/abs — API. Имена конкурентов и «процент выигрышей» — UI за 30 дней.",
    "Прирост — оценка при сохранении CTR/CR/CPC; не гарантия.",
    "LP-аудит: 4 страницы, H1/H2, объём, формы, бренды. Сервисные страницы сильные, главная — нет.",
    "19 объявлений на главную — только СТО-По маркам; 31 — все, включая паузу.",
    "В аккаунте ничего не менял.",
], size=10.0, gap=8)
textbox(s, 0.55, 6.55, 12.2, 0.35, "Дальше: выбрать один рычаг на кампанию и не менять всё одновременно.", 10, True, RED)

out = "/Users/maksim/Desktop/Реклама/03_анализ/ДАСТО_дневной_анализ_22.10.2026.pptx"
prs.save(out)
print("saved", out, "slides", len(prs.slides))
