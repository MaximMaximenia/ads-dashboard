"""Сбор данных по аккаунтам Google Ads. ТОЛЬКО ЧТЕНИЕ — ничего не меняет."""
import json, os, urllib.parse, urllib.request, urllib.error

KEYS = os.path.expanduser("~/Desktop/Реклама/04_ключи/google_ads_token.json")
OUT = os.path.expanduser("~/Desktop/Реклама/01_google_ads/snapshot.json")
API = "https://googleads.googleapis.com/v26"
ACCOUNTS = {
    "4001664019": "ДАСТО — СТО",
    "6081209300": "Тонировка Минск",
    "4434931076": "aera",
    "7822265664": "VTI",
    "2726193942": "DTC",
    "2321582658": "airzon",
}
PERIOD = "LAST_7_DAYS"

def access_token():
    c = json.load(open(KEYS))
    d = urllib.parse.urlencode({"client_id": c["client_id"], "client_secret": c["client_secret"],
        "refresh_token": c["refresh_token"], "grant_type": "refresh_token"}).encode()
    return json.load(urllib.request.urlopen(urllib.request.Request(c["token_uri"], data=d)))["access_token"]

def search(cid, query, at):
    req = urllib.request.Request(f"{API}/customers/{cid}/googleAds:searchStream",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": "Bearer " + at, "Content-Type": "application/json"})
    try:
        chunks = json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e:
        return {"__error__": e.read().decode()[:300]}
    rows = []
    for ch in chunks:
        rows.extend(ch.get("results", []))
    return rows

Q_CAMP = f"""SELECT campaign.name, campaign.status, campaign.advertising_channel_type,
campaign_budget.amount_micros, metrics.cost_micros, metrics.clicks, metrics.impressions,
metrics.ctr, metrics.average_cpc, metrics.conversions, metrics.search_impression_share,
metrics.search_budget_lost_impression_share, metrics.search_rank_lost_impression_share
FROM campaign WHERE segments.date DURING {PERIOD}"""

Q_TERMS = f"""SELECT search_term_view.search_term, campaign.name, metrics.clicks,
metrics.cost_micros, metrics.conversions, metrics.impressions
FROM search_term_view WHERE segments.date DURING {PERIOD}"""

def m(r, k, d=0):
    return r.get("metrics", {}).get(k, d)

def collect():
    at = access_token()
    out = {"period": PERIOD, "accounts": []}
    for cid, name in ACCOUNTS.items():
        acc = {"id": cid, "name": name, "campaigns": [], "terms": [], "errors": []}
        camps = search(cid, Q_CAMP, at)
        if isinstance(camps, dict):
            acc["errors"].append("кампании: " + camps["__error__"])
            camps = []
        for r in camps:
            acc["campaigns"].append({
                "name": r["campaign"]["name"],
                "status": r["campaign"]["status"],
                "type": r["campaign"].get("advertisingChannelType", ""),
                "budget": int(r.get("campaignBudget", {}).get("amountMicros", 0)) / 1e6,
                "cost": int(m(r, "costMicros")) / 1e6,
                "clicks": int(m(r, "clicks")),
                "impr": int(m(r, "impressions")),
                "ctr": float(m(r, "ctr", 0)) * 100,
                "cpc": int(m(r, "averageCpc", 0)) / 1e6,
                "conv": float(m(r, "conversions", 0)),
                "is": float(m(r, "searchImpressionShare", 0)) * 100,
                "lost_budget": float(m(r, "searchBudgetLostImpressionShare", 0)) * 100,
                "lost_rank": float(m(r, "searchRankLostImpressionShare", 0)) * 100,
            })
        terms = search(cid, Q_TERMS, at)
        if isinstance(terms, dict):
            acc["errors"].append("запросы: " + terms["__error__"])
            terms = []
        for r in terms:
            acc["terms"].append({
                "term": r["searchTermView"]["searchTerm"],
                "campaign": r["campaign"]["name"],
                "clicks": int(m(r, "clicks")),
                "impr": int(m(r, "impressions")),
                "cost": int(m(r, "costMicros")) / 1e6,
                "conv": float(m(r, "conversions", 0)),
            })
        out["accounts"].append(acc)
        print(f"{name}: кампаний {len(acc['campaigns'])}, запросов {len(acc['terms'])}"
              + (f", ОШИБКИ: {acc['errors']}" if acc["errors"] else ""))
    json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=1)
    print("\nСохранено:", OUT)
    return out

if __name__ == "__main__":
    collect()
