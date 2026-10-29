"""Сбор по ДАСТО за 30 дней. Только чтение."""
import json, os, urllib.parse, urllib.request, urllib.error
K=os.path.expanduser("~/Desktop/Реклама/04_ключи/google_ads_token.json")
API="https://googleads.googleapis.com/v26"; CID="4001664019"
OUT=os.path.expanduser("~/Desktop/Реклама/01_google_ads/dasto_clean.json")
FROM,TO="2026-10-06","2026-10-23"
c=json.load(open(K))
d0=urllib.parse.urlencode({"client_id":c["client_id"],"client_secret":c["client_secret"],
 "refresh_token":c["refresh_token"],"grant_type":"refresh_token"}).encode()
AT=json.load(urllib.request.urlopen(urllib.request.Request(c["token_uri"],data=d0)))["access_token"]
def q(query,label=""):
    r=urllib.request.Request(f"{API}/customers/{CID}/googleAds:searchStream",
      data=json.dumps({"query":query}).encode(),
      headers={"Authorization":"Bearer "+AT,"Content-Type":"application/json"})
    try:
        out=[]
        for ch in json.load(urllib.request.urlopen(r)): out+=ch.get("results",[])
        return out
    except urllib.error.HTTPError as e:
        print(f"  ! {label}: {e.read().decode()[:160]}"); return []
def m(r,k,d=0): return r.get("metrics",{}).get(k,d)
def mk(r): return {"cost":int(m(r,"costMicros"))/1e6,"clicks":int(m(r,"clicks")),
  "impr":int(m(r,"impressions")),"conv":float(m(r,"conversions",0)),
  "ctr":float(m(r,"ctr",0))*100,"cpc":int(m(r,"averageCpc",0))/1e6}
IS=("metrics.search_impression_share, metrics.search_budget_lost_impression_share,"
    "metrics.search_rank_lost_impression_share, metrics.search_top_impression_share,"
    "metrics.search_absolute_top_impression_share")
BASE="metrics.cost_micros, metrics.clicks, metrics.impressions, metrics.conversions, metrics.ctr, metrics.average_cpc"
W=f"segments.date BETWEEN '{FROM}' AND '{TO}'"
def isr(r): return {"is":float(m(r,"searchImpressionShare",0))*100,
  "lost_b":float(m(r,"searchBudgetLostImpressionShare",0))*100,
  "lost_r":float(m(r,"searchRankLostImpressionShare",0))*100,
  "top":float(m(r,"searchTopImpressionShare",0))*100,
  "abstop":float(m(r,"searchAbsoluteTopImpressionShare",0))*100}
D={"from":FROM,"to":TO}

D["camp_daily"]=[{"date":r["segments"]["date"],"camp":r["campaign"]["name"],
  "budget":int(r.get("campaignBudget",{}).get("amountMicros",0))/1e6,**mk(r),**isr(r)}
  for r in q(f"SELECT segments.date, campaign.name, campaign_budget.amount_micros, {BASE}, {IS} "
             f"FROM campaign WHERE {W} AND metrics.impressions > 0","camp_daily")]

D["camp"]=[{"camp":r["campaign"]["name"],"status":r["campaign"]["status"],
  "bid":r["campaign"].get("biddingStrategyType"),
  "budget":int(r.get("campaignBudget",{}).get("amountMicros",0))/1e6,**mk(r),**isr(r)}
  for r in q(f"SELECT campaign.name, campaign.status, campaign.bidding_strategy_type,"
             f"campaign_budget.amount_micros, {BASE}, {IS} FROM campaign "
             f"WHERE {W} AND metrics.impressions > 0","camp")]

D["groups"]=[{"camp":r["campaign"]["name"],"group":r["adGroup"]["name"],**mk(r),
  "is":float(m(r,"searchImpressionShare",0))*100,
  "lost_r":float(m(r,"searchRankLostImpressionShare",0))*100,
  "top":float(m(r,"searchTopImpressionShare",0))*100}
  for r in q(f"SELECT campaign.name, ad_group.name, {BASE}, metrics.search_impression_share,"
             f"metrics.search_rank_lost_impression_share, metrics.search_top_impression_share "
             f"FROM ad_group WHERE {W} AND metrics.impressions > 0","groups")]

D["keywords"]=[{"camp":r["campaign"]["name"],"group":r["adGroup"]["name"],
  "kw":r["adGroupCriterion"]["keyword"]["text"],
  "match":r["adGroupCriterion"]["keyword"]["matchType"],
  "qs":r["adGroupCriterion"].get("qualityInfo",{}).get("qualityScore"),
  "lp":r["adGroupCriterion"].get("qualityInfo",{}).get("postClickQualityScore"),
  "rel":r["adGroupCriterion"].get("qualityInfo",{}).get("searchPredictedCtr"),
  "adrel":r["adGroupCriterion"].get("qualityInfo",{}).get("creativeQualityScore"),**mk(r)}
  for r in q(f"SELECT campaign.name, ad_group.name, ad_group_criterion.keyword.text,"
             f"ad_group_criterion.keyword.match_type, ad_group_criterion.quality_info.quality_score,"
             f"ad_group_criterion.quality_info.post_click_quality_score,"
             f"ad_group_criterion.quality_info.search_predicted_ctr,"
             f"ad_group_criterion.quality_info.creative_quality_score, {BASE} "
             f"FROM keyword_view WHERE {W} AND metrics.impressions > 0","keywords")]

for seg,key in [("segments.day_of_week","dow"),("segments.hour","hour"),("segments.device","device")]:
    D[key]=[{"k":r["segments"][key if key!="dow" else "dayOfWeek"],**mk(r)}
      for r in q(f"SELECT {seg}, {BASE} FROM campaign WHERE {W} AND metrics.impressions > 0",key)]

D["dow_daily"]=[{"date":r["segments"]["date"],"dow":r["segments"]["dayOfWeek"],**mk(r)}
  for r in q(f"SELECT segments.date, segments.day_of_week, {BASE} FROM customer "
             f"WHERE {W} AND metrics.impressions > 0","dow_daily")]

D["dev_daily"]=[{"date":r["segments"]["date"],"dev":r["segments"]["device"],**mk(r)}
  for r in q(f"SELECT segments.date, segments.device, {BASE} FROM customer "
             f"WHERE {W} AND metrics.impressions > 0","dev_daily")]

json.dump(D, open(OUT,"w"), ensure_ascii=False, indent=1)
for k,v in D.items():
    if isinstance(v,list): print(f"{k}: {len(v)}")
print("\nСохранено:", OUT)
