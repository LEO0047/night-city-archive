"""Index typed quest references, journal paths, localization and script literals.

No acceptance fixture is read. Game and first-phase archive databases are read-only.
Full game text stays in the ignored private evidence database.
"""
import argparse, collections, hashlib, json, pathlib, re, sqlite3, zlib
from phase2_index import ROOT, OUT, tweak_id

def walk(node,pointer=''):
    yield pointer,node
    if isinstance(node,dict):
        for k,v in node.items():yield from walk(v,pointer+'/'+k.replace('~','~0').replace('/','~1'))
    elif isinstance(node,list):
        for i,v in enumerate(node):yield from walk(v,pointer+'/'+str(i))

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',default='evidence.db');p.add_argument('--rebuild-memory-journal',action='store_true');args=p.parse_args()
    target=(OUT/args.output).resolve();assert target.is_relative_to(OUT.resolve())
    db=sqlite3.connect(target);db.execute('PRAGMA journal_mode='+('MEMORY' if args.rebuild_memory_journal else 'WAL'))
    core=sqlite3.connect('file:'+str(ROOT/'data/archive.db').replace('\\','/')+'?mode=ro',uri=True)
    db.executescript('''
    CREATE TABLE IF NOT EXISTS context_sources(key TEXT PRIMARY KEY,sha256 TEXT,rows INTEGER);
    CREATE TABLE IF NOT EXISTS core_fields(hash TEXT,archive_id INTEGER,pointer TEXT,value TEXT,red_type TEXT);
    CREATE INDEX IF NOT EXISTS cf_value ON core_fields(value);
    CREATE INDEX IF NOT EXISTS cf_hash ON core_fields(hash);
    CREATE TABLE IF NOT EXISTS journal_nodes(hash TEXT,archive_id INTEGER,pointer TEXT,path TEXT,type TEXT,node TEXT);
    CREATE INDEX IF NOT EXISTS jn_path ON journal_nodes(path);
    CREATE TABLE IF NOT EXISTS localization(hash TEXT,archive_id INTEGER,language TEXT,kind TEXT,key TEXT,secondary TEXT,female TEXT,male TEXT,pointer TEXT);
    CREATE INDEX IF NOT EXISTS loc_key ON localization(key);
    CREATE INDEX IF NOT EXISTS loc_secondary ON localization(secondary);
    CREATE TABLE IF NOT EXISTS script_refs(line INTEGER,owner TEXT,literal TEXT,target TEXT,context TEXT);
    CREATE INDEX IF NOT EXISTS script_target ON script_refs(target);
    ''')
    if not db.execute("SELECT 1 FROM context_sources WHERE key='core'").fetchone():
        # A prior interrupted pass is replaced transactionally.
        for t in ['core_fields','journal_nodes','localization']:db.execute('DELETE FROM '+t)
        counts=collections.Counter()
        q='SELECT r.hash,r.archive_id,a.path,a.extension,r.json_zlib FROM resources r JOIN assets a USING(hash) ORDER BY r.hash,r.archive_id'
        for h,aid,path,ext,blob in core.execute(q):
            if ext not in ('.quest','.questphase','.scene','.gamedef','.journal','.json','.inkwidget','.inkanim','.inkstyle','.inkmenu','.inkhud','.inklayers','.inkgamesettings','.inkenginesettings'):continue
            if '\\localization\\' in path and not any('\\'+lang+'\\' in path for lang in ('en-us','zh-tw')):continue
            data=json.loads(zlib.decompress(blob));counts['resources']+=1
            if ext=='.json':
                root=data.get('Data',{}).get('RootChunk',{}).get('root',{}).get('Data',{}) if isinstance(data,dict) else {}
                kind=root.get('$type','');language=next((x for x in path.split('\\') if re.fullmatch(r'[a-z]{2}-[a-z]{2}',x)),'')
                if kind in ('localizationPersistenceOnScreenEntries','localizationPersistenceSubtitleEntries'):
                    rows=[(h,aid,language,kind,str(e.get('primaryKey',e.get('stringId',''))),e.get('secondaryKey',''),e.get('femaleVariant',''),e.get('maleVariant',''),f'/Data/RootChunk/root/Data/entries/{i}') for i,e in enumerate(root.get('entries',[]))]
                    db.executemany('INSERT INTO localization VALUES(?,?,?,?,?,?,?,?,?)',rows);counts['localization']+=len(rows)
                    continue
            fields=[]
            for ptr,node in walk(data):
                if isinstance(node,dict) and node.get('$type') in ('TweakDBID','NodeRef'):
                    v=str(node.get('$value',''))
                    if v not in ('','0','None'):fields.append((h,aid,ptr+'/$value',v,node['$type']))
                # journal references are locator evidence, not runtime acquisition.
                elif isinstance(node,str) and (ptr.endswith('/path') or ptr.endswith('/journalPath')) and node:
                    fields.append((h,aid,ptr,node,'journal_path'))
            db.executemany('INSERT INTO core_fields VALUES(?,?,?,?,?)',fields);counts['typed_fields']+=len(fields)
            if ext=='.journal':
                def journal(node,ptr='',trail=()):
                    if isinstance(node,dict):
                        ident=node.get('id');current=trail+((ident,) if isinstance(ident,str) and ident else ())
                        if isinstance(ident,str) and ident:
                            compact={k:v for k,v in node.items() if k!='entries'}
                            db.execute('INSERT INTO journal_nodes VALUES(?,?,?,?,?,?)',(h,aid,ptr,'/'.join(current),node.get('$type',''),json.dumps(compact,ensure_ascii=False)))
                            counts['journal_nodes']+=1
                        for k,v in node.items():journal(v,ptr+'/'+k,current)
                    elif isinstance(node,list):
                        for i,v in enumerate(node):journal(v,ptr+'/'+str(i),trail)
                journal(data)
            if counts['resources']%1000==0:print(dict(counts),flush=True)
        db.execute('INSERT INTO context_sources VALUES(?,?,?)',('core','logical source: reports/rebuild.json',counts['resources']));db.commit()
        print('Core context',dict(counts),flush=True)
    path=OUT/'scripts/final.reds';digest=hashlib.sha256(path.read_bytes()).hexdigest()
    if not db.execute('SELECT 1 FROM context_sources WHERE key=? AND sha256=?',('scripts',digest)).fetchone():
        db.execute('DELETE FROM script_refs');owner='';n=0
        for number,line in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
            if re.search(r'\b(?:func|class)\b',line):owner=line.strip()
            for value in re.findall(r'(?<![A-Za-z0-9_\"])t\"([^\"\n]+)\"',line):
                db.execute('INSERT INTO script_refs VALUES(?,?,?,?,?)',(number,owner,value,tweak_id(value),line.strip()));n+=1
        db.execute('INSERT OR REPLACE INTO context_sources VALUES(?,?,?)',('scripts',digest,n));db.commit();print('Script literals',n,flush=True)
    db.execute('PRAGMA wal_checkpoint(TRUNCATE)');db.close()

if __name__=='__main__':main()
