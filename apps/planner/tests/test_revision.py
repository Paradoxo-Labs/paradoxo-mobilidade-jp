import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from revise import policies, Network, OUTPUT, STUDY, distance, inside, read, segment_distance


class RevisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = read(OUTPUT / 'catalogo.json')
        cls.features = read(OUTPUT / 'linhas-por-sentido.geojson')['features']
        cls.audit = read(OUTPUT / 'auditoria.json')
        cls.waypoints = read(OUTPUT / 'waypoints-roteamento.json')

    def test_all_services_and_directions_are_preserved(self):
        original = read(STUDY / 'dados/linhas-por-sentido.geojson')['features']
        self.assertEqual(len(self.catalog['linhas']), 24)
        self.assertEqual(len(self.features), 41)
        self.assertEqual({f['id'] for f in self.features}, {f['id'] for f in original} | {'I-131', 'I-131-volta'})
        for line in self.catalog['linhas']:
            for entry in line['sentidos']:
                self.assertTrue(all(key in self.waypoints for key in entry['waypoints']))
                feature = next(f for f in self.features if f['id'] == entry['chave'])
                measured = sum(distance(a, b) for a, b in zip(feature['geometry']['coordinates'], feature['geometry']['coordinates'][1:])) / 1000
                self.assertAlmostEqual(measured, entry['distancia_km'], delta=.01)

    def test_station_is_external_and_not_the_old_campus_terminal(self):
        place = self.catalog['lugares']['universidade']
        self.assertIn('Estação Cidade Universitária', place['label'])
        self.assertLess(distance(place['position'], [-34.8512665, -7.1389503]), 1)
        self.assertGreater(distance(place['position'], [-34.84553, -7.13822]), 500)
        for code in ['BRS-300', 'BRS-800', 'I-334', 'R-343']:
            line = next(line for line in self.catalog['linhas'] if line['code'] == code)
            self.assertIn('Estação Cidade Universitária', line['itinerary'])
            for entry in line['sentidos']:
                self.assertNotIn('Via UFPB', entry['street_sequence'])

    def test_campus_interior_is_excluded_except_public_perimeter(self):
        ring = self.audit['campus_polygon']
        perimeter = [pair for path in self.audit['public_perimeter'] for pair in zip(path, path[1:])]
        for feature in self.features:
            for a, b in zip(feature['geometry']['coordinates'], feature['geometry']['coordinates'][1:]):
                p = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]
                if not (-34.863 < p[0] < -34.832 and -7.149 < p[1] < -7.124) or not inside(p, ring):
                    continue
                clearance = min(segment_distance(p, u, v) for u, v in zip(ring, ring[1:]))
                if clearance > 25.01:
                    self.assertLess(min(segment_distance(p, u, v) for u, v in perimeter), 1, feature['id'])

    def test_varadouro_uses_exact_observed_access_and_lake(self):
        center = self.audit['central_reference']
        radial = {'BRS-100', 'BRS-200', 'BRS-300', 'BRS-500', 'BRS-501', 'T-410', 'T-610'}
        entries = [f for f in self.features if f['properties']['codigo'] in radial]
        self.assertEqual(len(entries), 14)
        self.assertLess(distance(self.catalog['lugares']['metro']['position'], [-34.8897, -7.1183]), 100)
        for f in entries:
            coords = f['geometry']['coordinates']
            if f['properties']['sentido'] == 'ida':
                self.assertEqual(coords[-len(center['entry']):], center['entry'])
            else:
                self.assertEqual(coords[:len(center['exit'])], center['exit'])
            self.assertLess(min(distance(p, center['lake']) for p in coords), 220)
        self.assertIn('AV PADRE AZEVEDO', center['streets']['volta'])
        self.assertIn('RUA DES TRINDADE', center['streets']['ida'])

    def test_terminals_follow_the_confirmed_references(self):
        places = self.catalog['lugares']
        self.assertEqual(places['oitizeiro']['position'], policies.OITIZEIRO_MARKET)
        self.assertEqual(places['cristo']['position'], policies.CRISTO_TERMINAL)
        self.assertEqual(places['lagoa']['position'], policies.LAGOA_PLATFORM)
        self.assertIn('Terminal de Passageiros', places['lagoa']['label'])
        self.assertIn('pendente', self.audit['oitizeiro_reference']['status'])
        self.assertGreater(self.audit['oitizeiro_reference']['market_to_road_m'], 100)

    def test_reference_offsets_are_bounded_and_reported(self):
        self.assertTrue(self.audit['snap_adjustments'])
        self.assertLessEqual(max(item['distance_m'] for item in self.audit['snap_adjustments']), 150)
        for route in self.audit['routes']:
            self.assertLessEqual(max(route['central_join_m'], default=0), 35)

    def test_comparisons_use_active_revision(self):
        comparisons = read(OUTPUT / 'comparativos-i332.json')
        active = next(f for f in self.features if f['id'] == 'I-332')['geometry']['coordinates']
        for item in comparisons.values():
            self.assertEqual(item['revision'], self.audit['revision'])
            self.assertIn(item['after'][0], active)
            self.assertIn(item['after'][-1], active)

    def test_preference_for_observed_streets_and_direction(self):
        graph = Network.__new__(Network)
        graph.graph = {0: [1, 2], 2: [1], 1: []}
        graph.positions = {0: [0, 0], 1: [1, 0], 2: [.5, 1]}
        graph.edges = {(0, 1): {'length': 100, 'observed': set(), 'street_count': 0}, (0, 2): {'length': 60, 'observed': {'0101', '0102'}, 'street_count': 12}, (2, 1): {'length': 60, 'observed': {'0101', '0102'}, 'street_count': 12}}
        # A concentração não deve impor uma volta 20% maior.
        self.assertEqual(graph.route(0, 1), [0, 1])
        graph.edges[0, 2]['length'] = graph.edges[2, 1]['length'] = 50
        self.assertEqual(graph.route(0, 1), [0, 2, 1])
        self.assertEqual(graph.route(0, 1, goals={2}), [0, 2])
        with self.assertRaisesRegex(ValueError, 'caminho dirigido'):
            graph.route(1, 0)


    def test_highways_and_beira_rio_constraints(self):
        for route in self.audit['routes']:
            streets = ' '.join(route['street_sequence']).upper()
            if route['code'] in {'T-610', 'TRV-321'}:
                self.assertFalse(any('BR-230' in ref for ref in route['road_refs']), route['key'])
            if route['code'] == 'T-410':
                self.assertNotIn('EPITÁCIO', streets)
                self.assertNotIn('UFPB', streets)
                self.assertIn('JOSÉ AMÉRICO DE ALMEIDA', streets)
                for leg in route['legs']:
                    if leg['from'].startswith('beira') and leg['to'].startswith('beira'):
                        self.assertTrue(all('JOSÉ AMÉRICO DE ALMEIDA' in street.upper() or street == 'Via sem nome cadastrado' for street in leg['streets']), leg)
            if route['code'] == 'BRS-800':
                for leg in route['legs']:
                    if leg['from'] == 'estacao_ida':
                        self.assertTrue(any('BR-230' in ref for ref in leg['road_refs']))

    def test_southern_coverage_and_original_metropolitan_route(self):
        lines = {line['code']: line for line in self.catalog['linhas']}
        for entry in lines['I-332']['sentidos']:
            self.assertFalse({'clodoaldo', 'severina', 'balbina', 'joao_maria', 'parque'} & set(entry['waypoints']))
            self.assertIn(['mucu', 'val'], [entry['waypoints'][i:i+2] for i in range(len(entry['waypoints'])-1)] + [entry['waypoints'][i:i+2][::-1] for i in range(len(entry['waypoints'])-1)])
        for point in ['parque', 'clodoaldo', 'severina', 'balbina', 'joao_maria']:
            self.assertIn(point, lines['L-751']['sentidos'][0]['waypoints'])
        for code in ['R-241', 'R-242']:
            street_text = ' '.join(lines[code]['sentidos'][0]['street_sequence']).upper()
            for name in ['FERNANDO TORRES', 'COLIBRIS', 'PAULO GOMES', 'CLIMACO', 'ARISTOTELES']:
                self.assertIn(name, policies.fold(street_text))
        local = lines['L-251']['sentidos'][0]
        self.assertIn('ifpb', local['waypoints'])
        self.assertGreater(local['distancia_km'], 13)
        original = read(STUDY / 'dados/linhas-por-sentido.geojson')['features']
        for f in self.features:
            if f['properties']['codigo'] == 'M-961':
                before = next(old for old in original if old['properties']['chave'] == f['id'])
                self.assertEqual(f['geometry'], before['geometry'])

    def test_beach_axis_is_different_and_planalto_is_avoided(self):
        lines = {line['code']: line for line in self.catalog['linhas']}
        for entry in lines['BRS-501']['sentidos']:
            self.assertIn('praia_interior_brandao', entry['waypoints'])
            self.assertIn('praia_interior_morais', entry['waypoints'])
        for entry in lines['TRV-721']['sentidos']:
            self.assertNotIn('perimetral_leste', entry['waypoints'])
            self.assertNotIn('perimetral_leste_back', entry['waypoints'])



    def test_west_feeder_preserves_108_and_connects_the_four_areas(self):
        line = next(line for line in self.catalog['linhas'] if line['code'] == 'I-131')
        self.assertEqual(line['type'], 'integracional')
        self.assertEqual({e['sentido'] for e in line['sentidos']}, {'ida', 'volta'})
        for entry in line['sentidos']:
            keys = entry['waypoints']
            sequence = ['alto_mateus', 'novais_108_' + entry['sentido'], 'planalto_terminal_' + entry['sentido'], 'cidade_funcionarios', 'oitizeiro']
            order = sequence if entry['sentido'] == 'ida' else sequence[::-1]
            self.assertEqual(sorted(order, key=keys.index), order)
            self.assertTrue(any(key.startswith('novais') for key in keys))
            self.assertTrue(any(key.startswith('planalto_terminal') for key in keys))
            feature = next(f for f in self.features if f['id'] == entry['chave'])
            report = next(r for r in self.audit['routes'] if r['key'] == entry['chave'])
            self.assertIsNone(report['old_distance_km'])
            section = report['observed_sections'][0]
            locked = section['coordinates']
            self.assertEqual(section['line'], '0108')
            self.assertLessEqual(section['join_m'], 35)
            self.assertGreater(sum(distance(a, b) for a, b in zip(locked, locked[1:])), 4000)
            coords = feature['geometry']['coordinates']
            self.assertEqual(coords[:len(locked)] if entry['sentido'] == 'ida' else coords[-len(locked):], locked)
            self.assertTrue({'0105', '0108', '0110'} <= set(entry['reference_lines']))
            self.assertGreater(entry['distancia_km'], 6)
            self.assertLess(entry['distancia_km'], 12)
            source_max = max(distance(a,b) for section in report['observed_sections'] for a,b in zip(section['coordinates'], section['coordinates'][1:]))
            self.assertLessEqual(max(distance(a,b) for a,b in zip(coords, coords[1:])), max(100, source_max) + .01)
            self.assertEqual(len(report['observed_sections']), 2)
            plan = report['observed_sections'][1]
            self.assertEqual(plan['line'], '0110')
            self.assertTrue(any(coords[i:i+len(plan['coordinates'])] == plan['coordinates'] for i in range(len(coords))))
        self.assertTrue(self.catalog['lugares']['alto_mateus']['terminal'])
        self.assertIn('Tiradentes', line['note'])

if __name__ == '__main__':
    unittest.main()
