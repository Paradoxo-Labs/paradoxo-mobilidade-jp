from collections import Counter
from pathlib import Path
import json
import re

import numpy as np
from matplotlib.path import Path as Polygon
from sklearn.cluster import DBSCAN

folder = Path(__file__).parent
mapa = (folder.parent.parent / 'historico' / 'mapa-mangabeira-rotas-locais-revisadas.html').read_text()
plan = json.loads(re.search(r'id="mgb-geodados">(.*?)</script>', mapa, re.S)[1])
stops = json.loads((folder / 'paradas.geojson').read_text())['features']
baseline = json.loads((folder / 'itinerarios-originais.geojson').read_text())['features']
neighborhoods = json.loads((folder.parent / 'bairros.json').read_text())['features']

scope = {
    'MANGABEIRA', 'BANCÁRIOS', 'JARDIM CIDADE UNIVERSITÁRIA', 'VALENTINA',
    'PARATIBE', 'MUÇUMAGRO', 'PLANALTO DA BOA ESPERANÇA', 'GRAMAME',
    'PORTAL DO SOL', 'ALTIPLANO CABO BRANCO', 'PENHA', 'COSTA DO SOL', 'PONTA DO SEIXAS',
    'ANATÓLIA', 'JARDIM SÃO PAULO', 'CASTELO BRANCO', 'CIDADE DOS COLIBRIS', 'ÁGUA FRIA',
}


def xy(points):
    return (np.asarray(points) - [-34.84, -7.17]) * [110440, 110580]


def segments(paths):
    lines = [xy(p) for p in paths if len(p) > 1]
    a = np.vstack([x[:-1] for x in lines])
    b = np.vstack([x[1:] for x in lines])
    ab = b - a
    keep = (ab != 0).any(axis=1)
    return a[keep], ab[keep], (ab[keep] ** 2).sum(axis=1)


def nearest_segments(points, roads):
    a, ab, ab2 = roads
    batches = []
    for x in np.array_split(points, max(1, int(np.ceil(len(points) / 36)))):
        ap = x[:, None, :] - a[None, :, :]
        t = ((ap * ab[None, :, :]).sum(axis=2) / ab2).clip(0, 1)
        batches.extend(np.sqrt(((ap - t[..., None] * ab) ** 2).sum(axis=2).min(axis=1)))
    return np.array(batches)


positions = xy([s['geometry']['coordinates'] for s in stops])
planned = {r['code']: segments(r['traces']) for r in plan['routes']}
current_roads = segments([r['geometry']['coordinates'] for r in baseline])
rows = []
for n in neighborhoods:
    name = n['properties']['nome']
    if name not in scope:
        continue
    parts = n['geometry']['coordinates']
    if n['geometry']['type'] == 'Polygon':
        parts = [parts]
    inside = np.zeros(len(stops), bool)
    for outer, *holes in parts:
        contains = Polygon(xy(outer)).contains_points(positions)
        for hole in holes:
            contains &= ~Polygon(xy(hole)).contains_points(positions)
        inside |= contains
    relevant = np.flatnonzero(inside)
    points = positions[relevant]
    baseline_distance = nearest_segments(points, current_roads)
    distances = np.vstack([nearest_segments(points, road) for road in planned.values()])
    for i, index in enumerate(relevant):
        d = distances[:, i]
        rows.append({'area': name, 'index': int(index), 'x': points[i, 0], 'y': points[i, 1], 'baseline': baseline_distance[i], 'proposal': d.min(), 'nearest': list(planned)[d.argmin()], 'address': stops[index]['properties']['address']})

result = [x for x in rows if x['baseline'] < 95]
for name in sorted(scope):
    n = [x for x in result if x['area'] == name]
    print(name, len(n), 'fora 300', sum(x['proposal']>300 for x in n), 'fora 400', sum(x['proposal']>400 for x in n), 'fora 500', sum(x['proposal']>500 for x in n))

for key in ['MANGABEIRA','VALENTINA','PARATIBE','MUÇUMAGRO','PLANALTO DA BOA ESPERANÇA','GRAMAME','PORTAL DO SOL','BANCÁRIOS','JARDIM CIDADE UNIVERSITÁRIA','COSTA DO SOL','PENHA','CASTELO BRANCO']:
    relevant = [x for x in result if x['area']==key and x['proposal']>275]
    if not relevant:
        continue
    labels = DBSCAN(eps=420, min_samples=1).fit_predict([(x['x'],x['y']) for x in relevant])
    for lab,n in Counter(labels).most_common(7):
        group = [x for x,l in zip(relevant,labels) if l==lab]
        group.sort(key=lambda x:-x['proposal'])
        print(key, 'grupo',n, 'alcance', [round(x['proposal']) for x in (group[-1],group[0])], ' | '.join(str((round(x['proposal']),round(x['baseline']),x['nearest'],x['address'])) for x in group[:9]))

(folder/'triagem.json').write_text(json.dumps(result, ensure_ascii=False))
