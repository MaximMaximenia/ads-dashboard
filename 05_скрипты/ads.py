"""Сбор сводки по аккаунтам Google Ads."""
import json, os, urllib.parse, urllib.request, urllib.error

KEYS = os.path.expanduser("~/Desktop/Реклама/04_ключи/google_ads_token.json")
API = "https://googleads.googleapis.com/v26"
ACCOUNTS = {
    "2321582658": "airzon",
    "2726193942": "DTC",
    "4001664019": "ДАСТО",
    "4434931076": "aera",
    "6081209300": "Тонировка",
    "7822265664": "VTI",
}

def access_token():
    c = json.load(open(KEYS))
    d = urllib.parse.urlencode({"client_id": c["client_id"], "client_secret": c["client_secret"],
        "refresh_token": c["refresh_token"], "grant_type": "refresh_token"}).encode()
    return json.load(urllib.request.urlopen(urllib.request.Request(c["token_uri"], data=d)))["access_token"]

def search(cid, query, at):
    req = urllib.request.Request(
        f"{API}/customers/{cid}/googleAds:searchStream",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": "Bearer " + at, "Content-Type": "application/json"})
    try:
        chunks = json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode()[:400]}
    rows = []
    for ch in chunks:
        rows.extend(ch.get("results", []))
    return rows

Q = """SELECT campaign.name, campaign.status, campaign_budget.amount_micros,
metrics.cost_micros, metrics.clicks, metrics.impressions, metrics.conversions
FROM campaign WHERE segments.date DURING LAST_7_DAYS"""

if __name__ == "__main__":
    at = access_token()
    grand = {"cost": 0.0, "clicks": 0, "conv": 0.0}
    for cid, name in ACCOUNTS.items():
        rows = search(cid, Q, at)
        if isinstance(rows, dict):
            print(f"\n=== {name} ({cid}) — ОШИБКА: {rows['error'][:200]}")
            continue
        cost = sum(int(r["metrics"].get("costMicros", 0)) for r in rows) / 1e6
        clicks = sum(int(r["metrics"].get("clicks", 0)) for r in rows)
        conv = sum(float(r["metrics"].get("conversions", 0)) for r in rows)
        budget = sum(int(r.get("campaignBudget", {}).get("amountMicros", 0)) for r in rows
                     if r["campaign"]["status"] == "ENABLED") / 1e6
        act = sum(1 for r in rows if r["campaign"]["status"] == "ENABLED")
        grand["cost"] += cost; grand["clicks"] += clicks; grand["conv"] += conv
        cpa = f"${cost/conv:.2f}" if conv else "—"
        print(f"\n=== {name} ({cid})")
        print(f"    кампаний активных {act} из {len(rows)} | бюджет ${budget:.2f}/день")
        print(f"    за 7 дней: ${cost:.2f} | {clicks} кликов | {conv:.0f} конверсий | CPA {cpa}")
    gcpa = f"${grand['cost']/grand['conv']:.2f}" if grand["conv"] else "—"
    print(f"\n=== ИТОГО за 7 дней: ${grand['cost']:.2f} | {grand['clicks']} кликов | "
          f"{grand['conv']:.0f} конверсий | CPA {gcpa}")
