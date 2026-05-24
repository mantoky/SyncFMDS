from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from urllib.request import Request, urlopen
import json
import time

HOST = "127.0.0.1"
PORT = 8090
BASE = "https://apiprevmet3.inmet.gov.br"
CACHE_TTL = 1800
CACHE = {}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, payload: dict):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self._send(200, {"ok": True})

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != "/weather":
            self._send(404, {"ok": False, "error": "not_found"})
            return
        q = parse_qs(parsed.query)
        place = (q.get("place", ["parauapebas"])[0] or "parauapebas").strip().lower()
        key = place
        now = time.time()
        cached = CACHE.get(key)
        if cached and (now - cached["ts"] <= CACHE_TTL):
            self._send(200, {"ok": True, "source": "INMET", "place": place, "stale": False, "data": cached["data"]})
            return
        try:
            # 1) Resolve geocode with official autocomplete endpoint used by previsao.inmet.gov.br
            req_auto = Request(f"{BASE}/autocomplete/{place}", headers={"User-Agent": "FMDS-INMET-Proxy/1.0"})
            with urlopen(req_auto, timeout=12) as resp:
                auto_raw = resp.read().decode("utf-8", "ignore")
            candidates = json.loads(auto_raw) if auto_raw else []
            if not candidates:
                raise RuntimeError("cidade_nao_encontrada")
            chosen = candidates[0]
            geocode = chosen.get("geocode")
            if not geocode:
                raise RuntimeError("geocode_invalido")

            # 2) Fetch forecast by geocode (stable official route)
            req_prev = Request(f"{BASE}/previsao/{geocode}", headers={"User-Agent": "FMDS-INMET-Proxy/1.0"})
            with urlopen(req_prev, timeout=12) as resp:
                prev_raw = resp.read().decode("utf-8", "ignore")
            data = json.loads(prev_raw) if prev_raw else {}
            payload = {"geocode": geocode, "label": chosen.get("label"), "custom": chosen.get("custom"), "forecast": data}
            CACHE[key] = {"ts": now, "data": payload}
            self._send(200, {"ok": True, "source": "INMET", "place": place, "stale": False, "data": payload})
        except Exception as exc:
            if cached:
                self._send(200, {"ok": True, "source": "INMET", "place": place, "stale": True, "data": cached["data"], "warning": str(exc)})
            else:
                self._send(502, {"ok": False, "source": "INMET", "place": place, "error": str(exc)})


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"INMET proxy running at http://{HOST}:{PORT}")
    server.serve_forever()
