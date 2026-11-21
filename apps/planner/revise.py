"""Revisão reproduzível da proposta por ruas públicas e concentração da rede observada.

Entradas brutas locais: coleta SEMOB e consulta OSM descrita no relatório.
Não substitui projeto de circulação, restrições de conversão ou validação de frota.
"""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import heapq
import json
import math
from pathlib import Path
import unicodedata

ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / 'docs/proposta-brs-bhls/estudos/rede-integrada-2026-11-21'
OUTPUT = ROOT / 'docs/proposta-brs-bhls/revisao-atual'
SCALE_X, SCALE_Y = 110440, 110580


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def distance(a, b):
    return math.hypot((a[0] - b[0]) * SCALE_X, (a[1] - b[1]) * SCALE_Y)


def segment_distance(p, a, b):
    dx, dy = (b[0] - a[0]) * SCALE_X, (b[1] - a[1]) * SCALE_Y
    px, py = (p[0] - a[0]) * SCALE_X, (p[1] - a[1]) * SCALE_Y
    t = max(0, min(1, (px * dx + py * dy) / (dx * dx + dy * dy))) if dx or dy else 0
    return math.hypot(px - t * dx, py - t * dy)


def inside(p, ring):
    x, y = p
    result = False
    for a, b in zip(ring, ring[1:]):
        if (a[1] > y) != (b[1] > y) and x < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]:
            result = not result
    return result


def street_key(name):
    text = ''.join(c for c in unicodedata.normalize('NFD', name.upper()) if not unicodedata.combining(c))
    replacements = {'AV': 'AVENIDA', 'R': 'RUA', 'DR': 'DOUTOR', 'PROF': 'PROFESSOR', 'PRES': 'PRESIDENTE', 'GOV': 'GOVERNADOR', 'BANC': 'BANCARIO', 'EMPRE': 'EMPRESARIO', 'DES': 'DESEMBARGADOR', 'SEN': 'SENADOR', 'DEP': 'DEPUTADO', 'TAB': 'TABELIAO', 'GAL': 'GENERAL'}
    words = [replacements.get(w.strip('.,'), w.strip('.,')) for w in text.split()]
    if words and words[0] in {'AVENIDA', 'RUA', 'RODOVIA', 'PRACA'}:
        words.pop(0)
    return ' '.join(words)


class Network:
    def __init__(self, osm, observed):
        elements = osm['elements']
        self.positions = {e['id']: [e['lon'], e['lat']] for e in elements if e['type'] == 'node'}
        self.ways = {e['id']: e for e in elements if e['type'] == 'way'}
        self.campus = [self.positions[n] for n in self.ways[217158058]['nodes']]
        self.public_perimeter = {59821461} | {wid for wid, way in self.ways.items() if street_key(way.get('tags', {}).get('name', '')) in {'VIA EXPRESSA PADRE ZE', 'CONTORNO DA CIDADE UNIVERSITARIA'}}
        self.station_nodes = {node for wid in self.public_perimeter for node in self.ways[wid]['nodes']}
        self.graph, self.edges, self.edge_grid = defaultdict(list), {}, defaultdict(set)
        self.street_lines = defaultdict(set)
        for line in observed['lines']:
            for itinerary in line['itineraries']:
                for street in itinerary['streets']:
                    self.street_lines[street_key(street)].add(line['code'])
        blocked = {node for node, point in self.positions.items() if self.blocked(point) and node not in self.station_nodes}
        for way in self.ways.values():
            tags = way.get('tags', {})
            if tags.get('highway') not in {'motorway', 'motorway_link', 'trunk', 'trunk_link', 'primary', 'primary_link', 'secondary', 'secondary_link', 'tertiary', 'tertiary_link', 'unclassified', 'residential', 'living_street', 'service', 'busway', 'bus_guideway', 'road'}:
                continue
            # Os giradores públicos de CCHLA/CT são vias de contorno, não ruas do campus.
            if street_key(tags.get('name', '')) == 'VIA UFPB':
                continue
            psv = tags.get('bus', tags.get('psv')) in {'yes', 'designated', 'permissive'}
            if not psv and (tags.get('access') in {'no', 'private'} or tags.get('motor_vehicle') in {'no', 'private'} or tags.get('vehicle') == 'no' or tags.get('service') in {'parking_aisle', 'driveway', 'drive-through'}):
                continue
            oneway = tags.get('oneway:bus', tags.get('oneway:psv', tags.get('oneway', 'yes' if tags.get('junction') == 'roundabout' else 'no')))
            for a, b in zip(way['nodes'], way['nodes'][1:]):
                if a in blocked or b in blocked or a not in self.positions or b not in self.positions:
                    continue
                pa, pb = self.positions[a], self.positions[b]
                midpoint = [(pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2]
                if self.blocked(midpoint) and way['id'] not in self.public_perimeter:
                    continue
                if oneway != '-1':
                    self.add_edge(a, b, way)
                if oneway not in {'yes', '1', 'true'}:
                    self.add_edge(b, a, way)
        # Evita encaixar referências em pontas isoladas criadas pelo bloqueio do campus,
        # vias privadas ou recortes da consulta. Toda referência precisa ter ida e saída.
        all_nodes = set(self.graph) | {b for bs in self.graph.values() for b in bs}
        reverse = defaultdict(list)
        for a, bs in self.graph.items():
            for b in bs:
                reverse[b].append(a)
        visited, order = set(), []
        for root in sorted(all_nodes):
            if root in visited:
                continue
            stack = [(root, False)]
            while stack:
                node, done = stack.pop()
                if done:
                    order.append(node)
                elif node not in visited:
                    visited.add(node)
                    stack.append((node, True))
                    stack.extend((b, False) for b in self.graph.get(node, []) if b not in visited)
        visited, components = set(), []
        for root in reversed(order):
            if root in visited:
                continue
            component, stack = set(), [root]
            while stack:
                node = stack.pop()
                if node in visited:
                    continue
                visited.add(node)
                component.add(node)
                stack.extend(reverse[node])
            components.append(component)
        keep = max(components, key=len)
        self.graph = defaultdict(list, {a: [b for b in bs if b in keep] for a, bs in self.graph.items() if a in keep})
        self.edges = {key: edge for key, edge in self.edges.items() if key[0] in keep and key[1] in keep}
        # Uma amostra de cada ~60 m do GeoJSON associa a concentração de linhas à via física.
        for line in observed['lines']:
            for feature in line['geojson']['features']:
                geometry = feature['geometry']
                paths = [geometry['coordinates']] if geometry['type'] == 'LineString' else geometry['coordinates']
                for path in paths:
                    accumulated = 60
                    for a, b in zip(path, path[1:]):
                        length = distance(a, b)
                        accumulated += length
                        if accumulated < 60 or length < .1:
                            continue
                        accumulated = 0
                        point = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]
                        candidates = self.near_edges(point)
                        best = None
                        for key in candidates:
                            u, v = key
                            p, q = self.positions[u], self.positions[v]
                            dx, dy = (q[0] - p[0]) * SCALE_X, (q[1] - p[1]) * SCALE_Y
                            vx, vy = (b[0] - a[0]) * SCALE_X, (b[1] - a[1]) * SCALE_Y
                            if (dx * vx + dy * vy) / max(.01, math.hypot(dx, dy) * math.hypot(vx, vy)) < .5:
                                continue
                            gap = segment_distance(point, p, q)
                            if gap <= 22 and (best is None or gap < best[0]):
                                best = gap, key
                        if best:
                            self.edges[best[1]]['observed'].add(line['code'])
        self.node_grid = defaultdict(list)
        for node in self.graph:
            self.node_grid[self.cell(self.positions[node])].append(node)
        self.snaps = {}

    def blocked(self, point):
        if not (-34.863 < point[0] < -34.832 and -7.149 < point[1] < -7.124):
            return False
        # Margem de 25 m preserva ruas de contorno; a baia de ônibus tem exceção explícita.
        return inside(point, self.campus) and min(segment_distance(point, a, b) for a, b in zip(self.campus, self.campus[1:])) > 25

    @staticmethod
    def cell(point):
        return math.floor(point[0] * SCALE_X / 70), math.floor(point[1] * SCALE_Y / 70)

    def add_edge(self, a, b, way):
        key = a, b
        if key in self.edges:
            return
        length = distance(self.positions[a], self.positions[b])
        tags = way['tags']
        self.edges[key] = {'length': length, 'name': tags.get('name', tags.get('ref', 'Via sem nome cadastrado')), 'way': way['id'], 'observed': set(), 'street_count': len(self.street_lines[street_key(tags.get('name', ''))])}
        self.graph[a].append(b)
        ca, cb = self.cell(self.positions[a]), self.cell(self.positions[b])
        for x in range(min(ca[0], cb[0]), max(ca[0], cb[0]) + 1):
            for y in range(min(ca[1], cb[1]), max(ca[1], cb[1]) + 1):
                self.edge_grid[x, y].add(key)

    def near_edges(self, point):
        x, y = self.cell(point)
        return {key for key in set().union(*(self.edge_grid[x + dx, y + dy] for dx in (-1, 0, 1) for dy in (-1, 0, 1))) if key in self.edges}

    def snap(self, point):
        key = tuple(point)
        if key not in self.snaps:
            x, y = self.cell(point)
            candidates = []
            for radius in range(1, 12):
                candidates = [node for dx in range(-radius, radius + 1) for dy in range(-radius, radius + 1) for node in self.node_grid[x + dx, y + dy]]
                if candidates:
                    best = min(candidates, key=lambda n: distance(point, self.positions[n]))
                    if distance(point, self.positions[best]) < radius * 70 - 30:
                        break
            if not candidates:
                raise ValueError(f'Sem via pública próxima de {point}')
            self.snaps[key] = best
        return self.snaps[key]

    def support_metric(self, coords):
        total, supported = 0, 0
        for a, b in zip(coords, coords[1:]):
            length = distance(a, b)
            if length < .1:
                continue
            total += length
            point = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]
            best = None
            for u, v in self.near_edges(point):
                p, q = self.positions[u], self.positions[v]
                dx, dy = (q[0] - p[0]) * SCALE_X, (q[1] - p[1]) * SCALE_Y
                vx, vy = (b[0] - a[0]) * SCALE_X, (b[1] - a[1]) * SCALE_Y
                if (dx * vx + dy * vy) / max(.01, math.hypot(dx, dy) * math.hypot(vx, vy)) < .5:
                    continue
                gap = segment_distance(point, p, q)
                if gap <= 22 and (best is None or gap < best[0]):
                    best = gap, self.edges[u, v]
            if best and (best[1]['observed'] or best[1]['street_count']):
                supported += length
        return round(100 * supported / total, 1) if total else 0

    def route(self, start, end):
        if start == end:
            return [start]
        costs, previous, queue = {start: 0}, {}, [(0, start)]
        while queue:
            cost, a = heapq.heappop(queue)
            if cost > costs[a]:
                continue
            if a == end:
                result = [end]
                while result[-1] != start:
                    result.append(previous[result[-1]])
                return result[::-1]
            for b in self.graph[a]:
                edge = self.edges[a, b]
                support = max(len(edge['observed']), min(edge['street_count'], 12))
                candidate = cost + edge['length'] * (.8 + 2.4 / (1 + support))
                if candidate < costs.get(b, math.inf):
                    costs[b], previous[b] = candidate, a
                    heapq.heappush(queue, (candidate, b))
        raise ValueError(f'Sem caminho dirigido entre {self.positions[start]} e {self.positions[end]}')


def main():
    osm_path, semob_path = ROOT / 'data/raw/cartografia/osm-revisao-rotas.json', ROOT / 'data/processed/semob/latest.json'
    osm, observed = read(osm_path), read(semob_path)
    network = Network(osm, observed)
    print(f'Grafo público: {len(network.graph)} nós, {len(network.edges)} segmentos dirigidos', flush=True)
    catalog, waypoints, old_geo = read(STUDY / 'dados/catalogo.json'), read(STUDY / 'dados/waypoints-roteamento.json'), read(STUDY / 'dados/linhas-por-sentido.geojson')
    station = network.positions[2533629066]
    central_line = next(line for line in observed['lines'] if line['code'] == '0301')
    donor = {f['properties']['ITINERARIO'].lower(): f['geometry']['coordinates'] for f in central_line['geojson']['features']}
    lake = [-34.87915, -7.1217]
    cuts = {direction: min(range(len(path)), key=lambda i: distance(path[i], lake)) for direction, path in donor.items()}
    central = {'ida': donor['ida'][cuts['ida']:], 'volta': donor['volta'][:cuts['volta'] + 1]}
    central_streets = {}
    for itinerary in central_line['itineraries']:
        streets = itinerary['streets']
        i = streets.index('PARQUE SOLON DE LUCENA')
        central_streets[itinerary['direction'].lower()] = streets[i:] if itinerary['direction'].lower() == 'ida' else streets[:i + 1]
    station_refs = {direction: network.positions[network.snap(min(path, key=lambda p: distance(p, station)))] for direction, path in donor.items()}
    station_refs['volta'] = station
    overrides = {
        'metro': central['ida'][-1], 'oitizeiro': [-34.89655, -7.16518], 'oitizeiro_back': [-34.89658, -7.16518],
        'universidade_public': station, 'universidade': station, 'estacao_ida': station_refs['ida'], 'estacao_volta': station_refs['volta'],
        'lagoa_ida': central['ida'][0], 'lagoa_volta': central['volta'][-1],
    }
    waypoints.update(overrides)
    catalog['lugares']['universidade'].update(label='Estação Cidade Universitária · Via Expressa Padre Zé', short='Cidade Universitária', position=station, terminal=True)
    catalog['lugares']['metro'].update(label='Terminal Metropolitano · mesmo espaço do TIV Varadouro', position=overrides['metro'])
    catalog['lugares']['oitizeiro'].update(label='Terminal Oitizeiro · área junto ao viaduto/BR-230', position=overrides['oitizeiro'], note='Área indicada pelo usuário e referência do plano municipal; acesso e plataformas ainda não definidos.')
    catalog['lugares']['lagoa'] = {'label': 'Lagoa · Parque Solon de Lucena', 'position': central['ida'][0], 'terminal': True}
    catalog['lugares']['lagoa_ida'] = {'label': 'Lagoa · sentido Varadouro', 'position': central['ida'][0]}
    catalog['lugares']['lagoa_volta'] = {'label': 'Lagoa · saída do Varadouro', 'position': central['volta'][-1]}
    for direction in ['ida', 'volta']:
        catalog['lugares']['estacao_' + direction] = {'label': 'Estação Cidade Universitária · ' + ('referência Centro/Norte' if direction == 'ida' else 'referência Bancários/Sul'), 'position': station_refs[direction]}
    features, audit, snap_audit = [], [], []
    radial_codes = {'BRS-100', 'BRS-200', 'BRS-300', 'BRS-500', 'BRS-501', 'T-410', 'T-610'}
    for line in catalog['linhas']:
        code = line['code']
        line['points'] = list(dict.fromkeys('universidade' if key == 'campus' else key for key in line['points'] if key not in {'ct', 'ponte'}))
        if code == 'I-334':
            line['name'] = 'Circular Cidade Universitária via Três Ruas e Bancários'
        for entry in line['sentidos']:
            direction, key = entry['sentido'], entry['chave']
            keys = entry['waypoints'][:]
            if code == 'BRS-300':
                keys = (['hub', 'hilton_leste', 'jcu_main', 'bancarios_main', 'estacao_ida', 'ufpb_dp2', 'metro'] if direction == 'ida' else ['metro', 'ufpb_dp2_back', 'estacao_volta', 'bancarios_main', 'jcu_main_back', 'hilton_leste_back', 'hub'])
            if code == 'BRS-800':
                keys = [({'ida': 'estacao_ida', 'volta': 'estacao_volta'}[direction] if k == 'universidade_public' else k) for k in keys]
            if code == 'I-334':
                keys = ['estacao_volta' if k == 'universidade_public' else k for k in keys if k != 'ct_public']
            if code == 'R-343':
                keys = ['estacao_volta' if k == 'padre' else k for k in keys if k != 'ponte']
            if code in radial_codes:
                # As plataformas e os acessos centrais são cópia do traçado SEMOB da 0301.
                keys = [k for k in keys if k not in {'metro', 'pedro', 'pedro_back', 'centro_lagoa'}]
                keys = keys + ['lagoa_ida'] if direction == 'ida' else ['lagoa_volta'] + keys
            nodes = [network.snap(waypoints[k]) for k in keys]
            for name, node in zip(keys, nodes):
                gap = distance(waypoints[name], network.positions[node])
                if gap > 35:
                    snap_audit.append({'route': key, 'waypoint': name, 'distance_m': round(gap, 1), 'reference': waypoints[name], 'road_point': network.positions[node]})
            joined = []
            for a, b in zip(nodes, nodes[1:]):
                path = network.route(a, b)
                joined.extend(path if not joined else path[1:])
            coords = [network.positions[node] for node in joined]
            gaps = []
            if code in radial_codes:
                locked = central[direction]
                gaps = [distance(coords[-1], locked[0])] if direction == 'ida' else [distance(locked[-1], coords[0])]
                coords = coords + locked if direction == 'ida' else locked + coords
            dedup = [coords[0]]
            for point in coords[1:]:
                if distance(point, dedup[-1]) > .05:
                    dedup.append(point)
            length = sum(distance(a, b) for a, b in zip(dedup, dedup[1:]))
            old = next(f for f in old_geo['features'] if f['properties']['chave'] == key)
            edge_list = [network.edges[a, b] for a, b in zip(joined, joined[1:]) if a != b]
            street_order = []
            for edge in edge_list:
                if not street_order or street_order[-1] != edge['name']:
                    street_order.append(edge['name'])
            if code in radial_codes:
                street_order = street_order + central_streets[direction] if direction == 'ida' else central_streets[direction] + street_order
            report = {'code': code, 'key': key, 'direction': direction, 'old_distance_km': old['properties']['distancia_km'], 'distance_km': round(length / 1000, 2), 'baseline_observed_streets_percent': network.support_metric(old['geometry']['coordinates']), 'observed_streets_percent': network.support_metric(dedup), 'reference_lines': sorted(set().union(*(e['observed'] for e in edge_list))), 'street_sequence': street_order, 'way_sequence': list(dict.fromkeys(e['way'] for e in edge_list)), 'central_pattern': '0301/' + direction if code in radial_codes else None, 'central_join_m': [round(gap, 1) for gap in gaps]}
            audit.append(report)
            entry.update(waypoints=keys, distancia_km=report['distance_km'], source='revisao-rede-observada', street_sequence=street_order, central_pattern=report['central_pattern'], reference_lines=report['reference_lines'], observed_streets_percent=report['observed_streets_percent'])
            properties = {**old['properties'], 'nome': line['name'], 'distancia_km': report['distance_km'], 'waypoints': keys, 'revision': 'rede-observada-2026-11-21', 'observed_streets_percent': report['observed_streets_percent']}
            features.append({'type': 'Feature', 'id': key, 'properties': properties, 'geometry': {'type': 'LineString', 'coordinates': dedup}})
            print(key, report['distance_km'], f"{report['observed_streets_percent']}% em ruas observadas", flush=True)
        line['itinerary'] = line['itinerary'].replace('T. UFPB', 'Estação Cidade Universitária').replace('CT/UFPB', 'Via Expressa Padre Zé').replace('Ponte Altiplano–UFPB', 'vias públicas Altiplano–Castelo Branco').replace('HU → UFPB', 'entorno do HU → Estação Cidade Universitária')
        line['itinerary'] = line['itinerary'].replace('→ HU →', '→ entorno do HU →')
        if code == 'BRS-300':
            line['itinerary'] = 'T. Mangabeira → Jardim Cidade Universitária / Bancários → Estação Cidade Universitária → Dom Pedro II → Lagoa → TIV Varadouro'
        if code in radial_codes and 'Lagoa' not in line['itinerary']:
            line['itinerary'] = line['itinerary'].replace('Centro', 'Lagoa / Centro')
        line['note'] = 'Revisão por ruas públicas, priorizando concentração da rede SEMOB. ' + ('Acesso ao Varadouro e passagem pela Lagoa preservados por sentido.' if code in radial_codes else 'Percursos sem uso de ruas internas do campus UFPB.')
        if code in {'BRS-300', 'BRS-800', 'I-334', 'R-343'}:
            line['note'] += ' Integração na Estação Cidade Universitária, com referências por sentido e circulação pública de contorno.'
        if code in {'BRS-100', 'BRS-800', 'TRV-721'}:
            line['note'] += ' Oitizeiro deslocado para a área junto ao viaduto/BR-230; acessos internos do terminal pendentes.'
    report = {'revision': 'rede-observada-2026-11-21', 'generated_at': datetime.now(timezone.utc).isoformat(), 'method': 'Grafo dirigido OSM; custo por distância com preferência por concentração SEMOB; bloqueio do interior do campus e da Via UFPB; trechos centrais copiados da linha 0301. Percentuais por correspondência de segmentos a até 22 m e mesma direção em ruas com linhas observadas; comparação antes/depois pelo mesmo método.', 'inputs': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [osm_path, semob_path]}, 'osm_source': osm.get('paradoxo_source'), 'central_reference': {'line': '0301', 'lake': lake, 'entry': central['ida'], 'exit': central['volta'], 'streets': central_streets}, 'station_reference': {'osm_way': 59821461, 'osm_stop': 2533629066, 'position': station, 'direction_references': station_refs}, 'oitizeiro_reference': {'position': overrides['oitizeiro'], 'status': 'Área aproximada indicada pelo usuário junto ao viaduto/BR-230; entrada operacional pendente.'}, 'campus_polygon': network.campus, 'public_perimeter': [[network.positions[n] for n in network.ways[wid]['nodes']] for wid in sorted(network.public_perimeter)], 'street_concentration': [{'street': name, 'line_count': len(codes), 'lines': sorted(codes)} for name, codes in sorted(network.street_lines.items(), key=lambda item: (-len(item[1]), item[0])) if not name.startswith(('TERMINAL', 'RETORNO'))][:40], 'snap_adjustments': snap_audit, 'routes': audit, 'limits': ['Restrições de conversão por relação OSM e gabarito de ônibus ainda exigem validação.', 'Concentração de linhas não representa demanda ou frequência.', 'Oitizeiro e demais novos terminais não têm circulação interna aprovada.']}
    comparisons = read(STUDY / 'dados/comparativos-i332.json')
    revised = next(f['geometry']['coordinates'] for f in features if f['id'] == 'I-332')
    for name, start, end in [('paratibe', 'porfirio', 'mucu'), ('parque-do-sol', 'mucu', 'val')]:
        a = min(range(len(revised)), key=lambda i: distance(revised[i], waypoints[start]))
        b = min(range(a + 1, len(revised)), key=lambda i: distance(revised[i], waypoints[end]))
        comparisons[name]['after'] = revised[a:b + 1]
        comparisons[name]['revision'] = report['revision']
    catalog.update(revision=report['revision'], generated_at=report['generated_at'])
    OUTPUT.mkdir(parents=True, exist_ok=True)
    geometry = {'type': 'FeatureCollection', 'name': 'proposta_revisada_rede_observada', 'attribution': 'Malha viária © OpenStreetMap contributors (ODbL); referência operacional SEMOB-JP; estudo independente Paradoxo Labs.', 'license': 'https://www.openstreetmap.org/copyright', 'features': features}
    for name, data in [('catalogo.json', catalog), ('linhas-por-sentido.geojson', geometry), ('waypoints-roteamento.json', waypoints), ('comparativos-i332.json', comparisons), ('auditoria.json', report)]:
        (OUTPUT / name).write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')


if __name__ == '__main__':
    main()
