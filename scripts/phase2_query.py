"""Read-only reproducible evidence queries; outputs local research, never uploads."""
import argparse,json,sqlite3
from phase2_index import ROOT,OUT

def main():
    p=argparse.ArgumentParser();p.add_argument('--record');p.add_argument('--quest');p.add_argument('--operations');p.add_argument('--route');p.add_argument('--dossier');p.add_argument('--sql');p.add_argument('--db',choices=['core','evidence'],default='evidence');a=p.parse_args()
    if a.route:
        parents=json.loads((OUT/'asset-reachability.json').read_text());c=sqlite3.connect('file:'+str(ROOT/'data/archive.db').replace('\\','/')+'?mode=ro',uri=True);h=a.route;route=[]
        while h is not None and h in parents:
            row=c.execute('SELECT path FROM assets WHERE hash=?',(h,)).fetchone();route.append({'hash':h,'path':row[0] if row else h});h=parents[h]
        print(json.dumps(route[::-1],ensure_ascii=False,indent=2));return
    if a.operations:
        print(json.dumps([r for r in json.loads((OUT/'quest-operations.json').read_text(encoding='utf-8')) if a.operations in (r['record'],r['record_id'])],ensure_ascii=False,indent=2));return
    if a.dossier:
        d=json.loads((ROOT/'web/catalogue.json').read_text(encoding='utf-8'));ident=d['aliases'].get(a.dossier,a.dossier)
        print(json.dumps(next((f for f in d['findings'] if f['id']==ident),None),ensure_ascii=False,indent=2));return
    if a.sql:
        path=ROOT/'data/archive.db' if a.db=='core' else OUT/'evidence.db'
        db=sqlite3.connect('file:'+str(path).replace('\\','/')+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
        print(json.dumps([dict(r) for r in db.execute(a.sql)],ensure_ascii=False,indent=2));return
    rules=json.loads((OUT/'rules.json').read_text(encoding='utf-8'))
    if a.record:
        result=[r for r in rules['records'] if a.record in (r['record_id'],r['name'],r['id'])]
        db=sqlite3.connect('file:'+str(OUT/'evidence.db').replace('\\','/')+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
        for r in result:
            r['definitions']=[dict(d) for d in db.execute('SELECT r.*,s.input_sha256 source_sha256 FROM records r JOIN sources s ON s.key=r.source WHERE r.id=? ORDER BY source',(r['record_id'],))]
            for d in r['definitions']:
                d['properties']=[dict(v) for v in db.execute('SELECT field,type,value FROM flats WHERE source=? AND owner=? ORDER BY field',(d['source'],r['record_id']))]
                for v in d['properties']:v['value']=json.loads(v['value'])
    elif a.quest:result=[q for q in rules['quests'] if a.quest.lower() in q['prefix'].lower()]
    else:result={k:v for k,v in rules.items() if k not in ('records','quests')}
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
