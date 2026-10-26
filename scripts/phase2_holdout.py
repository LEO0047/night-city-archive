"""Independent evaluation: discovery output is frozen before fixtures are read.

Finding a residue is separate from proving the community's unobtainability claim.
This evaluator never rewrites a rule, confidence or discovery output.
"""
import collections,hashlib,json,re,sqlite3,unicodedata
from phase2_index import ROOT,OUT

def normalize(s):return ''.join(c for c in unicodedata.normalize('NFKD',s).casefold() if c.isalnum())

def main():
    raw=(OUT/'rules.json').read_bytes();rules_hash=hashlib.sha256(raw).hexdigest();rules=json.loads(raw)
    fixture_path=ROOT/'research/phase2/user-fixtures.json';fixtures=json.loads(fixture_path.read_text(encoding='utf-8'))
    e=sqlite3.connect('file:'+str(OUT/'evidence.db').replace('\\','/')+'?mode=ro',uri=True);e.row_factory=sqlite3.Row
    c=sqlite3.connect('file:'+str(ROOT/'data/archive.db').replace('\\','/')+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
    lookup={normalize(r['name']):r for r in rules['records'] if r['name']}
    byid={r['record_id']:r for r in rules['records']}
    locals_by_title=collections.defaultdict(list)
    for r in e.execute("SELECT hash,archive_id,key,secondary,female,pointer FROM localization WHERE language='en-us' AND kind='localizationPersistenceOnScreenEntries'"):
        if len(r['female'])<220:locals_by_title[normalize(r['female'])].append(dict(r))
    names_by_key=collections.defaultdict(set)
    for owner,value in e.execute("SELECT owner,value FROM flats WHERE source=? AND field='displayName'",(rules['snapshot'],)):
        v=json.loads(value);key=v.get('key') if isinstance(v,dict) else None
        if key:names_by_key[str(key)].add(owner)
    paths={r['hash']:r['path'] for r in c.execute('SELECT hash,path FROM assets')}
    flow=set(rules['flow_assets'])
    rows=[]
    def evaluate_record(f,rs,localization=None,journal=None):
        evidence={'records':[r['name'] or r['record_id'] for r in rs],'localization':localization or [],'journal_paths':journal or []}
        isolated=[r for r in rs if r['rule_status'] in ('DEFINITION_ONLY','ISOLATED_DEFINED_CONTENT')]
        channels=sorted({k for r in rs for k in r['channels']})
        if rs:
            lead=bool(isolated)
            # The fixture asks for an unobtainability classification, not merely
            # a filename hit or an isolated definition. Do not inflate recall.
            result='找到' if any(r['classification'] in ('確認遊戲內未使用','疑似刪除內容') for r in rs) else '漏掉'
            detail=f"已對應 {', '.join(r['name'] or r['record_id'] for r in rs)}；規則結果 {', '.join(sorted({r['rule_status'] for r in rs}))}。"
            detail+=('自動列出缺少已觀察使用入口的定義線索。' if lead else '系統保留使用關係，沒有把它列作孤立內容。')
            if channels:detail+='已見途徑：'+', '.join(channels)+'；這是可能使用鏈，並非實際取得紀錄。'
            detail+='不可取得的社群說法仍未證實；未達清單預期分類，記為漏掉／待核，而不是驗收通過。'
            if f.get('baseid')=='sq018_jackie_machete':detail+='本機型別為 gamedataItem_Record / Gen_Misc，不能把「非可用武器」改寫成「整個任務物品未使用」。'
            attribution='判定未定：仍缺執行與動態入口證據；不能據此裁定 wiki 有誤或版本差異'
        elif localization or journal:
            result='漏掉';detail=f"找到 {len({x['key'] for x in localization or []})} 個文字鍵與 {len(set(journal or []))} 條日誌路徑，但尚未對應到可驗證的道具使用鏈。"
            attribution='系統漏掉：目前解析與對應不足；wiki 資料有誤／版本差異未證實'
        else:
            result='漏掉';detail='已查目前兩份 canonical TweakDB、英文螢幕文字與日誌，未完成對應。不能因為這次沒找到就宣稱已從遊戲刪除。';attribution='原因未定：系統漏掉、wiki 資料有誤、版本差異均待證據'
        return dict(fixture_id=f['fixture_id'],name=f['name'],baseid=f.get('baseid'),category=f.get('category'),expected=f['expected'],result=result,detail=detail,attribution=attribution,residue_found=bool(rs or localization or journal),unobtainability_verified=False,classification_origin='rule_output_evaluated_against_community_claim',evidence=evidence,reproduce='python -X utf8 scripts/phase2_holdout.py'+(' # then phase2_query.py --record '+rs[0]['record_id'] if rs else ''))
    for f in fixtures['fixtures']:
        expected=f['expected'];base=f.get('baseid','')
        if expected in ('active','active_not_cut','not_cut') or f['fixture_id'].startswith('USER-C'):
            token=base.lower().replace('ep1 mq301','mq301');candidates=[]
            for h,path in paths.items():
                if token in path.lower() and path.endswith(('.quest','.questphase','.scene')) and h in flow:candidates.append({'hash':h,'path':path})
            flagged=[q for q in rules['quests'] if q['classification'] in ('確認遊戲內未使用','疑似刪除內容') and token in q['prefix'].lower()]
            active=bool(candidates);external=token=='ncart'
            rows.append(dict(fixture_id=f['fixture_id'],name=f['name'],baseid=base,expected=expected,result='誤判' if flagged else '找到' if active else '漏掉',detail=f'正式流程連通的場景／階段：{len(candidates)}；系統疑似刪除標記：{len(flagged)}。'+('NCART 另有 2.1 官方實裝記錄；此項要求本機引用也能對上，沒有以官方資料替系統補分。' if external else ''),attribution='本機規則正面對照' if active else '系統入口對應不足；不能判成廢案',origin='rule + independent official/user control',evidence=candidates[:10],reproduce='python -X utf8 scripts/phase2_holdout.py',false_positive=bool(flagged)))
            continue
        rs=[]
        for key in ((normalize('Items.'+base),normalize(base)) if base else ()):
            if key in lookup and lookup[key] not in rs:rs.append(lookup[key])
        loc=locals_by_title.get(normalize(f['name']),[])
        for l in loc:
            for rid in names_by_key[l['key']]:
                if rid in byid and byid[rid] not in rs:rs.append(byid[rid])
        if f['fixture_id'].startswith('USER-B'):
            r=evaluate_record(f,rs,loc);r['result']='找到' if r['residue_found'] else '未找到殘留';r['attribution']='只回報本版殘留；未下載舊版，移除版本未獨立驗證';r['detail']=f"目前對應 {len(rs)} 個記錄，{len({x['key'] for x in loc})} 個本機名稱鍵。"+r['detail'];rows.append(r)
        else:rows.append(evaluate_record(f,rs,loc))
    titles=(ROOT/'research/phase2/archived-conversation-titles.txt').read_text(encoding='utf-8').splitlines()
    # Exact title -> local string key -> journal node. No website baseid is invented.
    journals=[dict(r) for r in e.execute("SELECT path,node,hash,pointer FROM journal_nodes WHERE type IN ('gameJournalOnscreen','gameJournalFileEntry','gameJournalEmail','gameJournalInternetSite') OR path LIKE '%shards%'")]
    journalkeys=collections.defaultdict(list)
    for j in journals:
        node=json.loads(j['node'])
        title=node.get('title',{})
        if isinstance(title,dict):
            m=re.search(r'LocKey#(\d+)',str(title.get('value','')))
            if m:journalkeys[m[1]].append(j)
    for i,title in enumerate(titles,1):
        name='Archived Conversation: '+title;loc=locals_by_title.get(normalize(name),[]);jpaths=sorted({j['path'] for l in loc for j in journalkeys[l['key']]});rs=[]
        for path in jpaths:
            key=normalize('Items.'+path.rsplit('/',1)[-1])
            if key in lookup and lookup[key] not in rs:rs.append(lookup[key])
        f={'fixture_id':f'WIKI-AC-{i:02}','name':name,'expected':'unobtainable_community_claim','category':'對話紀錄'}
        row=evaluate_record(f,rs,loc,jpaths);row['origin']='Cyberpunk Wiki contributors category snapshot / CC-BY-SA; exact local title mapping';rows.append(row)
    result={'schema':'nca.phase2.holdout/v1','rules_sha256':rules_hash,'fixture_sha256':hashlib.sha256(fixture_path.read_bytes()).hexdigest(),'cases':rows,'counts':dict(collections.Counter(r['result'] for r in rows)),'notes':['For A/Archived Conversation positives, residue hits without the expected classification are reported as misses/pending, not successful cut-content detection. Positive controls and B residue-only cases have separate expectations.','Every positive community claim remains a hypothesis until acquisition routes are resolved; never turn a miss into a wiki error without evidence.','Archived Conversation titles are matched against local English title keys, not copied dialogue.']}
    assert hashlib.sha256((OUT/'rules.json').read_bytes()).hexdigest()==rules_hash
    (ROOT/'reports/phase2/holdout.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(result['counts'])

if __name__=='__main__':main()
