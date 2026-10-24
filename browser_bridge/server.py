"""Локальный сервер моста. Слушает только 127.0.0.1:8765.

Расширение раз в секунду забирает команду через /poll и кладёт результат
в /result. Команды отправляются через ask.py.
"""
import json
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

TOKEN = "0c689ac52222d755d6bde0886f1051c7"
LOCK = threading.Lock()
PENDING = None
RESULTS = {}


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Private-Network", "true")

    def _send(self, code, obj=None):
        if obj is None:
            self.send_response(code)
            self._cors()
            self.end_headers()
            return
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(204)

    def do_GET(self):
        global PENDING
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        if query.get("token", [""])[0] != TOKEN:
            return self._send(403, {"error": "bad token"})

        if parsed.path == "/poll":
            with LOCK:
                cmd, PENDING = PENDING, None
            if cmd is None:
                return self._send(204)
            return self._send(200, cmd)

        if parsed.path.startswith("/result/"):
            rid = parsed.path.rsplit("/", 1)[-1]
            with LOCK:
                res = RESULTS.get(rid)
            if res is None:
                return self._send(204)
            return self._send(200, res)

        if parsed.path == "/health":
            return self._send(200, {"ok": True, "pending": PENDING is not None})

        return self._send(404, {"error": "not found"})

    def do_POST(self):
        global PENDING
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        if query.get("token", [""])[0] != TOKEN:
            return self._send(403, {"error": "bad token"})

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw)
        except Exception:
            return self._send(400, {"error": "bad json"})

        if parsed.path == "/cmd":
            cid = body.get("id") or secrets.token_hex(8)
            body["id"] = cid
            with LOCK:
                if PENDING is not None:
                    return self._send(409, {"error": "busy", "pending": PENDING.get("id")})
                PENDING = body
                RESULTS.pop(cid, None)
            print("cmd:", cid, body.get("op"), flush=True)
            return self._send(200, {"id": cid})

        if parsed.path == "/result":
            cid = body.get("id")
            with LOCK:
                RESULTS[cid] = body
            ok = body.get("ok")
            print("result:", cid, "ok" if ok else "error", flush=True)
            return self._send(200, {"ok": True})

        return self._send(404, {"error": "not found"})

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
    print("bridge listening on http://127.0.0.1:8765", flush=True)
    server.serve_forever()
