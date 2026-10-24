"""Глубокий сбор по ДАСТО. Только чтение."""
import json, os, urllib.parse, urllib.request, urllib.error
K=os.path.expanduser("~/Desktop/Реклама/04_ключи/google_ads_token.json")
API="https://googleads.googleapis.com/v26"; CID="4001664019"
OUT=os.path.expanduser("~/Desktop/Реклама/01_google_ads/dasto_deep.json")
c=json.load(open(K))
d=urllib.parse.urlencode({"client_id":c["client_id"],"client_secret":c["client_secret"],
 "refresh_token":c["refresh_token"],"grant_type":"refresh_token"}).encode()
AT=json.load(urllib.request.urlopen(urllib.request.Request(c["token_uri"],data=d)))["access_token"]
def q(query):
    r=urllib.request.Request(f"{API}/customers/{CID}/googleAds:searchStream",
      data=json.dumps({"query":query}).encode(),
      headers={"Authorization":"Bearer "+AT,"Content-Type":"application/json"})
    try:
        out=[]
        for ch in json.load(urllib.request.urlopen(r)): out+=ch.get("results",[])
        return out
    except urllib.error.HTTPError as e:
        return {"__err__": e.read().decode()[:400]}
def ok(rows, label):
    if isinstance(rows, dict):
        print(f"  ! {label}: {rows['__err__'][:200]}")
        return []
    return rows
def M(r,k,d=0): return r.get("metrics",{}).get(k,d)
def mk(r):
    return {"cost":int(M(r,"costMicros"))/1e6,"clicks":int(M(r,"clicks")),
            "impr":int(M(r,"impressions")),"conv":float(M(r,"conversions",0)),
            "convval":float(M(r,"conversionsValue",0)),
            "ctr":float(M(r,"ctr",0))*100,"cpc":int(M(r,"averageCpc",0))/1e6,
            "is":float(M(r,"searchImpressionShare",0))*100,
            "lost_b":float(M(r,"searchBudgetLostImpressionShare",0))*100,
            "lost_r":float(M(r,"searchRankLostImpressionShare",0))*100,
            "top_is":float(M(r,"searchTopImpressionShare",0))*100,
            "abs_top":float(M(r,"searchAbsoluteTopImpressionShare",0))*100}
MET_G=("metrics.cost_micros, metrics.clicks, metrics.impressions, metrics.conversions,"
     "metrics.conversions_value, metrics.ctr, metrics.average_cpc,"
     "metrics.search_impression_share, metrics.search_rank_lost_impression_share,"
     "metrics.search_top_impression_share, metrics.search_absolute_top_impression_share")
MET=("metrics.cost_micros, metrics.clicks, metrics.impressions, metrics.conversions,"
     "metrics.conversions_value, metrics.ctr, metrics.average_cpc,"
     "metrics.search_impression_share, metrics.search_budget_lost_impression_share,"
     "metrics.search_rank_lost_impression_share, metrics.search_top_impression_share,"
     "metrics.search_absolute_top_impression_share")
data={}

data["camp_daily"]=[{"date":r["segments"]["date"],"name":r["campaign"]["name"],
  "status":r["campaign"]["status"],**mk(r)} for r in
  ok(q(f"SELECT segments.date, campaign.name, campaign.status, {MET} FROM campaign "
    "WHERE segments.date BETWEEN '2026-10-10' AND '2026-10-24'"), "camp_daily")]

for key,rng in [("week","segments.date BETWEEN '2026-10-17' AND '2026-10-23'"),
                ("friday","segments.date = '2026-10-23'"),
                ("prev_week","segments.date BETWEEN '2026-10-10' AND '2026-10-16'")]:
    data[f"camp_{key}"]=[{"name":r["campaign"]["name"],"status":r["campaign"]["status"],
      "bid":r["campaign"].get("biddingStrategyType"),
      "budget":int(r.get("campaignBudget",{}).get("amountMicros",0))/1e6,**mk(r)} for r in
      ok(q(f"SELECT campaign.name, campaign.status, campaign.bidding_strategy_type,"
        f"campaign_budget.amount_micros, {MET} FROM campaign WHERE {rng}"), "camp_"+key)]
    data[f"group_{key}"]=[{"camp":r["campaign"]["name"],"group":r["adGroup"]["name"],
      "status":r["adGroup"]["status"],**mk(r)} for r in
      ok(q(f"SELECT campaign.name, ad_group.name, ad_group.status, {MET_G} FROM ad_group WHERE {rng}"), "group_"+key)]

data["changes"]=[{"when":r["changeEvent"].get("changeDateTime"),
  "what":r["changeEvent"].get("changeResourceType"),
  "op":r["changeEvent"].get("resourceChangeOperation"),
  "fields":r["changeEvent"].get("changedFields"),
  "camp":r.get("campaign",{}).get("name"),
  "who":r["changeEvent"].get("userEmail")} for r in
  ok(q("SELECT change_event.change_date_time, change_event.change_resource_type,"
    "change_event.resource_change_operation, change_event.changed_fields,"
    "change_event.user_email, campaign.name FROM change_event "
    "WHERE change_event.change_date_time BETWEEN '2026-10-20' AND '2026-10-25' "
    "ORDER BY change_event.change_date_time DESC LIMIT 200"), "changes")]

json.dump(data, open(OUT,"w"), ensure_ascii=False, indent=1)
for k,v in data.items():
    print(f"{k}: {'ОШИБКА '+str(v)[:120] if isinstance(v,dict) else str(len(v))+' строк'}")
print("\nСохранено:", OUT)
