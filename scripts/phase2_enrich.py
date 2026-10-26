"""Supplement record labels and lifecycle fields, without any fixture input."""
import gzip,json,sqlite3
from phase2_index import ROOT,OUT

def main():
    db=sqlite3.connect(OUT/'evidence.db');db.execute('CREATE TABLE IF NOT EXISTS record_properties(source TEXT,id TEXT,owner TEXT,field TEXT,value TEXT,PRIMARY KEY(source,id))')
    db.execute('CREATE INDEX IF NOT EXISTS rp_owner ON record_properties(owner)')
    keep={'entityName','deprecated','fullDisplayName','canDrop','appearanceResourceName'}
    for filename in ('r6_cache_tweakdb.bin.jsonl.gz','r6_cache_tweakdb_ep1.bin.jsonl.gz'):
        source=filename.removesuffix('.jsonl.gz').replace('r6_cache_','r6/cache/')
        names=dict(db.execute('SELECT name,id FROM records WHERE source=?',(source,)))
        with gzip.open(OUT/filename,'rt',encoding='utf-8') as f:
            for line in f:
                row=json.loads(line)
                if row['kind']!='flat':continue
                parent,_,field=(row.get('name') or '').rpartition('.')
                if field in keep and parent in names:db.execute('INSERT OR REPLACE INTO record_properties VALUES(?,?,?,?,?)',(source,row['id'],names[parent],field,json.dumps(row['value'],ensure_ascii=False,separators=(',',':'))))
        db.commit()
    print('record properties',db.execute('SELECT count(*) FROM record_properties').fetchone()[0],flush=True);db.close()

if __name__=='__main__':main()
