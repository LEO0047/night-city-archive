"""Rebuild the SQLite asset catalog from WolvenKit's read-only archive dump."""
import collections, hashlib, json, sqlite3, time, os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DB=Path(os.environ.get('NCA_DATABASE',str(ROOT/'data/archive.db'))).resolve()
if not DB.is_relative_to((ROOT/'data').resolve()):
    raise RuntimeError('Database must remain inside this project data directory.')
SCHEMA='''
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT);
CREATE TABLE IF NOT EXISTS archives(id INTEGER PRIMARY KEY,path TEXT UNIQUE,sha256 TEXT,size INTEGER,entries INTEGER);
CREATE TABLE IF NOT EXISTS assets(hash TEXT PRIMARY KEY,path TEXT,extension TEXT,size INTEGER,archive_id INTEGER,variants INTEGER DEFAULT 1);
CREATE TABLE IF NOT EXISTS entries(id INTEGER PRIMARY KEY,hash TEXT,archive_id INTEGER,size INTEGER,compressed INTEGER,sha1 TEXT, UNIQUE(hash,archive_id));
CREATE TABLE IF NOT EXISTS refs(source_entry INTEGER,source_hash TEXT,target_hash TEXT,kind TEXT DEFAULT 'archive_dependency');
CREATE TABLE IF NOT EXISTS documents(id INTEGER PRIMARY KEY,hash TEXT,archive_id INTEGER,kind TEXT,field TEXT,text TEXT,language TEXT DEFAULT '', UNIQUE(hash,archive_id,field));
CREATE TABLE IF NOT EXISTS media(hash TEXT PRIMARY KEY,kind TEXT,file TEXT,status TEXT,detail TEXT);
CREATE TABLE IF NOT EXISTS findings(id TEXT PRIMARY KEY,slug TEXT UNIQUE,title TEXT,category TEXT,confidence TEXT,community TEXT,summary TEXT,details TEXT,score REAL);
CREATE TABLE IF NOT EXISTS finding_assets(finding_id TEXT,hash TEXT,role TEXT,PRIMARY KEY(finding_id,hash));
CREATE VIRTUAL TABLE IF NOT EXISTS asset_search USING fts5(hash UNINDEXED,path, tokenize='trigram');
CREATE VIRTUAL TABLE IF NOT EXISTS text_search USING fts5(doc_id UNINDEXED,text, tokenize='trigram');
CREATE INDEX IF NOT EXISTS idx_entry_hash ON entries(hash);
CREATE INDEX IF NOT EXISTS idx_refs_source ON refs(source_hash);
CREATE INDEX IF NOT EXISTS idx_refs_target ON refs(target_hash);
CREATE INDEX IF NOT EXISTS idx_assets_ext ON assets(extension);
CREATE INDEX IF NOT EXISTS idx_docs_hash ON documents(hash);
'''

def connect():
    db=sqlite3.connect(DB,timeout=60); db.row_factory=sqlite3.Row
    return db

def build():
    db=connect(); db.executescript(SCHEMA)
    if db.execute('SELECT count(*) FROM assets').fetchone()[0]:
        raise RuntimeError('Refusing to mix scans in an existing database. Use Rebuild.ps1 to build an empty database and verify it.')
    for table in ['archives','assets','entries','refs','asset_search']:
        db.execute(f'DELETE FROM {table}')
    manifest={r['path']:r for r in map(json.loads,(ROOT/'reports/game-before.jsonl').read_text(encoding='utf-8').splitlines())}
    archives={}
    for row in map(json.loads,(ROOT/'data/archives.jsonl').read_text(encoding='utf-8').splitlines()):
        cursor=db.execute('INSERT INTO archives(path,sha256,size,entries) VALUES(?,?,?,?)',(row['path'],manifest[row['path']]['sha256'],row['size'],row['entries']))
        archives[row['path']]=cursor.lastrowid
    counts=collections.Counter(); size=collections.Counter(); count=0
    with (ROOT/'data/archive-index.jsonl').open(encoding='utf-8') as source:
        for line in source:
            row=json.loads(line); aid=archives[row['archive']]
            db.execute('INSERT INTO assets VALUES(?,?,?,?,?,1) ON CONFLICT(hash) DO UPDATE SET variants=variants+1', (row['hash'],row['path'],row['extension'],row['size'],aid))
            eid=db.execute('INSERT INTO entries(hash,archive_id,size,compressed,sha1) VALUES(?,?,?,?,?)',(row['hash'],aid,row['size'],row['compressed'],row['sha1'])).lastrowid
            db.executemany('INSERT INTO refs(source_entry,source_hash,target_hash) VALUES(?,?,?)',[(eid,row['hash'],h) for h in row['dependencies']])
            counts[row['extension']]+=1;size[row['extension']]+=row['size'];count+=1
            if count%50000==0: db.commit(); print(f'Indexed {count}',flush=True)
    db.execute('INSERT INTO asset_search(hash,path) SELECT hash,path FROM assets')
    for k,v in json.loads((ROOT/'config.json').read_text()).items(): db.execute('INSERT OR REPLACE INTO meta VALUES(?,?)',(k,json.dumps(v,ensure_ascii=False)))
    db.execute('INSERT OR REPLACE INTO meta VALUES(?,?)',('canonical_policy',json.dumps('All archive variants retained; primary preview uses first indexed variant. This is not a claim of runtime override precedence.')))
    db.commit(); db.execute('PRAGMA wal_checkpoint(TRUNCATE)')
    report={'entries':count,'unique_assets':db.execute('SELECT count(*) FROM assets').fetchone()[0],'references':db.execute('SELECT count(*) FROM refs').fetchone()[0],
            'extensions':[{"extension":e,"entries":c,"bytes":size[e]} for e,c in counts.most_common()]}
    (ROOT/'reports/catalog.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='extensions'}))

if __name__=='__main__':build()
