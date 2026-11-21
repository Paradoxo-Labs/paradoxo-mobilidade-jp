from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import Request, urlopen
import json
import re
from ampliacao import EXTRA_LINEAR, EXTRA_LOOPS, EXTRA_RETURN, EXTRA_POINTS, ROUTING_POINTS


directory = Path(__file__).parent
old_map = directory.parent / 'historico' / 'mapa-terminal-mangabeira-transversal-ampliada.html'
source = re.search(r'id="mgb-geodados">(.*?)</script>', old_map.read_text(), re.S)
places = {key: row['position'] for key, row in json.loads(source[1])['places'].items()}

# Public-road reference points. These keep the router outside buildings and on the specified corridor.
places.update({
    'hub': [-34.82191, -7.16079],                        # access beside the former Contax
    'hilton_penha': [-34.81595, -7.16049],
    'hilton_east': [-34.80308, -7.16097],
    'hilton_west': [-34.84847, -7.163785],
    'hilton_west_back': [-34.84884, -7.16414],
    'hilton_leste': [-34.83158, -7.16315],
    'hilton_leste_back': [-34.83138, -7.16331],
    'hilton': [-34.84317, -7.16184],
    'hilton_back': [-34.84409, -7.16226],
    'cristo': [-34.874973, -7.166678],
    'portal_arterial': [-34.81689, -7.15021],
    'altiplano_arterial': [-34.82337, -7.13456],
    'joao_cirilo': [-34.80354, -7.14738],
    'principal': [-34.84355, -7.14825],
    'principal_jcu': [-34.83862, -7.15511],
    'jcu_main': [-34.83856, -7.15301],
    'jcu_main_back': [-34.83884, -7.15248],
    'bancarios_main': [-34.84355, -7.14825],
    'ct_public': [-34.85052, -7.14531],
    'ufpb_dp2': [-34.858159, -7.135352],
    'ufpb_dp2_back': [-34.858198, -7.135423],
    'pedro': [-34.882242, -7.122249],
    'pedro_back': [-34.879173, -7.122678],
    'beira': [-34.853189, -7.12792],
    'beira_oeste': [-34.868454, -7.124139],
    'beira_back': [-34.853051, -7.127965],
    'beira_oeste_back': [-34.868758, -7.124122],
    'universidade_public': [-34.84553, -7.13822],
    'campus_via': [-34.85048, -7.13700],
    'hu_public': [-34.84092, -7.13439],
    'centro_lagoa': [-34.87879, -7.12231],
    'convencoes_public': [-34.80204, -7.18850],
    'retorno_convencoes': [-34.80448, -7.19306],
    'boulevard': [-34.8004375, -7.1880625],
    'penha_arterial': [-34.79808, -7.16346],
    'farol_public': [-34.79879, -7.14842],
    'seixas_public': [-34.79538, -7.15607],
    'cabo_atlantico': [-34.82391, -7.12053],
    'cabo_atlantico_back': [-34.823875, -7.124618],
    'tambau_beira': [-34.822799, -7.112354],
    'tambau_beira_back': [-34.823214, -7.117063],
    'manaira_beira': [-34.831614, -7.101683],
    'manaira_beira_back': [-34.833411, -7.09698],
    'creuza': [-34.84139, -7.18453],
    'herotildes': [-34.82528, -7.18235],
    'garrafao': [-34.83426, -7.16739],
    'trauminha': [-34.836865, -7.175782],
    'porfirio': [-34.83914, -7.18660],
    'diogenes': [-34.836105, -7.176872],
    'diogenes_back': [-34.834373, -7.176914],
    'corujinha': [-34.839205, -7.179098],
    'josefa_sul': [-34.842627, -7.180935],
    'euclides': [-34.843189, -7.183082],
    'alfredo_inicio': [-34.842086, -7.162515],
    'alfredo_meio': [-34.844353, -7.176522],
    'alfredo_fim': [-34.847318, -7.187609],
    'detran': [-34.826784, -7.165508],
    'anizio': [-34.845559, -7.181781],
    'castelo_via': [-34.841009, -7.129246],
    'felix_leste': [-34.837733, -7.207447],
    'felix_oeste': [-34.840035, -7.205289],
    'humberto': [-34.84138, -7.20589],
    'clodoaldo': [-34.844781, -7.220145],
    'severina': [-34.84604, -7.22210],
    'joao_maria': [-34.846198, -7.218445],
    'balbina': [-34.84797, -7.22128],
    'maria_regina_oeste': [-34.820153, -7.177516],
    'maria_regina_leste': [-34.816036, -7.177958],
    'jatoba': [-34.815133, -7.17978],
    'patricia': [-34.815163, -7.184128],
    'severino_dias': [-34.835396, -7.195769],
    'maria_ines': [-34.834758, -7.196606],
    'jacaranda': [-34.827845, -7.208137],
})

linear = {
    'BRS-300': 'hub hilton_leste jcu_main bancarios_main ct_public ufpb_dp2 pedro metro',
    'T-410': 'hub mariz portal_arterial altiplano_arterial beira beira_oeste centro_lagoa metro',
    'TRV-321': 'hub mariz portal_arterial altiplano_arterial cabo_atlantico tambau_beira manaira_beira retao_orla shopping leocadio bessa',
    'I-331': 'hub hilton_leste josefa val1 val',
    'I-332': 'hub garrafao trauminha porfirio severino_dias maria_ines paratibe felix_leste felix_oeste humberto jacaranda mucu clodoaldo severina balbina joao_maria parque val',
    'I-333': 'hub hilton coqueiral val2 planalto val',
    'L-351': 'hub hilton alfredo_inicio diogenes corujinha josefa_sul euclides creuza herotildes maria_regina_oeste maria_regina_leste jatoba patricia',
    'M-961': 'hub hilton_penha pb008 jacuma',
}
loops = {
    'TRV-322': 'hub hilton_penha convencoes_public retorno_convencoes boulevard penha_arterial farol_public hilton_east hilton_leste hilton_west cristo hilton_west_back hilton_leste_back hub',
    'I-334': 'hub mariz medico tres hu_public castelo_via universidade_public ct_public principal principal_jcu josefa josefa_sul anizio alfredo_meio alfredo_inicio hilton_leste_back hub',
    'R-343': 'hub hilton_penha seixas_public farol_public portal_arterial amaral ponte hu_public padre borba anatolia aurelio alfredo_inicio alfredo_meio anizio josefa_sul corujinha trauminha detran hub',
}
variants = {
    'TRV-322-direta': 'hub hilton_leste hilton_west cristo',
    'TRV-322-orla-cristo': 'hub hilton_penha convencoes_public retorno_convencoes boulevard penha_arterial farol_public hilton_east hilton_leste hilton_west cristo',
    'TRV-322-volta': 'cristo hilton_west_back coqueiral josefa mangabeira_67 hub',
    'TRV-322-orla': 'hub hilton_penha convencoes_public retorno_convencoes boulevard penha_arterial farol_public hilton_east hub',
    'M-961-PB008': 'hub hilton_penha pb008 jacuma',
}

places.update({key: info[1] for key, info in EXTRA_POINTS.items()})
places.update(ROUTING_POINTS)
linear.update(EXTRA_LINEAR)
loops.update(EXTRA_LOOPS)
opposite_lanes = {key[:-5]: key for key in places if key.endswith('_back')}
opposite_lanes['hilton_penha'] = 'hilton_east'


def load_route(item):
    name, waypoints = item
    keys = waypoints.split()
    coordinates = ';'.join(f'{places[key][0]:.6f},{places[key][1]:.6f}' for key in keys)
    query = '?steps=true&geometries=geojson&overview=full&annotations=nodes,distance&continue_straight=true'
    for base in ('https://router.project-osrm.org',):
        try:
            url = f'{base}/route/v1/driving/{coordinates}{query}'
            req = Request(url, headers={'User-Agent': 'Geographic transit corridor analysis'} )
            with urlopen(req, timeout=15) as response:
                result = json.load(response)
            if result.get('code') == 'Ok':
                return name, {'keys': keys, 'data': result}
            print(name, result.get('code'), flush=True)
        except Exception as error:
            print(name, error, flush=True)
    raise ValueError(f'Falha de roteamento em {name}')


if __name__ == '__main__':
    paths = {**linear, **loops, **variants}
    paths.update({f'{code}-volta': ' '.join(opposite_lanes.get(point, point) for point in reversed(points.split())) for code, points in linear.items()})
    paths.update(EXTRA_RETURN)
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = dict(executor.map(load_route, paths.items()))
    (directory / 'malha-roteada.json').write_text(json.dumps(results, ensure_ascii=False, separators=(',', ':')))
    for code, info in results.items():
        path = info['data']['routes'][0]
        large_snaps = [(key, round(waypoint['distance']), waypoint['name']) for key, waypoint in zip(info['keys'], info['data']['waypoints']) if waypoint['distance'] > 30]
        print(code, round(path['distance'] / 1000, 2), 'km', f'{round(path["duration"] / 60)} min carro', large_snaps)
        for ix, leg in enumerate(path['legs']):
            streets = list(dict.fromkeys(step['name'] or step.get('ref', '') for step in leg['steps']))
            print(' ', info['keys'][ix], '→', info['keys'][ix + 1], round(leg['distance']), 'm', ' | '.join(x for x in streets if x))
