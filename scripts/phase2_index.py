"""Rebuild a supplemental evidence index. No fixture IDs or manual classifications.

The first-phase database is opened read-only and is never updated here.
"""
import argparse,collections,gzip,hashlib,json,pathlib,re,sqlite3,sys,time,zlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'data/phase2'

def tweak_id(value):
    if value.isdecimal():return value
    return str(zlib.crc32(value.encode())+(len(value.encode())<<32))

def asset_id(path):
    if path.isdecimal():return path
    h=14695981039346656037
    for byte in path.lower().replace('/','\\').encode():h=((h^byte)*1099511628211)&0xffffffffffffffff
    return str(h)

def typed(node,pointer=''):
    if isinstance(node,dict):
        if node.get('$type') in ('TweakDBID','ResourcePath'):
            value=str(node.get('$value',''))
            if value not in ('','0','None'):yield node['$type'],value,pointer+'/$value'
        for key,value in node.items():
            if isinstance(value,(dict,list)):yield from typed(value,pointer+'/'+key)
    elif isinstance(node,list):
        for index,value in enumerate(node):yield from typed(value,pointer+'/'+str(index))

def category(typ):
    return {'gamedataVehicle_Record':'車輛','gamedataWeaponItem_Record':'武器','gamedataClothing_Record':'服裝','gamedataCharacter_Record':'角色','gamedataItem_Record':'其他道具','gamedataConsumableItem_Record':'其他道具'}.get(typ,'')

def keep_resource_field(pointer,value,red_type):
    if value in ('','0','None'):return False
    if red_type in ('TweakDBID','ResourcePath','NodeRef'):return True
    return bool(re.search(r'/(?:tags|tag|recordID|recordId|journalPath|journalEntry|appearanceName|factName|entityID|entityId|itemID|itemId|debugName)/',pointer) or re.search(r'/appearances/\d+/(?:Data/)?name/',pointer))

SCHEMA='''
CREATE TABLE sources(key TEXT PRIMARY KEY,sha256 TEXT,input_sha256 TEXT,kind TEXT);
CREATE TABLE records(source TEXT,id TEXT,name TEXT,type TEXT,category TEXT,PRIMARY KEY(source,id));
CREATE TABLE flats(source TEXT,id TEXT,owner TEXT,field TEXT,type TEXT,value TEXT,PRIMARY KEY(source,id));
CREATE TABLE tweak_edges(source TEXT,owner TEXT,target TEXT,field TEXT,pointer TEXT);
CREATE TABLE asset_refs(source TEXT,owner TEXT,target TEXT,path TEXT,field TEXT,pointer TEXT);
CREATE TABLE coverage(source TEXT PRIMARY KEY,report TEXT);
CREATE TABLE resource_fields(hash TEXT,archive TEXT,pointer TEXT,value TEXT,red_type TEXT);
CREATE TABLE resource_scan(hash TEXT,archive TEXT,path TEXT,types TEXT,PRIMARY KEY(hash,archive));
CREATE INDEX rec_name ON records(name);CREATE INDEX rec_category ON records(category);
CREATE INDEX flat_owner ON flats(owner);CREATE INDEX te_source ON tweak_edges(owner);CREATE INDEX te_target ON tweak_edges(target);
CREATE INDEX ar_owner ON asset_refs(owner);CREATE INDEX ar_target ON asset_refs(target);
CREATE INDEX rf_hash ON resource_fields(hash);CREATE INDEX rf_value ON resource_fields(value);
'''

def index_tweaks(db):
    keep={'displayName','localizedDescription','description','entityTemplatePath','appearanceName','itemType','equipArea','isIconic','isQuest','tags','isHidden','isGarment','attachmentSlots','journalEntry','journalPath','audioName','savable','isPlayerVehicle','manufacturer','entityTemplate','isPart'}
    for name in ['r6_cache_tweakdb.bin.jsonl.gz','r6_cache_tweakdb_ep1.bin.jsonl.gz']:
        path=OUT/name;source=name.removesuffix('.jsonl.gz').replace('r6_cache_','r6/cache/')
        meta=json.loads(path.with_name(path.name+'.manifest.json').read_text(encoding='utf-8-sig'))
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest.upper()==meta['output_sha256'].upper()
        db.execute('INSERT INTO sources VALUES(?,?,?,?)',(source,digest,meta['source_sha256'],'WolvenKit TweakDB'))
        counts=collections.Counter();names={};types={}
        with gzip.open(path,'rt',encoding='utf-8') as stream:
            for line in stream:
                row=json.loads(line);kind=row['kind'];counts[kind]+=1
                if kind=='record':
                    rid=row['id'];names[row.get('name')]=rid;types[rid]=row['type']
                    db.execute('INSERT INTO records VALUES(?,?,?,?,?)',(source,rid,row.get('name'),row['type'],category(row['type'])))
                elif kind=='flat':
                    name=row.get('name') or '';parent,_,field=name.rpartition('.')
                    owner=names.get(parent,'flat:'+row['id'])
                    if not name:counts['unresolved_flat_names']+=1
                    if owner.startswith('flat:'):counts['unresolved_flat_owners']+=1
                    value=row['value']
                    for typ,target,pointer in typed(value):
                        if typ=='TweakDBID':
                            db.execute('INSERT INTO tweak_edges VALUES(?,?,?,?,?)',(source,owner,tweak_id(target),field,pointer));counts['record_edges']+=1
                        else:
                            db.execute('INSERT INTO asset_refs VALUES(?,?,?,?,?,?)',(source,owner,asset_id(target),target,field,pointer));counts['asset_refs']+=1
                    if field in keep or row['type']=='gamedataLocKeyWrapper':
                        db.execute('INSERT INTO flats VALUES(?,?,?,?,?,?)',(source,row['id'],owner,field,row['type'],json.dumps(value,ensure_ascii=False,separators=(',',':'))))
                if sum(counts[k] for k in ['record','flat','query'])%100000==0:db.commit()
        db.execute('INSERT INTO coverage VALUES(?,?)',(source,json.dumps(counts)));db.commit();print(source,json.dumps(counts),flush=True)

def index_resources(db):
    directories=[('resource-scans',''),('resource-scans-retry','retry/'),('resource-scans-extra','extra/'),('resource-scans-recovery','recovery/')]
    paths=[(path,prefix) for directory,prefix in directories for path in sorted((OUT/directory).glob('*.jsonl.gz'))]
    for path,prefix in paths:
        source='resources/'+prefix+path.name
        if db.execute('SELECT 1 FROM sources WHERE key=?',(source,)).fetchone():continue
        db.execute('INSERT INTO sources VALUES(?,?,?,?)',(source,hashlib.sha256(path.read_bytes()).hexdigest(),'see archive table','WolvenKit CR2W compact fields'))
        count=fields=0
        with gzip.open(path,'rt',encoding='utf-8') as stream:
            for line in stream:
                row=json.loads(line)
                db.execute('INSERT INTO resource_scan VALUES(?,?,?,?)',(row['hash'],row['archive'],row['path'],json.dumps(row['types'])))
                # Full compact fields remain in the gzip source. The SQL layer
                # indexes runtime identities/references, not every bone name.
                selected=[f for f in row['fields'] if keep_resource_field(f['pointer'],f['value'],f.get('red_type',''))]
                # Keep one exact witness per value/type/resource. All occurrences
                # remain in the compact source; SQL is a lookup, not a full tree.
                unique={}
                for f in selected:
                    key=(f['value'],f.get('red_type',''))
                    unique[key]=min(unique.get(key,f['pointer']),f['pointer'])
                values=[(row['hash'],row['archive'],ptr,v,typ) for (v,typ),ptr in sorted(unique.items())]
                db.executemany('INSERT INTO resource_fields VALUES(?,?,?,?,?)',values)
                count+=1;fields+=len(values)
                if count%500==0:
                    if sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file())>19_500_000_000:raise RuntimeError('Stop before the approved 20 GB cap.')
        db.commit();db.execute('PRAGMA wal_checkpoint(TRUNCATE)');print(source,count,fields,flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',default='evidence.db');p.add_argument('--resources-only',action='store_true');p.add_argument('--rebuild-memory-journal',action='store_true');args=p.parse_args()
    target=(OUT/args.output).resolve()
    if not target.is_relative_to(OUT.resolve()):raise SystemExit('Output must remain in phase2 data.')
    if target.exists() and not args.resources_only:raise SystemExit('Output exists; choose a fresh verification name.')
    if not target.exists() and args.resources_only:raise SystemExit('Build tweak index first.')
    db=sqlite3.connect(target);db.execute('PRAGMA journal_mode='+('MEMORY' if args.rebuild_memory_journal else 'WAL'));db.execute('PRAGMA synchronous=NORMAL')
    if not args.resources_only:db.executescript(SCHEMA);index_tweaks(db)
    index_resources(db);db.commit();db.execute('PRAGMA wal_checkpoint(TRUNCATE)');print('complete',str(target),target.stat().st_size,flush=True);db.close()

if __name__=='__main__':main()
