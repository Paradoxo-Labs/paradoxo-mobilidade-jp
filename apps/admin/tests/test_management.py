"""Publicação de infraestrutura e linhas, conflitos e recuperação de dados."""
import copy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from apps.admin.store import Store, Problem, normalize
from apps.admin.routing import Router


class ManagementTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = Store(self.temp.name)

    def place(self, **extra):
        overview = self.store.overview()
        body = {'revision': overview['places_revision'], 'place': {'label': 'Estação de teste', 'kind': 'station',
                'position': [-34.9, -7.14], 'route_position': [-34.9001, -7.1401],
                'accesses': {'ida': [-34.9002, -7.1402], 'volta': [-34.9003, -7.1403]}}}
        body.update(extra)
        return self.store.save_place(body, 'admin')

    def draft(self, code='I-999', station=None):
        features = [{'type': 'Feature', 'properties': {'sentido': direction, 'station_ids': [station] if station else []},
                     'geometry': {'type': 'LineString', 'coordinates': [[-34.9,-7.14],[-34.901,-7.141],[-34.902,-7.142]]}}
                    for direction in ['ida','volta']]
        draft = self.store.create({'payload': {'line': {'code': code, 'name': code, 'type': 'integracional', 'points': []}, 'features': features}}, 'admin')
        return self.save(draft)

    def save(self, d):
        return self.store.save_version(d['id'], {'revision': d['revision']}, 'admin')

    def batch(self, drafts=(), remove=(), places=False):
        return {'draft_ids': [d['id'] for d in drafts], 'remove_ids': list(remove), 'include_places': places}

    def publish(self, body):
        report = self.store.batch_review(body)
        return self.store.publish_batch({**body, 'review_token': report['review_token'], 'acknowledge_warnings': True}, 'admin')

    def state(self, lid, action, **extra):
        o = self.store.overview()
        return self.store.manage_line({'line_id': lid, 'action': action, 'revision': o['line_states'].get(lid, {}).get('revision', 0), **extra}, 'admin')

    def test_infrastructure_is_staged_and_accesses_are_persistent(self):
        before = self.store.public_proposal()
        self.assertEqual(before['catalog']['lugares']['universidade']['kind'], 'station')
        place = self.place()
        key = place['id']
        self.assertNotIn(key, self.store.public_proposal()['catalog']['lugares'])
        restored = Store(self.temp.name)
        self.assertEqual(restored.overview()['places'][key]['accesses']['volta'], [-34.9003, -7.1403])
        self.publish(self.batch(places=True))
        self.assertEqual(self.store.public_proposal()['waypoints'][key], [-34.9001, -7.1401])
        self.assertEqual(self.store.public_proposal()['geojson'], before['geojson'])
        old = restored.overview()['places_revision']
        self.place()
        with self.assertRaises(Problem) as e:
            self.place(revision=old)
        self.assertEqual(e.exception.status, 409)

    def test_two_lines_and_new_station_publish_as_one_release(self):
        p = self.place()['id']
        a, b = self.draft(station=p), self.draft('I-998', p)
        self.assertTrue(self.store.review(a['id'])['errors'])
        self.assertTrue(self.store.batch_review(self.batch([a,b]))['errors'])
        body = self.batch([a,b], places=True)
        r = self.store.batch_review(body)
        self.assertEqual(r['errors'], [])
        self.assertEqual(r['line_count'], 26)
        self.publish(body)
        public = self.store.public_proposal()
        self.assertEqual(public['catalog']['publication']['number'], 2)
        self.assertEqual(len(public['catalog']['linhas']), 26)
        self.assertIn(p, public['catalog']['lugares'])
        line = next(l for l in public['catalog']['linhas'] if l['code'] == 'I-999')
        self.assertEqual(line['sentidos'][0]['station_ids'], [p])

    def test_changed_draft_station_or_line_state_invalidates_review_atomically(self):
        p = self.place()['id']
        d = self.draft(station=p)
        body = self.batch([d], places=True)
        r = self.store.batch_review(body)
        self.place()
        with self.assertRaises(Problem) as e:
            self.store.publish_batch({**body, 'review_token': r['review_token'], 'acknowledge_warnings': True}, 'admin')
        self.assertEqual(e.exception.status, 409)
        self.assertEqual(self.store.overview()['release']['number'], 1)
        r = self.store.batch_review(body)
        payload = copy.deepcopy(d['payload']); payload['line']['name'] = 'Mudou'
        d = self.store.update(d['id'], {'revision': d['revision'], 'payload': payload}, 'admin')
        with self.assertRaises(Problem):
            self.store.publish_batch({**body, 'review_token': r['review_token'], 'acknowledge_warnings': True}, 'admin')
        d = self.save(d);r = self.store.batch_review(body)
        self.state(d['line_id'], 'archive')
        with self.assertRaises(Problem):
            self.store.publish_batch({**body, 'review_token': r['review_token'], 'acknowledge_warnings': True}, 'admin')
        self.assertEqual(len(self.store.public_proposal()['catalog']['linhas']), 24)

    def test_archiving_withdrawal_and_reactivation_keep_history(self):
        d = self.draft();self.publish(self.batch([d]))
        d = self.store.draft(d['id'])
        self.state(d['line_id'], 'archive')
        self.assertEqual(len(self.store.public_proposal()['catalog']['linhas']), 25)
        self.assertTrue(self.store.batch_review(self.batch([d]))['errors'])
        self.publish(self.batch(remove=[d['line_id']]))
        self.assertEqual(len(self.store.public_proposal()['catalog']['linhas']), 24)
        self.assertIn(d['line_id'], [l['id'] for l in self.store.overview()['inactive_lines']])
        self.state(d['line_id'], 'restore')
        d = self.store.create({'line_id': d['line_id'], 'edit': True}, 'admin')
        self.assertIsNone(d['base_version'])
        self.publish(self.batch([d]))
        self.assertEqual(len(self.store.public_proposal()['catalog']['linhas']), 25)

    def test_final_network_checks_allow_code_exchange_but_reject_duplicates(self):
        lines = self.store.overview()['lines'][:2]
        drafts = [self.store.create({'line_id': l['id'], 'edit': True}, 'admin') for l in lines]
        updated = []
        for i,d in enumerate(drafts):
            payload = copy.deepcopy(d['payload']);payload['line']['code'] = lines[1-i]['code']
            updated.append(self.save(self.store.update(d['id'], {'revision': d['revision'], 'payload': payload}, 'admin')))
        self.assertTrue(self.store.review(updated[0]['id'])['errors'])
        self.assertEqual(self.store.batch_review(self.batch(updated))['errors'], [])
        self.publish(self.batch(updated))
        duplicate = self.draft(lines[0]['code'])
        body = self.batch([duplicate]);r = self.store.batch_review(body)
        self.assertTrue(any('duplicado' in e for e in r['errors']))
        number = self.store.overview()['release']['number']
        with self.assertRaises(Problem):self.publish(body)
        self.assertEqual(self.store.overview()['release']['number'], number)

    def test_used_station_cannot_be_archived_without_updating_final_network(self):
        key = self.place()['id'];d = self.draft(station=key)
        self.publish(self.batch([d], places=True))
        p = self.store.overview()['places'][key];p['archived'] = True
        self.place(id=key, place=p)
        r = self.store.batch_review(self.batch(places=True))
        self.assertTrue(any('arquivada' in e for e in r['errors']))
        self.state(d['line_id'], 'archive')
        self.publish(self.batch(remove=[d['line_id']], places=True))
        self.assertNotIn(key, self.store.public_proposal()['catalog']['lugares'])

    def test_release_restore_includes_stations_and_preserves_pending_edits(self):
        first = self.store.overview()['release']['id'];key = self.place()['id']
        self.publish(self.batch(places=True))
        active = self.store.overview()['release']['id']
        self.store.restore_release({'release_id': first, 'expected_release': active}, 'admin')
        self.assertNotIn(key, self.store.public_proposal()['catalog']['lugares'])
        self.assertNotIn(key, self.store.overview()['places'])
        pending = self.place()['id']
        active = self.store.overview()['release']['id']
        self.store.restore_release({'release_id': first, 'expected_release': active}, 'admin')
        self.assertIn(pending, self.store.overview()['places'])
        self.assertNotIn(pending, self.store.public_proposal()['catalog']['lugares'])

    def test_discard_requires_current_revision_and_keeps_saved_versions(self):
        d = self.draft();vid = d['saved_version']
        with self.assertRaises(Problem):self.state(d['line_id'], 'discard-draft', draft_revision=0)
        self.state(d['line_id'], 'discard-draft', draft_revision=d['revision'])
        with self.assertRaises(Problem):self.store.draft(d['id'])
        self.assertEqual(self.store.version(vid)['line_id'], d['line_id'])
        reopened = self.store.create({'line_id': d['line_id'], 'edit': True}, 'admin')
        self.assertEqual(reopened['payload'], d['payload'])

    def test_controls_survive_restart_and_versions_and_are_validated(self):
        d = self.draft();payload = copy.deepcopy(d['payload'])
        p = payload['features'][0]['properties']
        p['control_points'] = [{'id':'11111111-1111-1111-1111-111111111111','label':'Passagem','position':[-34.9,-7.14]}]
        d = self.save(self.store.update(d['id'], {'revision':d['revision'],'payload':payload}, 'admin'))
        self.assertEqual(Store(self.temp.name).version(d['saved_version'])['payload']['features'][0]['properties']['control_points'], p['control_points'])
        invalid = copy.deepcopy(payload);invalid['features'][0]['properties']['control_points'] *= 2
        with self.assertRaises(Problem):normalize(invalid)
        with self.assertRaises(Problem):self.place(place={'label':'Inválida','position':[0,0]})

    def test_old_database_migrates_without_rewriting_versions_or_drafts(self):
        d = self.draft()
        before = self.store.version(d['saved_version'])
        with self.store.db(write=True) as db:
            for name in ['release_places','place_workspace','line_state']:db.execute('DROP TABLE '+name)
        again = Store(self.temp.name)
        self.assertEqual(again.version(d['saved_version']), before)
        self.assertEqual(again.draft(d['id'])['payload'], d['payload'])
        self.assertFalse(again.overview()['places_dirty'])


class TrimTests(unittest.TestCase):
    def test_trim_is_preview_preserves_locks_and_rejects_stale_or_empty_paths(self):
        coords = [[-34.9,-7.14],[-34.901,-7.141],[-34.902,-7.142],[-34.903,-7.143]]
        f = {'properties': {'path_id': 'path', 'locked_sections': [{'coordinates': coords[1:3]}]}, 'geometry': {'type':'LineString','coordinates':coords}}
        draft = {'revision': 3, 'payload': {'features': [f]}}
        router = Router('/missing')
        body = {'revision':3,'path_id':'path','index':1,'side':'before'}
        self.assertEqual(router.trim(draft, body)['geometry']['coordinates'], coords[1:])
        self.assertEqual(f['geometry']['coordinates'], coords)
        with self.assertRaises(Problem):router.trim(draft, {**body,'index':2})
        with self.assertRaises(Problem):router.trim(draft, {**body,'index':0,'side':'after'})
        with self.assertRaises(Problem):router.trim(draft, {**body,'revision':2})
