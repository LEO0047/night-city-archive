"""Generic candidate discovery. No community fixture hashes or quest IDs are used here."""
import collections,hashlib,json,re
from catalog import ROOT,connect

def main():
    db=connect();assets={r['hash']:dict(r) for r in db.execute('SELECT * FROM assets')}
    graph=collections.defaultdict(set);incoming=collections.defaultdict(set)
    for table,s,t in [('refs','source_hash','target_hash'),('semantic_refs','source_hash','target_hash')]:
        for row in db.execute(f'SELECT {s},{t} FROM {table}'):
            graph[row[0]].add(row[1]);incoming[row[1]].add(row[0])
    root_paths={r'base\quest\cyberpunk2077.gamedef',r'ep1\quest\ep1_standalone.gamedef'}
    roots=sorted(h for h,a in assets.items() if a['path'] in root_paths)
    flow_types={'.gamedef','.quest','.questphase','.scene'}
    reached=set(roots);todo=list(roots)
    while todo:
        for target in graph[todo.pop()]:
            if target not in reached and target in assets and assets[target]['extension'] in flow_types:reached.add(target);todo.append(target)
    db.execute('CREATE TABLE IF NOT EXISTS flow_reachability(hash TEXT PRIMARY KEY,root TEXT)')
    db.execute('DELETE FROM flow_reachability');db.executemany('INSERT INTO flow_reachability VALUES(?,?)',[(h,','.join(roots)) for h in reached])
    groups=[];minor=collections.defaultdict(list);dev=collections.defaultdict(list)
    for h,a in assets.items():
        path=a['path']
        m=re.match(r'(base|ep1)\\quest\\minor_quests\\(mq\d+)\\',path)
        if m:minor[m.group(0)].append(h)
        m=re.search(r'\\(?:tests?|debug|prototypes?|obsolete|unused)\\',path,re.I)
        if m:dev[path[:m.end()]].append(h)
    for prefix,hs in minor.items():
        structural=[h for h in hs if assets[h]['extension'] in {'.questphase','.scene'} and not re.search(r'\\(?:tests?|versions)\\',assets[h]['path'])]
        if len(structural)>=2 and not any(h in reached for h in structural):
            code=prefix.rstrip('\\').split('\\')[-1]
            related=[h for h,a in assets.items() if re.search(r'(?:\\|_)'+code+r'(?:\\|_)',a['path'])]
            groups.append(dict(slug='quest-'+prefix.replace('\\','-').strip('-'),prefix=prefix,title=code.upper()+' / 孤立任務內容群',category='任務與對白',members=related,core=hs,confidence='證據不足',score=90+len(structural)/100,reason='任務階段與場景在指定本體／EP1 入口的靜態流程引用圖中未連通。'))
    for prefix,hs in dev.items():
        defs=[h for h in hs if assets[h]['extension']=='.gamedef']
        structural=[h for h in hs if assets[h]['extension'] in flow_types]
        edges=sum(len(graph[h]&set(hs)) for h in hs)
        # File names alone never qualify: require linked structures and actual typed roots.
        if len(defs)>=1 and len(structural)>=2 and edges>=1:
            title='/'.join(prefix.rstrip('\\').split('\\')[-3:])
            groups.append(dict(slug='dev-'+prefix.replace('\\','-').strip('-'),prefix=prefix,title=title+' / 開發入口群',category='開發場景',members=hs,core=hs,confidence='測試或開發殘留',score=60+min(edges,50)/10,reason='保留獨立 gsmGameDefinition 入口、spawnPointTags 與相互連結的任務／場景資源；具備可檢驗的開發入口結構。'))
    for prefix,hs in dev.items():
        ext={assets[h]['extension'] for h in hs};edges=sum(len(graph[h]&set(hs)) for h in hs)
        if len(hs)>=3 and edges and '.mesh' in ext and '.ent' in ext and not any(g['prefix']==prefix for g in groups):
            groups.append(dict(slug='prototype-'+prefix.replace('\\','-').strip('-'),prefix=prefix,title='/'.join(prefix.rstrip('\\').split('\\')[-3:])+' / 原型實體群',category='模型與原型',members=hs,core=hs,confidence='證據不足',score=77,reason='實體、模型及其他資源形成可重建的關聯群；名稱只用來定位，不能證明其未被使用。'))
    unresolved=[h for h,a in assets.items() if a['path'].isdecimal() and a['extension'] in {'.inkwidget','.inkanim'} and not incoming[h]]
    if len(unresolved)>=2:
        hs=set(unresolved)
        for h in unresolved:hs.update(x for x in graph[h] if x in assets)
        groups.append(dict(slug='unresolved-unreferenced-ink',prefix='',title='無名 UI / 無入向引用的介面資源群',category='介面與圖集',members=list(hs),core=unresolved,confidence='證據不足',score=98,reason='路徑字典未解析的 UI 類型資源沒有已知入向引用，並保留可解析的 Widget／動畫結構。'))
    groups.sort(key=lambda g:(-g['score'],g['slug']))
    report={'root_hashes':roots,'flow_reachable':len(reached),'candidates':[]}
    for g in groups:
        members=set(g['members']);core=set(g['core']);internal=sorted((h,t) for h in core for t in graph[h] if t in members)
        external=sorted((s,h) for h in core for s in incoming[h] if s not in members)
        g['members']=sorted(members);g['core']=sorted(core)
        g['id']='NCA-'+hashlib.sha256(g['slug'].encode()).hexdigest()[:12].upper()
        g['asset_count']=len(members);g['internal_edges']=len(internal);g['external_incoming']=len(external)
        g['flow_reachable_count']=len(core&reached);g['extensions']=dict(sorted(collections.Counter(assets[h]['extension'] for h in members).items()));g['edge_examples']=[{'source':assets[s]['path'],'target':assets[t]['path']} for s,t in internal[:5]]
        g['incoming_examples']=[{'source':assets[s]['path'],'target':assets[t]['path']} for s,t in external[:5] if s in assets]
        report['candidates'].append(g)
    (ROOT/'data/discovery.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');db.commit()
    print(json.dumps({'flow_reachable':len(reached),'candidates':len(groups),'top':[(g['id'],g['title'],g['asset_count'],g['flow_reachable_count']) for g in groups[:45]]},ensure_ascii=False,indent=1))

if __name__=='__main__':main()
