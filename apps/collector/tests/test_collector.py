import copy
import fcntl
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from collector import atomic_json, collect, discover, export_csv, export_geojson, load_snapshot
from semob import BASE_URL, parse_geojson, parse_itineraries, parse_listing, parse_schedules
from server import AtlasServer


def listing(code="0002", name="ROGER", links=""):
    return f'<table><tr><td>{code} - {name}</td><td><a href="/linhas-de-onibus/{code}/itinerario/">Ver</a></td><td><a href="/linhas-de-onibus/{code}/horario/">Horário</a></td></tr></table><nav class="paginator">{links}</nav>'


ITINERARY = '<a role="tab" href="#principal">PRINCIPAL</a><div class="tab-pane active" id="principal"><table><tr><th>Ida</th></tr><tr><td>RUA A &amp; B</td></tr><tr><td>TERMINAL</td></tr></table><table><tr><th>Volta</th></tr><tr><td>RUA C</td></tr></table></div>'
SCHEDULE = '<div><div><strong>Dia útil</strong> | 2 viagens<br><span>06:00</span><span>12:30</span></div><div><strong>Sábado</strong> | 0 viagens</div></div>'
GEOJSON = {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {"CODIGO_LIN": "0002", "ITINERARIO": "IDA", "ATUALIZACA": "2024-08-02T00:00:00.000Z"}, "geometry": {"type": "LineString", "coordinates": [[-34.87, -7.1], [-34.88, -7.11]]}}]}


class FakeClient:
    failures = set()

    def __init__(self, raw_dir):
        self.raw_dir, self.manifest, self.calls = Path(raw_dir), [], []

    def get(self, url, filename):
        self.calls.append(url)
        if any(url.endswith(failure) for failure in self.failures):
            raise ValueError("Fonte indisponível no teste")
        if "itinerario/geojson" in url:
            return json.dumps(GEOJSON)
        if "itinerario/" in url:
            return ITINERARY
        if "horario/" in url:
            return SCHEDULE
        if "page=2" in url:
            return listing("I004", "PRAIA DO SOL", '<a href="?page=2&">2</a>')
        return listing(links='<a href="?page=2&">2</a><a href="?page=2">Próxima</a>')


class ParserTests(unittest.TestCase):
    def test_catalog_preserves_codes_and_follows_pagination(self):
        client = FakeClient("/tmp/unused-sem-ob")
        lines = discover(client)
        self.assertEqual([line["code"] for line in lines], ["0002", "I004"])
        self.assertEqual(len(client.calls), 2)
        self.assertEqual(lines[0]["name"], "ROGER")
        self.assertEqual(lines[1]["geojson_url"], BASE_URL + "I004/itinerario/geojson")

    def test_rejects_unexpected_page_and_external_links(self):
        with self.assertRaisesRegex(ValueError, "estrutura"):
            parse_listing("<h1>Serviço temporariamente indisponível</h1>")
        with self.assertRaisesRegex(ValueError, "fora"):
            parse_listing(listing(links='<a href="https://example.com/?page=2">2</a>'))

    def test_itinerary_preserves_variants_and_order(self):
        alternate = '<a role="tab" href="#variante">VIA CENTRO</a><div class="tab-pane" id="variante"><table><th>Ida</th><td>RUA D</td></table></div>'
        rows = parse_itineraries(ITINERARY + alternate)
        self.assertEqual(rows[0]["streets"], ["RUA A & B", "TERMINAL"])
        self.assertEqual(rows[1]["direction"], "Volta")
        self.assertEqual(rows[2]["variant"], "VIA CENTRO")

    def test_schedules_do_not_invent_missing_days(self):
        rows = parse_schedules(SCHEDULE)
        self.assertEqual(rows, [{"day": "Dia útil", "departures": ["06:00", "12:30"], "declared_trips": 2}, {"day": "Sábado", "departures": [], "declared_trips": 0}])
        with self.assertRaises(ValueError):
            parse_schedules("<p>Sem dados</p>")
        self.assertEqual(parse_schedules('<div><strong>Domingo</strong> | 1 viagem<span>08:00</span></div>')[0]["declared_trips"], 1)

    def test_geojson_rejects_bad_coordinates_and_accepts_multiple_paths(self):
        geo = copy.deepcopy(GEOJSON)
        geo["features"][0]["geometry"]["coordinates"][0] = [-200, -7]
        with self.assertRaises(ValueError):
            parse_geojson(json.dumps(geo))
        geo = copy.deepcopy(GEOJSON)
        geometry = geo["features"][0]["geometry"]
        geometry.update(type="MultiLineString", coordinates=[geometry["coordinates"]])
        self.assertEqual(parse_geojson(json.dumps(geo)), geo)


class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.data = Path(self.temp.name)
        FakeClient.failures = set()

    def tearDown(self):
        self.temp.cleanup()

    def collect(self, codes=None, factory=FakeClient):
        return collect(codes=codes, data_dir=self.data, client_factory=factory)

    def test_snapshot_exports_and_per_line_provenance(self):
        first = self.collect(["2"])
        self.assertEqual(first["lines"][0]["code"], "0002")
        self.assertEqual(first["lines"][0]["source_updated_at"], ["2024-08-02T00:00:00.000Z"])
        self.assertNotEqual(first["lines"][0]["retrieved_at"], first["lines"][0]["source_updated_at"][0])
        second = self.collect(["I004"])
        self.assertEqual(len(second["lines"]), 2)
        self.assertEqual(second["lines"][0], first["lines"][0])
        exported = export_geojson(second)
        self.assertEqual(exported["features"][1]["properties"]["line_code"], "I004")
        self.assertIn("0002,ROGER,", export_csv(first))
        self.assertEqual(load_snapshot(self.data), second)

    def test_partial_failure_is_visible_and_total_failure_preserves_snapshot(self):
        self.collect(["0002"])
        FakeClient.failures = {"horario/"}
        partial = self.collect(["0002"])
        self.assertEqual(len(partial["last_run"]["errors"]), 1)
        self.assertEqual(partial["lines"][0]["schedules"], [])
        FakeClient.failures = {"horario/", "itinerario/", "itinerario/geojson"}
        with self.assertRaisesRegex(ValueError, "preservada"):
            self.collect(["0002"])
        self.assertEqual(load_snapshot(self.data), partial)
        manifests = list((self.data / "raw/semob").glob("*/manifest.json"))
        self.assertEqual(len(manifests), 3)

    def test_failed_catalog_and_unknown_code_leave_previous_data_intact(self):
        first = self.collect(["0002"])
        with self.assertRaisesRegex(ValueError, "não encontradas"):
            self.collect(["9999"])
        FakeClient.failures = {"page=2"}
        with self.assertRaises(ValueError):
            self.collect()
        self.assertEqual(load_snapshot(self.data), first)

    def test_concurrent_collection_is_rejected(self):
        path = self.data / "processed/semob/collection.lock"
        path.parent.mkdir(parents=True)
        with path.open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaisesRegex(ValueError, "Outra coleta"):
                self.collect()


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        FakeClient.failures = set()
        cls.temp = tempfile.TemporaryDirectory()
        cls.server = AtlasServer(("127.0.0.1", 0), cls.temp.name)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.temp.cleanup()

    def get(self, path):
        with urlopen(self.url + path, timeout=5) as response:
            return response.read()

    def test_offline_assets_and_historical_network(self):
        self.assertIn(b'lang="pt-BR"', self.get("/"))
        self.assertIn(b'23', self.get("/proposta"))
        self.assertIn(b'd3', self.get("/vendor/d3.js"))
        network = json.loads(self.get("/api/network?source=historical"))
        self.assertEqual(len(network["lines"]), 111)
        self.assertEqual(len(network["geojson"]["features"]), 296)
        self.assertEqual(len(network["stops"]["features"]), 3047)

    def test_missing_official_data_and_path_traversal(self):
        for path in ["/api/network?source=semob", "/api/download", "/../.git/config", "/%2e%2e/.env"]:
            with self.assertRaises(HTTPError) as context:
                self.get(path)
            self.assertEqual(context.exception.code, 404)

    def test_official_data_and_downloads(self):
        data = Path(self.temp.name)
        collect(codes=["0002"], data_dir=data, client_factory=FakeClient)
        network = json.loads(self.get("/api/network?source=semob"))
        self.assertEqual(network["lines"][0]["schedules"][0]["departures"], ["06:00", "12:30"])
        self.assertEqual(network["stops"]["features"], [])
        self.assertIn(b'0002,ROGER,', self.get("/api/download?format=csv"))
        snapshot = json.loads(self.get("/api/download?format=json"))
        self.assertEqual(len(snapshot["lines"]), 1)
        exported = json.loads(self.get("/api/download?format=geojson"))
        self.assertEqual(exported["features"][0]["properties"]["line_code"], "0002")
        (data / "processed/semob/latest.json").unlink()

    def test_cross_origin_and_invalid_input_cannot_start_collection(self):
        for headers, body, status in [
            ({"Content-Type": "application/json", "Origin": "https://example.com"}, b'{"codes":[]}', 403),
            ({"Content-Type": "text/plain"}, b'{"codes":[]}', 403),
            ({"Content-Type": "application/json"}, b'{"codes":["../../etc"]}', 400),
            ({"Content-Type": "application/json"}, b'[]', 400),
        ]:
            with self.assertRaises(HTTPError) as context:
                urlopen(Request(self.url + "/api/collect", data=body, headers=headers), timeout=5)
            self.assertEqual(context.exception.code, status)
        self.assertFalse(self.server.job["running"])

    def test_running_job_rejects_second_collection(self):
        with self.server.job_lock:
            self.server.job["running"] = True
        try:
            self.assertFalse(self.server.start_collection(["0002"]))
            req = Request(self.url + "/api/collect", data=b'{"codes":["0002"]}', headers={"Content-Type": "application/json"})
            with self.assertRaises(HTTPError) as context:
                urlopen(req, timeout=5)
            self.assertEqual(context.exception.code, 409)
        finally:
            with self.server.job_lock:
                self.server.job["running"] = False

    def test_docker_published_port_keeps_same_origin_check(self):
        previous = self.server.public_port
        self.server.public_port = 18080
        with self.server.job_lock:
            self.server.job["running"] = True
        try:
            for host, origin, expected in [
                ("localhost:18080", "http://localhost:18080", 409),
                ("127.0.0.1:18080", "http://127.0.0.1:18080", 409),
                ("localhost:18080", "http://localhost:8000", 403),
                ("example.com:18080", "http://example.com:18080", 403),
            ]:
                request = Request(self.url + "/api/collect", data=b'{"codes":["0002"]}', headers={"Content-Type": "application/json", "Host": host, "Origin": origin})
                with self.assertRaises(HTTPError) as context:
                    urlopen(request, timeout=5)
                self.assertEqual(context.exception.code, expected)
        finally:
            self.server.public_port = previous
            with self.server.job_lock:
                self.server.job["running"] = False


if __name__ == "__main__":
    unittest.main()
