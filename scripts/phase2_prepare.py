"""Prepare versioned, read-only extraction requests and an optional pinned tool.

No game installation/modification, old-version download, login or publishing.
"""
import argparse,hashlib,json,pathlib,sqlite3,subprocess,urllib.request
from phase2_index import ROOT,OUT

PRIMARY=('.ent','.app','.community','.streamingsector','.streamingworld','.world','.smartobject')
EXTRA=('.streamingblock','.streamingsector_inplace','.streamingquerydata','.loot','.devices','.persistency')

def main():
    p=argparse.ArgumentParser();p.add_argument('--fetch-redscript',action='store_true');p.add_argument('--decompile',action='store_true');a=p.parse_args();OUT.mkdir(parents=True,exist_ok=True);(ROOT/'reports/phase2').mkdir(parents=True,exist_ok=True)
    config=json.loads((ROOT/'config.json').read_text());core=sqlite3.connect('file:'+str(ROOT/'data/archive.db').replace('\\','/')+'?mode=ro',uri=True);core.row_factory=sqlite3.Row
    for filename,extensions in [('resource-request.json',PRIMARY),('resource-extra-request.json',EXTRA)]:
        rows=[dict(r) for r in core.execute('SELECT a.hash,r.path archive,a.extension,e.size FROM assets a JOIN entries e ON e.hash=a.hash JOIN archives r ON r.id=e.archive_id WHERE a.extension IN ('+','.join('?'*len(extensions))+') ORDER BY r.path,a.hash',extensions)]
        (OUT/filename).write_text(json.dumps(rows,separators=(',',':')),encoding='utf-8');print(filename,len(rows),'raw bytes',sum(r['size'] for r in rows))
    meta=json.loads((ROOT/'research/phase2/redscript-tool.json').read_text());tool=ROOT/'tools/redscript-0.5.32/redscript-cli.exe'
    if a.fetch_redscript:
        used=sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file())
        if used+meta['bytes']+30_000_000>config['storage_limit_bytes']:raise SystemExit('Approved capacity insufficient; no download performed.')
        if not tool.exists():
            tool.parent.mkdir(parents=True,exist_ok=True)
            with urllib.request.urlopen(meta['url'],timeout=60) as r:body=r.read(meta['bytes']+1)
            if len(body)!=meta['bytes'] or hashlib.sha256(body).hexdigest()!=meta['sha256']:raise SystemExit('Pinned redscript checksum mismatch')
            tool.write_bytes(body)
    if a.decompile:
        if not tool.exists() or hashlib.sha256(tool.read_bytes()).hexdigest()!=meta['sha256']:raise SystemExit('Obtain the pinned redscript tool first.')
        source=pathlib.Path(config['game_root'])/'r6/cache/final.redscripts';destination=OUT/'scripts/final.reds';destination.parent.mkdir(exist_ok=True)
        subprocess.run([str(tool),'decompile','-i',str(source),'-o',str(destination)],check=True)
        (OUT/'scripts/manifest.json').write_text(json.dumps({'source':'r6/cache/final.redscripts','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'decoded_sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),'tool':meta},indent=2),encoding='utf-8')

if __name__=='__main__':main()
