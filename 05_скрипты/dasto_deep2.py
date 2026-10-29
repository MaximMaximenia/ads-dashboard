"""Глубокий сбор ДАСТО. Только чтение."""
import json, os, urllib.parse, urllib.request, urllib.error
K=os.path.expanduser("~/Desktop/Реклама/04_ключи/google_ads_token.json")
API="https://googleads.googleapis.com/v26"; CID="4001664019"
OUT=os.path.expanduser("~/Desktop/Реклама/01_google_ads/dasto_deep2.json")
A,B="2026-10-20","2026-10-28"      # текущий период
PA,PB="2026-10-06","2026-10-19"    # предыдущий
c=json.load(open(K))
d0=urllib.parse.urlencode({"client_id":c["client_id"],"client_secret":c["client_secret"],
 "refresh_token":c["refresh_token"],"grant_type":"refresh_token"}).encode()
AT=json.load(urllib.request.urlopen(urllib.request.Request(c["token_uri"],data=d0)))["access_token"]
def q(query,lbl=""):
    r=urllib.request.Request(f"{API}/customers/{CID}/googleAds:searchStream",
      data=json.dumps({"query":query}).encode(),
      headers={"Authorization":"Bearer "+AT,"Content-Type":"application/json"})
    try:
        o=[]
        for ch in json.load(urllib.request.urlopen(r)): o+=ch.get("results",[])
        return o
    except urllib.error.HTTPError as e:
        print(f"  ! {lbl}: {e.read().decode()[:140]}"); return []
def m(r,k,d=0): return r.get("metrics",{}).get(k,d)
def mk(r): return {"cost":int(m(r,"costMicros"))/1e6,"clicks":int(m(r,"clicks")),
  "impr":int(m(r,"impressions")),"conv":float(m(r,"conversions",0))}
MET="metrics.cost_micros, metrics.clicks, metrics.impressions, metrics.conversions"
IS=("metrics.search_impression_share, metrics.search_budget_lost_impression_share,"
    "metrics.search_rank_lost_impression_share, metrics.search_top_impression_share,"
    "metrics.search_absolute_top_impression_share")
def isr(r): return {"is":float(m(r,"searchImpressionShare",0))*100,
  "lb":float(m(r,"searchBudgetLostImpressionShare",0))*100,
  "lr":float(m(r,"searchRankLostImpressionShare",0))*100,
  "top":float(m(r,"searchTopImpressionShare",0))*100,
  "abs":float(m(r,"searchAbsoluteTopImpressionShare",0))*100}
D={"A":A,"B":B,"PA":PA,"PB":PB}

D["daily"]=[{"d":r["segments"]["date"],"camp":r["campaign"]["name"],**mk(r),**isr(r)} for r in
  q(f"SELECT segments.date, campaign.name, {MET}, {IS} FROM campaign "
    f"WHERE segments.date BETWEEN '{PA}' AND '{B}' AND metrics.impressions>0","daily")]

for tag,(x,y) in {"cur":(A,B),"prev":(PA,PB)}.items():
    D[f"camp_{tag}"]=[{"camp":r["campaign"]["name"],"bid":r["campaign"].get("biddingStrategyType"),
      "budget":int(r.get("campaignBudget",{}).get("amountMicros",0))/1e6,**mk(r),**isr(r)} for r in
      q(f"SELECT campaign.name, campaign.bidding_strategy_type, campaign_budget.amount_micros,"
        f"{MET}, {IS} FROM campaign WHERE segments.date BETWEEN '{x}' AND '{y}' "
        f"AND metrics.impressions>0",f"camp_{tag}")]
    D[f"terms_{tag}"]=[{"term":r["searchTermView"]["searchTerm"],
      "camp":r["campaign"]["name"],"grp":r["adGroup"]["name"],
      "kw":r.get("segments",{}).get("keyword",{}).get("info",{}).get("text"),
      "match":r.get("segments",{}).get("keyword",{}).get("info",{}).get("matchType"),
      **mk(r)} for r in
      q(f"SELECT search_term_view.search_term, campaign.name, ad_group.name,"
        f"segments.keyword.info.text, segments.keyword.info.match_type, {MET} "
        f"FROM search_term_view WHERE segments.date BETWEEN '{x}' AND '{y}'",f"terms_{tag}")]

D["kw"]=[{"camp":r["campaign"]["name"],"grp":r["adGroup"]["name"],
  "kw":r["adGroupCriterion"]["keyword"]["text"],
  "match":r["adGroupCriterion"]["keyword"]["matchType"],
  "qs":r["adGroupCriterion"].get("qualityInfo",{}).get("qualityScore"),
  "lp":r["adGroupCriterion"].get("qualityInfo",{}).get("postClickQualityScore"),
  "ctr_exp":r["adGroupCriterion"].get("qualityInfo",{}).get("searchPredictedCtr"),
  "adrel":r["adGroupCriterion"].get("qualityInfo",{}).get("creativeQualityScore"),
  **mk(r)} for r in
  q(f"SELECT campaign.name, ad_group.name, ad_group_criterion.keyword.text,"
    f"ad_group_criterion.keyword.match_type, ad_group_criterion.quality_info.quality_score,"
    f"ad_group_criterion.quality_info.post_click_quality_score,"
    f"ad_group_criterion.quality_info.search_predicted_ctr,"
    f"ad_group_criterion.quality_info.creative_quality_score, {MET} "
    f"FROM keyword_view WHERE segments.date BETWEEN '{A}' AND '{B}' AND metrics.impressions>0","kw")]

D["hour"]=[{"h":r["segments"]["hour"],"camp":r["campaign"]["name"],**mk(r)} for r in
  q(f"SELECT segments.hour, campaign.name, {MET} FROM campaign "
    f"WHERE segments.date BETWEEN '{A}' AND '{B}' AND metrics.impressions>0","hour")]
D["dev"]=[{"dev":r["segments"]["device"],"camp":r["campaign"]["name"],**mk(r)} for r in
  q(f"SELECT segments.device, campaign.name, {MET} FROM campaign "
    f"WHERE segments.date BETWEEN '{A}' AND '{B}' AND metrics.impressions>0","dev")]
D["ads"]=[{"camp":r["campaign"]["name"],"grp":r["adGroup"]["name"],
  "id":r["adGroupAd"]["ad"]["id"],**mk(r)} for r in
  q(f"SELECT campaign.name, ad_group.name, ad_group_ad.ad.id, {MET} FROM ad_group_ad "
    f"WHERE segments.date BETWEEN '{A}' AND '{B}' AND metrics.impressions>0","ads")]

json.dump(D,open(OUT,"w"),ensure_ascii=False,indent=1)
for k,v in D.items():
    if isinstance(v,list): print(f"{k}: {len(v)}")
print("\n→",OUT)
