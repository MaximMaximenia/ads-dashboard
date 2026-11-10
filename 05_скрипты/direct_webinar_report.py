# -*- coding: utf-8 -*-
"""Разбор поисковой кампании 715945832 (вебинар Мейнарда) за 10.11.2026.
Читает снимок из 03_анализ/директ_вебинар_2026-11-10, пишет две страницы в dashboard/."""
import os, json, csv, re, html
from collections import defaultdict

ROOT = os.path.expanduser("~/Desktop/Реклама")
D = os.path.join(ROOT, "03_анализ", "директ_вебинар_2026-11-10")
OUT = os.path.join(ROOT, "dashboard")
e = html.escape
VAT = 1.22
OLD_CEIL, NEW_CEIL = 70, 120
OLD_WEEK, NEW_WEEK = 10000, 23000
MERGED = 3  # три новые фразы Директ склеил с уже существующими

def J(name): return json.load(open(os.path.join(D, name), encoding="utf-8"))
def T(name): return list(csv.DictReader(open(os.path.join(D, name), encoding="utf-8"), delimiter="\t"))
def n0(x): return f"{x:,.0f}".replace(",", " ")
def n2(x): return f"{x:,.2f}".replace(",", " ").replace(".", ",")

plan = J("plan.json"); before = J("auction_before.json"); after = J("auction_after.json")
ws = J("wordstat.json"); crit = T("crit.tsv"); today = T("cp_2026-11-10.tsv")
demand = {r[0]: r[1] for r in ws["rows"]}
shown = {r["Criterion"]: int(r["Impressions"]) for r in today}
G = {5821632611: "Биржи фриланса", 5821632612: "Инструменты фрилансера", 5821632613: "Поиск клиентов",
     5821741115: "Возражения и скрипты", 5821741116: "Цена и переговоры",
     5821741117: "Наставничество и консалтинг", 5821765188: "Широкие — продажи"}

# ---------- куда ушли деньги за три дня ----------
NAV = re.compile(r"kwork|кворк|upwork|апворк|freelance ?spaces?|freelancespace|\bfl\b|фл ру|фриланс ру|xwork|толока|figma|фигма|официальный сайт", re.I)
FRL = re.compile(r"фриланс|бирж", re.I)
buckets = defaultdict(lambda: [0, 0.0])
for r in crit:
    c, s = int(r["Clicks"]), float(r["Cost"])
    if not c: continue
    q = r["Query"]
    if r["MatchType"] == "NONE": k = "auto"
    elif NAV.search(q): k = "nav"
    elif FRL.search(q): k = "frl"
    else: k = "sales"
    buckets[k][0] += c; buckets[k][1] += s
tot_c = sum(v[0] for v in buckets.values()); tot_s = sum(v[1] for v in buckets.values())
BK = [("nav", "Искали сайт биржи: kwork, upwork, freelancespace, фл ру", "bad"),
      ("auto", "Автотаргетинг: запросы, которые Директ подобрал сам", "warn"),
      ("frl", "Фриланс в целом: биржи и заказы", "warn"),
      ("sales", "Фразы про продажи, цену и клиентов", "good")]

# ---------- таблица «почему не откручивало» ----------
HEADS = ["как продавать", "биржа фриланса -новичок", "скрипты продаж", "работа с возражениями",
         "тренинг по продажам", "обучение продажам", "техники продаж", "школа продаж",
         "отработка возражений", "этапы продаж", "психология продаж", "возражение я подумаю"]
DEM_KEY = {"биржа фриланса -новичок": "биржа фриланса"}
def why_rows():
    out = []
    for h in HEADS:
        a = before[h]["v"]; bid, price = a["65"]
        dm = demand.get(DEM_KEY.get(h, h))
        st = ("no", "не проходила") if bid > OLD_CEIL + 0.5 else (("edge", "на грани") if bid > OLD_CEIL - 8 else ("ok", "проходила"))
        out.append((h.replace(" -новичок", ""), dm, bid, price, shown.get(h, 0), st))
    return out

# ---------- что изменено ----------
SUSP = [("как продавать", "804 тысячи запросов в месяц про квартиры и машины. Отсюда хомяк и гигабайты"),
        ("продажи услуг", "ловила «услуги по продаже» чего угодно"),
        ("биржа фриланса", "58 % сегодняшнего расхода. Люди ищут сайт биржи, а не как продавать"),
        ("биржи фриланса для новичков", "то же самое"),
        ("работа фрилансером удаленно", "ищут вакансии"),
        ("фигма, figma, фигма онлайн", "ищут саму программу. Клик там 46–70 ₽ без НДС, дёшево не было"),
        ("тильда конструктор, tilda конструктор сайтов", "ищут конструктор сайтов"),
        ("behance портфолио, портфолио дизайнера", "ищут чужие работы для примера"),
        ("что такое воронка продаж", "учебный запрос, и спорила с минусом «что такое»"),
        ("что почитать про продажи", "ищут книги")]
RETEXT = [("техники продаж", "[техники продаж]", "без скобок ловила «продажа техники». Со скобками вход подешевел с 94 до 51 ₽"),
          ("как продавать больше", "\"как продавать больше\"", "в кавычках показывается только по самому запросу, без «…на авито»"),
          ("как продавать дорого", "\"как продавать дорого\"", "то же, без «…дорого квартиру»"),
          ("система продаж", "\"система продаж\"", "без кавычек ловила «продажа системы отопления»"),
          ("продажи в телеграм", "\"продажи в телеграм\"", "без кавычек ловила «как продать подарок в телеграм»"),
          ("как вести себя на созвоне с клиентом", "как вести созвон с клиентом", "спорила с минусом «как вести себя»")]
NEG_OUT = [("Резали целевые запросы", "интернет · телефон · ответы · урок · презентацию · инструмент · кейсы · карту · ставка · тариф · боль · эфир · прокачку · трафик · маркетинг · анализы · смотреть · часы",
            "«в интернете», «по телефону», «ответы на возражения», «уроки продаж», «карта возражений», «боли клиента», «прямой эфир»"),
           ("Отсекали нашу аудиторию", "самозанятый · ип · фотограф · видеограф · репетитор · агентство · студию · бизнес",
            "это и есть эксперты, которые продают свои услуги"),
           ("Спорили с бесплатным вебинаром", "бесплатно · бесплатный курс · скачать бесплатно",
            "вебинар бесплатный, в объявлениях написано «участие бесплатное»"),
           ("Перекрывали рабочие фразы", "мастеров · ведущий · чеки",
            "«мастер-класс по продажам», «как вести переговоры», «средний чек». «Чеки» оставил в точной форме"),
           ("Шум", "под · го · блок · центр · рф · электронные", "предлог и случайные слова из пакета на 562 минуса")]

new_by_group = defaultdict(list)
for it in plan["add_items"]: new_by_group[G[it["AdGroupId"]]].append(it["Keyword"])
neg_added = plan["neg_added"]; neg_removed = plan["neg_removed"]
active_total = len(J("active_final.json"))

# цены после правок
p65 = sorted(v["65"][1] for v in after.values() if "65" in v and v["65"][0] <= NEW_CEIL)
in65 = len(p65); med65 = p65[len(p65) // 2]; max65 = p65[-1]
locked = sorted(((k, v["65"][0]) for k, v in after.items() if "65" in v and v["65"][0] > NEW_CEIL), key=lambda x: x[1])

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@500&family=Fira+Sans:wght@400;500;600;700&display=swap');
/* Раскладка: одна колонка-записка. Сверху вывод, ниже доказательства таблицами, в конце полные списки под спойлерами. */
:root{--bg:#F8FAFC;--card:#FFF;--ink:#0F172A;--mfg:#475569;--border:#DBEAFE;--line:#E2E8F0;
--primary:#1E40AF;--secondary:#3B82F6;--muted:#E9EEF6;
--good:#065F46;--good-bg:#D1FAE5;--warn:#92400E;--warn-bg:#FEF3C7;--bad:#991B1B;--bad-bg:#FEE2E2;
--sans:'Fira Sans',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;--mono:'Fira Code',ui-monospace,Menlo,monospace;
color-scheme:light}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 var(--sans);-webkit-font-smoothing:antialiased}
.w{max-width:820px;margin:0 auto;padding-block:36px 80px;
padding-left:max(18px,env(safe-area-inset-left,0px));padding-right:max(18px,env(safe-area-inset-right,0px))}
h1{font-size:30px;line-height:1.2;margin:0 0 6px;letter-spacing:-.8px;text-wrap:balance}
.lead{color:var(--mfg);font-size:14px;margin:0 0 26px}
h2{font-size:21px;line-height:1.25;margin:44px 0 10px;letter-spacing:-.4px;text-wrap:balance}
h3{font-size:12px;letter-spacing:1.2px;text-transform:uppercase;color:var(--primary);margin:26px 0 8px;font-weight:700}
p{margin:0 0 12px;max-width:68ch}
.verdict{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:20px 22px}
.verdict p:last-child{margin-bottom:0}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:14px 0 0}
.tile{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;min-width:0}
.tile .l{font-size:12.5px;color:var(--mfg)}
.tile .v{font:500 19px var(--mono);margin-top:4px;font-variant-numeric:tabular-nums;letter-spacing:-.4px}
.tile .v s{color:var(--mfg);text-decoration:none;font-size:14px}
.tw{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:12px;margin:12px 0}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{padding:10px 14px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:11.5px;text-transform:uppercase;letter-spacing:.6px;color:var(--mfg);font-weight:600;white-space:nowrap}
tr:last-child td{border-bottom:0}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
td.q{min-width:170px}
.pill{display:inline-block;font:600 11.5px var(--sans);padding:3px 9px;border-radius:20px;white-space:nowrap}
.pill.no,.pill.bad{background:var(--bad-bg);color:var(--bad)}
.pill.edge,.pill.warn{background:var(--warn-bg);color:var(--warn)}
.pill.ok,.pill.good{background:var(--good-bg);color:var(--good)}
.note{font-size:13.5px;color:var(--mfg);line-height:1.6;margin:8px 0 0;max-width:72ch}
.bars{display:grid;gap:12px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:12px 0}
.bar .top{display:flex;gap:12px;justify-content:space-between;align-items:baseline;flex-wrap:wrap;font-size:14px}
.bar .top b{font-weight:500}
.bar .top span{font:500 13px var(--mono);color:var(--mfg);white-space:nowrap}
.track{height:10px;background:var(--muted);border-radius:6px;margin-top:6px;overflow:hidden}
.fill{height:100%;border-radius:6px}
.fill.bad{background:#DC2626}.fill.warn{background:#D97706}.fill.good{background:#059669}
ul{margin:8px 0 12px;padding-left:20px;max-width:72ch}
li{margin:7px 0}
li b,p b{font-weight:600}
code{font:500 13px var(--mono);background:var(--muted);padding:2px 6px;border-radius:5px;overflow-wrap:anywhere}
details{background:var(--card);border:1px solid var(--line);border-radius:12px;margin:10px 0;padding:0 18px}
summary{cursor:pointer;padding:14px 0;font-weight:600;font-size:15px}
summary:focus-visible{outline:3px solid var(--secondary);outline-offset:4px;border-radius:4px}
details[open] summary{border-bottom:1px solid var(--line);margin-bottom:12px}
details .body{padding-bottom:16px;font-size:14px;line-height:1.75;color:var(--mfg)}
details .body b{color:var(--ink)}
.kw{display:inline-block;font:500 12.5px var(--mono);color:var(--ink);background:var(--muted);border-radius:6px;padding:2px 7px;margin:3px 4px 3px 0;overflow-wrap:anywhere}
.wrong li{margin:10px 0}
"""

P = ['<meta name="claude:viewport-fit-sides" content="cover">',
     "<title>Поиск по вебинару Мейнарда</title>", f"<style>{CSS}</style><div class='w'>",
     "<h1>Поиск по вебинару Мейнарда</h1>",
     "<p class='lead'>Яндекс Директ · кампания 715945832 «Поиск — Фрилансеры» · разбор и правки 10.11.2026</p>"]
A = P.append

# ---------- вывод ----------
A("<div class='verdict'>")
A(f"<p><b>Реклама не откручивала из-за потолка ставки.</b> При потолке {OLD_CEIL} ₽ нас не пускало в аукцион "
  "по главным запросам про продажи: вход туда стоит 75–110 ₽. Проходили только дешёвые фразы, "
  "«биржа фриланса» и голое «как продавать». Поэтому показов было мало, а трафик шёл не тот.</p>")
A(f"<p><b>Что сделано.</b> Потолок поднят до {NEW_CEIL} ₽, недельный лимит до {n0(NEW_WEEK)} ₽. "
  f"Остановлены фразы, которые тянули мусор, добавлено {len(plan['add_items']) - MERGED} фраз про продажи. "
  "Минус-слова вычищены: ни один минус больше не спорит с рабочей фразой.</p>")
A(f"<p><b>Чего ждать.</b> 40–60 кликов в день по запросам про продажи, это 2,5–4,5 тысячи рублей. "
  f"Клик будет стоить около {n0(med65 * VAT)} ₽ с НДС, самые дорогие до {n0(max65 * VAT)} ₽. "
  "Дешёвыми по 15 ₽ были только биржи и мусор. Это оценка по ценам аукциона и спросу, первые живые цифры будут через 2–3 часа.</p>")
A("</div>")
A("<div class='tiles'>")
for l, a, b in [("Потолок клика, без НДС", f"{OLD_CEIL} ₽", f"{NEW_CEIL} ₽"),
                ("Лимит на неделю, без НДС", f"{n0(OLD_WEEK)} ₽", f"{n0(NEW_WEEK)} ₽"),
                ("Рабочих фраз", "136", str(active_total)),
                ("Минус-слов", "759", str(len(plan["neg_final"]))),
                ("Фраз, которым мешал свой же минус", "11", "0")]:
    A(f"<div class='tile'><div class='l'>{e(l)}</div><div class='v'><s>{e(a)} →</s> {e(b)}</div></div>")
A("</div>")
A(f"<p class='note'>Лимит {n0(NEW_WEEK)} ₽ в неделю без НДС — это примерно {n0(round(NEW_WEEK * VAT / 7, -2))} ₽ в день с НДС. "
  f"Потолок {NEW_CEIL} ₽ — жёсткий предел цены клика, с НДС это {n0(NEW_CEIL * VAT)} ₽. "
  "В отчётах и в телеграме суммы идут с НДС 22 %.</p>")

# ---------- почему не откручивало ----------
A("<h2>Почему не откручивало</h2>")
A("<p>Директ отдаёт по каждой фразе цену входа в блок над выдачей. Ниже фразы, по которым есть спрос, "
  "и ставка, нужная для четвёртого места в этом блоке. Всё, что выше потолка, показывалось единицы раз.</p>")
A("<div class='tw'><table><tr><th>Фраза</th><th class='n'>Ищут в день</th><th class='n'>Ставка для входа</th>"
  f"<th class='n'>Спишут за клик</th><th class='n'>Показов сегодня</th><th>При потолке {OLD_CEIL} ₽</th></tr>")
for name, dm, bid, price, sh, (cls, lab) in why_rows():
    dd = "до 1\u202f600*" if name == "техники продаж" else (f"≈ {n0(dm / 30)}" if dm else "нет данных")
    A(f"<tr><td class='q'>{e(name)}</td><td class='n'>{dd}</td><td class='n'>{n0(bid)} ₽</td>"
      f"<td class='n'>{n0(price)} ₽</td><td class='n'>{sh}</td><td><span class='pill {cls}'>{lab}</span></td></tr>")
A("</table></div>")
A("<p class='note'>«Ищут в день» — месячный спрос из Вордстата по России, делённый на 30. «Показов сегодня» — до правок, на 15:00. "
  "Ставки и цены из аукциона Директа на 10.11, без НДС. «Обучение продажам» ищут около 280 раз в день, мы показались 11 раз. "
  "* У «техники продаж» большая часть спроса — это «продажа техники», чистую долю Вордстат не выделяет.</p>")

# ---------- куда ушли деньги ----------
A("<h2>Куда ушли деньги за три дня</h2>")
A(f"<p>С 8 по 10 ноября в отчёте по запросам {tot_c} кликов на {n2(tot_s)} ₽. Вот как они делятся.</p>")
A("<div class='bars'>")
for k, lab, cls in BK:
    c, s = buckets[k]; sh = s / tot_s * 100
    A(f"<div class='bar'><div class='top'><b>{e(lab)}</b><span>{n0(s)} ₽ · {sh:.0f} % · {c} кл.</span></div>"
      f"<div class='track'><div class='fill {cls}' style='width:{sh:.1f}%'></div></div></div>")
A("</div>")
sal = buckets["sales"]
A(f"<p>На фразы про продажи пришлось {sal[0]} кликов и {n0(sal[1])} ₽ за три дня. "
  "Стратегия «максимум кликов» покупает самые дешёвые клики, а дешёвыми были биржи. "
  "Пока в кампании лежат дешёвые нецелевые фразы, она будет лить бюджет в них.</p>")

# ---------- спрос ----------
A("<h2>Сколько людей это ищет</h2>")
A("<div class='tw'><table><tr><th>Запрос</th><th class='n'>В месяц</th><th>Что внутри</th></tr>")
for q, v, c in ws["rows"]:
    A(f"<tr><td class='q'>{e(q)}</td><td class='n'>{n0(v)}</td><td>{e(c)}</td></tr>")
A("</table></div>")
A(f"<p class='note'>Вордстат, {e(ws['region'])}, {e(ws['period'])}. По «как привлечь клиентов» сервис данных не отдал, идут работы.</p>")
A("<p>Запросов именно про навык продаж по всей России примерно 1 300–1 600 в день, если сложить возражения, скрипты, обучение, курсы, тренинги и чистую часть «техник продаж». "
  "На третьем-четвёртом месте блока это, по моей оценке, 40–60 кликов в день. Первое место даст больше, но клик там стоит 110–230 ₽ с НДС. "
  "Объём сверх этого лежит во фрилансе, но там ищут заказы, а лендинг говорит про созвоны и чеки от 2 000 долларов.</p>")

# ---------- что изменено ----------
A("<h2>Что изменено</h2>")
A("<h3>Ставка и бюджет</h3>")
A(f"<ul><li>Потолок ставки {OLD_CEIL} → {NEW_CEIL} ₽. При нём в блок над выдачей входят все фразы, кроме шести. Они перечислены в конце.</li>"
  f"<li>Недельный лимит {n0(OLD_WEEK)} → {n0(NEW_WEEK)} ₽ без НДС. Стратегия прежняя, «максимум кликов».</li>"
  "<li>Автотаргетинг снова только «целевые запросы». «Альтернативные», которые я включил в 13:30, за полтора часа не дали ничего.</li></ul>")
A(f"<h3>Остановлено {len(plan['susp_ids'])} фраз</h3><div class='tw'><table><tr><th>Фраза</th><th>Почему</th></tr>")
for k, w in SUSP: A(f"<tr><td class='q'>{e(k)}</td><td>{e(w)}</td></tr>")
A("</table></div>")
A("<h3>Переписано 6 фраз</h3><div class='tw'><table><tr><th>Было</th><th>Стало</th><th>Зачем</th></tr>")
for a, b, w in RETEXT: A(f"<tr><td class='q'>{e(a)}</td><td class='q'><code>{e(b)}</code></td><td>{e(w)}</td></tr>")
A("</table></div>")
A(f"<h3>Добавлено {len(plan['add_items']) - MERGED} фраз</h3>")
A(f"<p>Все про продажи услуг, созвоны, возражения и цену. Каждая проверена на конфликт с минусами по словоформам. "
  f"Отправил {len(plan['add_items'])}, три Директ склеил с уже существующими.</p>")
for g in ["Возражения и скрипты", "Широкие — продажи", "Цена и переговоры", "Наставничество и консалтинг", "Поиск клиентов"]:
    ks = new_by_group.get(g, [])
    A(f"<details><summary>{e(g)} · {len(ks)}</summary><div class='body'>" + "".join(f"<span class='kw'>{e(k)}</span>" for k in ks) + "</div></details>")
A(f"<h3>Минус-слова: убрано {len(neg_removed)}, добавлено {len(neg_added)}</h3>")
A("<div class='tw'><table><tr><th>Что убрал</th><th>Слова</th><th>Что они резали</th></tr>")
for t, wds, w in NEG_OUT: A(f"<tr><td class='q'><b>{e(t)}</b></td><td>{e(wds)}</td><td>{e(w)}</td></tr>")
A("</table></div>")
A(f"<details><summary>Добавленные минусы · {len(neg_added)}</summary><div class='body'>"
  "<b>Зачем:</b> маркетплейсы и доски объявлений, «продажа техники», курс валют, книги и скачивание, учёба и должностные инструкции, "
  "суд, розница и смежные сферы, CRM, трейдинг, продажа бизнеса, кино.<br><br>"
  + "".join(f"<span class='kw'>{e(k)}</span>" for k in neg_added) + "</div></details>")

# ---------- где ошибся ----------
A("<h2>Где я был неправ</h2>")
A("<ul class='wrong'>"
  "<li><b>Ставка.</b> Я дважды сказал, что потолок 70 ₽ не упирается, потому что клик стоит 14 ₽. "
  "14 ₽ — это цена тех кликов, что мы выиграли. В аукционы по продажам нас не пускало совсем. Ты предлагал поднять ставку и был прав.</li>"
  "<li><b>Бюджет.</b> Вчера расход без НДС вышел 1 413 ₽ при дневной доле лимита 1 429 ₽. Похоже, вечером стратегия уже тормозила по лимиту, а я писал, что он не мешает.</li>"
  "<li><b>Сверка минусов.</b> Я сверял минусы с фразами по точному слову, без словоформ, и написал, что конфликтов нет. "
  "Проверка по словоформам нашла 11 рабочих фраз, которым мешал минус: «интернет», «телефон», «мастеров», «ведущий», «чеки», «что такое», «биржа».</li>"
  "<li><b>Фраза «как продавать».</b> Добавил её вчера без уточнения. Сегодня она дала 240 показов из 502, почти половину.</li>"
  "<li><b>Автоминусовка.</b> Я писал, что она работает. В скрипте стоял предел в 200 минусов, и после него она молча ничего не добавляла. Поправил предел на 1000.</li>"
  "<li><b>Фигма и тильда.</b> Вернул их днём как дешёвый трафик. По аукциону клик по фигме 46–70 ₽ без НДС, и ищут там саму программу. Остановил обратно.</li>"
  "<li><b>«Бесплатно».</b> Заминусовал «бесплатно» и «бесплатный курс». Вебинар бесплатный, эти люди наши. Убрал.</li>"
  "</ul>")

# ---------- дальше ----------
A("<h2>Что дальше</h2>")
lk = ", ".join(f"«{e(k)}» {n0(b)} ₽" for k, b in locked)
A("<ul>"
  "<li><b>Сегодня вечером.</b> Правки доезжают за час-два. Я сниму расход, показы по фразам и запросы и напишу, как пошло.</li>"
  f"<li><b>Шесть фраз всё ещё не проходят.</b> {lk}. Это самые точные запросы, но им нужен потолок 145 ₽. Если вечер пройдёт спокойно, предложу поднять.</li>"
  "<li><b>Возраст.</b> Корректировки «младше 18», «45–54» и «старше 55» стояли на 0 %, то есть не работали: показы шли всем возрастам. "
  "После твоего ответа выставил им −100 %. Теперь показы идут только на 18–44, ближе к 20–40 Директ резать не умеет.</li>"
  "<li><b>Заявки.</b> Директ за три дня показывает 7 достижений цели «Заявка подтверждена». Ты говоришь, заявок не было. Я их не считаю, нужна сверка в Метрике.</li>"
  "<li><b>Если не понравится.</b> Снимок кампании до правок лежит в <code>05_скрипты/директ_вебинар/backup_2026-11-10_до_правок</code>. Вернуть всё как было можно за пару минут.</li>"
  "</ul>")
A("</div>")

body = "\n".join(P)
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, "direct_webinar_artifact.html"), "w", encoding="utf-8").write(body)
stand = ('<!doctype html><html lang="ru"><head><meta charset="utf-8">'
         '<meta name="viewport" content="width=device-width,initial-scale=1">'
         + body.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '', 1)
               .replace("<div class='w'>", "</head><body><div class='w'>", 1) + "</body></html>")
open(os.path.join(OUT, "direct_webinar.html"), "w", encoding="utf-8").write(stand)
print("ok", len(body))
print("деньги:", {k: (v[0], round(v[1], 2)) for k, v in buckets.items()}, "| всего", tot_c, round(tot_s, 2))
print("вход при 120:", in65, "из", len(after), "| медиана", med65, "макс", max65, "| не проходят:", locked)
for r in why_rows(): print("  ", r)
