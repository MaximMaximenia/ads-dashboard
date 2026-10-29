# -*- coding: utf-8 -*-
import os, html, datetime
OUT=os.path.expanduser("~/Desktop/Реклама/dashboard"); e=html.escape
R=[
 ("Отчёт по неделям","29.10","6R4j9xCKNpRRb5RuaRVjrn",
  "Динамика за 4 недели, таймлайн правок, слив бюджета, прогноз, минус-слова","свежий"),
 ("Глубокий разбор","29.10","4zbHKivRqRJgoBMNN8pA1D",
  "14 слайдов: качество ключей, связка ключ-запрос, пересечения групп",""),
 ("План на неделю","24.10","Aqx3EakKqZKAd9Kg9HQNqN",
  "Перераспределение бюджета с учётом доступного трафика",""),
 ("Прогноз выручки","24.10","63nzfbSULBqv74XEqqULoq",
  "Конверсии, доезд, выручка по кампаниям",""),
 ("Разбор недели 17–23","24.10","Gce4tos9bP5Teg9y6e5e6g",
  "Эффект «Максимума конверсий», устройства, часы, экономика услуг",""),
 ("Дашборд по аккаунтам","20.10","GobfxgC5EycNb68J5J9aZC",
  "Шесть аккаунтов: расход, обращения, доля показов, запросы","обновляется"),
]
CSS="""
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@500&family=Fira+Sans:wght@400;500;600;700&display=swap');
:root{--bg:#F8FAFC;--card:#FFF;--ink:#0F172A;--mfg:#475569;--border:#DBEAFE;
--primary:#1E40AF;--secondary:#3B82F6;--accent:#D97706;--muted:#E9EEF6;color-scheme:light}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.55 'Fira Sans',-apple-system,sans-serif;-webkit-font-smoothing:antialiased}
.w{max-width:760px;margin:0 auto;padding-block:40px 80px;
padding-left:max(18px,env(safe-area-inset-left,0px));padding-right:max(18px,env(safe-area-inset-right,0px))}
h1{font-size:30px;margin:0 0 6px;letter-spacing:-.8px}
.lead{color:var(--mfg);font-size:14px;margin:0 0 32px}
a.item{display:block;background:var(--card);border:1px solid var(--border);border-radius:14px;
padding:18px 20px;margin-bottom:12px;text-decoration:none;color:inherit;
transition:border-color .18s ease, transform .18s ease}
a.item:hover{border-color:var(--secondary);transform:translateY(-1px)}
a.item:focus-visible{outline:3px solid var(--secondary);outline-offset:2px}
.row{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
.t{font-size:17px;font-weight:600;letter-spacing:-.2px}
.d{font:500 12px 'Fira Code',monospace;color:var(--mfg);margin-left:auto}
.s{font-size:13.5px;color:var(--mfg);margin-top:5px;line-height:1.5}
.tag{font:600 10.5px 'Fira Sans';padding:3px 9px;border-radius:20px;
background:#D1FAE5;color:#065F46;letter-spacing:.3px}
.tag.b{background:var(--muted);color:var(--mfg)}
h2{font-size:12px;letter-spacing:1.3px;text-transform:uppercase;color:var(--primary);
margin:34px 0 12px;font-weight:700}
.note{font-size:13px;color:var(--mfg);line-height:1.65;background:var(--card);
border:1px solid var(--border);border-radius:14px;padding:16px 20px}
.note b{color:var(--ink)}
code{font:500 13px 'Fira Code',monospace;background:var(--muted);padding:2px 6px;border-radius:5px}
"""
P=[f'<meta name="claude:viewport-fit-sides" content="cover">',
   "<title>ДАСТО — отчёты</title>",f"<style>{CSS}</style><div class='w'>",
   "<h1>Отчёты по рекламе</h1>",
   f"<p class='lead'>Все разборы в одном месте · обновлено {datetime.datetime.now():%d.%m.%Y}</p>"]
for t,d,uid,s,tag in R:
    tg=f"<span class='tag {'b' if tag!='свежий' else ''}'>{e(tag)}</span>" if tag else ""
    P.append(f"<a class='item' href='https://claude.ai/artifact/{uid}'>"
             f"<div class='row'><span class='t'>{e(t)}</span>{tg}<span class='d'>{d}</span></div>"
             f"<div class='s'>{e(s)}</div></a>")
P.append("<h2>Где лежат файлы</h2>")
P.append("<div class='note'>Исходники отчётов и скрипты сбора — в репозитории "
 "<code>MaximMaximenia/ads-dashboard</code>, папка <code>dashboard/</code>.<br><br>"
 "<b>Записи разговоров и номера клиентов в репозиторий не попадают</b> — папки "
 "<code>06_звонки</code> и <code>06_офлайн</code> исключены.</div>")
P.append("</div>")
body="\n".join(P)
os.makedirs(OUT,exist_ok=True)
open(os.path.join(OUT,"hub_artifact.html"),"w",encoding="utf-8").write(body)
stand=('<!doctype html><html lang="ru"><head><meta charset="utf-8">'
 '<meta name="viewport" content="width=device-width,initial-scale=1">'
 + body.replace('<meta name="claude:viewport-fit-sides" content="cover">\n','',1)
       .replace("<div class='w'>","</head><body><div class='w'>",1)+"</body></html>")
open(os.path.join(OUT,"hub.html"),"w",encoding="utf-8").write(stand)
print("ok", len(body))
