#!/usr/bin/env python3
"""Проверяет YouTube-кампанию и присылает отчёт в Telegram.

Запуск:
  python3 -I telegram_watch.py            # один раз в день (маркер)
  python3 -I telegram_watch.py --force    # отправить принудительно
"""
import datetime
import html
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path.home() / "Desktop" / "Реклама"
KEYS = ROOT / "04_ключи" / "google_ads_token.json"
MARK = ROOT / "05_скрипты" / ".last_tg_report"
LOG = ROOT / "05_скрипты" / "telegram_watch.log"

TOKEN = "7724314363:AAG5OuDDLOTpz7DT0UjXPvWGkqdKENkGMiw"
CHAT_ID = "636168342"

CAMPAIGN_ID = "24386283079"
OLD_CAMPAIGN_ID = "24361330682"
API = "https://googleads.googleapis.com/v26"


def log(msg):
    line = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ") + msg
    print(line)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def access_token():
    c = json.loads(KEYS.read_text(encoding="utf-8"))
    data = urllib.parse.urlencode({
        "client_id": c["client_id"],
        "client_secret": c["client_secret"],
        "refresh_token": c["refresh_token"],
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request(c["token_uri"], data=data)
    return json.load(urllib.request.urlopen(req, timeout=30))["access_token"]


def q(at, query):
    req = urllib.request.Request(
        f"{API}/customers/4434931076/googleAds:searchStream",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": "Bearer " + at, "Content-Type": "application/json"},
    )
    try:
        chunks = json.load(urllib.request.urlopen(req, timeout=60))
    except urllib.error.HTTPError as e:
        return {"err": e.read().decode()[:400]}
    rows = []
    for ch in chunks:
        rows.extend(ch.get("results", []))
    return rows


def send(text):
    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    }).encode()
    req = urllib.request.Request(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data=data)
    res = json.load(urllib.request.urlopen(req, timeout=30))
    if not res.get("ok"):
        raise RuntimeError(str(res)[:300])
    return res


def main():
    force = "--force" in sys.argv
    today = datetime.date.today().isoformat()
    if not force and MARK.exists() and MARK.read_text().strip() == today:
        log("already sent today")
        return 0

    at = access_token()

    metrics = q(
        at,
        f"SELECT campaign.status, campaign.serving_status, campaign.name, "
        f"campaign_budget.amount_micros, metrics.impressions, metrics.clicks, "
        f"metrics.cost_micros, metrics.video_trueview_views "
        f"FROM campaign WHERE campaign.id={CAMPAIGN_ID} AND segments.date DURING TODAY",
    )
    if isinstance(metrics, dict):
        log("metrics error: " + metrics["err"])
        metrics = []

    if metrics:
        r = metrics[0]
        m = r.get("metrics", {})
        name = r["campaign"].get("name", "YouTube In-Feed")
        status = r["campaign"].get("status", "?")
        serving = r["campaign"].get("servingStatus", "")
        budget = int(r.get("campaignBudget", {}).get("amountMicros", 0)) / 1e6
        impr = int(m.get("impressions", 0))
        clicks = int(m.get("clicks", 0))
        cost = int(m.get("costMicros", 0)) / 1e6
        views = int(m.get("videoTrueviewViews", 0) or 0)
    else:
        base = q(
            at,
            f"SELECT campaign.status, campaign.serving_status, campaign.name, "
            f"campaign_budget.amount_micros FROM campaign WHERE campaign.id={CAMPAIGN_ID}",
        )
        r = base[0] if isinstance(base, list) and base else {}
        c = r.get("campaign", {})
        name = c.get("name", "YouTube In-Feed")
        status = c.get("status", "?")
        serving = c.get("servingStatus", "")
        budget = int(r.get("campaignBudget", {}).get("amountMicros", 0)) / 1e6
        impr = clicks = views = 0
        cost = 0.0

    review = q(
        at,
        f"SELECT ad_group_ad.policy_summary.review_status, "
        f"ad_group_ad.policy_summary.approval_status "
        f"FROM ad_group_ad WHERE campaign.id={CAMPAIGN_ID}",
    )
    review_status = "?"
    if isinstance(review, list) and review:
        ps = review[0].get("adGroupAd", {}).get("policySummary", {})
        review_status = ps.get("reviewStatus", "?")

    old = q(at, f"SELECT campaign.status FROM campaign WHERE campaign.id={OLD_CAMPAIGN_ID}")
    old_status = old[0]["campaign"]["status"] if isinstance(old, list) and old else "?"

    lines = [
        "📊 <b>YouTube In-Feed — отчёт</b>",
        f"Кампания: <b>{html.escape(name)}</b>",
        f"Статус: <b>{status}</b>" + (f" / {serving}" if serving else ""),
        f"Бюджет: ${budget:.2f}/день",
        f"Показы: <b>{impr:,}</b> | Клики: <b>{clicks:,}</b> | Расход: <b>${cost:.2f}</b>",
    ]
    if views:
        lines.append(f"Просмотры TrueView: {views:,} | CPV: ${cost / views:.4f}")
    lines.append(f"Проверка объявления: {review_status}")
    lines.append(f"Старая Demand Gen: {old_status}")
    lines.append("")
    if impr == 0:
        lines.append("⚠️ Показов пока нет. Проверь: проверку объявления, ставку $0.01, бюджет.")
    else:
        lines.append("✅ Кампания показывает. Смотри Метрику: визиты по UTM infeed_test, время/отказы; заявки в Telegram.")

    text = "\n".join(lines)
    send(text)
    MARK.write_text(today)
    log("telegram sent: " + text.replace("\n", " | ")[:500])
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        log("ERROR: " + str(e))
        sys.exit(1)
