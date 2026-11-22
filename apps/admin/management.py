"""Referências compartilhadas e publicação conjunta, sempre em transação."""
from copy import deepcopy
import json
import math
import re
from .store import Problem, coordinates, encode, digest, uid, now, validation


def point(value):
    result = coordinates({'type': 'LineString', 'coordinates': [value]})[0]
    if not (-35.1 <= result[0] <= -34.6 and -7.5 <= result[1] <= -6.9):
        raise Problem('Posicione a referência na área de João Pessoa.')
    return result


def normalize_place(body):
    if not isinstance(body, dict):raise Problem('Cadastro de referência inválido.')
    label = body.get('label')
    if not isinstance(label, str) or not label.strip() or len(label) > 160:
        raise Problem('Informe um nome de até 160 caracteres.')
    kind = body.get('kind', 'station')
    if kind not in {'terminal', 'station', 'stop', 'reference'}:
        raise Problem('Tipo de referência inválido.')
    note = body.get('note', '')
    if not isinstance(note, str) or len(note) > 2000:
        raise Problem('Observações inválidas (máximo 2.000 caracteres).')
    accesses = body.get('accesses', {})
    if not isinstance(accesses, dict) or len(accesses) > 12:
        raise Problem('Acessos inválidos.')
    for key, value in accesses.items():
        if not re.fullmatch(r'[a-z0-9-]{1,40}', key) or key in {'position','route_position'}:
            raise Problem('Use a chave do sentido para identificar o acesso.')
        point(value)
    if not isinstance(body.get('archived', False), bool):
        raise Problem('Estado de referência inválido.')
    return {'label': label.strip(), 'kind': kind, 'terminal': kind == 'terminal',
            'position': point(body.get('position')), 'route_position': point(body.get('route_position', body.get('position'))),
            'accesses': accesses, 'note': note.strip(), 'archived': body.get('archived', False)}


def route_distance(position, coords):
    """Distância aproximada ponto-segmento em metros, apenas para alertas editoriais."""
    best = math.inf
    for a, b in zip(coords, coords[1:]):
        ax, ay = (a[0]-position[0])*110440, (a[1]-position[1])*110580
        bx, by = (b[0]-position[0])*110440, (b[1]-position[1])*110580
        dx, dy = bx-ax, by-ay
        ratio = max(0, min(1, -(ax*dx+ay*dy)/(dx*dx+dy*dy))) if dx*dx+dy*dy else 0
        best = min(best, math.hypot(ax+ratio*dx, ay+ratio*dy))
    return best


class Management:
    def migrate_management(self, db):
        db.executescript('''
        CREATE TABLE IF NOT EXISTS release_places(release_id TEXT PRIMARY KEY,payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS place_workspace(id INTEGER PRIMARY KEY CHECK(id=1),revision INTEGER NOT NULL,payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS line_state(line_id TEXT PRIMARY KEY,revision INTEGER NOT NULL,archived INTEGER NOT NULL DEFAULT 0);
        ''')
        places = deepcopy(self.base['catalogo.json']['lugares'])
        for key, p in places.items():
            p.setdefault('kind', 'station' if 'estação' in p['label'].lower() else 'terminal' if p.get('terminal') else 'reference')
            p['terminal'] = p['kind'] == 'terminal'
            p.setdefault('route_position', self.base['waypoints-roteamento.json'].get(key, p['position']))
            p.setdefault('accesses', {})
            p.setdefault('archived', False)
        # Publicações antigas nunca tiveram referências editáveis: mantenha sua semente.
        for row in db.execute('SELECT id FROM releases').fetchall():
            db.execute('INSERT OR IGNORE INTO release_places VALUES(?,?)', (row['id'], encode(places)))
        active = self.places_in(db)
        db.execute('INSERT OR IGNORE INTO place_workspace VALUES(1,1,?)', (encode(active),))

    def places_in(self, db, release=None):
        release = release or self.active(db)
        row = db.execute('SELECT payload FROM release_places WHERE release_id=?', (release['id'],)).fetchone()
        return json.loads(row[0]) if row else deepcopy(self.base['catalogo.json']['lugares'])

    def places_workspace_in(self, db):
        row = db.execute('SELECT * FROM place_workspace WHERE id=1').fetchone()
        places = json.loads(row['payload'])
        return {'revision': row['revision'], 'places': places, 'dirty': places != self.places_in(db)}

    def save_place(self, body, user):
        value = normalize_place(body.get('place', {}))
        key = body.get('id') or uid()
        if not isinstance(key, str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}', key):
            raise Problem('Identificador de referência inválido.')
        with self.db(write=True) as db:
            workspace = self.places_workspace_in(db)
            if body.get('revision') != workspace['revision']:
                raise Problem('As estações mudaram em outra aba. Atualize antes de salvar.', 409)
            if body.get('id') and key not in workspace['places']:
                raise Problem('Referência não encontrada.', 404)
            workspace['places'][key] = value
            db.execute('UPDATE place_workspace SET revision=revision+1,payload=? WHERE id=1', (encode(workspace['places']),))
            self.audit(db, user, 'save-place', key)
            return {**self.places_workspace_in(db), 'id': key}

    def management_overview(self, db):
        workspace = self.places_workspace_in(db)
        states = {r['line_id']: dict(r) for r in db.execute('SELECT * FROM line_state')}
        active = json.loads(self.active(db)['items'])
        inactive = []
        for row in db.execute('SELECT * FROM versions ORDER BY number DESC').fetchall():
            lid = row['line_id']
            if lid not in active and not any(v['id'] == lid for v in inactive):
                inactive.append({'id': lid, 'version_id': row['id'], 'version': row['number'], **json.loads(row['payload'])['line']})
        return {'places': workspace['places'], 'places_revision': workspace['revision'], 'places_dirty': workspace['dirty'],
                'published_places': self.places_in(db), 'line_states': states, 'inactive_lines': inactive}

    def manage_line(self, body, user):
        lid = body.get('line_id')
        action = body.get('action')
        if not isinstance(lid,str) or len(lid)>80:raise Problem('Identificador de linha inválido.')
        if action not in {'archive', 'restore', 'discard-draft'}:
            raise Problem('Ação de linha inválida.')
        with self.db(write=True) as db:
            known = db.execute('SELECT 1 FROM versions WHERE line_id=? UNION SELECT 1 FROM drafts WHERE line_id=?', (lid, lid)).fetchone()
            if not known:
                raise Problem('Linha não encontrada.', 404)
            state = db.execute('SELECT * FROM line_state WHERE line_id=?', (lid,)).fetchone()
            revision = state['revision'] if state else 0
            if body.get('revision') != revision:
                raise Problem('O estado da linha mudou. Atualize a lista.', 409)
            if action == 'discard-draft':
                draft = db.execute('SELECT revision FROM drafts WHERE line_id=?', (lid,)).fetchone()
                if not draft or body.get('draft_revision') != draft['revision']:
                    raise Problem('O rascunho mudou. Atualize antes de descartá-lo.', 409)
                db.execute('DELETE FROM drafts WHERE line_id=?', (lid,))
            archived = action == 'archive' if action != 'discard-draft' else bool(state and state['archived'])
            db.execute('INSERT INTO line_state VALUES(?,?,?) ON CONFLICT(line_id) DO UPDATE SET revision=excluded.revision,archived=excluded.archived', (lid, revision+1, int(archived)))
            self.audit(db, user, action, lid)
        return {'ok': True}

    def validate_references(self, payload, places):
        errors = []
        refs = list(payload['line'].get('points', []))
        for feature in payload['features']:
            refs += [key for key in feature['properties'].get('waypoints', []) if key in places]
            refs += feature['properties'].get('station_ids', [])
            refs += [c['station_id'] for c in feature['properties'].get('control_points', []) if c.get('station_id')]
        for key in set(refs):
            if key not in places or places[key].get('archived'):
                errors.append('Referência ausente ou arquivada: '+str(key)+'. Revise as linhas ou inclua as estações nesta publicação.')
        return errors

    def reference_warnings(self, payload, places):
        warnings = []
        for f in payload['features']:
            p = f['properties']; coords = f['geometry']['coordinates']; label = p.get('label', p['sentido'])
            for key in p.get('station_ids', []):
                place = places.get(key)
                if place and route_distance(place.get('accesses', {}).get(p['sentido'], place.get('route_position', place['position'])), coords) > 150:
                    warnings.append(label+': acesso de '+place['label']+' distante mais de 150 m do percurso. Confira o vínculo e recalcule se necessário.')
            for c in p.get('control_points', []):
                if route_distance(c['position'], coords) > 80:
                    warnings.append(label+': referência '+c['label']+' distante mais de 80 m do percurso. Mover referências não altera a geometria automaticamente.')
        return warnings

    def batch_review_in(self, db, body):
        draft_ids = body.get('draft_ids', [])
        remove_ids = body.get('remove_ids', [])
        include_places = body.get('include_places', False)
        if (not isinstance(draft_ids, list) or not isinstance(remove_ids, list) or
                len(draft_ids) > 300 or len(remove_ids) > 300 or not isinstance(include_places, bool) or
                any(not isinstance(v, str) for v in draft_ids+remove_ids) or
                len(set(draft_ids)) != len(draft_ids) or len(set(remove_ids)) != len(remove_ids)):
            raise Problem('Seleção de publicação inválida.')
        release = self.active(db)
        items = json.loads(release['items'])
        workspace = self.places_workspace_in(db)
        published_places = self.places_in(db)
        places = workspace['places'] if include_places else published_places
        errors, warnings, changes, plan = [], [], [], []
        for did in draft_ids:
            row = db.execute('SELECT * FROM drafts WHERE id=?', (did,)).fetchone()
            if not row:
                raise Problem('Um rascunho selecionado não existe mais. Atualize a seleção.', 409)
            payload = json.loads(row['payload'])
            report = validation(payload)
            code = payload['line']['code']
            errors += [code+': '+e for e in report['errors']]
            warnings += report['warnings']
            if row['line_id'] in remove_ids:
                errors.append(code+': não é possível publicar e retirar a mesma linha.')
            state = db.execute('SELECT * FROM line_state WHERE line_id=?', (row['line_id'],)).fetchone()
            if state and state['archived']:
                errors.append(code+': reative a linha antes de publicar seu rascunho.')
            if items.get(row['line_id']) != row['base_version']:
                errors.append(code+': a publicação de origem mudou. Recupere a versão atual em um novo rascunho.')
            saved = db.execute('SELECT * FROM versions WHERE id=?', (row['saved_version'],)).fetchone()
            if not saved or saved['digest'] != digest(payload):
                errors.append(code+': salve uma versão com as últimas alterações.')
            else:
                items[row['line_id']] = saved['id']
            changes.append({'draft_id': did, 'line_id': row['line_id'], 'code': code, 'name': payload['line']['name'], 'revision': row['revision'], 'version_id': row['saved_version'], 'version': saved['number'] if saved else None, 'features': payload['features']})
            plan.append([did, row['revision'], row['saved_version'], state['revision'] if state else 0])
        removals = []
        for lid in remove_ids:
            state = db.execute('SELECT * FROM line_state WHERE line_id=?', (lid,)).fetchone()
            if lid not in items or not state or not state['archived']:
                errors.append('Só é possível retirar uma linha publicada marcada para arquivamento.')
                continue
            version = db.execute('SELECT payload FROM versions WHERE id=?', (items[lid],)).fetchone()
            removals.append({'line_id': lid, 'code': json.loads(version[0])['line']['code']})
            plan.append([lid, state['revision'], items.pop(lid)])
        codes = set()
        features = []
        for lid, vid in items.items():
            p = json.loads(db.execute('SELECT payload FROM versions WHERE id=?', (vid,)).fetchone()[0])
            code = p['line']['code']
            if code in codes:
                errors.append('Código duplicado na composição final: '+code)
            codes.add(code)
            errors += [code+': '+e for e in self.validate_references(p, places)]
            warnings += [code+': '+w for w in self.reference_warnings(p, places)]
            features.extend(p['features'])
        if not draft_ids and not remove_ids and not (include_places and workspace['dirty']):
            errors.append('Selecione alguma alteração para publicar.')
        token = digest({'release': release['id'], 'plan': plan, 'include_places': include_places,
                        'places_revision': workspace['revision'] if include_places else None, 'items': items})
        return {'review_token': token, 'release_id': release['id'], 'release_number': release['number'],
                'errors': sorted(set(errors)), 'warnings': sorted(set(warnings)), 'changes': changes, 'removals': removals,
                'include_places': include_places, 'places_revision': workspace['revision'], 'places': places,
                'places_changed': sorted(k for k in set(places)|set(published_places) if places.get(k) != published_places.get(k)),
                'line_count': len(items), 'features': features, '_items': items}

    def batch_review(self, body):
        with self.db() as db:
            report = self.batch_review_in(db, body)
            report.pop('_items')
            return report

    def publish_batch(self, body, user):
        with self.db(write=True) as db:
            report = self.batch_review_in(db, body)
            if body.get('review_token') != report['review_token']:
                raise Problem('A revisão conjunta ficou desatualizada. Revise novamente.', 409)
            if report['errors']:
                raise Problem('Corrija os impedimentos antes de publicar.', 422, errors=report['errors'])
            if body.get('acknowledge_warnings') is not True:
                raise Problem('Confirme a revisão da composição e das pendências.', 422)
            rid = uid()
            number = report['release_number']+1
            note = f"Publicação conjunta: {len(report['changes'])} linhas, {len(report['removals'])} retiradas, {len(report['places_changed'])} referências alteradas"
            db.execute('INSERT INTO releases VALUES(?,?,?,?,?)', (rid, number, encode(report['_items']), now(), note))
            db.execute('INSERT INTO release_places VALUES(?,?)', (rid, encode(report['places'])))
            db.execute("UPDATE meta SET value=? WHERE key='active_release'", (rid,))
            for c in report['changes']:
                db.execute('UPDATE drafts SET base_version=?,revision=revision+1,updated=? WHERE id=?', (c['version_id'], now(), c['draft_id']))
            # Uma retirada pode ser reativada posteriormente sem um vínculo antigo de publicação.
            for r in report['removals']:
                db.execute('UPDATE drafts SET base_version=NULL,revision=revision+1,updated=? WHERE line_id=?', (now(), r['line_id']))
            self.audit(db, user, 'publish-batch', rid, note)
        return {'release_id': rid, 'number': number}
