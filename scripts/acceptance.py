"""Repeatable local acceptance: provenance, regression fixtures, media, API and scope."""
import hashlib,json,sqlite3,struct,time,urllib.request,urllib.error,urllib.parse,wave
from pathlib import Path
from catalog import ROOT,connect
from text_index import fnv

def main():
    checks=[];db=connect();config=json.loads((ROOT/'config.json').read_text())
    def check(name,ok,detail=None):
        checks.append(dict(name=name,passed=bool(ok),detail=detail));print(('PASS ' if ok else 'FAIL ')+name,flush=True)
    count=lambda table:db.execute('SELECT count(*) FROM '+table).fetchone()[0]
    check('catalog_inventory',count('archives')==57 and count('assets')==553470 and count('entries')==592071,{k:count(k) for k in ('archives','assets','entries','refs','semantic_refs','documents','resources')})
    extensions=['.json','.scene','.quest','.questphase','.journal','.gamedef','.inkwidget','.inkanim','.inkatlas','.inkstyle','.inkhud','.inkmenu','.inklayers','.inktypography','.inkfullscreencomposition','.inkenginesettings','.inkgamesettings','.credits','.csv']
    missing=db.execute('SELECT count(*) FROM entries e JOIN assets a ON a.hash=e.hash LEFT JOIN resources r ON r.hash=e.hash AND r.archive_id=e.archive_id WHERE a.extension IN ('+','.join('?'*len(extensions))+') AND r.hash IS NULL',extensions).fetchone()[0]
    check('all_selected_structured_variants_decoded',missing==0,{'missing':missing,'extensions':extensions,'note':'Other binary types have path/archive references; not every binary field is decoded.'})
    fts=db.execute('SELECT count(*) FROM text_search').fetchone()[0]
    check('all_text_records_indexed',fts==count('documents'),{'records':fts,'note':'Includes localization IDs and resource fields; not a count of spoken sentences.'})
    fixtures=json.loads((ROOT/'research/community-fixtures.json').read_text(encoding='utf-8'))
    discovery=json.loads((ROOT/'data/discovery.json').read_text(encoding='utf-8'))
    found={x['id']:set(x['members']) for x in discovery['candidates']}
    for f in fixtures['positive']:
        check('community: '+f['name'],set(f['hashes'])<=found.get(f['expected_finding'],set()),f)
    for f in fixtures['negative']:
        reachable=db.execute('SELECT 1 FROM flow_reachability WHERE hash=?',(f['hash'],)).fetchone()
        cut=db.execute("SELECT f.id FROM finding_assets a JOIN findings f ON f.id=a.finding_id WHERE a.hash=? AND f.confidence IN ('確認遊戲內未使用','疑似刪除內容')",(f['hash'],)).fetchall()
        check('active control: '+f['name'],reachable and not cut,f)
    findings=[dict(r) for r in db.execute('SELECT * FROM findings')]
    valid=True
    for f in findings:
        d=json.loads(f['details']);stable='NCA-'+hashlib.sha256(f['slug'].encode()).hexdigest()[:12].upper()
        valid &= all((stable==f['id'],d['asset_count']>=2,bool(d['support']),bool(d['counter']),bool(d['sql']),bool(d['command'])))
    check('30_plus_grouped_reproducible_dossiers',len(findings)>=30 and valid,{'groups':len(findings),'confirmed_unused':sum(f['confidence']=='確認遊戲內未使用' for f in findings)})
    sample=db.execute("SELECT hash,path FROM assets WHERE path LIKE 'base%mq009%' AND extension='.scene' LIMIT 1").fetchone()
    check('path_hash_roundtrip',fnv(sample['path'])==sample['hash'],dict(sample))
    check('sqlite_quick_check',db.execute('PRAGMA quick_check').fetchone()[0]=='ok')
    # Verify actual generated media, not placeholder assets.
    glb=ROOT/'data/media/3817949997515060327.glb';raw=glb.read_bytes()
    magic,version,length=struct.unpack_from('<4sII',raw);chunk_size,chunk_type=struct.unpack_from('<I4s',raw,12)
    model=json.loads(raw[20:20+chunk_size]);vertices=sum(a.get('count',0) for a in model['accessors'] if a['type']=='VEC3')
    check('real_model_glb',magic==b'glTF' and version==2 and length==len(raw) and vertices>0,{'bytes':len(raw),'vec3_accessor_elements':vertices})
    png=(ROOT/'data/media/2728351791735005788.png').read_bytes();w,h=struct.unpack_from('>II',png,16)
    check('real_texture_png',png.startswith(b'\x89PNG\r\n\x1a\n') and w>0 and h>0,{'width':w,'height':h})
    with wave.open(str(ROOT/'data/media/5193555934131789.wav'),'rb') as audio:
        duration=audio.getnframes()/audio.getframerate();frames=audio.readframes(audio.getnframes())
    check('real_voice_wav',duration>0 and any(frames),{'seconds':duration,'sample_hash':'5193555934131789','note':'Playback capability sample; not itself classified as cut content.'})
    base=f'http://127.0.0.1:{config["port"]}'
    def http(path,method='GET',headers=None):
        req=urllib.request.Request(base+path,method=method,headers=headers or {})
        try:
            with urllib.request.urlopen(req,timeout=60) as r:return r.status,r.read(),dict(r.headers)
        except urllib.error.HTTPError as e:return e.code,e.read(),dict(e.headers)
    timings={}
    for name,params in [('English subtitle',{'q':'Where\'s the cash','kind':'text'}),('Chinese text',{'q':'夜之城','kind':'text'}),('Quest path',{'q':'mq009','kind':'assets'}),('Stable asset ID',{'q':'NCA-ASSET-5193555934131789','kind':'assets'})]:
        started=time.time();status,body,_=http('/api/search?'+urllib.parse.urlencode(params));timings[name]=round((time.time()-started)*1000,1)
        result=json.loads(body);check('search: '+name,status==200 and len(result.get('results',[]))>0,{'milliseconds':timings[name],'returned':len(result.get('results',[]))})
    status,body,_=http('/api/asset/5193555934131789');asset=json.loads(body)
    check('archive_and_reference_provenance',status==200 and len(asset['archives'][0]['sha256'])==64 and any(x['path'].endswith('voiceovermap.json') for x in asset['incoming']))
    check('cross_origin_conversion_blocked',http('/api/preview/5193555934131789','POST',{'Origin':'https://example.invalid'})[0]==403)
    check('foreign_host_blocked',http('/api/stats',headers={'Host':'example.invalid'})[0]==403)
    check('directory_traversal_blocked',http('/media/%2e%2e/%2e%2e/config.json')[0]==404)
    game=ROOT/'reports/game-after-summary.json'
    integrity=json.loads(game.read_text()) if game.exists() else {}
    check('original_game_unchanged',integrity.get('unchanged') is True,integrity)
    usage=sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file())
    check('approved_storage_cap',usage<config['storage_limit_bytes'],{'bytes':usage,'limit':config['storage_limit_bytes']})
    result={'completed_at_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'passed':all(x['passed'] for x in checks),'passed_checks':sum(x['passed'] for x in checks),'total_checks':len(checks),'community_scope':fixtures['scope_note'],'checks':checks}
    (ROOT/'reports/acceptance.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='checks'},ensure_ascii=False,indent=2),flush=True)
    if not result['passed']:raise SystemExit(1)

if __name__=='__main__':main()
