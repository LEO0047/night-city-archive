"""Capacity-bounded fresh rebuild with a verified compressed recovery copy.

Only the generated phase2/evidence.db is replaced. Game/core DB are read-only.
Order-independent table fingerprints combine count, sum and xor of SHA-256
row digests. Two independent serial builds must match every table.
"""
import gzip,hashlib,json,pathlib,sqlite3,subprocess,sys,time
from phase2_index import ROOT,OUT

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()

def fingerprints(path):
    db=sqlite3.connect('file:'+str(path).replace('\\','/')+'?mode=ro',uri=True);result={}
    tables=[r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    for name in tables:
        n=total=xor=0
        for r in db.execute('SELECT * FROM "'+name+'"'):
            h=int.from_bytes(hashlib.sha256(json.dumps(r,ensure_ascii=False,separators=(',',':')).encode()).digest(),'big');total=(total+h)%(1<<256);xor^=h;n+=1
        result[name]={'count':n,'sum_sha256':f'{total:064x}','xor_sha256':f'{xor:064x}','columns':[r[1] for r in db.execute('PRAGMA table_info("'+name+'")')]}
        print('fingerprint',name,n,flush=True)
    result['_integrity']=db.execute('PRAGMA quick_check').fetchone()[0];db.close();return result

def main():
    path=OUT/'evidence.db';backup=OUT/'evidence-recovery.db.gz';report=ROOT/'reports/phase2/supplement-rebuild.json'
    if backup.exists():raise SystemExit('Recovery copy already exists. Inspect the previous attempt before rerunning.')
    start=time.time();db=sqlite3.connect(path);db.execute('PRAGMA wal_checkpoint(TRUNCATE)');db.close()
    original=sha(path);before=fingerprints(path);limit=json.loads((ROOT/'config.json').read_text())['storage_limit_bytes'];used=sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file())
    with path.open('rb') as src,gzip.open(backup,'wb',compresslevel=6) as dst:
        for block in iter(lambda:src.read(8*1024*1024),b''):
            dst.write(block)
            if used+backup.stat().st_size>limit-150_000_000:raise RuntimeError('Compressed recovery copy would exceed the approved cap; original DB untouched.')
    check=hashlib.sha256()
    with gzip.open(backup,'rb') as src:
        for block in iter(lambda:src.read(8*1024*1024),b''):check.update(block)
    assert check.hexdigest()==original,'Recovery copy mismatch; original DB untouched'
    state={'status':'rebuilding','original_sha256':original,'backup_sha256':sha(backup),'backup_bytes':backup.stat().st_size,'before':before,'method':'fresh database from saved inputs; verified gzip recovery copy; memory journal only for disposable rebuild'}
    report.write_text(json.dumps(state,indent=2),encoding='utf-8');print('verified recovery copy',backup.stat().st_size,flush=True)
    assert path.resolve()==(ROOT/'data/phase2/evidence.db').resolve();path.unlink()
    try:
        for args in [('phase2_index.py','--rebuild-memory-journal'),('phase2_context.py','--rebuild-memory-journal'),('phase2_enrich.py',)]:
            subprocess.run([sys.executable,'-X','utf8',str(ROOT/'scripts'/args[0]),*args[1:]],cwd=ROOT,check=True)
        after=fingerprints(path);state.update(after=after,logical_match=after==before,new_sha256=sha(path))
        if not state['logical_match']:raise RuntimeError('Fresh supplemental index differs from reference')
        state.update(status='passed',elapsed_seconds=round(time.time()-start,2));report.write_text(json.dumps(state,indent=2),encoding='utf-8')
        backup.unlink();print('SUPPLEMENT_REBUILD_PASS',flush=True)
    except BaseException as exc:
        # Preserve diagnostics, restore only our generated DB from verified copy.
        if path.exists():path.unlink()
        for suffix in ('-wal','-shm','-journal'):
            side=path.with_name(path.name+suffix)
            if side.exists():side.unlink()
        with gzip.open(backup,'rb') as src,path.open('wb') as dst:
            for block in iter(lambda:src.read(8*1024*1024),b''):dst.write(block)
        assert sha(path)==original
        state.update(status='failed_reference_restored',error=str(exc));report.write_text(json.dumps(state,indent=2),encoding='utf-8');raise

if __name__=='__main__':main()
