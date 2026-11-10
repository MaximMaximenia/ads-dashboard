"""Клиент API Яндекс.Директа."""
import json, os, urllib.request, urllib.error
KEY = os.path.expanduser("~/Desktop/Реклама/04_ключи/direct_api.key")
URL = "https://api.direct.yandex.com/json/v5/"
def creds():
    tok = login = None
    for line in open(KEY, encoding="utf-8"):
        line = line.strip()
        if line.startswith("DIRECT_TOKEN="): tok = line.split("=", 1)[1].strip()
        elif line.startswith("DIRECT_LOGIN="): login = line.split("=", 1)[1].strip()
    return tok, login
def call(service, method, params):
    tok, login = creds()
    body = json.dumps({"method": method, "params": params}, ensure_ascii=False).encode("utf-8")
    h = {"Authorization": "Bearer " + tok, "Accept-Language": "ru",
         "Client-Login": login, "Content-Type": "application/json; charset=utf-8"}
    req = urllib.request.Request(URL + service, body, h)
    try:
        r = urllib.request.urlopen(req, timeout=120)
        raw = r.read().decode("utf-8")
        return json.loads(raw) if raw.strip().startswith("{") else {"_raw": raw[:300], "_code": r.status}
    except urllib.error.HTTPError as e:
        return {"_http": e.code, "_body": e.read().decode("utf-8")[:400]}
if __name__ == "__main__":
    print(json.dumps(call("campaigns", "get",
        {"SelectionCriteria": {}, "FieldNames": ["Id","Name","State","Status"]}),
        ensure_ascii=False)[:600])

