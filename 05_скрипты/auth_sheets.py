import json, os, secrets, urllib.parse, urllib.request, webbrowser, socket
from http.server import HTTPServer, BaseHTTPRequestHandler
KEYS=os.path.expanduser("~/Desktop/Реклама/04_ключи")
CLIENT=os.path.join(KEYS,"google_ads_oauth_client.json")
OUT=os.path.join(KEYS,"google_sheets_token.json")
SCOPE="https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/drive.file"
cfg=json.load(open(CLIENT))["installed"]; state=secrets.token_urlsafe(16); holder={}
class H(BaseHTTPRequestHandler):
 def do_GET(self):
  q=urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
  self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.end_headers()
  if q.get("state",[None])[0]!=state:
   self.wfile.write("<h2>Ошибка state</h2>".encode()); return
  if "code" in q:
   holder["code"]=q["code"][0]; self.wfile.write("<h2>Готово. Можно закрыть.</h2>".encode())
  else: self.wfile.write(f"<h2>Отказано: {q.get('error',['?'])[0]}</h2>".encode())
 def log_message(self,*a): pass
s=socket.socket(); s.bind(("127.0.0.1",0)); port=s.getsockname()[1]; s.close()
redirect=f"http://localhost:{port}"
url="https://accounts.google.com/o/oauth2/auth?"+urllib.parse.urlencode({"client_id":cfg["client_id"],"redirect_uri":redirect,"response_type":"code","scope":SCOPE,"access_type":"offline","prompt":"consent","state":state})
print(url,flush=True)
try: webbrowser.open(url)
except Exception: pass
srv=HTTPServer(("127.0.0.1",port),H); srv.timeout=300
while "code" not in holder: srv.handle_request()
data=urllib.parse.urlencode({"code":holder["code"],"client_id":cfg["client_id"],"client_secret":cfg["client_secret"],"redirect_uri":redirect,"grant_type":"authorization_code"}).encode()
tok=json.load(urllib.request.urlopen(urllib.request.Request(cfg["token_uri"],data=data)))
json.dump({"refresh_token":tok["refresh_token"],"client_id":cfg["client_id"],"client_secret":cfg["client_secret"],"token_uri":cfg["token_uri"]},open(OUT,"w"),indent=2)
os.chmod(OUT,0o600); print("saved",OUT,flush=True)
