"""Rebuild in a new database, compare logical content, never overwrite the working DB."""
import argparse,hashlib,json,os,sqlite3,subprocess,sys,time
from pathlib import Path
from catalog import ROOT,DB

def size():
    return sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file())

def logical(db):
    out={}
    for table,cols,order in [
        ('archives','path,sha256,size,entries','path'),
        ('assets','hash,path,extension,size,archive_id,variants','hash'),
        ('entries','hash,archive_id,size,compressed,sha1','hash,archive_id'),
        ('refs','source_hash,target_hash,kind','source_hash,target_hash,kind'),
        ('documents','hash,archive_id,kind,field,text,language','hash,archive_id,field'),
        ('semantic_refs','source_hash,archive_id,target_hash,target_path,field,position','source_hash,archive_id,target_hash,field,position'),
        ('resources','hash,archive_id,root_class','hash,archive_id'),
        ('findings','id,slug,title,category,confidence,community,summary,details,score','id'),
        ('finding_assets','finding_id,hash,role','finding_id,hash')]:
        h=hashlib.sha256();n=0
        for row in db.execute(f'SELECT {cols} FROM {table} ORDER BY {order}'):
            h.update((json.dumps(list(row),ensure_ascii=False,separators=(',',':'))+'\n').encode());n+=1
        out[table]={'rows':n,'sha256':h.hexdigest()}
        print('Compared table:',table,n,flush=True)
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--from-cache',action='store_true');p.add_argument('--keep',action='store_true');args=p.parse_args()
    config=json.loads((ROOT/'config.json').read_text());limit=config['storage_limit_bytes']
    baseline=DB.exists();target=ROOT/'data/rebuilt.db' if baseline else DB
    if target.exists():raise SystemExit('Output already exists: '+str(target)+'. Review it before removing or renaming it.')
    expected=DB.stat().st_size if baseline else 9_000_000_000
    if size()+expected+700_000_000>limit:raise SystemExit('Not enough room within the approved 20 GB cap. No files changed.')
    started=time.time();env=os.environ.copy();env['NCA_DATABASE']=str(target)
    from runtime import find_pwsh
    pwsh=find_pwsh(required=not args.from_cache)
    def run(script,*extra):
        subprocess.run([sys.executable,'-X','utf8',str(ROOT/'scripts'/script),*extra],cwd=ROOT,env=env,check=True)
    if not args.from_cache:
        # Verify the entire source against the preserved baseline before reading new cache data.
        run('manifest.py','after')
        if not json.loads((ROOT/'reports/game-after-summary.json').read_text())['unchanged']:
            raise SystemExit('Game differs from this scan. Keep scans separate; do not merge different versions.')
        old=hashlib.sha256((ROOT/'data/archive-index.jsonl').read_bytes()).hexdigest()
        subprocess.run([str(pwsh),'-NoProfile','-File',str(ROOT/'scripts/bridge.ps1'),'-Mode','index'],cwd=ROOT,check=True)
        if old!=hashlib.sha256((ROOT/'data/archive-index.jsonl').read_bytes()).hexdigest():
            raise SystemExit('Archive inventory changed. Inspect source/tool versions before proceeding.')
    run('catalog.py')
    # Cached decoded JSON is sufficient to rebuild. --from-cache does not rescan game files.
    # A fresh extraction recipe is provided in README; no cached resource is represented as newly decoded.
    run('text_index.py');run('discover.py');run('curate.py')
    with sqlite3.connect(target) as rebuilt:
        rebuilt.execute('PRAGMA wal_checkpoint(TRUNCATE)')
        integrity=rebuilt.execute('PRAGMA quick_check').fetchone()[0]
        actual=logical(rebuilt)
    rebuilt.close()  # sqlite3's context manager ends transactions but does not close Windows file handles.
    report={'completed_at_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'mode':'cached JSON -> empty SQLite database','source_inventory_repeated':not args.from_cache,'integrity':integrity,'rebuilt':actual}
    if baseline:
        with sqlite3.connect(DB) as original:expected=logical(original)
        original.close()
        report['baseline']=expected;report['logical_match']=actual==expected
    else:report['logical_match']=None
    report['elapsed_seconds']=round(time.time()-started,2)
    report['passed']=integrity=='ok' and (not baseline or report['logical_match'])
    (ROOT/'reports/rebuild.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    if baseline and report['passed'] and not args.keep:
        # Only this newly created, reproducible verification database can be removed.
        if target.resolve()!=(ROOT/'data/rebuilt.db').resolve():raise RuntimeError('Unexpected cleanup target')
        for suffix in ('','-wal','-shm'):
            candidate=Path(str(target)+suffix)
            if candidate.exists():candidate.unlink()
    print(json.dumps({k:v for k,v in report.items() if k not in ('rebuilt','baseline')},indent=2),flush=True)
    if not report['passed']:raise SystemExit(1)

if __name__=='__main__':main()
