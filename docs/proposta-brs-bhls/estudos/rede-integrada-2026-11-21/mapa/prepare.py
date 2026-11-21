from pathlib import Path
import json
import math
from ampliacao import EXTRA_POINTS, EXTRA_LINES, ROUTING_POINTS

directory = Path(__file__).parent


def read(name):
    return json.loads((directory / (name + '.json')).read_text())


def feature(geometry_type, coordinates, **properties):
    return {'type': 'Feature', 'properties': properties, 'geometry': {'type': geometry_type, 'coordinates': coordinates}}


def ring_area(points):
    lon, lat = points[0]
    shifted = [(x - lon, y - lat) for x, y in points]
    return sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(shifted, shifted[1:]))


def centroid(best_ring):
    lon, lat = best_ring[0]
    points = [(x - lon, y - lat) for x, y in best_ring]
    cross = [p[0] * q[1] - q[0] * p[1] for p, q in zip(points, points[1:])]
    tuples = list(zip(points, points[1:], cross))
    return tuple(offset + sum((p[i] + q[i]) * factor for p, q, factor in tuples) / (3 * sum(cross)) for i, offset in enumerate([lon, lat]))


def round_line(line):
    result = []
    for position in line:
        point = [round(x, 5) for x in position[:2]]
        if not result or result[-1] != point:
            result.append(point)
    return result


def polygon(parts):
    result = []
    for index, raw_ring in enumerate(parts):
        ring = round_line(raw_ring)
        if len(ring) >= 4:
            if (ring_area(ring) > 0) == (index == 0):
                ring.reverse()
            result.append(ring)
    return result


def clean(raw, **properties):
    geometry_type = raw['geometry']['type']
    coords = raw['geometry']['coordinates']
    if geometry_type == 'Polygon':
        coords = polygon(coords)
    elif geometry_type == 'MultiPolygon':
        coords = [x for part in coords if (x := polygon(part))]
    elif geometry_type == 'LineString':
        coords = round_line(coords)
    elif geometry_type == 'MultiLineString':
        coords = [x for line in coords if len(x := round_line(line)) >= 2]
    else:
        raise ValueError(geometry_type)
    if len(coords) < (2 if geometry_type == 'LineString' else 1):
        return None
    return feature(geometry_type, coords, **properties)


neighborhoods = {row['properties']['nome']: row for row in read('bairros')['features']}
corridors = read('corredores')['features']
references = read('geocoded')
additional_references = read('geocoded-more')
places = {}


def position(key, label, coordinate, short=None, terminal=False):
    places[key] = {'label': label, 'position': [round(x, 6) for x in coordinate]}
    if short:
        places[key]['short'] = short
    if terminal:
        places[key]['terminal'] = True


def area(key, label, official_name, short=None, terminal=False):
    geometry = neighborhoods[official_name]['geometry']
    polygons = [geometry['coordinates']] if geometry['type'] == 'Polygon' else geometry['coordinates']
    largest = max((part[0] for part in polygons), key=lambda ring: abs(ring_area(ring)))
    position(key, label, centroid(largest), short, terminal)


def geocoded(key, label, ref, index=0, **options):
    place = references[ref][index]
    position(key, label, [place['lon'], place['lat']], **options)


def from_osm(key, label, name, osm_id, **options):
    osm = json.loads((directory / name).read_text())['elements']
    nodes = {e['id']: (e['lon'], e['lat']) for e in osm if e['type'] == 'node'}
    item = next(e for e in osm if e['id'] == osm_id)
    points = [nodes[n] for n in item['nodes'] if n in nodes] if item['type'] == 'way' else [nodes[osm_id]]
    position(key, label, [sum(a) / len(a) for a in zip(*points)], **options)


def on_corridor(key, label, index, nearby):
    corridor = corridors[index]['geometry']
    points = corridor['coordinates'] if corridor['type'] == 'LineString' else sum(corridor['coordinates'], [])
    position(key, label, min(points, key=lambda p: math.dist(p, nearby)))


from_osm('hub', 'T. Mangabeira', 'osmbox.txt', 379220878, terminal=True)
geocoded('metro', 'T. Metropolitano · Varadouro', 'met', short='Varadouro', terminal=True)
position('bessa', 'T. Bessa · referência na integração existente', ROUTING_POINTS['bessa'], 'Bessa', terminal=True)
for key, (label, coordinate, terminal) in EXTRA_POINTS.items():
    position(key, label, coordinate, terminal=terminal)
position('cristo', 'T. Cristo · Estádio Almeidão', [-34.874973, -7.166678], 'Cristo · Almeidão', terminal=True)
from_osm('val', 'NTI Valentina · referência', 'osm-sul.json', 1204790151, short='Valentina', terminal=True)
from_osm('campus', 'UFPB', 'osm-univ.json', 217158058)
from_osm('universidade', 'T. UFPB · referência no campus', 'osm-univ.json', 9754851919, short='UFPB', terminal=True)
from_osm('hu', 'HU Lauro Wanderley', 'osm-univ.json', 538755591)
from_osm('tres', 'Três Ruas', 'osm-univ.json', 12303134509)
from_osm('coqueiral', 'Coqueiral', 'osm-leste.json', 731222869)
from_osm('josefa', 'Av. Josefa Taveira', 'osm-leste.json', 47430562)
from_osm('hilton', 'Av. Hilton Souto Maior', 'osm-leste.json', 47430991)
from_osm('hilton_leste', 'Av. Hilton Souto Maior', 'osmbox.txt', 224248845)
from_osm('hilton_penha', 'Hilton Souto Maior · sentido Penha', 'osmbox.txt', 248547175)
from_osm('seixas', 'Seixas', 'osm-mar.json', 3004602799)
from_osm('estacao', 'Estação Cabo Branco', 'osm-mar.json', 191634951)
from_osm('estacao_farol', 'Estação Cabo Branco / Farol', 'osm-mar.json', 191653569)
from_osm('convencoes', 'Centro de Convenções', 'osm-mar.json', 360441579)
from_osm('retorno_convencoes', 'Retorno na PB-008 · referência', 'osm-mar.json', 47402015)
# Centro do Plus Code 6947R56X+QR, usado como referência do Boulevard dos Ipês.
position('boulevard', 'Boulevard dos Ipês', [-34.8004375, -7.1880625])
from_osm('mangabeira_67', 'Mangabeira VI / VII', 'osm-leste.json', 47435175)
from_osm('amaral', 'R. Antônio Franciscano do Amaral', 'osm-univ.json', 217168016)
from_osm('ponte', 'Ponte Altiplano–UFPB', 'osm-univ.json', 1270370061)
from_osm('padre', 'Via Expressa Padre Zé', 'osm-univ.json', 46570005)
from_osm('borba', 'R. Joaquim Borba Filho · Jardim São Paulo', 'osm-univ.json', 191656875)
from_osm('aurelio', 'R. Aurélio Menezes de Albuquerque', 'osm-univ.json', 355781761)
from_osm('benvenuto', 'R. Benvenuto Gonçalves da Costa', 'osm-leste.json', 247032817)
from_osm('mariz', 'Av. Gov. Antônio da Silva Mariz', 'osmbox.txt', 118229960)
from_osm('medico', 'Av. Médico Industrial', 'osm-univ.json', 48244362)
from_osm('ct', 'Centro de Tecnologia · UFPB', 'osm-univ.json', 494426487)
from_osm('principal', 'Principal dos Bancários', 'osm-univ.json', 246912903)
from_osm('principal_jcu', 'Principal no Jd. Cidade Universitária', 'osm-univ.json', 260390539)
from_osm('alfredo', 'Alfredo F. da Rocha', 'osm-leste.json', 47430567)
position('alfredo_inicio', 'Alfredo F. da Rocha · acesso pela Hilton', [-34.842086, -7.162515])
position('alfredo_meio', 'Coqueiral · Alfredo F. da Rocha', [-34.844353, -7.176522])
position('alfredo_fim', 'Final da Alfredo F. da Rocha', [-34.847319, -7.187829])
position('garrafao', 'Garrafão', [-34.83426, -7.16739])
position('trauminha', 'Trauminha', [-34.836865, -7.175782])
position('porfirio', 'R. Francisco Porfírio Ribeiro', [-34.83914, -7.18660])
position('diogenes', 'R. Diógenes Gomes da Silva', [-34.836105, -7.176872])
position('corujinha', 'Corujinha · Rodopiano Ferreira Nóbrega', [-34.839205, -7.179098], short='Corujinha')
position('josefa_sul', 'Josefa Taveira · trecho sul', [-34.842627, -7.180935])
position('euclides', 'R. Dr. Euclides Neiva de Oliveira', [-34.843189, -7.183082])
position('detran', 'Detran Mangabeira', [-34.826784, -7.165508])
position('anizio', 'R. Anízio de Azevedo Lima', [-34.845559, -7.181781])
position('castelo_via', 'Castelo Branco', [-34.841009, -7.129246])
position('humberto', 'Humberto Maul', [-34.84138, -7.20589])
position('felix_cahino', 'Comerciante Félix Cahino', [-34.83919, -7.20608])
position('severino_dias', 'Av. Severino Dias de Oliveira', [-34.835396, -7.195769], short='Severino Dias')
position('maria_ines', 'Av. Maria Inês Caetano de Oliveira', [-34.834758, -7.196606], short='Maria Inês Caetano')
position('jacaranda', 'Av. Jacarandá', [-34.827845, -7.208137])
position('clodoaldo', 'Economista Clodoaldo P. de Araújo', [-34.844781, -7.220145], short='Clodoaldo P. de Araújo')
position('severina', 'Severina Ramos de Azevedo', [-34.84604, -7.22210])
position('balbina', 'Balbina Ferreira', [-34.84797, -7.22128])
position('joao_maria', 'Av. João Maria de Araújo', [-34.846198, -7.218445])
position('maria_regina', 'R. Maria Regina Martins', [-34.816036, -7.177958])
position('jatoba', 'Av. Jatobá', [-34.815133, -7.17978])
position('patricia', 'Patrícia Tomaz · Três Marias', [-34.815163, -7.184128], terminal=True)
from_osm('verde', 'Cidade Verde', 'osm-leste.json', 2268756772)
from_osm('sete', 'Mangabeira VII · ref. Três Marias', 'osm-sul.json', 274445984, short='Mangabeira VII')
from_osm('jacarape', 'Comunidade Jacarapé', 'osm-sul.json', 2791614741)
from_osm('polo', 'Polo Turístico', 'osm-mar.json', 12477042490)
from_osm('jacuma', 'Jacumã', 'osm-jac.json', 4926886240, terminal=True)
from_osm('pb008', 'PB-008', 'osm-jac.json', 252296797)
geocoded('parque', 'Parque do Sol', 'parque', 1)
from_osm('val1', 'Valentina I · ref. no bairro', 'osm-sul.json', 251401728, short='Valentina I')
valentina_ii = additional_references['val2'][0][1]
position('val2', 'Valentina II · ref. no bairro', [valentina_ii['x'], valentina_ii['y']], short='Valentina II')
on_corridor('beira', 'Av. Beira-Rio', 0, [-34.850, -7.129])
on_corridor('pedro', 'Av. Dom Pedro II', 7, [-34.871, -7.135])

for key, label, name in [
    ('centro', 'Centro', 'CENTRO'), ('bancarios', 'Bancários', 'BANCÁRIOS'),
    ('jcu', 'Jardim Cidade Universitária', 'JARDIM CIDADE UNIVERSITÁRIA'),
    ('portal', 'Portal do Sol', 'PORTAL DO SOL'), ('altiplano', 'Altiplano', 'ALTIPLANO CABO BRANCO'),
    ('cabo', 'Cabo Branco', 'CABO BRANCO'), ('tambau', 'Tambaú', 'TAMBAÚ'), ('manaira', 'Manaíra', 'MANAÍRA'),
    ('castelo', 'Castelo Branco', 'CASTELO BRANCO'), ('paratibe', 'Paratibe', 'PARATIBE'),
    ('mucu', 'Muçumagro', 'MUÇUMAGRO'), ('planalto', 'Planalto da Boa Esperança', 'PLANALTO DA BOA ESPERANÇA'),
    ('penha', 'Penha', 'PENHA'), ('anatolia', 'Anatólia', 'ANATÓLIA')
]:
    area(key, label, name)
places['jcu']['short'] = 'Jd. Cidade Universitária'


def route(code, type_, name, itinerary, points, note=''):
    split_points = points.split()
    for point in split_points:
        assert point in places, point
    return {'code': code, 'type': type_, 'name': name, 'itinerary': itinerary, 'points': split_points, 'note': note}


routes = [
    route('BRS-300', 'brs', 'Mangabeira–Varadouro', 'T. Mangabeira → Jardim Cidade Universitária / Bancários → UFPB → Dom Pedro II → Centro → T. Metropolitano', 'hub jcu bancarios campus pedro centro metro'),
    route('T-410', 'troncal', 'Beira-Rio–Mangabeira', 'T. Mangabeira → Portal do Sol → Altiplano → Beira-Rio → Centro → T. Metropolitano', 'hub portal altiplano beira centro metro'),
    route('TRV-321', 'transversal', 'Mangabeira–Orla', 'T. Mangabeira → Portal do Sol → Altiplano → Cabo Branco → Tambaú → Manaíra → Retão → Manaíra Shopping → T. Bessa', 'hub portal altiplano cabo tambau manaira shopping bessa', 'O acesso ao Manaíra Shopping usa o Retão e a Av. Vereador Gumercindo Barbosa Dunda.'),
    route('TRV-322', 'transversal', 'Mangabeira–Cristo via Convenções e Estação Ciência', 'T. Mangabeira → Hilton Souto Maior, sentido praia → Centro de Convenções → retorno → Boulevard dos Ipês → Penha → Estação Ciência / Farol → Hilton Souto Maior → T. Cristo (Estádio Almeidão) → Hilton Souto Maior → T. Mangabeira', 'hub hilton_penha convencoes retorno_convencoes boulevard penha estacao hilton_leste hilton cristo hilton hub', 'A volta do Almeidão ao Terminal Mangabeira segue pela Hilton Souto Maior. O acesso ao estádio e o retorno na PB-008 são referências de traçado.'),
    route('I-331', 'integracional', 'Valentina I via Josefa Taveira', 'T. Mangabeira → Josefa Taveira → Valentina I → NTI Valentina', 'hub josefa val1 val'),
    route('I-332', 'integracional', 'Valentina via Paratibe e Parque do Sol', 'T. Mangabeira → Garrafão → Trauminha → Francisco Porfírio Ribeiro → Severino Dias de Oliveira → Maria Inês Caetano de Oliveira → Sibipiruna → Félix Cahino → Humberto Maul → Av. Jacarandá → Muçumagro → Clodoaldo Pinheiro → Severina Ramos → Balbina Ferreira → João Maria de Araújo → Parque do Sol → NTI Valentina', 'hub garrafao trauminha porfirio severino_dias maria_ines sibipiruna paratibe felix_cahino humberto jacaranda mucu clodoaldo severina balbina joao_maria parque val', 'Itinerário consolidado com atendimento à Sibipiruna, no eixo principal de Paratibe, e às ruas internas do Parque do Sol.'),
    route('I-333', 'integracional', 'Valentina II / Planalto', 'T. Mangabeira → Coqueiral → Valentina II → Planalto da Boa Esperança → NTI Valentina', 'hub coqueiral val2 planalto val'),
    route('I-334', 'integracional', 'Circular UFPB via Três Ruas e Bancários', 'T. Mangabeira → Av. Gov. Antônio da Silva Mariz → Av. Médico Industrial → Três Ruas → HU → Castelo Branco → T. UFPB → CT/UFPB → Principal dos Bancários / Jd. Cidade Universitária → Josefa Taveira → R. Anízio de Azevedo Lima → Alfredo F. da Rocha (Coqueiral) → Hilton Souto Maior → T. Mangabeira', 'hub mariz medico tres hu castelo_via universidade ct principal principal_jcu josefa anizio alfredo_meio alfredo_inicio hilton_leste hub', 'Castelo Branco foi inserido entre o HU e o Terminal UFPB. O terminal usa uma referência no campus.'),
    route('R-343', 'regional', 'Circular Seixas–UFPB–Anatólia', 'T. Mangabeira → Hilton Souto Maior, sentido Penha → Seixas → Estação Cabo Branco → Portal do Sol → R. Antônio Franciscano do Amaral → Ponte Altiplano–UFPB → HU → UFPB → Via Expressa Padre Zé → R. Joaquim Borba Filho (Jardim São Paulo) → Anatólia → Aurélio Menezes de Albuquerque → Alfredo F. da Rocha → R. Anízio de Azevedo Lima → Josefa Taveira → R. do Corujinha → Trauminha → Detran → T. Mangabeira', 'hub hilton_penha seixas estacao portal amaral ponte hu campus padre borba anatolia aurelio alfredo_inicio alfredo_meio anizio josefa_sul corujinha trauminha detran hub'),
    route('L-351', 'local', 'Cidade Verde II / Patrícia Tomaz', 'T. Mangabeira → acesso pela Alfredo F. da Rocha → Diógenes Gomes da Silva → R. do Corujinha → Josefa Taveira → Dr. Euclides Neiva de Oliveira → Cidade Verde → R. Maria Regina Martins → Av. Jatobá → Três Marias / Patrícia Tomaz', 'hub alfredo_inicio diogenes corujinha josefa_sul euclides verde maria_regina jatoba patricia'),
    route('M-961', 'metropolitana', 'Litoral Sul via PB-008', 'Jacumã → PB-008 → trecho da Av. Jacarandá → acesso a Jacarapé → Hilton Souto Maior → T. Mangabeira', 'hub jacarape_acesso jacaranda pb008 jacuma', 'A Av. Jacarandá e a José Félix da Silva são nomes locais de trechos do eixo da PB-008. Jacarapé aparece pelo acesso na rodovia.'),
]
routes.extend(route(*row) for row in EXTRA_LINES)
routes.sort(key=lambda item: (('BRS-', 'T-', 'TRV-', 'I-', 'R-', 'L-', 'M-').index(item['code'].rsplit('-', 1)[0] + '-'), item['code']))

land_names = ('santa-rita', 'alhandra', 'pedras-de-fogo', 'bayeux', 'cabedelo', 'conde', 'jp')
land = [clean(row) for name in land_names if (directory / f'{name}.json').exists() for row in read(name)['features']]
blocks = [clean(row, home=name == 'MANGABEIRA') for name, row in neighborhoods.items()]
water = [g for row in read('rios')['features'] if (g := clean(row))]
roads = [clean(row) for row in corridors]
base = {'land': land, 'neighborhoods': blocks, 'rivers': water, 'roads': roads}
road_routes = read('malha-roteada')


def compact_path(raw, tolerance=.000026):
    if len(raw) < 3:
        return raw
    keep = {0, len(raw) - 1}
    stack = [(0, len(raw) - 1)]
    while stack:
        start, end = stack.pop()
        x, y = raw[start]
        dx, dy = raw[end][0] - x, raw[end][1] - y
        squared = dx * dx + dy * dy
        best, farthest = tolerance * tolerance, None
        for i in range(start + 1, end):
            px, py = raw[i][0] - x, raw[i][1] - y
            along = max(0, min(1, (px * dx + py * dy) / squared)) if squared else 0
            distance = (px - along * dx) ** 2 + (py - along * dy) ** 2
            if distance > best:
                best, farthest = distance, i
        if farthest is not None:
            keep.add(farthest)
            stack.extend([(start, farthest), (farthest, end)])
    return [raw[i] for i in sorted(keep)]


for item in routes:
    code = item['code']
    response = road_routes[code]
    item['traces'] = [compact_path(round_line(response['data']['routes'][0]['geometry']['coordinates']))]
    if item['points'][0] != item['points'][-1]:
        reverse_trace = road_routes[code + '-volta']['data']['routes'][0]['geometry']['coordinates']
        item['traces'].append(compact_path(round_line(reverse_trace)))
    assert all(len(trace) > 15 for trace in item['traces'])

previous_routes = json.loads((directory / 'comparacao-atual' / 'antes-ajustes.json').read_text())


def section(response, start, end):
    keys = response['keys']
    selected = response['data']['routes'][0]['legs'][keys.index(start):keys.index(end)]
    points = [position for leg in selected for step in leg['steps'] for position in step['geometry']['coordinates']]
    return round_line(points)


comparisons = {}
for key, label, start, end, points in [
    ('paratibe', 'Paratibe', 'porfirio', 'mucu', ['sibipiruna', 'severino_dias', 'maria_ines', 'humberto', 'felix_cahino', 'jacaranda', 'paratibe', 'mucu', 'porfirio']),
    ('parque-do-sol', 'Parque do Sol', 'mucu', 'val', ['clodoaldo', 'severina', 'balbina', 'joao_maria', 'parque', 'val', 'mucu']),
]:
    comparisons[key] = {
        'name': label,
        'before': section(previous_routes['I-332'], start, end),
        'after': section(road_routes['I-332'], start, end),
        'points': points,
    }

comparisons['paratibe']['stops'] = [[-34.840038, -7.205262], [-34.839943, -7.205448], [-34.841178, -7.205753]]
comparisons['parque-do-sol']['stops'] = [[-34.844844, -7.220099], [-34.846108, -7.222037], [-34.848, -7.221267], [-34.846184, -7.22155]]

data = {'routes': routes, 'places': places, 'base': base, 'comparisons': comparisons}
serialized = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
template = (directory / 'widget.html').read_text()
output = directory.parent / 'mapa-rede-joao-pessoa-revisada.html'
output.write_text(template.replace('__MGB_DATA__', serialized))
assert output.stat().st_size < 1_000_000
print(f'{len(routes)} linhas, {len(blocks)} bairros, {len(water)} rios. Arquivo com {output.stat().st_size} bytes.')
