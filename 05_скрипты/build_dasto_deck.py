#!/usr/bin/env python3
"""Собирает презентацию по 4 активным кампаниям ДАСТО - СТО."""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION

BG = RGBColor(0xF7, 0xF7, 0xF5)
DARK = RGBColor(0x17, 0x18, 0x1A)
RED = RGBColor(0xD0, 0x13, 0x0D)
GRAY = RGBColor(0x6E, 0x6E, 0x73)
LINE = RGBColor(0xE3, 0xE3, 0xDF)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
SOFT = RGBColor(0xEF, 0xEF, 0xEC)

FONT = "Arial"
W, H = 13.333, 7.5

prs = Presentation()
prs.slide_width = Inches(W)
prs.slide_height = Inches(H)


def add_slide(kicker=None, title=None, footer="ДАСТО — СТО · 13–21.10.2026 · без изменений в аккаунте"):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid(); bg.fill.fore_color.rgb = BG; bg.line.fill.background()
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.10), prs.slide_height)
    bar.fill.solid(); bar.fill.fore_color.rgb = RED; bar.line.fill.background()
    if kicker:
        t = s.shapes.add_textbox(Inches(0.55), Inches(0.32), Inches(11.8), Inches(0.28))
        p = t.text_frame.paragraphs[0]; r = p.add_run(); r.text = kicker
        r.font.name = FONT; r.font.size = Pt(9); r.font.bold = True; r.font.color.rgb = RED
    if title:
        t = s.shapes.add_textbox(Inches(0.55), Inches(0.60), Inches(12.2), Inches(0.62))
        p = t.text_frame.paragraphs[0]; r = p.add_run(); r.text = title
        r.font.name = FONT; r.font.size = Pt(25); r.font.bold = True; r.font.color.rgb = DARK
    if footer:
        t = s.shapes.add_textbox(Inches(0.55), Inches(7.10), Inches(12.2), Inches(0.20))
        p = t.text_frame.paragraphs[0]; r = p.add_run(); r.text = footer
        r.font.name = FONT; r.font.size = Pt(8); r.font.color.rgb = GRAY
    return s


def textbox(s, x, y, w, h, text, size=12, bold=False, color=DARK, align=PP_ALIGN.LEFT,
            line_spacing=1.0, space_after=0):
    box = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame; tf.word_wrap = True
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    lines = text.split("\n") if isinstance(text, str) else text
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align; p.line_spacing = line_spacing; p.space_after = Pt(space_after)
        r = p.add_run(); r.text = line
        r.font.name = FONT; r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color
    return box


def bullets(s, x, y, w, h, items, size=12, color=DARK, gap=6, bullet_color=RED):
    box = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame; tf.word_wrap = True
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap); p.line_spacing = 1.02
        r0 = p.add_run(); r0.text = "●  "; r0.font.name = FONT; r0.font.size = Pt(size-3); r0.font.color.rgb = bullet_color
        r = p.add_run(); r.text = item; r.font.name = FONT; r.font.size = Pt(size); r.font.color.rgb = color
    return box


def kpi(s, x, y, w, value, label, accent=RED, dark=False):
    card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(1.05))
    card.adjustments[0] = 0.10
    card.fill.solid(); card.fill.fore_color.rgb = DARK if dark else WHITE
    card.line.color.rgb = DARK if dark else LINE
    tb = s.shapes.add_textbox(Inches(x+0.18), Inches(y+0.12), Inches(w-0.36), Inches(0.48))
    p = tb.text_frame.paragraphs[0]; r = p.add_run(); r.text = value
    r.font.name = FONT; r.font.size = Pt(26); r.font.bold = True; r.font.color.rgb = WHITE if dark else accent
    tb2 = s.shapes.add_textbox(Inches(x+0.18), Inches(y+0.66), Inches(w-0.36), Inches(0.28))
    p2 = tb2.text_frame.paragraphs[0]; r2 = p2.add_run(); r2.text = label
    r2.font.name = FONT; r2.font.size = Pt(9); r2.font.color.rgb = RGBColor(0xD9,0xD9,0xD9) if dark else GRAY


def table(s, x, y, w, h, data, col_widths=None, font=9, header_font=8.5, row_h=0.28,
          highlight_first=False, align_right_from=1):
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
            cell.margin_left = Inches(0.06); cell.margin_right = Inches(0.05)
            cell.margin_top = Inches(0.02); cell.margin_bottom = Inches(0.02)
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
            p.alignment = PP_ALIGN.RIGHT if (c >= align_right_from and r > 0) else PP_ALIGN.LEFT
            if r == 0 and c >= align_right_from:
                p.alignment = PP_ALIGN.RIGHT
            rr = p.add_run(); rr.text = str(data[r][c])
            rr.font.name = FONT
            rr.font.size = Pt(header_font if r == 0 else font)
            rr.font.bold = (r == 0) or (highlight_first and r == 1)
            rr.font.color.rgb = WHITE if r == 0 else DARK
            if r == 0:
                rr.font.color.rgb = WHITE
    return tbl


# ───────────────────────── 1. Титул ─────────────────────────
s = prs.slides.add_slide(prs.slide_layouts[6])
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg.fill.solid(); bg.fill.fore_color.rgb = DARK; bg.line.fill.background()
accent = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.70), Inches(1.30), Inches(0.12), Inches(3.80))
accent.fill.solid(); accent.fill.fore_color.rgb = RED; accent.line.fill.background()
textbox(s, 1.05, 1.25, 10.6, 0.35, "GOOGLE ADS  /  АВТОСЕРВИС", 11, True, RED)
textbox(s, 1.05, 1.75, 10.8, 1.10, "ДАСТО — СТО", 54, True, WHITE)
textbox(s, 1.05, 2.95, 10.8, 0.85, "4 активные кампании:\nгде теряем трафик и что даёт рост", 24, False, RGBColor(0xE8,0xE8,0xE8))
textbox(s, 1.05, 4.25, 10.8, 0.45, "13–21 октября 2026  ·  Google Ads API + статистика аукционов", 13, False, RGBColor(0xB9,0xB9,0xB9))
line = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.05), Inches(5.15), Inches(5.0), Inches(0.02))
line.fill.solid(); line.fill.fore_color.rgb = RGBColor(0x3A,0x3A,0x3C); line.line.fill.background()
textbox(s, 1.05, 5.35, 10.8, 0.35, "Подготовлено 22.10.2026  ·  в аккаунте ничего не менял", 11, False, RGBColor(0xB9,0xB9,0xB9))

# ───────────────────────── 2. Executive summary ─────────────────────────
s = add_slide("ГЛАВНОЕ", "Коротко: аккаунт работает, но рост упирается в качество")
kpi(s, 0.55, 1.45, 2.85, "47", "звонков за 13–21.10")
kpi(s, 3.55, 1.45, 2.85, "$3,82", "CPA за звонок")
kpi(s, 6.55, 1.45, 2.85, "$179", "расход за 13–21.10")
kpi(s, 9.55, 1.45, 2.85, "530", "кликов за 13–21.10", dark=True)
bullets(s, 0.55, 2.85, 6.05, 3.7, [
    "13–21 октября: 47 кликов по номеру, CPA $3,82. Аккаунт приносит звонки.",
    "Неделя к неделе: расход в день +47%, CPA $3,42 → $4,74. Рост дал объём, но не эффективность.",
    "Главный резерв — не бюджет, а качество: «развал схождение» QS 3, «регулировка фар» QS 5, 19 брендовых объявлений ведут на главную.",
    "Первый приоритет — посадочные под топ-ключи и QS. tCPA — только после 30+ звонков на кампанию.",
], size=11.6, gap=9)
# right insight card
card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.95), Inches(2.85), Inches(5.85), Inches(3.55))
card.adjustments[0] = 0.05; card.fill.solid(); card.fill.fore_color.rgb = WHITE; card.line.color.rgb = LINE
textbox(s, 7.20, 3.05, 5.35, 0.30, "ЧТО ЭТО ЗНАЧИТ", 10, True, RED)
bullets(s, 7.20, 3.42, 5.35, 2.8, [
    "Развал и СТО-По маркам — драйверы звонков: 31 из 47 за 13–21.10.",
    "Развал упирается в бюджет (lostB 30–52%), СТО и Регулировка — в ранг (lostR 31–40%).",
    "Проточка просела по объёму: 7 кликов за эту неделю, 0 звонков. Малая выборка, не паниковать.",
], size=10.8, gap=8)

# ───────────────────────── 3. Неделя к неделе ─────────────────────────
s = add_slide("ДИНАМИКА", "Неделя к неделе: больше денег — дороже звонок")
data = [
    ["Кампания", "13–19: расход", "звонки", "CPA", "20–21: расход", "звонки", "CPA"],
    ["Развал-схождение", "$29,17", "8", "$3,65", "$16,17", "4", "$4,04"],
    ["Проточка", "$11,72", "1", "$11,72", "$3,23", "0", "—"],
    ["Регулировка фар", "$41,22", "12", "$3,44", "$16,24", "3", "$5,41"],
    ["СТО - По маркам", "$30,87", "12", "$2,57", "$30,76", "7", "$4,39"],
    ["Итого", "$112,98", "33", "$3,42", "$66,40", "14", "$4,74"],
]
table(s, 0.55, 1.45, 7.55, 2.55, data, col_widths=[1.95,1.10,0.75,0.80,1.10,0.75,0.80], font=9.5, row_h=0.36, highlight_first=False)
textbox(s, 0.55, 4.18, 7.45, 0.55, "Расход в день: $22,6 → $33,2 (+47%). CPA: $3,42 → $4,74 (+39%).\nЭта неделя — 2 дня данных (20–21.10), 22-е ещё без расхода.", 9.5, False, GRAY)
# chart CPA
cd = CategoryChartData()
cd.categories = ["Развал", "Проточка", "Регулировка", "СТО-По маркам"]
cd.add_series("13–19 окт", (3.65, 11.72, 3.44, 2.57))
cd.add_series("20–21 окт", (4.04, None, 5.41, 4.39))
chart = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(8.35), Inches(1.45), Inches(4.55), Inches(3.75), cd).chart
chart.has_legend = True; chart.legend.position = XL_LEGEND_POSITION.BOTTOM; chart.legend.include_in_layout = False
chart.legend.font.size = Pt(8); chart.legend.font.name = FONT
chart.font.name = FONT; chart.font.size = Pt(8)
chart.value_axis.has_major_gridlines = False
chart.value_axis.tick_labels.font.size = Pt(8)
chart.category_axis.tick_labels.font.size = Pt(8)
chart.plots[0].gap_width = 55
chart.series[0].format.fill.solid(); chart.series[0].format.fill.fore_color.rgb = RGBColor(0xB9,0xB9,0xB6)
chart.series[1].format.fill.solid(); chart.series[1].format.fill.fore_color.rgb = RED
chart.plots[0].has_data_labels = True
dl = chart.plots[0].data_labels; dl.font.size = Pt(7); dl.font.name = FONT; dl.number_format = '$0.00'; dl.number_format_is_linked = False
textbox(s, 8.35, 5.28, 4.55, 0.60, "CPA по звонкам. У Проточки на этой неделе 0 звонков —\nбар отсутствует, это «нет данных», а не «бесплатно».", 8, False, GRAY)

# ───────────────────────── 4. 30 дней ─────────────────────────
s = add_slide("30 ДНЕЙ", "Кто сколько приносит: 58 звонков, CPA $4,62")
data = [
    ["Кампания", "Бюджет", "Расход", "Клики", "Звонки", "CPA", "Доля показов", "Потеряно\nпо бюджету", "Потеряно\nпо рангу"],
    ["Развал-схождение", "$10", "$76,75", "230", "15", "$5,12", "50,1%", "46,6%", "3,3%"],
    ["Проточка", "$5", "$36,85", "76", "7", "$5,26", "71,5%", "4,2%", "24,3%"],
    ["Регулировка фар", "$10", "$85,95", "193", "16", "$5,37", "62,3%", "11,0%", "26,7%"],
    ["СТО - По маркам", "$10", "$68,46", "238", "20", "$3,42", "40,5%", "22,5%", "37,0%"],
    ["Итого", "—", "$268,01", "737", "58", "$4,62", "—", "—", "—"],
]
table(s, 0.55, 1.45, 12.2, 2.75, data, col_widths=[2.25,0.85,1.05,0.85,0.85,0.85,1.25,1.35,1.25], font=9.2, row_h=0.36)
bullets(s, 0.55, 4.55, 6.0, 2.1, [
    "63% звонков дают СТО-По маркам и Регулировка (36 из 58).",
    "Самый дешёвый звонок — СТО-По маркам: $3,42.",
    "Самый дорогой — Регулировка: $5,37, но и объём выше.",
], size=10.5, gap=7)
textbox(s, 6.85, 4.55, 5.9, 1.9, "30 дней — это контекст, а не текущий темп:\nкампании стояли на паузе 17–18 октября, 22-е ещё без данных.\nДля решений используем 13–21 октября.", 10.5, False, GRAY)

# ───────────────────────── 5. Где теряем трафик ─────────────────────────
s = add_slide("ПОТЕРИ ТРАФИКА", "Где теряем показы: бюджет vs ранг")
cd = CategoryChartData()
cd.categories = ["Развал", "Проточка", "Регулировка", "СТО-По маркам"]
cd.add_series("Получено", (46.2, 69.7, 56.5, 35.6))
cd.add_series("Потеряно по бюджету", (52.3, 0.0, 10.7, 25.8))
cd.add_series("Потеряно по рангу", (1.5, 30.3, 32.8, 38.6))
chart = s.shapes.add_chart(XL_CHART_TYPE.BAR_STACKED_100, Inches(0.55), Inches(1.45), Inches(6.55), Inches(4.55), cd).chart
chart.has_legend = True; chart.legend.position = XL_LEGEND_POSITION.BOTTOM; chart.legend.include_in_layout = False
chart.legend.font.size = Pt(8); chart.legend.font.name = FONT
chart.font.name = FONT; chart.font.size = Pt(8)
chart.value_axis.has_major_gridlines = False; chart.value_axis.tick_labels.font.size = Pt(7)
chart.category_axis.tick_labels.font.size = Pt(8)
colors = [RGBColor(0x2B,0x2B,0x2E), RED, RGBColor(0xB9,0xB9,0xB6)]
for i, ser in enumerate(chart.series):
    ser.format.fill.solid(); ser.format.fill.fore_color.rgb = colors[i]
textbox(s, 0.55, 6.05, 6.55, 0.35, "Прошлая неделя, 13–19.10. Сумма трёх сегментов = 100%.", 8, False, GRAY)
bullets(s, 7.35, 1.50, 5.35, 4.9, [
    "Развал: 52% потеряно по бюджету, 2% по рангу. Это единственная кампания, где деньги реально ограничивают охват.",
    "СТО-По маркам: 39% по рангу + 26% по бюджету. После роста бюджета осталась потеря по рангу — качество/посадочная.",
    "Регулировка: 33% по рангу. Бюджет не главное; нужен QS/посадочная.",
    "Проточка: 30% по рангу, но мало объёма — 26 кликов за неделю.",
    "На этой неделе потеря по бюджету у Развала 30%, у остальных 0–6%: фокус смещается в ранг/качество.",
], size=10.2, gap=8)

# ───────────────────────── 6. Quality Score ─────────────────────────
s = add_slide("КАЧЕСТВО", "Quality Score: CTR хороший, страдает посадочная")
data = [
    ["Кампания", "Средний QS", "LP ниже\nсреднего", "Объявление\nниже", "CTR выше\nсреднего"],
    ["Развал-схождение", "4,89", "15", "0", "6"],
    ["Проточка", "6,43", "4", "2", "6"],
    ["Регулировка фар", "5,38", "13", "1", "7"],
    ["СТО - По маркам", "6,42", "77", "0", "59"],
]
table(s, 0.55, 1.45, 6.55, 2.35, data, col_widths=[2.15,1.05,1.15,1.05,1.15], font=9.5, row_h=0.43)
textbox(s, 7.40, 1.45, 5.35, 0.30, "ТОП-КЛЮЧИ, ГДЕ БОЛЬНО", 10, True, RED)
bullets(s, 7.40, 1.82, 5.35, 2.5, [
    "«развал схождение» — QS 3, 110 кликов, $36,25, 6 звонков, LP ниже среднего.",
    "«регулировка фар» — QS 5, 46 кликов, $19,34, 2,5 звонка, LP ниже.",
    "«настройка фар» — QS 5, 26 кликов, $11,77, 1,5 звонка, LP ниже.",
    "«проточка тормозных дисков минск» — QS 8, 24 клика, $10,77, 0 звонков (малая выборка).",
], size=9.8, gap=6)
bullets(s, 0.55, 4.20, 12.2, 2.3, [
    "Реклама кликабельна: CTR выше среднего почти по всем кампаниям. Проблема не в том, что люди не кликают.",
    "Проблема в связке «ключ → посадочная»: у 15 ключей Развала и 13 ключей Регулировки LP ниже среднего.",
    "СТО-По маркам: 77 ключей с LP ниже среднего — это цена 19 брендовых объявлений на главную.",
], size=10.5, gap=7)

# ───────────────────────── 7. Объявления и посадочные ─────────────────────────
s = add_slide("ОБЪЯВЛЕНИЯ", "19 из 31 объявления ведут на главную — и все они в СТО-По маркам")
data = [
    ["Кампания", "Финальный URL", "Объявлений"],
    ["Развал-схождение", "/razval-shozhdenie/", "4"],
    ["Проточка", "/protochka-diskov/", "4"],
    ["Регулировка фар", "/regulirovka-far/", "4"],
    ["СТО - По маркам", "/  (главная)", "19"],
]
table(s, 0.55, 1.55, 6.3, 2.35, data, col_widths=[2.2,3.0,1.1], font=9.8, row_h=0.43)
bullets(s, 7.10, 1.55, 5.65, 3.8, [
    "19 объявлений на главную — это СТО-По маркам, по одному на каждую марку: Renault, Peugeot, Citroen, Opel, Ford, VW, Skoda, BMW, Mercedes, Audi, Hyundai, Kia, Nissan, Toyota, Mazda, Honda, Volvo, Chevrolet и группа марок.",
    "31 объявление на главную — это все объявления аккаунта, включая паузу и удалённые. По работающим — 19. Я сказал 31 — это была ошибка формулировки, не данных.",
    "Для брендовых запросов главная — слабая посадочная: 77 ключей с LP ниже среднего. Тест: отдельная страница «СТО по маркам» или брендовые блоки на главной.",
], size=10.3, gap=8)
textbox(s, 0.55, 4.25, 6.3, 1.9, "Что это значит:\n• Развал, Проточка, Регулировка ведут на свои страницы — это правильно.\n• СТО-По маркам — единственная кампания, где весь трафик идёт на главную.\n• Это не обязательно ошибка: CPA $3,42. Но QS/LP можно улучшить отдельной страницей.", 10.2, False, GRAY)

# ───────────────────────── 8. Запросы и минусовка ─────────────────────────
s = add_slide("ЗАПРОСЫ", "Мусора мало, минусовка сильная — не главный рычаг")
kpi(s, 0.55, 1.45, 2.75, "508", "уникальных запросов 13–21.10")
kpi(s, 3.50, 1.45, 2.75, "4 079", "минус-слов на кампаниях")
kpi(s, 6.45, 1.45, 2.75, "69", "в общем списке минусов")
kpi(s, 9.40, 1.45, 3.30, "0", "крупных мусорных кластеров", dark=True)
data = [
    ["Запрос", "Клики", "Расход", "Звонки"],
    ["регулировка фар минск", "26", "$10,56", "2,5"],
    ["развал схождение минск", "22", "$7,19", "4"],
    ["проточка тормозных дисков", "7", "$3,11", "0"],
    ["ремонт французских авто", "4", "$1,14", "0"],
    ["хонда сервис минск", "4", "$0,93", "0"],
]
table(s, 0.55, 4.05, 6.55, 2.55, data, col_widths=[3.25,0.95,1.10,1.00], font=9.5, row_h=0.40)
bullets(s, 7.35, 4.05, 5.45, 2.5, [
    "4 079 минусов на кампаниях и 69 в общем списке — аккаунт уже хорошо зачищен.",
    "Крупного мусора нет. Точечно проверить: «ремонт французских авто» и «хонда сервис» — есть ли услуга и посадочная.",
    "«проточка» — 0 звонков, но всего 7 кликов: это выборка, а не приговор. Не минусовать.",
], size=9.8, gap=7)

# ───────────────────────── 9. Аукцион ─────────────────────────
s = add_slide("АУКЦИОН", "Мы берём 45% показов, но проигрываем абсолютный топ")
data1 = [
    ["Конкурент", "Доля\nпоказов", "Пересе-\nчение", "Позиция\nвыше", "Топ\nстраницы", "Абс.\nтоп"],
    ["Вы", "45,3%", "—", "—", "83,2%", "29,0%"],
    ["развал-схождение.бел", "14,9%", "17,0%", "52,7%", "77,5%", "29,3%"],
    ["carlife.by", "14,8%", "21,7%", "21,2%", "61,2%", "5,0%"],
    ["autoprofi.by", "13,3%", "13,9%", "57,2%", "83,8%", "34,3%"],
    ["venimotors.by", "12,7%", "13,5%", "67,7%", "90,1%", "40,3%"],
    ["vsesto.by", "10,4%", "15,3%", "17,9%", "73,1%", "3,2%"],
]
table(s, 0.55, 1.45, 7.30, 3.55, data1, col_widths=[2.55,0.95,0.95,0.95,1.00,0.90], font=8.5, row_h=0.40, highlight_first=True)
data2 = [
    ["СТО-По маркам", "Доля", "Выше", "Абс. топ"],
    ["Вы", "42,1%", "—", "14,8%"],
    ["tonymotors.by", "21,6%", "84,3%", "30,8%"],
    ["nv-service.by", "17,8%", "45,9%", "10,8%"],
    ["vsesto.by", "13,9%", "26,8%", "2,2%"],
]
table(s, 8.15, 1.45, 4.55, 2.70, data2, col_widths=[1.75,0.80,0.95,0.95], font=8.6, row_h=0.38, highlight_first=True)
bullets(s, 0.55, 5.15, 12.2, 1.7, [
    "У нас самая высокая доля показов (45,3%), но абсолютный топ — 29,0% против 40,3% у venimotors и 34,3% у autoprofi.",
    "Конкуренты обходят нас в 52–68% пересечений: мы часто на странице, но не на самой верхней позиции.",
    "Рост — не через бюджет, а через QS/ставку на топ-ключах: «развал схождение» (QS 3) и «регулировка фар» (QS 5).",
], size=10.2, gap=7)
textbox(s, 0.55, 6.70, 12.2, 0.25, "Статистика аукционов: 30 дней, интерфейс Google Ads. Слева — все кампании, справа — фильтр «СТО - По маркам».", 7.8, False, GRAY)

# ───────────────────────── 10. План по кампаниям ─────────────────────────
s = add_slide("ПЛАН", "Что делать по каждой кампании — по шагам")
cards = [
    ("РАЗВАЛ-СХОЖДЕНИЕ", "$5,12 CPA · IS 50% · lostB 47%", [
        "Починить LP под «развал схождение» (QS 3): контент, скорость, форма/CTA.",
        "Добавить 5–8 заголовков с ценой/3D-стендом/гарантией.",
        "Поднять бюджет на 20–30% — это единственная кампания с большой потерей по бюджету.",
        "Цель: CPA < $5,5, IS 65%, lostB < 35%.",
    ]),
    ("СТО - ПО МАРКАМ", "$3,42 CPA · IS 40% · lostR 37%", [
        "Отдельная страница «СТО по маркам» или брендовые блоки: 77 ключей с LP ниже среднего.",
        "19 объявлений на главную — тест одной брендовой страницы.",
        "Масштабировать бюджет только если CPA < $4,5.",
        "Цель: lostR < 25%, CPA < $4,5.",
    ]),
    ("РЕГУЛИРОВКА ФАР", "$5,37 CPA · IS 62% · lostR 27%", [
        "LP под «регулировка фар»: QS 5, 13 ключей с LP ниже.",
        "Добавить заголовки про техосмотр, ПТФ, линзы.",
        "Бюджет не поднимать, пока CPA не вернётся к $4,5.",
        "Цель: lostR < 20%, CPA < $4,5.",
    ]),
    ("ПРОТОЧКА", "$5,26 CPA · IS 72% · lostR 24%", [
        "Расширить ключи: «проточка без снятия», «проточка дисков цена», «проточка минск».",
        "Поднять ставку/IS с 60% до 75%.",
        "Бюджет $5 — тест +$3–5/день.",
        "Цель: 15–20 кликов/нед, CPA < $6.",
    ]),
]
x0, y0, cw, ch = 0.55, 1.45, 3.02, 4.75
for i, (name, sub, items) in enumerate(cards):
    x = x0 + i*(cw+0.18)
    card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y0), Inches(cw), Inches(ch))
    card.adjustments[0] = 0.04; card.fill.solid(); card.fill.fore_color.rgb = WHITE; card.line.color.rgb = LINE
    head = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y0), Inches(cw), Inches(0.08))
    head.fill.solid(); head.fill.fore_color.rgb = RED; head.line.fill.background()
    textbox(s, x+0.15, y0+0.18, cw-0.30, 0.30, name, 9.2, True, DARK)
    textbox(s, x+0.15, y0+0.48, cw-0.30, 0.28, sub, 7.6, False, GRAY)
    bullets(s, x+0.15, y0+0.88, cw-0.30, 3.55, items, size=8.6, gap=6)
textbox(s, 0.55, 6.35, 12.2, 0.30, "Не включать все 8 кампаний. Не менять ставки, бюджеты и посадочные одновременно.", 9, False, GRAY)

# ───────────────────────── 11. tCPA и решения ─────────────────────────
s = add_slide("СТАВКИ", "tCPA: не сейчас, а после 30+ звонков на кампанию")
data = [
    ["Кампания", "Звонки 30 дн.", "CPA 30 дн.", "Готовность к tCPA"],
    ["Развал-схождение", "15", "$5,12", "Средняя: 15 звонков"],
    ["Проточка", "7", "$5,26", "Низкая: мало данных"],
    ["Регулировка фар", "16", "$5,37", "Средняя: 16 звонков"],
    ["СТО - По маркам", "20", "$3,42", "Лучшая: 20 звонков"],
]
table(s, 0.55, 1.45, 6.65, 2.35, data, col_widths=[2.30,1.35,1.20,1.80], font=9.2, row_h=0.44)
bullets(s, 7.35, 1.45, 5.45, 3.0, [
    "Max Conversions не включаем: при 15–20 звонках это риск роста CPC без данных.",
    "tCPA — только A/B 50/50 на одной кампании: СТО-По маркам или Регулировка.",
    "Ставить tCPA на уровне текущего CPA: $3,4–5,4, не ниже.",
    "2–4 недели, сравнивать CPA, CR, долю показов и абсолютный топ. Не CPC.",
], size=10.0, gap=7)
textbox(s, 0.55, 4.15, 12.2, 0.30, "ТРИ РЕШЕНИЯ, КОТОРЫЕ НУЖНЫ ОТ ТЕБЯ", 10, True, RED)
bullets(s, 0.55, 4.55, 12.2, 2.1, [
    "1. Развал: поднимаем бюджет на 20–30% сейчас или сначала чиним LP/QS?",
    "2. СТО-По маркам: делаем отдельную страницу под марки или оставляем главную?",
    "3. tCPA-тест: запускаем через 2 недели после LP или ждём 30+ звонков на кампанию?",
], size=11.2, gap=9)

# ───────────────────────── 12. Данные и ограничения ─────────────────────────
s = add_slide("ДАННЫЕ", "Что учтено и чего не хватает")
bullets(s, 0.55, 1.45, 6.0, 4.9, [
    "4 активные кампании: Развал, Проточка, Регулировка фар, СТО-По маркам.",
    "Периоды: 13–19.10 (прошлая неделя) и 20–22.10 (эта, данные 20–21).",
    "Звонки = «Исходящий клик» (клик по номеру). 30 дней: 58 звонков; 13–21: 47.",
    "Quality Score — по ключам с данными; у части ключей QS нет.",
    "Статистика аукционов — 30 дней, интерфейс Google Ads; API её не отдаёт.",
], size=10.5, gap=8)
bullets(s, 6.85, 1.45, 5.95, 4.9, [
    "Аукцион по всем кампаниям и отдельно по СТО-По маркам; по остальным трём — только IS/lost IS.",
    "Эта неделя — 2 дня, 22 октября без расхода; выводы по CPA неделя к неделе — осторожные.",
    "19 объявлений на главную — только СТО-По маркам. 31 — все объявления, включая паузу.",
    "Не хватает: CRM/коллтрекинг по каждому звонку, стоимость заявки, причины отказов.",
    "В аккаунте ничего не менял: только чтение и выгрузка.",
], size=10.5, gap=8)
textbox(s, 0.55, 6.55, 12.2, 0.35, "Дальше: фиксируем решения по трём пунктам и делаем пилот на одной кампании, а не на всех сразу.", 10, True, RED)

out = "/Users/maksim/Desktop/Реклама/03_анализ/ДАСТО_анализ_22.10.2026.pptx"
prs.save(out)
print("saved", out, "slides", len(prs.slides))
