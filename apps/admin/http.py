"""Rotas administrativas autenticadas para o servidor local existente."""
from http.cookies import SimpleCookie
import hmac
import json
import re
from urllib.parse import parse_qs,urlsplit

from .store import Problem

COOKIE='px_admin'


def token(handler):
    cookie=SimpleCookie()
    try:cookie.load(handler.headers.get('Cookie',''))
    except Exception:return ''
    return cookie[COOKIE].value if COOKIE in cookie else ''


def require(handler, write=False):
    session=handler.server.admin.session(token(handler))
    if not session:raise Problem('Entre como administrador para continuar.',401)
    if write and not hmac.compare_digest(handler.headers.get('X-CSRF-Token',''),session['csrf']):raise Problem('Sessão de edição inválida. Recarregue a página.',403)
    return session


def get(handler, path):
    if not path.startswith('/api/admin/'):return False
    store=handler.server.admin
    if path=='/api/admin/session':
        session=store.session(token(handler))
        handler.json({'configured':store.configured(),'user':session['username'] if session else None,'csrf':session['csrf'] if session else None})
        return True
    require(handler)
    if path=='/api/admin/overview':handler.json(store.overview())
    elif path=='/api/admin/roads':handler.json(handler.server.router.roads(parse_qs(urlsplit(handler.path).query).get('bbox',[''])[0]))
    elif path=='/api/admin/router':handler.json(handler.server.router.status(start=True))
    elif re.fullmatch(r'/api/admin/drafts/[a-f0-9-]+',path):handler.json(store.draft(path.rsplit('/',1)[1]))
    elif re.fullmatch(r'/api/admin/drafts/[a-f0-9-]+/review',path):handler.json(store.review(path.split('/')[-2]))
    elif re.fullmatch(r'/api/admin/versions/[a-f0-9-]+',path):handler.json(store.version(path.rsplit('/',1)[1]))
    else:raise Problem('Rota administrativa não encontrada.',404)
    return True


def post(handler, path, body):
    store=handler.server.admin
    if path in {'/api/admin/login','/api/admin/setup'}:
        session=store.login(body.get('username'),body.get('password')) if path.endswith('/login') else store.setup(body.get('token'),body.get('username'),body.get('password'))
        handler.extra_headers=[('Set-Cookie',f"{COOKIE}={session['token']}; HttpOnly; SameSite=Strict; Path=/; Max-Age=28800")]
        handler.json({'user':session['username'],'csrf':session['csrf']})
        return
    session=require(handler,write=True);user=session['username']
    if path=='/api/admin/logout':
        store.logout(token(handler));handler.extra_headers=[('Set-Cookie',f'{COOKIE}=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0')];handler.json({'ok':True})
    elif path=='/api/admin/drafts':handler.json(store.create(body,user),201)
    elif path=='/api/admin/route-create':handler.json(handler.server.router.create(body,store.draft(body.get('draft_id'))))
    elif path=='/api/admin/places/save':handler.json(store.save_place(body,user))
    elif path=='/api/admin/lines/manage':handler.json(store.manage_line(body,user))
    elif path=='/api/admin/batch/review':handler.json(store.batch_review(body))
    elif path=='/api/admin/batch/publish':handler.json(store.publish_batch(body,user))
    elif path=='/api/admin/restore-release':handler.json(store.restore_release(body,user))
    elif path in {'/api/admin/collect','/api/collect'}:
        if body.get('codes',[])!=[]:raise Problem('O painel coleta o catálogo completo. Use a CLI para manutenção pontual.')
        if not handler.server.start_collection([]):raise Problem('Uma coleta já está em andamento.',409)
        handler.json({'message':'Coleta completa iniciada.'},202)
    else:
        match=re.fullmatch(r'/api/admin/drafts/([a-f0-9-]+)/(update|save-version|publish|restore-version|route-preview|route-trim)',path)
        if not match:raise Problem('Rota administrativa não encontrada.',404)
        did,action=match.groups()
        if action=='route-preview':result=handler.server.router.preview(store.draft(did),body)
        elif action=='route-trim':result=handler.server.router.trim(store.draft(did),body)
        else:result={'update':store.update,'save-version':store.save_version,'publish':store.publish,'restore-version':store.restore_version}[action](did,body,user)
        handler.json(result)
