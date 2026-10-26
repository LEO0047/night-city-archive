"""Fail a release if tracked files include private data, credentials or game payloads."""
import json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FORBIDDEN_SUFFIXES={'.archive','.db','.sqlite','.sqlite3','.wem','.mesh','.xbm','.glb','.gltf','.wav','.mp3','.ogg','.png','.jpg','.jpeg','.zip','.dll','.exe','.pck'}

def validate_catalogue(data):
    errors=[]
    if data.get('schema') not in ('nca.public.research/v1','nca.public.research/v2'):errors.append('Unexpected public schema')
    phase2=data.get('schema')=='nca.public.research/v2'
    if phase2 and data.get('mode')!='public':errors.append('Private catalogue in public build')
    if phase2 and set(data)-{'schema','mode','game','source_manifest_sha256','integrity','metrics','findings','aliases','coverage','acceptance','method','sources'}:errors.append('Unexpected public top-level fields')
    if not data.get('findings'):errors.append('Missing dossiers')
    if not phase2 and len(data.get('findings',[]))<30:errors.append('Fewer than 30 dossiers')
    permitted={'hash','path','extension','role','archives'}
    for f in data.get('findings',[]):
        if phase2 and set(f)-{'id','title','summary','categories','classification','classification_origin','community','community_status','system_conclusion','analyst_conclusion','community_note','flow','sections','support','counter','evidence','confidence_explanation','assets','aliases','next_test','sources'}:errors.append('Unexpected dossier fields')
        if not (f.get('counter') if phase2 else f.get('details',{}).get('counter')):errors.append('Missing counterevidence: '+f.get('id','?'))
        if phase2 and (f.get('classification_origin') not in ('rule','analyst','community') or not f.get('confidence_explanation')):errors.append('Missing classification provenance')
        for a in f.get('assets',[]):
            if set(a)-permitted:errors.append('Unexpected asset payload fields')
            for r in a.get('archives',[]):
                if set(r)-{'path','sha256','entry_sha1'}:errors.append('Unexpected archive fields')
    if phase2:
        forbidden={'audio','transcription','localization','journal','female','male','json_zlib','segments','wav_sha256'}
        def inspect(node):
            if isinstance(node,dict):
                if set(node)&forbidden:errors.append('Private payload keys in public catalogue')
                for v in node.values():inspect(v)
            elif isinstance(node,list):
                for v in node:inspect(v)
        inspect(data)
        ids={f['id'] for f in data['findings']}
        if any(v not in ids or k in ids for k,v in data.get('aliases',{}).items()):errors.append('Broken alias target')
    return errors

def main():
    result=subprocess.run(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT,capture_output=True,check=True)
    files=sorted({Path(p.decode()) for p in result.stdout.split(b'\0') if p and (ROOT/Path(p.decode())).exists()})
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
