"""Servidor local do atlas. Execução: python3 apps/collector/server.py."""
import argparse
from collections import defaultdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
from pathlib import Path
import threading
import sqlite3
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from apps.admin.store import Store, Problem, uid
from apps.admin.routing import Router
from apps.admin import http as admin_http
from urllib.parse import parse_qs, urlsplit

from collector import DATA, ROOT, collect, export_csv, export_geojson, load_snapshot
from semob import CODE

STUDY = ROOT / "docs/proposta-brs-bhls/estudos/rede-integrada-2026-11-21"
PROPOSAL = ROOT / "docs/proposta-brs-bhls/revisao-atual"
WEB = ROOT / "apps/web"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def historical_network():
    geometry = read_json(STUDY / "mapa/comparacao-atual/itinerarios-originais.geojson")
    grouped = defaultdict(list)
    for feature in geometry["features"]:
        grouped[feature["properties"]["line_code"]].append(feature)
    lines = []
    for code, features in sorted(grouped.items()):
        props = features[0]["properties"]
        lines.append({"code": code, "name": props["route_name"], "names": sorted({f["properties"]["route_name"] for f in features}), "operator": props.get("operator_name"), "retrieved_at": props.get("retrieved_at"), "source_updated_at": [], "itineraries": [], "schedules": [], "errors": []})
    return {"source": "historical", "label": "Referência histórica · Bus4/EMS", "retrieved_at": lines[0]["retrieved_at"] if lines else None, "lines": lines, "geojson": geometry, "stops": read_json(STUDY / "mapa/comparacao-atual/paradas.geojson"), "catalog_count": len(lines), "warnings": ["Base importada, coletada em 02/11/2026. Operação atual e correspondência viária não validadas.", "Paradas são referências independentes; não há vínculo sequencial linha–parada nesta base."]}


def semob_network(snapshot):
    active = {item["code"] for item in snapshot["catalog"]}
    lines = [{**{k: v for k, v in line.items() if k != "geojson"}, "in_latest_catalog": line["code"] in active} for line in snapshot["lines"]]
    missing = [line["code"] for line in snapshot["lines"] if not line["geojson"]["features"]]
    warnings = ["Cada linha mantém sua data de coleta. A data de atualização declarada pela SEMOB pode ser anterior.", "Campos indisponíveis ficam identificados nos detalhes da linha."]
    if missing:
        warnings.append("Sem geometria disponível na coleta: " + ", ".join(missing) + ".")
    return {"source": "semob", "label": "Coleta local · SEMOB-JP", "retrieved_at": snapshot["retrieved_at"], "lines": lines, "geojson": export_geojson(snapshot), "stops": {"type": "FeatureCollection", "features": []}, "catalog_count": len(snapshot["catalog"]), "last_run": snapshot["last_run"], "warnings": warnings}


class AtlasServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, data_dir=DATA, public_port=None):
        super().__init__(address, Handler)
        self.public_port = public_port if public_port is not None else self.server_port
        self.data_dir = Path(data_dir)
        self.admin = Store(self.data_dir)
        self.router = Router(self.data_dir)
        self.job_lock = threading.Lock()
        self.job = {"running": False, "message": "Nenhuma coleta iniciada nesta sessão", "done": 0, "total": 0, "error": None}
        self.history = historical_network()

    def start_collection(self, codes):
        with self.job_lock:
            if self.job["running"]:
                return False
            job_id = uid()
            self.job = {"running": True, "message": "Iniciando coleta", "done": 0, "total": 0, "error": None}

        self.admin.job(job_id, "running", self.job)

        def update(message, done, total):
            with self.job_lock:
                self.job.update(message=message, done=done, total=total)
                self.admin.job(job_id, "running", self.job)

        def worker():
            try:
                result = collect(codes=codes, data_dir=self.data_dir, progress=update)
                update(f"{len(result['last_run']['updated_codes'])} linhas atualizadas · {len(result['last_run']['errors'])} pendências", self.job["done"], self.job["total"])
            except Exception as exc:
                with self.job_lock:
                    self.job.update(error=str(exc), message="Coleta interrompida; consulte o erro abaixo")
            finally:
                with self.job_lock:
                    self.job["running"] = False
                    self.admin.job(job_id, "failed" if self.job["error"] else "complete", self.job)

        threading.Thread(target=worker, daemon=True).start()
        return True


class Handler(BaseHTTPRequestHandler):
    def send(self, body, content_type="application/json; charset=utf-8", status=200, filename=None):
        if not isinstance(body, bytes):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Frame-Options", "DENY")
        policy = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        if urlsplit(self.path).path == '/proposta-original':
            policy = policy.replace("script-src 'self';", "script-src 'self' 'unsafe-inline';")
        self.send_header('Content-Security-Policy', policy)
        for key,value in getattr(self,"extra_headers",[]): self.send_header(key,value)
        self.extra_headers=[]
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        if filename:
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.end_headers()
        self.wfile.write(body)

    def json(self, data, status=200):
        self.send(json.dumps(data, ensure_ascii=False, allow_nan=False), status=status)

    def do_GET(self):
        try:
            self.get_route()
        except Problem as exc:
            self.json({"error":str(exc),**exc.details},exc.status)
        except (OSError, ValueError, KeyError, sqlite3.Error) as exc:
            self.json({"error": f"Não foi possível ler os dados locais: {exc}"}, 500)

    def get_route(self):
        url = urlsplit(self.path)
        params = parse_qs(url.query)
        if url.path.startswith('/api/admin/'):
            self.check_host()
            if admin_http.get(self,url.path): return
        if url.path == "/api/status":
            snapshot = load_snapshot(self.server.data_dir)
            with self.server.job_lock:
                job = dict(self.server.job)
            self.json({"job": job, "semob_available": bool(snapshot), "semob_lines": len(snapshot["lines"]) if snapshot else 0, "catalog_count": len(snapshot["catalog"]) if snapshot else 0, "geometry_count": sum(len(line["geojson"]["features"]) for line in snapshot["lines"]) if snapshot else 0, "pending_count": sum(len(line["errors"]) for line in snapshot["lines"]) if snapshot else 0, "retrieved_at": snapshot["retrieved_at"] if snapshot else None})
        elif url.path == "/api/base":
            self.json(read_json(STUDY / "dados/base-cartografica.json"))
        elif url.path == "/api/proposal":
            self.json(self.server.admin.public_proposal())
        elif url.path == "/api/map-sources":
            self.json(read_json(WEB / "map-sources.json"))
        elif url.path == "/proposta":
            self.send_response(302)
            self.send_header("Location", "/#proposta")
            self.send_header("Content-Length", "0")
            self.end_headers()
        elif url.path == "/api/network":
            source = params.get("source", ["historical"])[0]
            if source == "historical":
                self.json(self.server.history)
            elif source == "semob":
                snapshot = load_snapshot(self.server.data_dir)
                self.json(semob_network(snapshot) if snapshot else {"error": "Nenhuma coleta SEMOB disponível. Entre no painel administrativo para iniciar uma coleta."}, 200 if snapshot else 404)
            else:
                self.json({"error": "Fonte desconhecida"}, 400)
        elif url.path == "/api/download":
            snapshot = load_snapshot(self.server.data_dir)
            if not snapshot:
                self.json({"error": "Realize uma coleta antes de exportar"}, 404)
                return
            fmt = params.get("format", ["json"])[0]
            if fmt == "csv":
                self.send(export_csv(snapshot), "text/csv; charset=utf-8", filename="semob-linhas.csv")
            elif fmt == "geojson":
                self.send(json.dumps(export_geojson(snapshot), ensure_ascii=False), "application/geo+json; charset=utf-8", filename="semob-itinerarios.geojson")
            elif fmt == "json":
                self.send(json.dumps(snapshot, ensure_ascii=False), filename="semob-coleta.json")
            else:
                self.json({"error": "Formato desconhecido"}, 400)
        else:
            files = {"/": WEB / "index.html", "/app.js": WEB / "app.js", "/maps.js": WEB / "maps.js", "/proposal.js": WEB / "proposal.js", "/styles.css": WEB / "styles.css", "/vendor/d3.js": STUDY / "mapa/d3.js", "/proposta-original": STUDY / "mapa.html"}
            files.update({'/admin':WEB/'admin.html','/admin/':WEB/'admin.html','/admin.js':WEB/'admin.js','/admin.css':WEB/'admin.css','/admin-network.js':WEB/'admin-network.js'})
            for asset in (WEB / "assets").iterdir():
                if asset.is_file():
                    files["/assets/" + asset.name] = asset
            for name in ("leaflet.js", "leaflet.css"):
                files["/vendor/leaflet/" + name] = WEB / "vendor/leaflet" / name
            path = files.get(url.path)
            if path:
                self.send(path.read_bytes(), (mimetypes.guess_type(str(path))[0] or "application/octet-stream") + "; charset=utf-8")
            else:
                self.json({"error": "Página não encontrada"}, 404)

    def check_host(self):
        host=self.headers.get('Host','')
        allowed={f'127.0.0.1:{self.server.public_port}', f'localhost:{self.server.public_port}'}
        if host not in allowed: raise Problem('Acesso permitido somente pelo endereço local publicado.',403)
        return host

    def do_POST(self):
        try:
            host=self.check_host()
            if self.headers.get('Origin')!=f'http://{host}' or self.headers.get_content_type()!='application/json':
                raise Problem('A solicitação deve partir do painel local com conteúdo JSON.',403)
            path=urlsplit(self.path).path
            if not (path.startswith('/api/admin/') or path=='/api/collect'):
                raise Problem('Rota não encontrada.',404)
            # Autenticação antes de ler corpos grandes de rascunhos/rotas.
            if path not in {'/api/admin/setup','/api/admin/login'}: admin_http.require(self,write=True)
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=4_000_000: raise Problem('Corpo da solicitação inválido (máximo 4 MB).',413)
            body=json.loads(self.rfile.read(length))
            if not isinstance(body,dict): raise Problem('Informe um objeto JSON.')
            admin_http.post(self,path,body)
        except Problem as exc:
            self.json({'error':str(exc),**exc.details},exc.status)
        except (ValueError,TypeError,KeyError,AttributeError):
            self.json({'error':'Dados inválidos na solicitação.'},400)
        except (OSError,sqlite3.Error):
            self.json({'error':'Não foi possível persistir a operação local. Confira o serviço e o espaço em disco.'},500)


def main():
    parser = argparse.ArgumentParser(description="Atlas local Paradoxo Mobilidade JP")
    parser.add_argument("--host", choices=("127.0.0.1", "0.0.0.0"), default="127.0.0.1", help="Use 0.0.0.0 dentro do container")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--public-port", type=int, help="Porta publicada no host, quando diferente da porta interna do container")
    parser.add_argument("--data-dir", type=Path, default=DATA)
    args = parser.parse_args()
    try:
        server = AtlasServer((args.host, args.port), args.data_dir, public_port=args.public_port)
    except OSError as exc:
        parser.exit(1, f"Não foi possível abrir a porta {args.port}: {exc}\n")
    print(f"Paradoxo Mobilidade JP: http://127.0.0.1:{server.public_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
