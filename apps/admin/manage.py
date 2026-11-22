"""Operações locais explícitas de primeiro acesso, recuperação e backup."""
import argparse
import getpass
from pathlib import Path
import secrets
import sqlite3
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from apps.admin.store import Store, now

parser=argparse.ArgumentParser(description='Administração local do atlas')
parser.add_argument('action',choices=['setup-token','reset-password','backup'])
parser.add_argument('--data-dir',type=Path,default=Path(__file__).resolve().parents[2]/'data')
parser.add_argument('--output',type=Path)
args=parser.parse_args()
if args.action=='setup-token':
    path=args.data_dir/'admin/setup-token'
    if not path.exists():parser.exit(1,'Código indisponível: inicie o servidor ou use reset-password para recuperar a conta existente.\n')
    print(path.read_text().strip())
elif args.action=='reset-password':
    store=Store(args.data_dir)
    password=getpass.getpass('Nova senha (mínimo 12 caracteres): ')
    if len(password)<12 or len(password)>200 or password!=getpass.getpass('Repita a senha: '):parser.exit(1,'Senha inválida ou confirmação diferente.\n')
    salt=secrets.token_hex(16)
    with store.db(write=True) as db:
        account=db.execute('SELECT username FROM account').fetchone()
        if not account:parser.exit(1,'Cadastre primeiro o administrador em /admin.\n')
        db.execute('UPDATE account SET salt=?,password=?',(salt,store.credentials(password,salt)))
        db.execute('DELETE FROM sessions');db.execute('DELETE FROM attempts')
        store.audit(db,account['username'],'reset-password','administrator')
    print('Senha atualizada; sessões encerradas.')
else:
    if not args.output:parser.error('backup exige --output CAMINHO')
    if args.output.exists():parser.exit(1,'O destino já existe. Escolha outro arquivo.\n')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(args.data_dir/'admin/admin.sqlite3') as source,sqlite3.connect(args.output) as target:source.backup(target)
    args.output.chmod(0o600)
    print('Backup transacional criado:',args.output)
