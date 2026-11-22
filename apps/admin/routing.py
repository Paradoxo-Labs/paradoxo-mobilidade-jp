"""Roteamento local; prévias não gravam rascunhos nem publicam geometrias."""
import hashlib
import json
from pathlib import Path
import threading

from apps.planner.revise import Network, distance, read
from .store import Problem, coordinates, contains_section, length_km


class Router:
    def __init__(self, data_dir):
        self.data_dir=Path(data_dir)
        self.network=None
        self.loading=False
        self.error=None
        self.fingerprint=None
        self.load_lock=threading.Lock()
        self.route_lock=threading.Lock()

    def status(self, start=False):
        if start and self.network is None and not self.loading:
            with self.load_lock:
                if self.network is None and not self.loading:
                    self.loading=True;self.error=None
                    threading.Thread(target=self.load,daemon=True).start()
        return {'ready':self.network is not None,'loading':self.loading,'error':self.error,'fingerprint':self.fingerprint}

    def load(self):
        try:
            osm=self.data_dir/'raw/cartografia/osm-revisao-rotas.json'
            semob=self.data_dir/'processed/semob/latest.json'
            if not osm.exists() or not semob.exists():
                raise ValueError('Malha OSM ou coleta SEMOB ausente. Consulte docs/ADMINISTRACAO.md para preparar os dados locais.')
            network=Network(read(osm),read(semob))
            self.fingerprint=hashlib.sha256(osm.read_bytes()+semob.read_bytes()).hexdigest()
            self.network=network
        except Exception as exc:
            self.error=str(exc)
        finally:self.loading=False

    def roads(self, bbox):
        try:
            values=[float(v) for v in bbox.split(',')]
            if len(values)!=4:raise ValueError()
            west,south,east,north=values
            if not (-35.1<west<east<-34.6 and -7.5<south<north<-6.9) or east-west>.25 or north-south>.25:raise ValueError()
        except (ValueError,AttributeError):raise Problem('Enquadramento de ruas inválido.')
        if not self.network:return {'type':'FeatureCollection','features':[]}
        n=self.network
        if not hasattr(n,'context_ways'):n.context_ways={e['way'] for e in n.edges.values()}
        features=[]
        for wid in sorted(n.context_ways):
            way=n.ways[wid];coords=[n.positions[p] for p in way['nodes'] if p in n.positions]
            if not any(west<=p[0]<=east and south<=p[1]<=north for p in coords):continue
            features.append({'type':'Feature','properties':{'name':way.get('tags',{}).get('name','Via sem nome cadastrado')},'geometry':{'type':'LineString','coordinates':coords}})
            if len(features)>=1800:break
        return {'type':'FeatureCollection','features':features}

    def preview(self, draft, body):
        if body.get('revision')!=draft['revision']:raise Problem('Salve e atualize o rascunho antes de calcular.',409)
        if not self.network:
            status=self.status(start=True)
            raise Problem(status['error'] or 'Preparando a malha viária local. Tente calcular novamente em instantes.',503)
        feature=next((f for f in draft['payload']['features'] if f['properties']['path_id']==body.get('path_id')),None)
        if not feature:raise Problem('Sentido não encontrado.',404)
        points=feature['geometry']['coordinates']
        a,b=body.get('from'),body.get('to')
        if any(isinstance(i,bool) or not isinstance(i,int) for i in [a,b]) or not 0<=a<b<len(points):
            raise Problem('Selecione o início e o fim do trecho no percurso.')
        via=coordinates({'type':'LineString','coordinates':body.get('via',[])})
        if len(via)>100 or (not via and body.get('direct') is not True):raise Problem('Adicione uma passagem ou escolha reconectar diretamente pelas ruas.')
        if any(not (-35.05<p[0]<-34.70 and -7.40<p[1]<-6.95) for p in via):raise Problem('A referência está fora da área de trabalho de João Pessoa.')
        code=draft['payload']['line'].get('routing_policy') or draft['payload']['line']['code']
        with self.route_lock:
            n=self.network
            references=[points[a]]+via+[points[b]]
            nodes=[n.snap(p) for p in references]
            gaps=[round(distance(p,n.positions[node]),1) for p,node in zip(references,nodes)]
            if max(gaps)>80:raise Problem('Uma referência está a mais de 80 m de uma via roteável. Aproxime o ponto da rua desejada.')
            joined=[]
            try:
                for i,(u,v) in enumerate(zip(nodes,nodes[1:])):
                    # Referências intermediárias aceitam as duas pistas próximas; o final é fixo.
                    goals=n.candidates(references[i+1]) if i<len(nodes)-2 else {v}
                    segment=n.route(u,v,code,goals)
                    nodes[i+1]=segment[-1]
                    joined.extend(segment if not joined else segment[1:])
            except ValueError as exc:raise Problem('Não há caminho viário dirigido para este trecho. O percurso anterior foi mantido.') from exc
            segment=[points[a]]+[n.positions[node] for node in joined]+[points[b]]
            replacement=points[:a]+segment+points[b+1:]
            if len(replacement)>30000:raise Problem('O resultado excede o limite de coordenadas.')
            for lock in feature['properties'].get('locked_sections',[]):
                if not contains_section(replacement,lock['coordinates']):raise Problem('O cálculo alteraria um trecho preservado. Escolha outro intervalo ou desbloqueie o trecho.',409)
            streets=[]
            for u,v in zip(joined,joined[1:]):
                name=n.edges[u,v]['name']
                if not streets or streets[-1]!=name:streets.append(name)
        return {'geometry':{'type':'LineString','coordinates':replacement},'segment':segment,'old_km':round(length_km(points[a:b+1]),3),'new_km':round(length_km(segment),3),'distance_km':round(length_km(replacement),2),'streets':streets,'snap_offsets_m':gaps,'router_fingerprint':self.fingerprint,'from':a,'to':b,'revision':draft['revision'],'path_id':body['path_id'],'warnings':['Mãos únicas e acesso OSM considerados; relações de conversão, sinalização e gabarito de ônibus ainda exigem validação.']}

    def create(self, body, draft=None):
        if not self.network:raise Problem('Aguarde a preparação da malha viária local.',503)
        policy=None;feature=None
        if draft:
            if body.get('revision')!=draft['revision']:raise Problem('O rascunho mudou. Salve antes de calcular.',409)
            feature=next((f for f in draft['payload']['features'] if f['properties']['path_id']==body.get('path_id')),None)
            if not feature:raise Problem('Sentido não encontrado.',404)
            policy=draft['payload']['line'].get('routing_policy') or draft['payload']['line']['code']
        refs=coordinates({'type':'LineString','coordinates':body.get('points')})
        if not 2<=len(refs)<=100:raise Problem('Informe de 2 a 100 pontos para criar o percurso.')
        if any(not (-35.05<p[0]<-34.70 and -7.40<p[1]<-6.95) for p in refs):raise Problem('Referências fora da área de trabalho.')
        with self.route_lock:
            n=self.network;node=n.snap(refs[0]);joined=[node]
            if distance(refs[0],n.positions[node])>80:raise Problem('Origem distante de uma via roteável.')
            for p in refs[1:]:
                end=n.snap(p)
                if distance(p,n.positions[end])>80:raise Problem('Referência distante de uma via roteável.')
                try:segment=n.route(node,end,policy)
                except ValueError as exc:raise Problem('Não há caminho viário dirigido entre os pontos.') from exc
                joined.extend(segment[1:]);node=end
            coords=[n.positions[node] for node in joined]
            if len(coords)<2 or length_km(coords)<.01:raise Problem('As referências produziram um percurso vazio. Em circuitos, inclua passagens intermediárias.')
            streets=[]
            for u,v in zip(joined,joined[1:]):
                name=n.edges[u,v]['name']
                if not streets or streets[-1]!=name:streets.append(name)
            if feature:
                for lock in feature['properties'].get('locked_sections',[]):
                    if not contains_section(coords,lock['coordinates']):raise Problem('O novo percurso substituiria um trecho preservado. Desbloqueie-o explicitamente para recalcular o sentido inteiro.',409)
        return {'revision':draft['revision'] if draft else None,'geometry':{'type':'LineString','coordinates':coords},'streets':streets,'distance_km':round(length_km(coords),2),'router_fingerprint':self.fingerprint}

    def trim(self, draft, body):
        if body.get('revision') != draft['revision']:
            raise Problem('O rascunho mudou. Salve antes de cortar.', 409)
        feature = next((f for f in draft['payload']['features'] if f['properties']['path_id'] == body.get('path_id')), None)
        if not feature:raise Problem('Percurso não encontrado.', 404)
        points = feature['geometry']['coordinates']
        index = body.get('index')
        if isinstance(index, bool) or not isinstance(index, int) or not 0 <= index < len(points):
            raise Problem('Selecione um vértice válido para o corte.')
        if body.get('side') not in {'before','after'}:raise Problem('Tipo de corte inválido.')
        replacement = points[index:] if body['side'] == 'before' else points[:index+1]
        if len(replacement) < 2 or length_km(replacement) < .01:
            raise Problem('O corte deixaria um percurso vazio ou curto demais.')
        for lock in feature['properties'].get('locked_sections', []):
            if not contains_section(replacement, lock['coordinates']):
                raise Problem('O corte removeria um trecho preservado. Desbloqueie-o primeiro.', 409)
        return {'geometry': {'type':'LineString','coordinates': replacement},
                'old_km': round(length_km(points),3), 'new_km': round(length_km(replacement),3),
                'distance_km': round(length_km(replacement),2), 'streets': [], 'trimmed': True,
                'revision': draft['revision'], 'path_id': body['path_id']}
