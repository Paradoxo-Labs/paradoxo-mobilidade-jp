import copy
import json
import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from apps.admin.store import Store, Problem, normalize, validation
from apps.admin.routing import Router


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store=Store(self.temp.name)
        self.user='admin'

    def new(self, code='I-999'):
        fs=[{'type':'Feature','properties':{'sentido':key},'geometry':{'type':'LineString','coordinates':[[-34.9,-7.14],[-34.901,-7.141]]}} for key in ['ida','volta']]
        return self.store.create({'payload':{'line':{'code':code,'name':'Teste de alimentadora','type':'integracional','kind':'bidirectional','points':['oitizeiro']},'features':fs}},self.user)

    def saved(self,draft):
        return self.store.save_version(draft['id'],{'revision':draft['revision'],'note':'Verificação'},self.user)

    def publish(self,draft):
        r=self.store.review(draft['id'])
        return self.store.publish(draft['id'],{'revision':r['revision'],'release_id':r['release_id'],'version_id':r['version_id'],'acknowledge_warnings':True},self.user)

    def test_seed_and_authentication_survive_restart_without_plaintext_password(self):
        self.assertEqual(len(self.store.public_proposal()['catalog']['linhas']),24)
        token=(Path(self.temp.name)/'admin/setup-token').read_text()
        session=self.store.setup(token,self.user,'uma senha longa para teste')
        self.assertTrue(self.store.session(session['token']))
        self.assertFalse((Path(self.temp.name)/'admin/setup-token').exists())
        again=Store(self.temp.name)
        self.assertEqual(again.session(session['token'])['username'],self.user)
        with again.db() as db:
            account=db.execute('SELECT * FROM account').fetchone()
            self.assertNotIn('uma senha',account['password'])
        with self.assertRaises(Problem):again.login(self.user,'incorreta')
        self.assertEqual(again.login(self.user,'uma senha longa para teste')['username'],self.user)
        again.logout(session['token']);self.assertIsNone(again.session(session['token']))

    def test_optimistic_conflict_and_new_draft_survive_restart(self):
        d=self.new();body=copy.deepcopy(d['payload']);body['line']['name']='Alterada'
        updated=self.store.update(d['id'],{'revision':d['revision'],'payload':body},self.user)
        self.assertEqual(updated['revision'],2)
        with self.assertRaises(Problem) as e:self.store.update(d['id'],{'revision':1,'payload':body},self.user)
        self.assertEqual(e.exception.status,409)
        self.assertEqual(Store(self.temp.name).draft(d['id'])['payload']['line']['name'],'Alterada')
        self.assertEqual(len(self.store.public_proposal()['catalog']['linhas']),24)

    def test_save_publish_restore_and_publication_staleness(self):
        d=self.new();first=self.store.overview()['release']
        self.assertTrue(self.store.review(d['id'])['errors'])
        d=self.saved(d)
        self.assertEqual(self.store.review(d['id'])['errors'],[])
        before=self.store.public_proposal()
        self.publish(d)
        public=self.store.public_proposal()
        self.assertEqual(len(public['catalog']['linhas']),25)
        self.assertEqual(len(public['geojson']['features']),43)
        self.assertEqual(before['geojson']['features'],[f for f in public['geojson']['features'] if f['properties']['codigo']!='I-999'])
        active=self.store.overview()['release']
        self.store.restore_release({'expected_release':active['id'],'release_id':first['id']},self.user)
        self.assertEqual(len(self.store.public_proposal()['catalog']['linhas']),24)
        self.assertTrue(self.store.review(d['id'])['errors'])
        with self.assertRaises(Problem):self.store.restore_release({'expected_release':active['id'],'release_id':first['id']},self.user)

    def test_review_cannot_publish_old_geometry_or_duplicate_code(self):
        d=self.saved(self.new());review=self.store.review(d['id'])
        payload=copy.deepcopy(d['payload']);payload['features'][0]['geometry']['coordinates'].append([-34.902,-7.142])
        d=self.store.update(d['id'],{'revision':d['revision'],'payload':payload},self.user)
        with self.assertRaises(Problem) as e:self.store.publish(d['id'],{'revision':review['revision'],'release_id':review['release_id'],'version_id':review['version_id'],'acknowledge_warnings':True},self.user)
        self.assertEqual(e.exception.status,409)
        duplicate=self.saved(self.new('I-131'));self.assertTrue(any('código' in e for e in self.store.review(duplicate['id'])['errors']))

    def test_incomplete_geometry_and_unacknowledged_warnings_block_publication(self):
        d=self.new();payload=copy.deepcopy(d['payload']);payload['features'].pop()
        d=self.store.update(d['id'],{'revision':d['revision'],'payload':payload},self.user);d=self.saved(d)
        self.assertTrue(any('volta' in e for e in self.store.review(d['id'])['errors']))
        with self.assertRaises(Problem):self.publish(d)
        complete=self.saved(self.new('I-998'));r=self.store.review(complete['id'])
        with self.assertRaises(Problem):self.store.publish(complete['id'],{'revision':r['revision'],'release_id':r['release_id'],'version_id':r['version_id'],'acknowledge_warnings':False},self.user)

    def test_locked_sections_cannot_be_silently_replaced_and_invalid_coordinates_rejected(self):
        published=next(l for l in self.store.overview()['lines'] if l['code']=='I-131')
        d=self.store.create({'line_id':published['id'],'edit':True},self.user)
        payload=copy.deepcopy(d['payload']);payload['features'][0]['geometry']['coordinates'][3][0]+=.001
        with self.assertRaises(Problem):self.store.update(d['id'],{'revision':d['revision'],'payload':payload},self.user)
        bad=copy.deepcopy(d['payload']);bad['features'][0]['geometry']['coordinates']=[[float('nan'),-7],[0,0]]
        with self.assertRaises(Problem):normalize(bad)

    def test_duplicate_keeps_road_policy_and_accepts_explicit_new_identity(self):
        origin=next(l for l in self.store.overview()['lines'] if l['code']=='T-410')
        draft=self.store.create({'line_id':origin['id'],'code':'L-999','name':'Alternativa local','type':'local','kind':'bidirectional','points':['hub','metro']},self.user)
        line=draft['payload']['line']
        self.assertEqual(line['routing_policy'],'T-410')
        self.assertEqual(line['code'],'L-999')
        self.assertEqual(line['type'],'local')
        self.assertNotEqual(draft['line_id'],origin['id'])
        self.assertEqual(len(self.store.public_proposal()['catalog']['linhas']),24)

    def test_global_references_are_pinned_with_the_imported_seed(self):
        original=self.store.public_proposal()['catalog']['lugares']
        alternate=Path(self.temp.name)/'alternate-seed';alternate.mkdir()
        for name,value in self.store.base.items():
            copied=copy.deepcopy(value)
            if name=='catalogo.json':copied['lugares']['oitizeiro']['position']=[-34.95,-7.2]
            (alternate/name).write_text(json.dumps(copied))
        restarted=Store(self.temp.name,proposal_dir=alternate)
        self.assertEqual(restarted.public_proposal()['catalog']['lugares'],original)

    def test_restore_saved_version_is_only_a_draft_and_versions_are_immutable(self):
        d=self.saved(self.new());vid=d['saved_version'];before=self.store.version(vid)
        p=copy.deepcopy(d['payload']);p['line']['name']='Outro nome'
        d=self.store.update(d['id'],{'revision':d['revision'],'payload':p},self.user)
        restored=self.store.restore_version(d['id'],{'revision':d['revision'],'version_id':vid},self.user)
        self.assertEqual(restored['payload'],before['payload'])
        self.assertEqual(self.store.version(vid),before)
        self.assertEqual(len(self.store.public_proposal()['catalog']['linhas']),24)


class PreviewTests(unittest.TestCase):
    def test_failed_or_stale_routing_does_not_mutate_the_draft(self):
        router=Router('/missing')
        router.loading=True
        draft={'revision':3,'payload':{'line':{'code':'I-999'},'features':[]}}
        before=copy.deepcopy(draft)
        with self.assertRaises(Problem) as e:router.preview(draft,{'revision':2})
        self.assertEqual(e.exception.status,409)
        with self.assertRaises(Problem) as e:router.preview(draft,{'revision':3})
        self.assertEqual(e.exception.status,503)
        self.assertEqual(draft,before)


    def test_preview_uses_directed_roads_and_preserves_outside_selection(self):
        from apps.planner.revise import Network, distance
        n=Network.__new__(Network)
        n.positions={0:[-34.9,-7.14],1:[-34.901,-7.141],2:[-34.902,-7.142],3:[-34.902,-7.141],4:[-34.903,-7.143]}
        n.graph={0:[1],1:[2,3],3:[2],2:[4],4:[]}
        n.edges={(a,b):{'length':distance(n.positions[a],n.positions[b]),'name':'Rua '+str(a)+str(b),'way':a*10+b,'observed':set(),'street_count':0,'highway':'tertiary','ref':''} for a,bs in n.graph.items() for b in bs}
        n.snap=lambda p:min(n.positions,key=lambda k:distance(p,n.positions[k]))
        n.candidates=lambda p:{n.snap(p)}
        router=Router('/missing');router.network=n;router.fingerprint='test-network'
        coords=[n.positions[k] for k in [0,1,2,4]]
        feature={'properties':{'path_id':'path','locked_sections':[{'coordinates':coords[:2]}]},'geometry':{'type':'LineString','coordinates':coords}}
        draft={'revision':1,'payload':{'line':{'code':'I-999'},'features':[feature]}}
        result=router.preview(draft,{'revision':1,'path_id':'path','from':1,'to':3,'via':[n.positions[3]]})
        self.assertEqual(result['geometry']['coordinates'][:2],coords[:2])
        self.assertIn(n.positions[3],result['geometry']['coordinates'])
        self.assertEqual(result['geometry']['coordinates'][-1],coords[-1])
        self.assertEqual(draft['payload']['features'][0]['geometry']['coordinates'],coords)
        with self.assertRaises(Problem):router.create({'points':[n.positions[4],n.positions[0]]})
        feature['properties']['locked_sections']=[{'coordinates':coords[:3]}]
        with self.assertRaises(Problem):router.preview(draft,{'revision':1,'path_id':'path','from':1,'to':3,'via':[n.positions[3]]})


if __name__=='__main__':unittest.main()
