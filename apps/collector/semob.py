"""Leitura das páginas públicas da SEMOB, sem dependências externas."""
from dataclasses import dataclass, field
from html.parser import HTMLParser
import json
import math
import re
from urllib.parse import urljoin, urlsplit

BASE_URL = "https://servicos.semobjp.pb.gov.br/linhas-de-onibus/"
CODE = re.compile(r"^[A-Za-z0-9_-]{1,12}$")


@dataclass
class Element:
    tag: str
    attrs: dict = field(default_factory=dict)
    children: list = field(default_factory=list)

    def find(self, tag=None, **attrs):
        found = []
        for child in self.children:
            if isinstance(child, Element):
                if (tag is None or child.tag == tag) and all(child.attrs.get(k) == v for k, v in attrs.items()):
                    found.append(child)
                found.extend(child.find(tag, **attrs))
        return found

    def text(self):
        if self.tag in {"script", "style"}:
            return ""
        return " ".join(" ".join(c.text() if isinstance(c, Element) else c for c in self.children).split())


class Document(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.root = Element("document")
        self.stack = [self.root]
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        child = Element(tag, dict(attrs))
        self.stack[-1].children.append(child)
        if tag not in self.VOID:
            self.stack.append(child)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def source_url(url):
    """Limita links descobertos ao serviço de ônibus oficial."""
    parts = urlsplit(url)
    if parts.scheme != "https" or parts.netloc != urlsplit(BASE_URL).netloc or not parts.path.startswith("/linhas-de-onibus/"):
        raise ValueError("Link fora do serviço público de linhas da SEMOB")
    return url


def parse_listing(html, url=BASE_URL):
    root = Document(html).root
    lines = {}
    for row in root.find("tr"):
        cells = row.find("td")
        links = row.find("a")
        for link in links:
            match = re.fullmatch(r"/linhas-de-onibus/([A-Za-z0-9_-]+)/itinerario/", urlsplit(urljoin(url, link.attrs.get("href", ""))).path)
            if not match or not cells:
                continue
            code = match[1]
            name = re.sub(r"^" + re.escape(code) + r"\s*[-–]\s*", "", cells[0].text())
            itinerary = source_url(urljoin(url, link.attrs["href"]))
            schedule = next((source_url(urljoin(url, a.attrs["href"])) for a in links if urlsplit(urljoin(url, a.attrs.get("href", ""))).path.endswith("/horario/")), None)
            lines[code] = {"code": code, "name": name, "itinerary_url": itinerary, "schedule_url": schedule, "geojson_url": itinerary + "geojson"}
    pages = set()
    for nav in root.find("nav"):
        if "paginator" in nav.attrs.get("class", "").split():
            for link in nav.find("a"):
                href = link.attrs.get("href", "")
                if href and "page=" in href:
                    pages.add(source_url(urljoin(url, href)))
    if not lines:
        raise ValueError("A página não contém linhas reconhecíveis; a estrutura da SEMOB pode ter mudado")
    return list(lines.values()), sorted(pages)


def parse_itineraries(html):
    root = Document(html).root
    labels = {a.attrs.get("href", "").lstrip("#"): a.text() for a in root.find("a") if a.attrs.get("role") == "tab"}
    panes = [node for node in root.find("div") if "tab-pane" in node.attrs.get("class", "").split()]
    result = []
    for pane in panes or [root]:
        for table in pane.find("table"):
            headings = table.find("th")
            streets = [cell.text() for cell in table.find("td") if cell.text()]
            if headings and streets:
                result.append({"variant": labels.get(pane.attrs.get("id"), "Principal"), "direction": headings[0].text(), "streets": streets})
    if not result:
        raise ValueError("Itinerário textual não encontrado")
    return result


def parse_schedules(html):
    root = Document(html).root
    result = []
    for card in root.find("div"):
        strong = [c for c in card.children if isinstance(c, Element) and c.tag == "strong"]
        if not strong:
            continue
        times = [span.text() for span in card.find("span") if re.fullmatch(r"\d{2}:\d{2}", span.text())]
        declared = re.search(r"\b(\d+)\s+viage(?:m|ns)\b", card.text())
        if times or declared:
            result.append({"day": strong[0].text(), "departures": times, "declared_trips": int(declared[1]) if declared else None})
    if not result:
        raise ValueError("Quadro de horários não encontrado; não presumir ausência de serviço")
    return result


def parse_geojson(raw):
    data = json.loads(raw)
    if not isinstance(data, dict) or data.get("type") != "FeatureCollection" or not isinstance(data.get("features"), list) or not data["features"]:
        raise ValueError("GeoJSON sem coleção de traçados")
    for feature in data["features"]:
        geometry = feature.get("geometry") or {}
        if feature.get("type") != "Feature" or geometry.get("type") not in {"LineString", "MultiLineString"}:
            raise ValueError("Geometria de itinerário inesperada")
        paths = [geometry.get("coordinates")] if geometry["type"] == "LineString" else geometry.get("coordinates")
        if not paths:
            raise ValueError("Traçado vazio")
        for path in paths:
            if not isinstance(path, list) or len(path) < 2:
                raise ValueError("Traçado sem coordenadas suficientes")
            for point in path:
                if not isinstance(point, list) or len(point) < 2 or not all(isinstance(v, (int, float)) and math.isfinite(v) for v in point[:2]) or not (-180 <= point[0] <= 180 and -90 <= point[1] <= 90):
                    raise ValueError("Coordenada geográfica inválida")
        if not isinstance(feature.get("properties"), dict):
            raise ValueError("Atributos do traçado ausentes")
    return data
