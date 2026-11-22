import copy
from collections import defaultdict
from types import SimpleNamespace
import threading
import unittest
from apps.admin.dragging import preview_drag, streets_for_drag
from apps.admin.store import Problem, contains_section
from apps.planner.revise import Network, distance


class DragTests(unittest.TestCase):
    def setUp(self):
        n=Network.__new__(Network)
        n.positions={y*8+x:[-34.91+x*.0005,-7.15+y*.0005] for y in range(8) for x in range(8)}
        n.graph=defaultdict(list);n.edges={};n.edge_grid=defaultdict(set)
        for y in range(8):
            for x in range(8):
                u=y*8+x
                for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                    if not (0<=x+dx<8 and 0<=y+dy<8):continue
                    v=(y+dy)*8+x+dx
                    n.graph[u].append(v);n.edges[u,v]={'name':f'Rua {u}-{v}','length':distance(n.positions[u],n.positions[v]),'observed':set(),'street_count':0,'ref':'','highway':'residential'}
                    ca,cb=n.cell(n.positions[u]),n.cell(n.positions[v])
                    for cx in range(min(ca[0],cb[0]),max(ca[0],cb[0])+1):
                        for cy in range(min(ca[1],cb[1]),max(ca[1],cb[1])+1):n.edge_grid[cx,cy].add((u,v))
        n.snap=lambda p:min(n.positions,key=lambda i:distance(p,n.positions[i]))
        self.n=n;self.router=SimpleNamespace(network=n,fingerprint='grid',route_lock=threading.Lock())
        # Circuito: vinte segmentos, com o ponto inicial repetido apenas no fechamento.
        nodes=[8+x for x in range(1,7)]+[y*8+6 for y in range(2,7)]+[48+x for x in range(5,0,-1)]+[y*8+1 for y in range(5,0,-1)]
        self.points=[n.positions[i] for i in nodes]
        self.draft={'revision':3,'payload':{'line':{'code':'L-999','kind':'circular'},'features':[{'properties':{'path_id':'path','locked_sections':[]},'geometry':{'type':'LineString','coordinates':self.points}}]}}
        u,v=19,20
        self.body={'revision':3,'path_id':'path','segment_index':0,'fraction':.4,'drop_position':[(n.positions[u][0]+n.positions[v][0])/2,n.positions[u][1]],'edge':[u,v],'span_m':100}

    def test_closed_circuit_can_edit_across_start_without_reversing_rest(self):
        before=copy.deepcopy(self.draft)
        r=preview_drag(self.router,self.draft,self.body)
        self.assertTrue(r['wrapped'])
        cs=r['geometry']['coordinates']
        self.assertEqual(cs[0],cs[-1])
        self.assertIn(r['drag_target'],r['segment'])
        outside=self.points[r['to']+1:r['from']+1]
        self.assertTrue(contains_section(cs,outside))
        self.assertEqual(cs[0],self.points[0])
        self.assertEqual(self.draft,before)

    def test_occurrence_of_same_street_uses_path_order_instead_of_first_coordinate(self):
        self.draft['payload']['features'][0]['geometry']['coordinates']=self.points[:-1]+self.points
        first=preview_drag(self.router,self.draft,self.body)
        second=preview_drag(self.router,self.draft,{**self.body,'segment_index':len(self.points)-1})
        self.assertTrue(first['wrapped'])
        self.assertFalse(second['wrapped'])
        self.assertNotEqual((first['from'],first['to']),(second['from'],second['to']))

    def test_drop_in_empty_ground_nonexistent_or_forbidden_street_is_rejected(self):
        with self.assertRaises(Problem):preview_drag(self.router,self.draft,{**self.body,'drop_position':[self.body['drop_position'][0],self.body['drop_position'][1]+.001]})
        with self.assertRaises(Problem):preview_drag(self.router,self.draft,{**self.body,'edge':[0,63]})
        self.draft['payload']['line']['routing_policy']='T-610'
        self.n.edges[19,20]['name']='BR-230';self.n.edges[19,20]['ref']='BR-230'
        with self.assertRaises(Problem):preview_drag(self.router,self.draft,self.body)

    def test_long_road_segment_is_used_at_projection_not_nearest_junction(self):
        u,v=17,22
        self.n.graph[u].append(v);self.n.edges[u,v]={'name':'Rua longa','length':distance(self.n.positions[u],self.n.positions[v]),'observed':set(),'street_count':0,'ref':'','highway':'residential'}
        self.n.graph[v].append(u);self.n.edges[v,u]=self.n.edges[u,v]
        p=[(self.n.positions[u][0]+self.n.positions[v][0])/2,self.n.positions[u][1]]
        r=preview_drag(self.router,self.draft,{**self.body,'edge':[u,v],'drop_position':p})
        self.assertIn(p,r['geometry']['coordinates'])
        self.assertEqual(r['drag_target'],p)
        self.assertNotIn(p,[self.n.positions[u],self.n.positions[v]])

    def test_one_way_selected_edge_is_traversed_in_legal_direction(self):
        self.n.graph[20].remove(19);del self.n.edges[20,19]
        r=preview_drag(self.router,self.draft,self.body)
        cs=r['segment'];i=cs.index(r['drag_target'])
        self.assertEqual(cs[i-1],self.n.positions[19])
        self.assertEqual(cs[i+1],self.n.positions[20])

    def test_open_path_keeps_both_endpoints_and_locked_sections_are_not_overwritten(self):
        self.draft['payload']['features'][0]['geometry']['coordinates']=self.points[:-1]
        r=preview_drag(self.router,self.draft,self.body)
        self.assertEqual(r['geometry']['coordinates'][0],self.points[0])
        self.assertEqual(r['geometry']['coordinates'][-1],self.points[-2])
        self.draft['payload']['features'][0]['properties']['locked_sections']=[{'coordinates':self.points[:4]}]
        with self.assertRaises(Problem) as e:preview_drag(self.router,self.draft,self.body)
        self.assertEqual(e.exception.status,409)
        with self.assertRaises(Problem) as e:preview_drag(self.router,self.draft,{**self.body,'revision':1})
        self.assertEqual(e.exception.status,409)

    def test_source_on_preserved_circuit_is_rejected_even_if_a_detour_could_keep_original_loop(self):
        self.draft['payload']['features'][0]['properties']['locked_sections']=[{'coordinates':self.points}]
        with self.assertRaises(Problem) as error:preview_drag(self.router,self.draft,self.body)
        self.assertEqual(error.exception.status,409)
        self.assertIn('começa',str(error.exception))

    def test_streets_for_drag_only_expose_existing_allowed_edges_and_deduplicate(self):
        r=streets_for_drag(self.router,self.draft,'path','-34.911,-7.151,-34.905,-7.145')
        keys=[tuple(sorted(f['properties']['edge'])) for f in r['features']]
        self.assertEqual(len(keys),len(set(keys)))
        for f in r['features']:self.assertIn(tuple(f['properties']['edge']),self.n.edges)
