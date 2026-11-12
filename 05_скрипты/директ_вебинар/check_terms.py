#!/usr/bin/env python3
"""Проверка поисковых запросов кампании 716066143 раз в 20 минут.
Явный мусор минусуем сразу, спорное — в отчёт владельцу."""
import json, os, re, subprocess, sys, time, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import direct

CID = 716066143
STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "terms_state.json")
SEEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seen_queries.json")
ACC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hour_acc.json")
# явный мусор — минусуем без вопросов
TRASH = re.compile(r"(скач|торрент|кряк|взлом|бесплатн\w* верси|ваканс|резюме|"
 r"устроит|зарплат|подработк|как пользоват|"
 r"что так|что это|значени|перевод|википед|реферат|диплом|войти|логин|личный кабинет|"
 r"аналог|плагин|шрифт|шаблон|макет|иконк|мокап|на русском|расширени|"
 r"своими руками|самостоятельн|форум|развод|мошенн|не плат|кидают|"
 # биржи и трейдинг — правило владельца 08.11.2026
 r"бирж|трейд|крипт|биткои|биткои|битко|нфт|nft|форекс|брокер|финам|"
 r"акци[ияйюе]|облигац|дивиденд|котиров|фондов|инвест|"
 r"золот|нефт|серебр|валют|доллар|евро|обменник|"
 r"стакан|свеч[аиеу]|график акц|бинариум|тикер|p2p|bybit|coinbase|"
 r"толок|арбитраж|заработ\w* в интернет|быстро заработ)", re.I)

def report():
    tok, login = direct.creds() if hasattr(direct, "creds") else (None, None)
    import urllib.request, urllib.error
    tok = login = None
    for line in open(os.path.expanduser("~/Desktop/Реклама/04_ключи/direct_api.key"), encoding="utf-8"):
        line = line.strip()
        if line.startswith("DIRECT_TOKEN="): tok = line.split("=", 1)[1].strip()
        elif line.startswith("DIRECT_LOGIN="): login = line.split("=", 1)[1].strip()
    body = json.dumps({"params": {
        "SelectionCriteria": {"Filter": [{"Field": "CampaignId", "Operator": "EQUALS", "Values": [str(CID)]}]},
        "FieldNames": ["Query", "Impressions", "Clicks", "Cost", "Conversions"],
        "ReportName": "q_" + dt.datetime.now().strftime("%H%M%S%f"),
        "ReportType": "SEARCH_QUERY_PERFORMANCE_REPORT", "DateRangeType": "TODAY",
        "Format": "TSV", "IncludeVAT": "YES", "IncludeDiscount": "NO"}}, ensure_ascii=False).encode("utf-8")
    h = {"Authorization": "Bearer " + tok, "Client-Login": login, "Accept-Language": "ru",
         "processingMode": "auto", "returnMoneyInMicros": "false", "skipReportHeader": "true",
         "skipColumnHeader": "false", "skipReportSummary": "true",
         "Content-Type": "application/json; charset=utf-8"}
    import time
    for _ in range(12):
        try:
            r = urllib.request.urlopen(urllib.request.Request(
                "https://api.direct.yandex.com/json/v5/reports", body, h), timeout=180)
            if r.status == 200:
                t = r.read().decode("utf-8")
                if t.strip(): return t
        except urllib.error.HTTPError as e:
            return "ERR " + e.read().decode("utf-8")[:300]
        time.sleep(8)
    return ""

# целевое — не минусуем никогда, даже если совпало с мусорными паттернами
# чужая ниша и чужая профессия — режем, даже если в запросе есть «клиент» или «продажи».
# правило 12.11.2026: SAFE защищал почти всё подряд, из-за него автоминусовка весь день добавляла 0
HARD = re.compile(r"(маникюр|ногт|ресниц|броу|барбер|парикмахер|косметолог|массаж|тату|"
 r"смм|таргетолог|копирайт|верстк|дизайнер|монтажёр|монтажер|программист|"
 r"транспортн|логистик|грузоперевоз|строительн|ремонт квартир|натяжн|окна|"
 r"недвижимост|риелтор|автосалон|шиномонтаж|сахалин|казахстан|телефонов|"
 r"маркетплейс|озон|вайлдберриз|карточк|мозаик|парфюм|вэйп|коньяк|чипс|"
 r"менеджер|продавц|кассир|мерчендайз|ваканс|резюме|трудоустрой|зарплат)", re.I)

SAFE = re.compile(r"(фриланс|кворк|kwork|фигма|figma|тильда|портфолио|"
 r"продаж|продав|продать|продаю|возражен|переговор|созвон|"
 r"клиент|заказчик|эксперт|наставнич|консалтинг|коучинг|"
 r"скрипт|сделк|средний чек|закрыть|закрывать|впариван|услуг|цену|ценник)", re.I)

def send(msg):
    tg = os.path.expanduser("~/.claude/bin/tg.sh")
    for attempt in range(3):
        r = subprocess.run([tg, msg[:400]], capture_output=True, text=True)
        if r.returncode == 0 and "ошибка" not in (r.stdout + r.stderr).lower():
            return True
        time.sleep(5)
    print("ТЕЛЕГРАМ: не отправилось после 3 попыток")
    return False

def main():
    tsv = report()
    if tsv.startswith("ERR"): print(tsv); return 1
    lines = [l for l in tsv.splitlines() if l.strip()]
    if len(lines) < 2:
        print(json.dumps({"queries": 0, "added": 0}, ensure_ascii=False)); return 0
    hdr = lines[0].split("\t"); idx = {n: i for i, n in enumerate(hdr)}
    trash, watch, clicked, spend, clicks = [], [], [], 0.0, 0
    for l in lines[1:]:
        p = l.split("\t")
        if len(p) < len(hdr): continue
        q = p[idx["Query"]].strip()
        try:
            c = float(p[idx["Cost"]] or 0); k = int(p[idx["Clicks"]] or 0)
            cv = float(p[idx["Conversions"]] or 0)
        except ValueError: continue
        spend += c; clicks += k
        if k > 0: clicked.append((q, c, k))
        if k == 0 or cv > 0: continue
        (trash if (HARD.search(q) or (TRASH.search(q) and not SAFE.search(q))) else watch).append((q, c, k))

    cur = direct.call("campaigns", "get", {"SelectionCriteria": {"Ids": [CID]},
                                           "FieldNames": ["Id", "NegativeKeywords"]})
    items = cur["result"]["Campaigns"][0].get("NegativeKeywords", {}).get("Items", []) or []
    norm = lambda x: re.sub(r"[!+\[\]\"]", "", x.lower()).strip()
    have = {norm(x) for x in items}
    # Директ не принимает минус-фразы длиннее 7 слов — одна такая роняла весь пакет (12.11.2026)
    new = [q for q, _, _ in trash
           if norm(q) not in have and len(norm(q).split()) <= 7][:max(0, 1000 - len(items))]
    added = 0
    if new:
        r = direct.call("campaigns", "update", {"Campaigns": [
            {"Id": CID, "NegativeKeywords": {"Items": items + new}}]})
        res = r["result"]["UpdateResults"][0]
        added = len(new) if res.get("Id") and not res.get("Errors") else 0
        if not added: print("ОШИБКА:", json.dumps(r, ensure_ascii=False)[:300])

    st = {"at": dt.datetime.now().isoformat(timespec="seconds"), "spend": round(spend, 2),
          "clicks": clicks, "added": added, "watch": len(watch),
          "watch_top": [w[0] for w in sorted(watch, key=lambda x: -x[1])[:5]]}
    json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=False)
    print(json.dumps(st, ensure_ascii=False))

    # что появилось впервые с прошлой проверки
    try:
        seen = set(json.load(open(SEEN, encoding="utf-8")))
    except Exception:
        seen = set()
    fresh = [(q, c) for q, c, _ in clicked if q not in seen]
    seen |= {q for q, _, _ in clicked} | {q for q, _, _ in trash} | {q for q, _, _ in watch}
    json.dump(sorted(seen), open(SEEN, "w", encoding="utf-8"), ensure_ascii=False)

    # минусуем каждые 5 минут, в телеграм пишем раз в час — правило владельца 12.11.2026
    try:
        acc = json.load(open(ACC, encoding="utf-8"))
    except Exception:
        acc = {"since": dt.datetime.now().isoformat(timespec="seconds"), "added": [], "fresh": []}
    acc["added"] += new
    acc["fresh"] += [[q, c] for q, c in fresh]
    since = dt.datetime.fromisoformat(acc["since"])
    if (dt.datetime.now() - since).total_seconds() >= 3600:
        words = acc["added"]
        fr = sorted(acc["fresh"], key=lambda x: -x[1])[:12]
        msg = (f"{dt.datetime.now():%H:%M}. За час: заминусовал {len(words)}, "
               f"новых запросов с кликами {len(acc['fresh'])}.\n"
               f"Всего за сегодня {spend:.2f} ₽, {clicks} кликов.")
        if words:
            msg += "\n\nЗаминусовано:\n\n" + "\n\n".join(words[:25])
        if fr:
            msg += "\n\nНовые с кликами:\n\n" + "\n\n".join(f"{q} — {c:.0f} ₽" for q, c in fr)
        send(msg)
        acc = {"since": dt.datetime.now().isoformat(timespec="seconds"), "added": [], "fresh": []}
    json.dump(acc, open(ACC, "w", encoding="utf-8"), ensure_ascii=False)
    return 0

if __name__ == "__main__":
    sys.exit(main())
