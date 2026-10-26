"""Reproduce evidence with a read-only SQLite connection."""
import argparse,json,sqlite3,sys
from catalog import ROOT,DB

def main():
    p=argparse.ArgumentParser();p.add_argument('--sql');p.add_argument('--file');p.add_argument('--finding');p.add_argument('--asset');p.add_argument('--limit',type=int,default=1000);a=p.parse_args()
    db=sqlite3.connect(DB.as_uri()+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
    if a.finding:
        row=db.execute('SELECT * FROM findings WHERE id=?',(a.finding,)).fetchone()
        if not row:raise SystemExit('Unknown finding ID')
        result=dict(row);result['details']=json.loads(result['details'])
        result['assets']=[dict(r) for r in db.execute('SELECT a.* FROM finding_assets f JOIN assets a ON a.hash=f.hash WHERE finding_id=?',(a.finding,))]
        print(json.dumps(result,ensure_ascii=False,indent=2));return
    if a.asset:
        sql='SELECT a.*,r.path archive,r.sha256 archive_sha256,e.sha1 FROM assets a JOIN entries e ON e.hash=a.hash JOIN archives r ON r.id=e.archive_id WHERE a.hash=?';args=[a.asset]
    else:sql=a.sql or (open(a.file,encoding='utf-8').read() if a.file else sys.stdin.read());args=[]
    db.execute('PRAGMA query_only=ON')
    print(json.dumps([dict(r) for r in db.execute(sql,args).fetchmany(a.limit)],ensure_ascii=False,indent=2))

if __name__=='__main__':main()
