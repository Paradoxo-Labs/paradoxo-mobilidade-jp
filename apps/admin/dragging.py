"""Arraste direto: escolha uma ocorrência do percurso e uma aresta viária real."""
from bisect import bisect_left, bisect_right
import math
from apps.planner import policies
from apps.planner.revise import distance
from .store import Problem, coordinates, contains_section, length_km


def project(point, a, b):
    dx, dy = (b[0]-a[0])*110440, (b[1]-a[1])*110580
    px, py = (point[0]-a[0])*110440, (point[1]-a[1])*110580
    t = max(0, min(1, (px*dx+py*dy)/(dx*dx+dy*dy))) if dx*dx+dy*dy else 0
    return [a[0]+t*(b[0]-a[0]), a[1]+t*(b[1]-a[1])]


def allowed(n, edge, code):
    a,b = edge
    midpoint = [(n.positions[a][i]+n.positions[b][i])/2 for i in (0,1)]
    return edge in n.edges and not policies.forbidden(code, n.edges[edge], midpoint)


def path_feature(draft, path_id):
    feature = next((f for f in draft['payload']['features'] if f['properties']['path_id']==path_id), None)
    if not feature:raise Problem('Percurso não encontrado.',404)
    return feature


def streets_for_drag(router, draft, path_id, bbox):
    path_feature(draft,path_id)
    if not router.network:return {'type':'FeatureCollection','features':[],'ready':False}
    try:
        west,south,east,north = [float(v) for v in bbox.split(',')]
        if not (-35.1<west<east<-34.6 and -7.5<south<north<-6.9) or east-west>.16 or north-south>.16:raise ValueError()
    except (ValueError,TypeError):raise Problem('Aproxime o mapa para carregar as ruas do arraste.')
    n=router.network
    code=draft['payload']['line'].get('routing_policy') or draft['payload']['line']['code']
    lo,hi=n.cell([west,south]),n.cell([east,north])
    keys=set()
    for x in range(lo[0],hi[0]+1):
        for y in range(lo[1],hi[1]+1):keys.update(n.edge_grid.get((x,y),()))
    features=[]
    seen=set()
    for key in sorted(keys):
        if key not in n.edges:continue
        a,b=[n.positions[node] for node in key]
        if max(a[0],b[0])<west or min(a[0],b[0])>east or max(a[1],b[1])<south or min(a[1],b[1])>north:continue
        if not allowed(n,key,code):continue
        canonical=tuple(sorted(key))
        if canonical in seen:continue
        seen.add(canonical)
        features.append({'type':'Feature','geometry':{'type':'LineString','coordinates':[a,b]},
                         'properties':{'edge':list(key),'name':n.edges[key]['name']}})
        if len(features)>=20000:break
    return {'type':'FeatureCollection','features':features,'ready':True,'truncated':len(features)>=20000,'fingerprint':router.fingerprint}


def anchors(points, index, fraction, reach):
    accumulated=[0]
    for a,b in zip(points,points[1:]):accumulated.append(accumulated[-1]+distance(a,b))
    source=accumulated[index]+fraction*(accumulated[index+1]-accumulated[index])
    closed=points[0]==points[-1] and len(points)>3
    if closed:
        reach=min(reach,accumulated[-1]*.2)
        a=bisect_right(accumulated,(source-reach)%accumulated[-1])-1
        b=bisect_left(accumulated,(source+reach)%accumulated[-1])%(len(points)-1)
        if a==b:a,b=index,(index+1)%(len(points)-1)
    else:
        a=max(0,bisect_right(accumulated,max(0,source-reach))-1)
        b=min(len(points)-1,bisect_left(accumulated,min(accumulated[-1],source+reach)))
    return a,b,closed and a>b


def preview_drag(router, draft, body):
    if body.get('revision')!=draft['revision']:raise Problem('O rascunho mudou. Atualize antes de arrastar.',409)
    if not router.network:raise Problem('Aguarde o carregamento da malha de ruas.',503)
    f=path_feature(draft,body.get('path_id'));points=f['geometry']['coordinates']
    index,fraction=body.get('segment_index'),body.get('fraction')
    if isinstance(index,bool) or not isinstance(index,int) or not 0<=index<len(points)-1:raise Problem('Trecho de origem inválido.')
    if isinstance(fraction,bool) or not isinstance(fraction,(int,float)) or not math.isfinite(fraction) or not 0<=fraction<=1:raise Problem('Posição de origem inválida.')
    if distance(points[index],points[index+1])<.01:raise Problem('Arraste um trecho contínuo da linha.')
    for lock in f['properties'].get('locked_sections',[]):
        section=lock['coordinates']
        for start in range(max(0,index-len(section)+2),index+1):
            if points[start]==section[0] and points[start:start+len(section)]==section:
                raise Problem('Este arraste começa em um trecho preservado. Desbloqueie-o nas ferramentas avançadas.',409)
    raw=coordinates({'type':'LineString','coordinates':[body.get('drop_position')]})[0]
    if not (-35.05<raw[0]<-34.7 and -7.4<raw[1]<-6.95):raise Problem('Destino fora da área de edição.')
    edge=body.get('edge')
    if not isinstance(edge,list) or len(edge)!=2 or any(isinstance(v,bool) or not isinstance(v,int) for v in edge):raise Problem('Solte sobre uma rua disponível.')
    n=router.network;edge=tuple(edge)
    code=draft['payload']['line'].get('routing_policy') or draft['payload']['line']['code']
    if edge not in n.edges or not allowed(n,edge,code):raise Problem('Esta rua não está disponível para este percurso.')
    target=project(raw,n.positions[edge[0]],n.positions[edge[1]])
    if distance(raw,target)>22:raise Problem('Solte sobre uma rua. O ponto está longe da malha viária.')
    source=[points[index][i]+fraction*(points[index+1][i]-points[index][i]) for i in (0,1)]
    gap=distance(source,target)
    if gap>2500:raise Problem('Arraste um trecho por vez, a menos de 2,5 km da posição original.')
    reach=body.get('span_m',350)
    if isinstance(reach,bool) or not isinstance(reach,(int,float)) or not math.isfinite(reach) or not 100<=reach<=1200:raise Problem('Alcance de edição inválido.')
    a,b,wrapped=anchors(points,index,fraction,max(reach,min(1500,gap*1.5)))
    with router.route_lock:
        try:start,end=n.snap(points[a]),n.snap(points[b])
        except ValueError as exc:raise Problem('Não foi possível conectar o trecho à malha. O percurso foi mantido.') from exc
        if max(distance(points[a],n.positions[start]),distance(points[b],n.positions[end]))>80:raise Problem('As conexões do trecho estão distantes das ruas. O percurso foi mantido.')
        candidates=[]
        for u,v in [edge,edge[::-1]]:
            if (u,v) not in n.edges or not allowed(n,(u,v),code):continue
            try:
                origin=n.snap(points[0]) if wrapped else None
                if wrapped and index<a:
                    before=n.route(start,origin,code)+n.route(origin,u,code)[1:]
                    after=n.route(v,end,code)
                elif wrapped:
                    before=n.route(start,u,code)
                    after=n.route(v,origin,code)+n.route(origin,end,code)[1:]
                else:
                    before=n.route(start,u,code);after=n.route(v,end,code)
            except ValueError:continue
            nodes=before+[v]+after[1:]
            before_positions=[n.positions[node] for node in before]
            after_positions=[n.positions[node] for node in after]
            if wrapped:
                positions=before_positions if index<a else after_positions
                nodes_with_origin=before if index<a else after
                positions[nodes_with_origin.index(origin)]=points[0]
            geometry=[points[a]]+before_positions+[target]+after_positions+[points[b]]
            cost=length_km(geometry)
            candidates.append((cost,geometry,nodes))
        if not candidates:raise Problem('Não há ligação dirigida por essa rua. O percurso anterior foi mantido.')
        _,segment,nodes=min(candidates,key=lambda item:item[0])
        compact=[]
        for point in segment:
            if not compact or compact[-1]!=point:compact.append(point)
        segment=compact
        previous=points[a:-1]+points[:b+1] if wrapped else points[a:b+1]
        replacement=segment+points[b+1:a+1] if wrapped else points[:a]+segment+points[b+1:]
        if wrapped:
            # O terminal/início do circuito continua fixo; muda apenas a vizinhança do arraste.
            core=replacement[:-1]
            pivot=core.index(points[0])
            replacement=core[pivot:]+core[:pivot]+[points[0]]
        if len(replacement)>30000:raise Problem('O percurso excederia o limite de coordenadas.')
        for lock in f['properties'].get('locked_sections',[]):
            if not contains_section(replacement,lock['coordinates']):raise Problem('Este arraste alteraria um trecho preservado. Desbloqueie-o nas ferramentas avançadas.',409)
        streets=[]
        for u,v in zip(nodes,nodes[1:]):
            name=n.edges[u,v]['name']
            if not streets or streets[-1]!=name:streets.append(name)
    return {'geometry':{'type':'LineString','coordinates':replacement},'segment':segment,'from':a,'to':b,'wrapped':wrapped,
            'old_km':round(length_km(previous),3),'new_km':round(length_km(segment),3),'distance_km':round(length_km(replacement),2),
            'streets':streets,'revision':draft['revision'],'path_id':body['path_id'],'router_fingerprint':router.fingerprint,
            'drag_source':source,'drag_target':target,'drag_street':n.edges[edge]['name']}
