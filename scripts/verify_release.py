"""Read-only public snapshot checks; prints categories/counts, never matched secrets."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
EXEMPT={'INCLUDED_FILES.json'}  # Self-hashing manifest is intentionally excluded.
PATTERNS={
 'personal_home_path':re.compile(r'/(?:Users|home)/[^/\s]+/'),
 'provider_key_shape':re.compile(r'\b(?:sk-(?:proj-|ant-)?[A-Za-z0-9_-]{20,}|AKIA[A-Z0-9]{16}|gh[pousr]_[A-Za-z0-9]{30,})'),
 'private_key_material':re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
}

def public_files():
    return sorted(p for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.relative_to(ROOT).parts
                  and '__pycache__' not in p.parts and '.venv' not in p.parts and not p.name.endswith('.pyc'))

def main():
    findings=[];files=public_files()
    for p in files:
        rel=p.relative_to(ROOT).as_posix()
        if p.is_symlink():findings.append({'path':rel,'category':'symlink'})
        if p.suffix.lower() in ('.csv','.parquet','.sqlite','.db','.pkl','.pickle','.pem','.key','.log','.ipynb','.jsonl','.response','.headers'):
            findings.append({'path':rel,'category':'excluded_artifact_type'})
        if p.suffix.lower()=='.png':continue
        text=p.read_text(errors='replace')
        for name,pattern in PATTERNS.items():
            if pattern.search(text):findings.append({'path':rel,'category':name})
        if p.suffix=='.py' and rel.startswith(('src/','app/')):
            tree=ast.parse(text)
            for node in ast.walk(tree):
                names=[]
                if isinstance(node,ast.Import):names=[x.name.split('.')[0] for x in node.names]
                if isinstance(node,ast.ImportFrom) and node.module:names=[node.module.split('.')[0]]
                if set(names)&{'requests','httpx','urllib','socket','keyring','ctypes','openai','subprocess'}:
                    findings.append({'path':rel,'category':'forbidden_runtime_import'})
    manifest=json.loads((ROOT/'INCLUDED_FILES.json').read_text())
    recorded={x['path']:x['sha256'] for x in manifest['files'] if x['path'] not in EXEMPT}
    if {x['path'] for x in manifest['files']}!={p.relative_to(ROOT).as_posix() for p in files}:findings.append({'category':'manifest_file_set_mismatch'})
    actual={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.relative_to(ROOT).as_posix() not in EXEMPT}
    if recorded!=actual:findings.append({'category':'manifest_mismatch'})
    def git(*args):return subprocess.run(['git','-C',str(ROOT),*args],capture_output=True,text=True,check=True).stdout.strip()
    refs=git('for-each-ref','--format=%(refname)')
    commits=git('rev-list','--all','--count')
    remotes=git('remote')
    objects=git('count-objects','-v')
    if refs or commits!='0' or remotes:findings.append({'category':'unexpected_git_history_or_remote'})
    if not re.search(r'^count: 0$',objects,re.M):findings.append({'category':'unexpected_git_objects'})
    print(json.dumps({'files_checked':len(files),'findings':findings,'git_commits':int(commits),
                      'git_refs':len(refs.splitlines()) if refs else 0,'remotes':len(remotes.splitlines()) if remotes else 0,
                      'scope':'Pattern and provenance checks; not a guarantee of all secret types or legal ownership'},indent=2))
    return 1 if findings else 0

if __name__=='__main__':raise SystemExit(main())
