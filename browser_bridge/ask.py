"""Отправить команду в Chrome-мост и дождаться результата.

Пример:
  python3 ask.py '{"op":"ping"}'
  python3 ask.py '{"op":"list_tabs"}'
  python3 ask.py '{"op":"get","args":{"tabId":123,"what":"text"}}'
"""
import json
import sys
import time
import urllib.error
import urllib.request

TOKEN = "0c689ac52222d755d6bde0886f1051c7"
BASE = "http://127.0.0.1:8765"


def call(path, obj=None, method="GET"):
    data = json.dumps(obj).encode("utf-8") if obj is not None else None
    req = urllib.request.Request(
        f"{BASE}{path}?token={TOKEN}",
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            if resp.status == 204:
                return None
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        if exc.code == 204:
            return None
        if exc.code == 409:
            return {"__busy__": True}
        raise


def main():
    if len(sys.argv) < 2:
        print("usage: ask.py '<json command>'", file=sys.stderr)
        return 2
    cmd = json.loads(sys.argv[1])

    cid = None
    for _ in range(40):
        try:
            resp = call("/cmd", cmd, "POST")
        except urllib.error.URLError as exc:
            print(f"bridge offline: {exc}", file=sys.stderr)
            return 3
        if isinstance(resp, dict) and resp.get("__busy__"):
            time.sleep(0.5)
            continue
        cid = resp["id"]
        break

    if cid is None:
        print("bridge busy", file=sys.stderr)
        return 4

    for _ in range(180):
        res = call(f"/result/{cid}")
        if res is not None:
            print(json.dumps(res, ensure_ascii=False))
            return 0 if res.get("ok") else 1
        time.sleep(0.5)

    print("timeout waiting for extension", file=sys.stderr)
    return 5


if __name__ == "__main__":
    sys.exit(main())
