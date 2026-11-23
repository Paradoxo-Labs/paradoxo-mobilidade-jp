"""Estado administrativo transacional, separado dos insumos imutáveis do estudo."""
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import hmac
import json
import math
import os
from pathlib import Path
import re
import secrets
import sqlite3
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]
PROPOSAL = ROOT / 'docs/proposta-brs-bhls/revisao-atual'
CLASSES = {'brs', 'troncal', 'transversal', 'integracional', 'regional', 'local', 'metropolitana'}
CODE = re.compile(r'^[A-Z][A-Z0-9]{0,7}-[0-9]{1,5}$')


def now():
    return datetime.now(timezone.utc).isoformat()


def encode(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':'), sort_keys=True)


def digest(value):
    return hashlib.sha256(encode(value).encode()).hexdigest()


def uid():
    return str(uuid.uuid4())


class Problem(Exception):
    def __init__(self, message, status=400, **details):
        super().__init__(message)
        self.status, self.details = status, details


def coordinates(geometry):
    if not isinstance(geometry, dict) or geometry.get('type') != 'LineString':
        raise Problem('Use uma geometria LineString para cada percurso.')
    points = geometry.get('coordinates')
    if not isinstance(points, list) or len(points) > 30000:
        raise Problem('Quantidade de coordenadas inválida (máximo 30.000 por percurso).')
    for point in points:
        if not isinstance(point, list) or len(point) != 2 or any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in point):
            raise Problem('Coordenadas devem ser pares finitos [longitude, latitude].')
        if not (-180 <= point[0] <= 180 and -90 <= point[1] <= 90):
            raise Problem('Coordenada fora dos limites geográficos.')
    return points


def length_km(points):
    return sum(math.hypot((b[0]-a[0])*110440, (b[1]-a[1])*110580) for a,b in zip(points,points[1:]))/1000


def contains_section(points, section):
    return bool(section) and any(points[i:i+len(section)] == section for i in range(len(points)-len(section)+1))


def normalize(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get('line'), dict) or not isinstance(payload.get('features'), list):
        raise Problem('Rascunho deve conter linha e percursos.')
    result = deepcopy(payload)
    line = result['line']
    for key in ['code', 'name', 'type', 'itinerary', 'note']:
        value = line.get(key, '')
        if not isinstance(value, str) or len(value) > (10000 if key in {'itinerary', 'note'} else 300):
            raise Problem('Campo de identificação inválido: '+key)
        line[key] = value.strip()
    line['code'] = line['code'].upper()
    kind = line.get('kind', 'bidirectional')
    if kind not in {'bidirectional', 'circular', 'oneway'}:
        raise Problem('Organização da linha inválida.')
    if len(result['features']) > 12:
        raise Problem('Limite de 12 sentidos/variantes por linha.')
    line['kind'] = kind
    if not isinstance(line.get('points', []), list) or any(not isinstance(p, str) for p in line.get('points', [])):
        raise Problem('Referências territoriais inválidas.')
    line['points'] = line.get('points', [])
    entries, used, path_ids = [], set(), set()
    for f in result['features']:
        if not isinstance(f,dict) or not isinstance(f.get('properties',{}),dict):raise Problem('Percurso ou propriedades inválidos.')
        points = coordinates(f.get('geometry'))
        p = f.setdefault('properties', {})
        direction = p.get('sentido', '')
        if not isinstance(direction, str) or not re.fullmatch(r'[a-z0-9-]{1,40}', direction) or direction in used:
            raise Problem('Cada sentido/variante deve ter uma chave única.')
        used.add(direction)
        path_id = p.get('path_id') or uid()
        if not isinstance(path_id,str) or not re.fullmatch(r'[a-f0-9-]{36}',path_id) or path_id in path_ids:raise Problem('Identificador de percurso inválido ou duplicado.')
        path_ids.add(path_id)
        if not isinstance(p.get('label',direction),str) or len(p.get('label',direction))>160:raise Problem('Nome de sentido/variante inválido (máximo 160 caracteres).')
        locks = p.get('locked_sections', [])
        if not isinstance(locks, list) or len(locks) > 50:
            raise Problem('Trechos preservados inválidos.')
        for lock in locks:
            coords = coordinates({'type':'LineString', 'coordinates':lock.get('coordinates')})
            if len(coords) < 2 or not contains_section(points, coords):
                raise Problem('Um trecho preservado foi modificado. Desbloqueie-o explicitamente antes de editar.', 409)
        key = line['code'] + ('' if direction == 'ida' else '-'+direction)
        p.update(codigo=line['code'], nome=line['name'], classe=line['type'], chave=key, path_id=path_id, distancia_km=round(length_km(points),2))
        f.update(type='Feature', id=key)
        p.setdefault('locked_sections', [])
        p.setdefault('reference_lines', [])
        stations = p.setdefault('station_ids', [])
        if not isinstance(stations, list) or len(stations) > 200 or any(not isinstance(v, str) or len(v) > 80 for v in stations) or len(set(stations)) != len(stations):
            raise Problem('Estações do percurso inválidas ou duplicadas.')
        if 'control_points' not in p:
            legacy = p.get('editor_controls', [])
            if not isinstance(legacy,list) or len(legacy)>100:raise Problem('Referências legadas inválidas.')
            coordinates({'type':'LineString','coordinates':legacy})
            p['control_points'] = [{'id':uid(),'label':'Referência '+str(i+1),'position':c} for i,c in enumerate(legacy)]
        controls = p['control_points']
        if not isinstance(controls, list) or len(controls) > 100:
            raise Problem('Limite de 100 referências permanentes por percurso.')
        control_ids = set()
        for control in controls:
            if not isinstance(control, dict):raise Problem('Referência permanente inválida.')
            cid = control.get('id')
            if not isinstance(cid, str) or not re.fullmatch(r'[a-f0-9-]{36}',cid) or cid in control_ids:raise Problem('Identificador de referência permanente inválido.')
            control_ids.add(cid)
            if not isinstance(control.get('label'), str) or not control['label'].strip() or len(control['label']) > 160:raise Problem('Nome da referência permanente inválido.')
            coordinates({'type':'LineString','coordinates':[control.get('position')]})
            if control.get('station_id') is not None and (not isinstance(control['station_id'], str) or len(control['station_id']) > 80):raise Problem('Estação da referência inválida.')
        entries.append({'chave':key,'sentido':direction,'label':p.get('label',direction.capitalize()),'distancia_km':p['distancia_km'],'waypoints':p.get('waypoints',[]),'street_sequence':p.get('street_sequence',[]),'reference_lines':p['reference_lines'],'central_pattern':p.get('central_pattern'),'source':p.get('source','edicao-administrativa'),'station_ids':p.get('station_ids',[]),'control_points':p.get('control_points',[])})
        if p.get('observed_streets_percent') is not None:
            entries[-1]['observed_streets_percent'] = p['observed_streets_percent']
    line['sentidos'] = entries
    return result


def validation(payload):
    line = payload['line']
    errors = []
    if not CODE.fullmatch(line['code']):
        errors.append('Informe um código como I-132, BRS-100 ou T-410.')
    if not line['name']:
        errors.append('Informe o nome da linha.')
    if line['type'] not in CLASSES:
        errors.append('Escolha uma classe válida.')
    directions = {f['properties']['sentido'] for f in payload['features']}
    required = {'ida','volta'} if line['kind']=='bidirectional' else {'circuito'} if line['kind']=='circular' else {'ida'}
    if line['kind']=='oneway' and 'volta' in directions:
        errors.append('A linha está unidirecional, mas possui volta. Remova a volta ou escolha bidirecional.')
    if not required <= directions:
        errors.append('Conclua os sentidos obrigatórios: '+', '.join(sorted(required-directions))+'.')
    for f in payload['features']:
        points = f['geometry']['coordinates']
        if any(length_km([a,b])>1 for a,b in zip(points,points[1:])):
            errors.append(f"O percurso {f['properties']['sentido']} tem um salto superior a 1 km entre vértices. Revise sua continuidade.")
        if len(points)<2 or length_km(points)<.01:
            errors.append(f"O percurso {f['properties']['sentido']} está vazio ou não tem extensão suficiente.")
    warnings = ['Conversões, sinalização, gabarito, frota e frequência exigem validação operacional.']
    if 'oitizeiro' in line['points']:
        warnings.append('Entrada e plataformas de Oitizeiro dependem da planta; o traçado termina na conexão viária aproximada.')
    if any(f['properties'].get('manual') for f in payload['features']):
        warnings.append('Há desenho manual; sua circulação viária ainda não foi confirmada.')
    return {'errors':errors,'warnings':warnings}


from .management import Management


class Store(Management):
    def __init__(self, data_dir, proposal_dir=PROPOSAL):
        self.directory = Path(data_dir)/'admin'
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.path = self.directory/'admin.sqlite3'
        self.proposal_dir = Path(proposal_dir)
        self.base = {name:json.loads((self.proposal_dir/name).read_text()) for name in ['catalogo.json','linhas-por-sentido.geojson','waypoints-roteamento.json','comparativos-i332.json','auditoria.json']}
        with self.db() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS account(username TEXT PRIMARY KEY, salt TEXT NOT NULL, password TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY, username TEXT NOT NULL, csrf TEXT NOT NULL, expires REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS drafts(id TEXT PRIMARY KEY,line_id TEXT UNIQUE,base_version TEXT,payload TEXT NOT NULL,revision INTEGER NOT NULL,updated TEXT NOT NULL,saved_version TEXT);
            CREATE TABLE IF NOT EXISTS versions(id TEXT PRIMARY KEY,line_id TEXT NOT NULL,number INTEGER NOT NULL,payload TEXT NOT NULL,digest TEXT NOT NULL,created TEXT NOT NULL,note TEXT NOT NULL,UNIQUE(line_id,number));
            CREATE TABLE IF NOT EXISTS releases(id TEXT PRIMARY KEY,number INTEGER UNIQUE,items TEXT NOT NULL,created TEXT NOT NULL,note TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY,created TEXT NOT NULL,username TEXT NOT NULL,action TEXT NOT NULL,entity TEXT NOT NULL,detail TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS attempts(id INTEGER PRIMARY KEY,created REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY,state TEXT NOT NULL,detail TEXT NOT NULL,created TEXT NOT NULL,updated TEXT NOT NULL);
            ''')
            assets=db.execute("SELECT value FROM meta WHERE key='base_assets'").fetchone()
            if assets:self.base=json.loads(assets[0])
            else:db.execute('INSERT INTO meta VALUES(?,?)',('base_assets',encode(self.base)))
            db.execute("UPDATE jobs SET state='interrupted',updated=? WHERE state='running'",(now(),))
            if not db.execute("SELECT 1 FROM meta WHERE key='active_release'").fetchone():
                self.seed(db)
            self.migrate_management(db)
        os.chmod(self.path, 0o600)
        token = self.directory/'setup-token'
        if not self.configured() and not token.exists():
            fd=os.open(token, os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
            with os.fdopen(fd,'w') as f: f.write(secrets.token_urlsafe(24))

    @contextmanager
    def db(self, write=False):
        db = sqlite3.connect(self.path, timeout=15)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        db.execute('PRAGMA journal_mode=WAL')
        try:
            db.execute('BEGIN IMMEDIATE' if write else 'BEGIN')
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def audit(self, db, user, action, entity, detail=''):
        db.execute('INSERT INTO audit(created,username,action,entity,detail) VALUES(?,?,?,?,?)',(now(),user,action,entity,detail))

    def seed(self, db):
        audit = {r['key']:r for r in self.base['auditoria.json']['routes']}
        items = {}
        for line in self.base['catalogo.json']['linhas']:
            payload = {'line':deepcopy(line),'features':[deepcopy(f) for f in self.base['linhas-por-sentido.geojson']['features'] if f['properties']['codigo']==line['code']]}
            line_id = str(uuid.uuid5(uuid.NAMESPACE_URL,'paradoxo-mobilidade:'+line['code']))
            payload['line']['routing_policy'] = line['code']
            payload['line']['kind'] = 'circular' if {e['sentido'] for e in line['sentidos']}=={'circuito'} else 'bidirectional'
            entries = {e['chave']:e for e in line['sentidos']}
            for f in payload['features']:
                p=f['properties']; entry=entries[p['chave']]
                p.update(path_id=uid(), street_sequence=entry.get('street_sequence',[]),reference_lines=entry.get('reference_lines',[]),central_pattern=entry.get('central_pattern'),source=entry.get('source','estudo-importado'))
                p['locked_sections']=[{'id':uid(),'label':'SEMOB '+s['line']+' / '+s['direction'],'coordinates':s['coordinates']} for s in audit[p['chave']].get('observed_sections',[])]
            payload=normalize(payload)
            vid=uid();items[line_id]=vid
            db.execute('INSERT INTO versions VALUES(?,?,?,?,?,?,?)',(vid,line_id,1,encode(payload),digest(payload),now(),'Importação inicial da proposta versionada no Git'))
        rid=uid()
        db.execute('INSERT INTO releases VALUES(?,?,?,?,?)',(rid,1,encode(items),now(),'Proposta inicial preservada'))
        db.execute('INSERT INTO meta VALUES(?,?)',('active_release',rid))

    def configured(self):
        with self.db() as db:return bool(db.execute('SELECT 1 FROM account').fetchone())

    def credentials(self, password, salt):
        return hashlib.scrypt(password.encode(),salt=bytes.fromhex(salt),n=16384,r=8,p=1).hex()

    def attempt(self):
        with self.db(write=True) as db:
            db.execute('DELETE FROM attempts WHERE created<?',(time.time()-600,))
            if db.execute('SELECT COUNT(*) FROM attempts').fetchone()[0]>=12:
                raise Problem('Muitas tentativas. Aguarde dez minutos.',429)
            db.execute('INSERT INTO attempts(created) VALUES(?)',(time.time(),))

    def setup(self, token, username, password):
        self.attempt()
        if not isinstance(username,str) or not re.fullmatch(r'[a-zA-Z0-9_.-]{3,50}',username):
            raise Problem('Use de 3 a 50 letras, números, ponto, hífen ou sublinhado no usuário.')
        if not isinstance(password,str) or not 12<=len(password)<=200:
            raise Problem('A senha deve ter entre 12 e 200 caracteres.')
        path=self.directory/'setup-token'
        if not isinstance(token,str) or not path.exists() or not hmac.compare_digest(path.read_text().strip(),token):
            raise Problem('Código de primeiro acesso inválido.',403)
        salt=secrets.token_hex(16);hashed=self.credentials(password,salt)
        with self.db(write=True) as db:
            if db.execute('SELECT 1 FROM account').fetchone():raise Problem('O administrador já foi cadastrado.',409)
            db.execute('INSERT INTO account VALUES(?,?,?)',(username,salt,hashed))
            db.execute('DELETE FROM attempts')
            self.audit(db,username,'setup','administrator')
        path.unlink(missing_ok=True)
        return self.new_session(username)

    def login(self, username, password):
        self.attempt()
        if not isinstance(username,str) or not isinstance(password,str) or len(password)>200:raise Problem('Usuário ou senha incorretos.',401)
        with self.db() as db:row=db.execute('SELECT * FROM account WHERE username=?',(username,)).fetchone()
        salt=row['salt'] if row else '00'*16
        hashed=self.credentials(password,salt)
        if not row or not hmac.compare_digest(hashed,row['password']):raise Problem('Usuário ou senha incorretos.',401)
        with self.db(write=True) as db:
            db.execute('DELETE FROM attempts')
            self.audit(db,username,'login','administrator')
        return self.new_session(username)

    def new_session(self, username):
        token=secrets.token_urlsafe(32);csrf=secrets.token_urlsafe(24)
        with self.db(write=True) as db:
            db.execute('DELETE FROM sessions WHERE expires<?',(time.time(),))
            db.execute('INSERT INTO sessions VALUES(?,?,?,?)',(hashlib.sha256(token.encode()).hexdigest(),username,csrf,time.time()+8*3600))
        return {'token':token,'csrf':csrf,'username':username}

    def session(self, token):
        if not token:return None
        with self.db() as db:
            row=db.execute('SELECT username,csrf FROM sessions WHERE token=? AND expires>?',(hashlib.sha256(token.encode()).hexdigest(),time.time())).fetchone()
        return dict(row) if row else None

    def logout(self, token):
        with self.db(write=True) as db:db.execute('DELETE FROM sessions WHERE token=?',(hashlib.sha256(token.encode()).hexdigest(),))

    def active(self, db):
        return db.execute("SELECT * FROM releases WHERE id=(SELECT value FROM meta WHERE key='active_release')").fetchone()

    def versions_in(self, db, release=None):
        release=release or self.active(db)
        return [(line_id, db.execute('SELECT * FROM versions WHERE id=?',(version,)).fetchone()) for line_id,version in json.loads(release['items']).items()]

    def overview(self):
        places=deepcopy(self.base['catalogo.json']['lugares'])
        for key,place in places.items():place['route_position']=self.base['waypoints-roteamento.json'].get(key,place['position'])
        with self.db() as db:
            release=self.active(db)
            drafts={r['line_id']:dict(r) for r in db.execute('SELECT id,line_id,revision,updated FROM drafts')}
            lines=[]
            for lid,v in self.versions_in(db):
                p=json.loads(v['payload'])
                lines.append({'id':lid,'version_id':v['id'],'version':v['number'],**p['line'],'preview_features':p['features'],'draft':drafts.get(lid)})
            return {'lines':lines,'drafts':[self.draft_row(r) for r in db.execute('SELECT * FROM drafts ORDER BY updated DESC')],'release':{'id':release['id'],'number':release['number'],'created':release['created'],'note':release['note']},'places':places,'releases':[dict(r) for r in db.execute('SELECT id,number,created,note FROM releases ORDER BY number DESC LIMIT 30')],'jobs':[dict(r) for r in db.execute('SELECT * FROM jobs ORDER BY created DESC LIMIT 10')],**self.management_overview(db)}

    def draft_row(self, row):
        result=dict(row);result['payload']=json.loads(result['payload']);return result

    def draft(self, draft_id):
        with self.db() as db:
            row=db.execute('SELECT * FROM drafts WHERE id=?',(draft_id,)).fetchone()
            if not row:raise Problem('Rascunho não encontrado.',404)
            result=self.draft_row(row)
            result['versions']=[dict(r) for r in db.execute('SELECT id,number,created,note FROM versions WHERE line_id=? ORDER BY number DESC',(row['line_id'],))]
            return result

    def create(self, body, user):
        with self.db(write=True) as db:
            source_id=body.get('line_id')
            existing=body.get('edit',False)
            base_version=None
            if source_id:
                items=json.loads(self.active(db)['items'])
                base_version=items.get(source_id)
                source_version=base_version
                if not source_version:
                    historical=db.execute('SELECT id FROM versions WHERE line_id=? ORDER BY number DESC LIMIT 1',(source_id,)).fetchone()
                    if not historical:raise Problem('Linha de origem não encontrada.',404)
                    source_version=historical['id']
                if existing:
                    draft=db.execute('SELECT id FROM drafts WHERE line_id=?',(source_id,)).fetchone()
                    if draft:return self.draft_row(db.execute('SELECT * FROM drafts WHERE id=?',(draft['id'],)).fetchone())
                payload=json.loads(db.execute('SELECT payload FROM versions WHERE id=?',(source_version,)).fetchone()[0])
                if not existing:payload['line'].setdefault('routing_policy',payload['line']['code'])
            else:
                payload=body.get('payload') or {'line':{'code':body.get('code',''),'name':body.get('name',''),'type':body.get('type','integracional'),'kind':body.get('kind','bidirectional'),'points':[]},'features':[]}
            if not existing:
                payload['line']['code']=body.get('code',payload['line'].get('code',''))
                payload['line']['name']=body.get('name',payload['line'].get('name',''))
                for field in ['type','kind','points','itinerary','note']:
                    if field in body:payload['line'][field]=body[field]
                source_id=uid();base_version=None
                for f in payload['features']:f['properties']['path_id']=uid()
            payload=normalize(payload)
            did=uid()
            db.execute('INSERT INTO drafts VALUES(?,?,?,?,?,?,NULL)',(did,source_id,base_version,encode(payload),1,now()))
            self.audit(db,user,'create-draft',did)
        return self.draft(did)

    def update(self, draft_id, body, user):
        payload=normalize(body.get('payload'))
        with self.db(write=True) as db:
            row=db.execute('SELECT * FROM drafts WHERE id=?',(draft_id,)).fetchone()
            if not row:raise Problem('Rascunho não encontrado.',404)
            if body.get('revision')!=row['revision']:raise Problem('Este rascunho mudou em outra aba. Reabra a versão do servidor antes de salvar.',409,revision=row['revision'])
            if encode(payload)!=row['payload']:
                db.execute('UPDATE drafts SET payload=?,revision=revision+1,updated=? WHERE id=?',(encode(payload),now(),draft_id))
                self.audit(db,user,'update-draft',draft_id)
        return self.draft(draft_id)

    def save_version(self, draft_id, body, user):
        note=body.get('note','')
        if not isinstance(note,str) or len(note)>1000:raise Problem('Descrição de versão inválida.')
        with self.db(write=True) as db:
            row=db.execute('SELECT * FROM drafts WHERE id=?',(draft_id,)).fetchone()
            if not row:raise Problem('Rascunho não encontrado.',404)
            if body.get('revision')!=row['revision']:raise Problem('O rascunho mudou. Atualize a revisão antes de salvar.',409)
            payload=json.loads(row['payload']);sha=digest(payload)
            previous=db.execute('SELECT id FROM versions WHERE line_id=? AND digest=? ORDER BY number DESC',(row['line_id'],sha)).fetchone()
            if previous:vid=previous['id']
            else:
                vid=uid();number=db.execute('SELECT COALESCE(MAX(number),0)+1 FROM versions WHERE line_id=?',(row['line_id'],)).fetchone()[0]
                db.execute('INSERT INTO versions VALUES(?,?,?,?,?,?,?)',(vid,row['line_id'],number,row['payload'],sha,now(),note))
            db.execute('UPDATE drafts SET saved_version=? WHERE id=?',(vid,draft_id))
            self.audit(db,user,'save-version',vid,note)
        return self.draft(draft_id)

    def review_in(self, db, row):
        payload=json.loads(row['payload']);report=validation(payload);release=self.active(db);items=json.loads(release['items'])
        for lid,v in self.versions_in(db):
            if lid!=row['line_id'] and json.loads(v['payload'])['line']['code']==payload['line']['code']:
                report['errors'].append('Este código já está publicado em outra linha.')
        if items.get(row['line_id'])!=row['base_version']:
            report['errors'].append('A linha publicada mudou desde a criação deste rascunho. Abra um novo rascunho da publicação atual.')
        report['errors'].extend(self.validate_references(payload,self.places_in(db)))
        report['warnings'].extend(self.reference_warnings(payload,self.places_in(db)))
        state=db.execute('SELECT archived FROM line_state WHERE line_id=?',(row['line_id'],)).fetchone()
        if state and state['archived']:report['errors'].append('Reative a linha antes de publicar seu rascunho.')
        saved=db.execute('SELECT * FROM versions WHERE id=?',(row['saved_version'],)).fetchone()
        if not saved or saved['digest']!=digest(payload):report['errors'].append('Salve uma versão com as últimas alterações antes de publicar.')
        baseline=db.execute('SELECT payload FROM versions WHERE id=?',(items.get(row['line_id']),)).fetchone()
        return {**report,'release_id':release['id'],'release_number':release['number'],'version_id':row['saved_version'],'revision':row['revision'],'payload':payload,'baseline':json.loads(baseline[0]) if baseline else None,'saved_number':saved['number'] if saved else None}

    def review(self, draft_id):
        with self.db() as db:
            row=db.execute('SELECT * FROM drafts WHERE id=?',(draft_id,)).fetchone()
            if not row:raise Problem('Rascunho não encontrado.',404)
            return self.review_in(db,row)

    def publish(self, draft_id, body, user):
        with self.db(write=True) as db:
            row=db.execute('SELECT * FROM drafts WHERE id=?',(draft_id,)).fetchone()
            if not row:raise Problem('Rascunho não encontrado.',404)
            report=self.review_in(db,row)
            if body.get('revision')!=row['revision'] or body.get('release_id')!=report['release_id'] or body.get('version_id')!=report['version_id']:
                raise Problem('A revisão de publicação ficou desatualizada. Confira novamente.',409)
            if report['errors']:raise Problem('Corrija os impedimentos antes de publicar.',422,errors=report['errors'])
            if report['warnings'] and body.get('acknowledge_warnings') is not True:raise Problem('Confirme a publicação como estudo com as pendências declaradas.',422)
            release=self.active(db);items=json.loads(release['items']);items[row['line_id']]=row['saved_version'];rid=uid()
            db.execute('INSERT INTO releases VALUES(?,?,?,?,?)',(rid,release['number']+1,encode(items),now(),'Publicação de '+report['payload']['line']['code']))
            db.execute('INSERT INTO release_places VALUES(?,?)',(rid,encode(self.places_in(db,release))))
            db.execute("UPDATE meta SET value=? WHERE key='active_release'",(rid,))
            db.execute('UPDATE drafts SET base_version=?,revision=revision+1,updated=? WHERE id=?',(row['saved_version'],now(),draft_id))
            self.audit(db,user,'publish',rid,'Linha '+row['line_id'])
        return {'release_id':rid,'number':release['number']+1}

    def version(self, version_id):
        with self.db() as db:
            row=db.execute('SELECT * FROM versions WHERE id=?',(version_id,)).fetchone()
            if not row:raise Problem('Versão não encontrada.',404)
            result=dict(row);result['payload']=json.loads(result['payload']);return result

    def restore_version(self, draft_id, body, user):
        version=self.version(body.get('version_id'))
        draft=self.draft(draft_id)
        if version['line_id']!=draft['line_id']:raise Problem('A versão pertence a outra linha.')
        return self.update(draft_id,{'revision':body.get('revision'),'payload':version['payload']},user)

    def restore_release(self, body, user):
        with self.db(write=True) as db:
            current=self.active(db)
            if body.get('expected_release')!=current['id']:raise Problem('A publicação atual mudou. Atualize a tela.',409)
            previous=db.execute('SELECT * FROM releases WHERE id=?',(body.get('release_id'),)).fetchone()
            if not previous:raise Problem('Publicação não encontrada.',404)
            rid=uid();number=current['number']+1
            db.execute('INSERT INTO releases VALUES(?,?,?,?,?)',(rid,number,previous['items'],now(),'Restauração da publicação '+str(previous['number'])))
            places=self.places_in(db,previous)
            workspace=self.places_workspace_in(db)
            db.execute('INSERT INTO release_places VALUES(?,?)',(rid,encode(places)))
            if not workspace['dirty']:
                db.execute('UPDATE place_workspace SET revision=revision+1,payload=? WHERE id=1',(encode(places),))
            db.execute("UPDATE meta SET value=? WHERE key='active_release'",(rid,))
            self.audit(db,user,'restore-release',rid)
        return {'release_id':rid,'number':number}

    def public_proposal(self):
        catalog=deepcopy(self.base['catalogo.json']);geo=deepcopy(self.base['linhas-por-sentido.geojson']);catalog['linhas']=[];geo['features']=[]
        with self.db() as db:
            release=self.active(db)
            published_places=self.places_in(db,release)
            for lid,v in self.versions_in(db):
                payload=json.loads(v['payload']);catalog['linhas'].append(payload['line']);geo['features'].extend(payload['features'])
        catalog['lugares']={k:v for k,v in published_places.items() if not v.get('archived')}
        waypoints=deepcopy(self.base['waypoints-roteamento.json'])
        for key,place in published_places.items():
            if place.get('archived'):waypoints.pop(key,None)
            else:waypoints[key]=place.get('route_position',place['position'])
        catalog.update(publication={'id':release['id'],'number':release['number'],'created':release['created']})
        a=self.base['auditoria.json']
        comparisons=deepcopy(self.base['comparativos-i332.json'])
        baseline_i332=[f['geometry'] for f in self.base['linhas-por-sentido.geojson']['features'] if f['properties']['codigo']=='I-332']
        current_i332=[f['geometry'] for f in geo['features'] if f['properties']['codigo']=='I-332']
        if current_i332!=baseline_i332:comparisons={}  # não apresentar um recorte antigo como revisão atual
        return {'catalog':catalog,'geojson':geo,'waypoints':waypoints,'comparisons':comparisons,'review':{k:a[k] for k in ['revision','method','station_reference','oitizeiro_reference','limits']}}

    def job(self, job_id, state, detail):
        with self.db(write=True) as db:
            db.execute('INSERT INTO jobs VALUES(?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET state=excluded.state,detail=excluded.detail,updated=excluded.updated',(job_id,state,encode(detail),now(),now()))
