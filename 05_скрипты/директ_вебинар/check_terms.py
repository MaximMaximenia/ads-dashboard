#!/usr/bin/env python3
"""Получасовая проверка поисковых запросов кампании 715945832.
Явный мусор минусуем сразу, спорное — в отчёт владельцу."""
import json, os, re, subprocess, sys, time, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import direct

CID = 715945832
STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "terms_state.json")
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
        (trash if (TRASH.search(q) and not SAFE.search(q)) else watch).append((q, c, k))

    cur = direct.call("campaigns", "get", {"SelectionCriteria": {"Ids": [CID]},
                                           "FieldNames": ["Id", "NegativeKeywords"]})
    items = cur["result"]["Campaigns"][0].get("NegativeKeywords", {}).get("Items", []) or []
    norm = lambda x: re.sub(r"[!+\[\]\"]", "", x.lower()).strip()
    have = {norm(x) for x in items}
    new = [q for q, _, _ in trash if norm(q) not in have][:max(0, 1000 - len(items))]
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

    msg = (f"{dt.datetime.now():%H:%M}. Поиск-фрилансеры: заминусовал {added}, "
           f"на проверку {len(watch)}. Расход {spend:.2f} ₽, кликов {clicks}.")
    if clicked:
        msg += "\nКлики: " + "; ".join(f"{q} ({c:.0f}₽)" for q, c, _ in
                                        sorted(clicked, key=lambda x: -x[1])[:8])
    send(msg)
    return 0

if __name__ == "__main__":
    sys.exit(main())
