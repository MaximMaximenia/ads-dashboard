import json, os, urllib.parse, urllib.request, urllib.error
K = os.path.expanduser("~/Desktop/Реклама/04_ключи/google_ads_token.json")
c = json.load(open(K))
d = urllib.parse.urlencode({"client_id": c["client_id"], "client_secret": c["client_secret"],
    "refresh_token": c["refresh_token"], "grant_type": "refresh_token"}).encode()
at = json.load(urllib.request.urlopen(urllib.request.Request(c["token_uri"], data=d)))["access_token"]
print("access token получен, длина", len(at))
for v in ("v21","v20","v19"):
    url = f"https://googleads.googleapis.com/{v}/customers:listAccessibleCustomers"
    r = urllib.request.Request(url, headers={"Authorization": "Bearer " + at})
    try:
        print(f"\n[{v}] OK ->", json.load(urllib.request.urlopen(r)))
        break
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:600]
        print(f"\n[{v}] HTTP {e.code}: {body}")
        if e.code != 404: break
