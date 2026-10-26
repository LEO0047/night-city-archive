"""Fail a release if tracked files include private data, credentials or game payloads."""
import json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FORBIDDEN_SUFFIXES={'.archive','.db','.sqlite','.sqlite3','.wem','.mesh','.xbm','.glb','.gltf','.wav','.mp3','.ogg','.png','.jpg','.jpeg','.zip','.dll','.exe','.pck'}

def validate_catalogue(data):
    errors=[]
    if data.get('schema')!='nca.public.research/v1':errors.append('Unexpected public schema')
    if len(data.get('findings',[]))<30:errors.append('Fewer than 30 dossiers')
    permitted={'hash','path','extension','role','archives'}
    for f in data.get('findings',[]):
        if not f.get('details',{}).get('counter'):errors.append('Missing counterevidence: '+f.get('id','?'))
        for a in f.get('assets',[]):
            if set(a)-permitted:errors.append('Unexpected asset payload fields')
            for r in a.get('archives',[]):
                if set(r)-{'path','sha256'}:errors.append('Unexpected archive fields')
    return errors

def main():
    result=subprocess.run(['git','ls-files','-z'],cwd=ROOT,capture_output=True,check=True)
    files=[Path(p.decode()) for p in result.stdout.split(b'\0') if p]
    errors=[]
    for rel in files:
        p=ROOT/rel
        if rel.parts[0] in {'data','reports','tools','exports','release'} or rel.name=='config.json' or p.suffix.lower() in FORBIDDEN_SUFFIXES:errors.append('Excluded file tracked: '+str(rel));continue
        if p.stat().st_size>5_000_000:errors.append('Unexpected large public file: '+str(rel))
        raw=p.read_text(encoding='utf-8',errors='replace')
        for label,pattern in [('private Windows user path',r'[A-Za-z]:[\\/]{1,2}Users[\\/]{1,2}(?!Public\b)[A-Za-z0-9_-]+'),('private tailnet address',r'\b[a-z0-9-]+\.tail[a-z0-9]+\.ts\.net\b'),('GitHub token',r'gh[pousr]_[A-Za-z0-9]{30,}'),('API secret',r'sk-[A-Za-z0-9_-]{30,}')]:
            if re.search(pattern,raw):errors.append(label+': '+str(rel))
    errors.extend(validate_catalogue(json.loads((ROOT/'docs/catalogue.json').read_text(encoding='utf-8'))))
    report={'passed':not errors,'tracked_files':len(files),'tracked_bytes':sum((ROOT/p).stat().st_size for p in files),'errors':errors}
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if errors:raise SystemExit(1)

if __name__=='__main__':main()
