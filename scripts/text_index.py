"""Index local WolvenKit JSON, preserving complete compressed resource records."""
import collections,gzip,json,re,sqlite3,zlib,sys,time
from catalog import ROOT,connect
from ink_paths import iter_paths
sys.setrecursionlimit(10000)

def leaves(node,pointer=''):
    stack=[(node,pointer)]
    while stack:
        obj,p=stack.pop()
        if isinstance(obj,dict):
            stack.extend((v,p+'/'+str(k).replace('~','~0').replace('/','~1')) for k,v in reversed(list(obj.items())) if k not in ('$type','$storage','HandleId','BufferId','Version','BuildVersion'))
        elif isinstance(obj,list):stack.extend((v,p+'/'+str(i)) for i,v in reversed(list(enumerate(obj))))
        elif isinstance(obj,str) and len(obj)>1 and obj not in ('None','PLATFORM_PC'):yield p,obj

def fnv(path):
    value=14695981039346656037
    for byte in path.lower().replace('/','\\').encode('utf-8'):
        value=((value^byte)*1099511628211)&0xffffffffffffffff
    return str(value)

def main():
    db=connect();db.executescript('''
    CREATE TABLE IF NOT EXISTS resources(hash TEXT,archive_id INTEGER,json_zlib BLOB,root_class TEXT,PRIMARY KEY(hash,archive_id));
    CREATE TABLE IF NOT EXISTS semantic_refs(source_hash TEXT,archive_id INTEGER,target_hash TEXT,target_path TEXT,field TEXT,position INTEGER,UNIQUE(source_hash,archive_id,target_hash,field,position));
    CREATE INDEX IF NOT EXISTS sr_source ON semantic_refs(source_hash);
    CREATE INDEX IF NOT EXISTS sr_target ON semantic_refs(target_hash);
    CREATE TABLE IF NOT EXISTS ingest_files(name TEXT PRIMARY KEY,resources INTEGER,documents INTEGER);
    ''')
    archive_ids={r['path']:r['id'] for r in db.execute('select * from archives')}
    extension={r['hash']:r['extension'] for r in db.execute('select hash,extension from assets')}
    total=0
    sources=sorted((ROOT/'data/decoded').glob('*.jsonl.gz'))+sorted((ROOT/'data/decoded-retry').glob('*.jsonl.gz'))
    for source in sources:
        source_key=('retry-' if source.parent.name=='decoded-retry' else '')+source.name
        if db.execute('SELECT 1 FROM ingest_files WHERE name=?',(source_key,)).fetchone():continue
        count=0;docs=0
        with gzip.open(source,'rt',encoding='utf-8') as stream:
            for line in stream:
                row=json.loads(line);h=row['hash'];aid=archive_ids[row['archive']];data=row['data']
                lang_match=re.search(r'localization\\([^\\]+)',row['path']);lang=lang_match.group(1) if lang_match else ''
                root=data.get('Data',{}).get('RootChunk',{}) if isinstance(data,dict) else {}
                blob=zlib.compress(json.dumps(data,ensure_ascii=False,separators=(',',':')).encode(),3)
                db.execute('INSERT OR REPLACE INTO resources VALUES(?,?,?,?)',(h,aid,blob,root.get('$type','JSON')))
                refs=iter_paths(data)
                db.executemany('INSERT OR IGNORE INTO semantic_refs VALUES(?,?,?,?,?,?)',[(h,aid,p if p.isdecimal() else fnv(p),p,f,i) for p,f,i in refs])
                leaf=list(leaves(data.get('Data',data) if isinstance(data,dict) else data))
                # Localization sentences retain exact JSON Pointers; structural resources use one complete string corpus.
                if extension[h]=='.json':
                    texts=[(p,t) for p,t in leaf if t.strip() and not t.startswith(('base\\','ep1\\'))]
                else:texts=[('/','\n'.join(dict.fromkeys(t for p,t in leaf)))]
                for field,text in texts:
                    if not text:continue
                    old=db.execute('SELECT id FROM documents WHERE hash=? AND archive_id=? AND field=?',(h,aid,field)).fetchone()
                    if old:continue
                    did=db.execute('INSERT INTO documents(hash,archive_id,kind,field,text,language) VALUES(?,?,?,?,?,?)',(h,aid,extension[h],field,text,lang)).lastrowid
                    db.execute('INSERT INTO text_search(doc_id,text) VALUES(?,?)',(did,text));docs+=1
                    if docs%20000==0:
                        db.commit()
                        if sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file())>19_000_000_000:
                            raise RuntimeError('Storage guard: stop indexing before the approved 20 GB cap.')
                count+=1;total+=1
                if count%1000==0:
                    db.commit();print(f'{source.name}: {count} resources / {docs} text records',flush=True)
                    if sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file())>19_000_000_000:
                        raise RuntimeError('Storage guard stopped indexing below the approved 20 GB limit; explicit approval required to expand.')
        db.execute('INSERT INTO ingest_files VALUES(?,?,?)',(source_key,count,docs));db.commit()
        print(f'FINISHED {source.name}: {count} resources, {docs} documents',flush=True)
    report={k:db.execute('select count(*) from '+k).fetchone()[0] for k in ['resources','documents','semantic_refs','ingest_files']}
    (ROOT/'reports/text-coverage.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    db.execute('PRAGMA wal_checkpoint(TRUNCATE)');print(json.dumps(report),flush=True)

if __name__=='__main__':main()
