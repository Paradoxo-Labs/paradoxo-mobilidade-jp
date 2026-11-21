import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from revise import Network, OUTPUT, STUDY, distance, inside, read, segment_distance


class RevisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = read(OUTPUT / 'catalogo.json')
        cls.features = read(OUTPUT / 'linhas-por-sentido.geojson')['features']
        cls.audit = read(OUTPUT / 'auditoria.json')
        cls.waypoints = read(OUTPUT / 'waypoints-roteamento.json')

    def test_all_services_and_directions_are_preserved(self):
        original = read(STUDY / 'dados/linhas-por-sentido.geojson')['features']
        self.assertEqual(len(self.catalog['linhas']), 23)
        self.assertEqual(len(self.features), 39)
        self.assertEqual({f['id'] for f in self.features}, {f['id'] for f in original})
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

    def test_oitizeiro_is_next_to_interchange_and_not_old_market(self):
        position = self.catalog['lugares']['oitizeiro']['position']
        self.assertGreater(distance(position, [-34.896326, -7.161357]), 350)
        self.assertTrue(-7.1665 < position[1] < -7.164)
        self.assertIn('pendente', self.audit['oitizeiro_reference']['status'])

    def test_reference_offsets_are_bounded_and_reported(self):
        self.assertTrue(self.audit['snap_adjustments'])
        self.assertLessEqual(max(item['distance_m'] for item in self.audit['snap_adjustments']), 110)
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
        self.assertEqual(graph.route(0, 1), [0, 2, 1])
        with self.assertRaisesRegex(ValueError, 'caminho dirigido'):
            graph.route(1, 0)


if __name__ == '__main__':
    unittest.main()
