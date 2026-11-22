"""Alimentadora oeste: cobertura da 108 e ligação local às áreas da 110/105."""
try:
    from . import policies
except ImportError:
    import policies

CODE = 'I-131'
NAME = 'Alto do Mateus–Oitizeiro via Novais, Planalto e Cidade'
ITINERARY = 'Terminal Alto do Mateus → Novais → Jardim Planalto → Cidade dos Funcionários → Terminal Oitizeiro'


def build(network, observed, waypoints, catalog, distance):
    sources = {line['code']: line for line in observed['lines'] if line['code'] in {'0108', '0110', '0105'}}
    paths = {}
    for code, line in sources.items():
        for feature in line['geojson']['features']:
            if feature['geometry']['type'] != 'LineString':
                raise ValueError(f'{code}: esperado traçado contínuo para referência oeste')
            paths[code, feature['properties']['ITINERARIO'].lower()] = feature['geometry']['coordinates']

    def street(key, name, near):
        nodes = {n for title, ns in network.corridor_nodes.items() if policies.fold(name) in title for n in ns}
        if not nodes:
            raise ValueError(f'Via da alimentadora oeste ausente: {name}')
        waypoints[key] = min((network.positions[n] for n in nodes), key=lambda p: distance(p, near))
        return name

    hints = {
        'cidade_benedito': street('cidade_benedito', 'SÃO BENEDITO', [-34.892, -7.1565]),
        'cidade_ernani': street('cidade_ernani', 'ERNANI RABELO', [-34.891, -7.159]),
        'cidade_lauro': street('cidade_lauro', 'LAURO WANDERLEY', [-34.891, -7.161]),
    }
    street('novais', 'ADOLFO MASSA', [-34.8976, -7.1516])
    waypoints['alto_mateus'] = paths['0108', 'ida'][0]
    waypoints['jardim_planalto'] = paths['0110', 'ida'][0]
    waypoints['cidade_funcionarios'] = paths['0105', 'ida'][0]
    for key, label in [('alto_mateus', 'Terminal Alto do Mateus · terminal atual da 108'), ('novais', 'Novais · Coronel Adolfo Massa'), ('jardim_planalto', 'Jardim Planalto · referência da 110'), ('cidade_funcionarios', 'Cidade dos Funcionários · referência da 105')]:
        catalog['lugares'][key] = {'label': label, 'position': waypoints[key], 'terminal': key == 'alto_mateus'}

    features, reports, entries, offsets = [], [], [], []
    for direction in ['ida', 'volta']:
        source = paths['0108', direction]
        # Usa um vértice observado junto a um nó viário, evitando um salto no
        # meio de um segmento longo da geometria publicada.
        joins = [i for i, point in enumerate(source) if distance(point, waypoints['novais']) < 250 and distance(point, network.positions[network.snap(point)]) <= 25]
        if not joins:
            raise ValueError(f'108 / {direction}: sem conexão viária próxima de Novais')
        cut = min(joins, key=lambda i: distance(source[i], waypoints['novais']))
        locked = source[:cut+1] if direction == 'ida' else source[cut:]
        join_key = 'novais_108_' + direction
        waypoints[join_key] = locked[-1] if direction == 'ida' else locked[0]
        # A 110 vai do bairro ao Centro: usa-se sua volta na ida da alimentadora.
        plan_direction = 'volta' if direction == 'ida' else 'ida'
        plan_source = paths['0110', plan_direction]
        plan_joins = [i for i, point in enumerate(plan_source) if distance(point, waypoints['novais']) < 700 and distance(point, network.positions[network.snap(point)]) <= 25]
        if not plan_joins:
            raise ValueError(f'110 / {plan_direction}: sem conexão próxima de Novais')
        plan_cut = min(plan_joins, key=lambda i: distance(plan_source[i], waypoints['novais']))
        plan_locked = plan_source[plan_cut:] if direction == 'ida' else plan_source[:plan_cut+1]
        plan_join = 'planalto_110_' + direction
        waypoints[plan_join] = plan_locked[0] if direction == 'ida' else plan_locked[-1]
        plan_terminal = 'planalto_terminal_' + direction
        waypoints[plan_terminal] = plan_locked[-1] if direction == 'ida' else plan_locked[0]
        catalog['lugares'][join_key] = {'label': 'Novais · conexão com o trecho da 108', 'position': waypoints[join_key]}
        catalog['lugares'][plan_join] = {'label': 'Novais / Santos Stanislau · conexão com a 110', 'position': waypoints[plan_join]}
        catalog['lugares'][plan_terminal] = {'label': 'Jardim Planalto · terminal atual da 110', 'position': waypoints[plan_terminal]}
        city_keys = [plan_terminal, 'cidade_benedito', 'cidade_ernani', 'cidade_lauro', 'cidade_funcionarios', 'oitizeiro']
        legs, edge_list, join_gaps = [], [], []

        def connect(keys):
            node = network.snap(waypoints[keys[0]])
            result = [waypoints[keys[0]], network.positions[node]]
            join_gaps.append(distance(result[0], result[1]))
            for start, end in zip(keys, keys[1:]):
                fixed = end == keys[-1]
                goals = {network.snap(waypoints[end])} if fixed else network.candidates(waypoints[end], hints.get(end))
                path = network.route(node, network.snap(waypoints[end]), goals=goals)
                es = [network.edges[a, b] for a, b in zip(path, path[1:])]
                legs.append({'from': start, 'to': end, 'distance_m': round(sum(e['length'] for e in es), 1), 'streets': list(dict.fromkeys(e['name'] for e in es)), 'road_refs': sorted({e['ref'] for e in es if e['ref']})})
                edge_list.extend(es)
                node = path[-1]
                result.extend(network.positions[n] for n in path[1:])
                gap = distance(waypoints[end], network.positions[node])
                if gap > 35:
                    offsets.append({'route': CODE if direction == 'ida' else CODE+'-volta', 'waypoint': end, 'distance_m': round(gap, 1), 'reference': waypoints[end], 'road_point': network.positions[node]})
            join_gaps.append(distance(result[-1], waypoints[keys[-1]]))
            result.append(waypoints[keys[-1]])
            return result

        if direction == 'ida':
            middle = connect([join_key, plan_join])
            city = connect(city_keys)
            coords = locked + middle + plan_locked + city
            keys = [join_key, plan_join] + city_keys
        else:
            city = connect(city_keys[::-1])
            middle = connect([plan_join, join_key])
            coords = city + plan_locked + middle + locked
            keys = city_keys[::-1] + [plan_join, join_key]
        if max(join_gaps) > 35:
            raise ValueError(f'{CODE} / {direction}: conexão fora de tolerância ({max(join_gaps):.1f} m)')
        key = CODE if direction == 'ida' else CODE+'-volta'
        edges = edge_list
        km = round(sum(distance(a, b) for a, b in zip(coords, coords[1:])) / 1000, 2)
        # O texto de cada trecho observado exclui as ruas que seguem até o Centro.
        original_streets = next(i['streets'] for i in sources['0108']['itineraries'] if i['direction'].lower() == direction)
        marker = original_streets.index('AV CEL ADOLFO MASSA')
        local_streets = original_streets[:marker+1] if direction == 'ida' else original_streets[marker:]
        plan_streets = next(i['streets'] for i in sources['0110']['itineraries'] if i['direction'].lower() == plan_direction)
        marker = plan_streets.index('AV DES SANTOS STANISLAU')
        plan_streets = plan_streets[marker:] if direction == 'ida' else plan_streets[:marker+1]
        city_streets = [name for leg in legs if 'cidade' in leg['from'] or 'cidade' in leg['to'] for name in leg['streets']]
        middle_streets = [name for leg in legs if 'cidade' not in leg['from'] and 'cidade' not in leg['to'] for name in leg['streets']]
        streets = local_streets + middle_streets + plan_streets + city_streets if direction == 'ida' else city_streets + plan_streets + middle_streets + local_streets
        all_keys = ['alto_mateus'] + keys if direction == 'ida' else keys + ['alto_mateus']
        references = sorted({'0108', '0110', '0105'} | set().union(*(e['observed'] for e in edges)))
        percent = network.support_metric(coords)
        entries.append({'chave': key, 'sentido': direction, 'distancia_km': km, 'waypoints': all_keys, 'source': 'alimentadora-oeste-108-110-105', 'street_sequence': streets, 'central_pattern': None, 'reference_lines': references, 'observed_streets_percent': percent})
        features.append({'type': 'Feature', 'id': key, 'properties': {'codigo': CODE, 'classe': 'integracional', 'nome': NAME, 'chave': key, 'sentido': direction, 'distancia_km': km, 'waypoints': all_keys, 'revision': 'rede-observada-2026-11-21', 'observed_streets_percent': percent}, 'geometry': {'type': 'LineString', 'coordinates': coords}})
        reports.append({'code': CODE, 'key': key, 'direction': direction, 'old_distance_km': None, 'baseline_observed_streets_percent': None, 'distance_km': km, 'observed_streets_percent': percent, 'reference_lines': references, 'street_sequence': streets, 'way_sequence': list(dict.fromkeys(e['way'] for e in edges)), 'restored_original': False, 'legs': legs, 'road_refs': sorted({e['ref'] for e in edges if e['ref']}), 'central_pattern': None, 'central_join_m': [], 'observed_sections': [{'line': '0108', 'direction': direction, 'start_index': 0 if direction == 'ida' else cut, 'end_index': cut if direction == 'ida' else len(source)-1, 'coordinates': locked, 'join_m': round(max(join_gaps), 1)}, {'line': '0110', 'direction': plan_direction, 'start_index': plan_cut if direction == 'ida' else 0, 'end_index': len(plan_source)-1 if direction == 'ida' else plan_cut, 'coordinates': plan_locked, 'join_m': round(max(join_gaps), 1)}]})
    line = {'code': CODE, 'type': 'integracional', 'name': NAME, 'itinerary': ITINERARY, 'points': ['alto_mateus', 'novais', 'jardim_planalto', 'cidade_funcionarios', 'oitizeiro'], 'note': 'Alimentadora bidirecional proposta, com código de estudo I-131. Preserva os trechos locais da 108 no Alto do Mateus e da 110 no Jardim Planalto; conecta Novais e a área da 105 ao Terminal Oitizeiro. Cidade dos Funcionários corresponde ao setor da 105. Atendimento complementar de Tiradentes permanece para avaliação de cobertura e demanda. Entrada e plataformas de Oitizeiro dependem da planta; frequências e frota ainda não dimensionadas.', 'sentidos': entries}
    return line, features, reports, offsets
