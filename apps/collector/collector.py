"""Coletor CLI e serviço de coleta usado pelo painel local."""
import argparse
import csv
import fcntl
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from semob import BASE_URL, CODE, parse_geojson, parse_itineraries, parse_listing, parse_schedules, source_url

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"


def now():
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    os.replace(temp, path)


def load_snapshot(data_dir=DATA):
    path = Path(data_dir) / "processed/semob/latest.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


class Client:
    def __init__(self, raw_dir, delay=0.3, timeout=25, retries=2):
        self.raw_dir = Path(raw_dir)
        self.delay, self.timeout, self.retries = delay, timeout, retries
        self.last_request = 0
        self.manifest = []

    def get(self, url, filename):
        source_url(url)
        for attempt in range(self.retries + 1):
            time.sleep(max(0, self.delay - (time.monotonic() - self.last_request)))
            self.last_request = time.monotonic()
            try:
                req = Request(url, headers={"User-Agent": "ParadoxoMobilidadeJP/0.1 (local public transport research)", "Accept": "text/html,application/json"})
                with urlopen(req, timeout=self.timeout) as response:
                    source_url(response.url)
                    raw = response.read(15_000_001)
                    if len(raw) > 15_000_000:
                        raise ValueError("Resposta excede 15 MB")
                    charset = response.headers.get_content_charset() or "utf-8"
                    record = {"url": url, "final_url": response.url, "retrieved_at": now(), "status": response.status, "content_type": response.headers.get("Content-Type"), "file": filename}
                self.raw_dir.mkdir(parents=True, exist_ok=True)
                (self.raw_dir / filename).write_bytes(raw)
                self.manifest.append(record)
                return raw.decode(charset)
            except HTTPError as exc:
                if exc.code not in {429, 500, 502, 503, 504} or attempt == self.retries:
                    raise
            except (URLError, TimeoutError, OSError):
                if attempt == self.retries:
                    raise
            time.sleep(2 ** attempt)


def canonical_page(url):
    parts = urlsplit(source_url(url))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(sorted((k, v) for k, v in parse_qsl(parts.query) if k == "page")), ""))


def discover(client):
    pending, seen, lines = [BASE_URL], set(), {}
    while pending:
        url = canonical_page(pending.pop(0))
        if url in seen:
            continue
        if len(seen) >= 100:
            raise ValueError("Paginação excede o limite de segurança de 100 páginas")
        seen.add(url)
        page, links = parse_listing(client.get(url, f"listagem-{len(seen):03d}.html"), url)
        lines.update((line["code"], line) for line in page)
        pending.extend(link for link in links if canonical_page(link) not in seen)
    return sorted(lines.values(), key=lambda row: row["code"])


def collect(codes=None, limit=None, data_dir=DATA, progress=None, client_factory=Client):
    lock_path = Path(data_dir) / "processed/semob/collection.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError("Outra coleta já está usando esta pasta de dados") from exc
        return _collect(codes, limit, data_dir, progress, client_factory)


def _collect(codes=None, limit=None, data_dir=DATA, progress=None, client_factory=Client):
    """Atualiza só linhas solicitadas; mantém as demais e os dados de linhas totalmente falhas."""
    data_dir = Path(data_dir)
    requested = list(dict.fromkeys(codes or []))
    if any(not CODE.fullmatch(code) for code in requested):
        raise ValueError("Código de linha inválido")
    if limit is not None and limit < 1:
        raise ValueError("O limite deve ser maior que zero")
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    client = client_factory(data_dir / "raw/semob" / run_id)
    progress = progress or (lambda message, done, total: None)
    report = {"run_id": run_id, "started_at": now(), "errors": [], "updated_codes": []}
    try:
        progress("Consultando o catálogo e sua paginação", 0, 0)
        catalog = discover(client)
        available = {line["code"]: line for line in catalog}
        # Somente códigos numéricos recebem preenchimento; I004 e outros códigos são preservados.
        requested = [code.zfill(4) if code.isdigit() and code.zfill(4) in available else code for code in requested]
        unknown = set(requested) - available.keys()
        if unknown:
            raise ValueError("Linhas não encontradas no catálogo: " + ", ".join(sorted(unknown)))
        selected = [available[code] for code in requested] if requested else catalog
        if limit:
            selected = selected[:limit]
        old = load_snapshot(data_dir)
        existing = {line["code"]: line for line in old["lines"]} if old else {}
        for index, item in enumerate(selected):
            code = item["code"]
            progress(f"Coletando {code} · {item['name']}", index, len(selected))
            line = {**item, "retrieved_at": now(), "itineraries": [], "schedules": [], "geojson": {"type": "FeatureCollection", "features": []}, "errors": [], "source_updated_at": []}
            success = 0
            for field, url_key, parser, suffix in [
                ("itineraries", "itinerary_url", parse_itineraries, "itinerario.html"),
                ("schedules", "schedule_url", parse_schedules, "horario.html"),
                ("geojson", "geojson_url", parse_geojson, "geojson.json"),
            ]:
                try:
                    if not item.get(url_key):
                        raise ValueError("Link não publicado no catálogo")
                    line[field] = parser(client.get(item[url_key], f"{code}-{suffix}"))
                    success += 1
                except (ValueError, URLError, TimeoutError, OSError) as exc:
                    error = {"code": code, "field": field, "message": str(exc)}
                    line["errors"].append(error)
                    report["errors"].append(error)
            if success:
                line["source_updated_at"] = sorted({str(f["properties"]["ATUALIZACA"]) for f in line["geojson"]["features"] if f["properties"].get("ATUALIZACA")})
                existing[code] = line
                report["updated_codes"].append(code)
        report.update({"finished_at": now(), "selected_count": len(selected), "catalog_count": len(catalog)})
        if not report["updated_codes"]:
            raise ValueError("Nenhuma linha foi atualizada. A coleta anterior foi preservada; consulte o relatório bruto.")
        report["status"] = "partial" if report["errors"] else "complete"
        snapshot = {"schema_version": 1, "source": "SEMOB-JP", "source_url": BASE_URL, "catalog": catalog, "retrieved_at": report["finished_at"], "lines": sorted(existing.values(), key=lambda row: row["code"]), "last_run": dict(report)}
        atomic_json(data_dir / "processed/semob/latest.json", snapshot)
        progress("Coleta concluída" if not report["errors"] else "Coleta concluída com pendências", len(selected), len(selected))
        return snapshot
    except Exception as exc:
        report.update(status="failed", fatal_error=str(exc), finished_at=now())
        raise
    finally:
        report["requests"] = client.manifest
        atomic_json(client.raw_dir / "manifest.json", report)


def export_csv(snapshot):
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["codigo", "nome", "coletado_em", "atualizacao_fonte", "tracados", "itinerarios", "quadros_horario", "pendencias"])
    for line in snapshot["lines"]:
        writer.writerow([line["code"], line["name"], line["retrieved_at"], "; ".join(line["source_updated_at"]), len(line["geojson"]["features"]), len(line["itineraries"]), len(line["schedules"]), len(line["errors"])])
    return "\ufeff" + output.getvalue()


def export_geojson(snapshot):
    features = []
    for line in snapshot["lines"]:
        for feature in line["geojson"]["features"]:
            features.append({**feature, "properties": {**feature["properties"], "line_code": line["code"], "retrieved_at": line["retrieved_at"], "source_url": line["geojson_url"]}})
    return {"type": "FeatureCollection", "features": features}


def main():
    parser = argparse.ArgumentParser(description="Coleta local dos dados públicos de ônibus da SEMOB-JP")
    parser.add_argument("--line", action="append", help="Código da linha; pode repetir. Sem esta opção coleta todo o catálogo.")
    parser.add_argument("--limit", type=int, help="Limita o número de linhas nesta execução")
    parser.add_argument("--data-dir", type=Path, default=DATA)
    args = parser.parse_args()
    try:
        snapshot = collect(args.line, args.limit, args.data_dir, lambda msg, done, total: print(f"[{done}/{total}] {msg}", flush=True))
    except (ValueError, URLError, TimeoutError, OSError) as exc:
        parser.exit(1, f"Falha na coleta: {exc}\n")
    print(f"{len(snapshot['last_run']['updated_codes'])} linhas atualizadas; {len(snapshot['last_run']['errors'])} pendências.")
    if snapshot["last_run"]["errors"]:
        parser.exit(2, "Coleta parcial; confira latest.json e o manifesto da execução.\n")


if __name__ == "__main__":
    main()
