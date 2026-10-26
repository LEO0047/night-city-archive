"""Evidence-only discovery. This module does not read community/user fixtures.

Absence is not proof of unreachability. Paths are may-use paths, not executed paths.
The displayed completeness ratio counts checked channels; it is not a probability.
"""
import collections,hashlib,json,pathlib,re,sqlite3
from phase2_index import ROOT,OUT,tweak_id,asset_id

SNAPSHOT='r6/cache/tweakdb_ep1.bin'
ROOT_PATHS=(r'base\quest\cyberpunk2077.gamedef',r'ep1\quest\ep1_standalone.gamedef')
CHANNEL_TYPES={
 'shop':{'gamedataVendor_Record'},
 'loot':{'gamedataLootTable_Record'},
 'reward':{'gamedataRewardBase_Record','gamedataRewardSet_Record','gamedataCurrencyReward_Record','gamedataGOGReward_Record'},
 'crafting':{'gamedataItemRecipe_Record','gamedataCraftingPackage_Record','gamedataCraftingResult_Record'},
 'equipment':{'gamedataCharacter_Record','gamedataNPCEquipmentGroup_Record','gamedataNPCEquipmentItem_Record','gamedataNPCEquipmentItemPool_Record','gamedataNPCEquipmentItemsPoolEntry_Record','gamedataBuildEquipmentSet_Record','gamedataBuildEquipment_Record'},
}

def bfs(graph,seeds):
    parents={s:None for s in sorted(seeds)};todo=collections.deque(parents)
    while todo:
        s=todo.popleft()
        for t in sorted(graph.get(s,())):
            if t not in parents:parents[t]=s;todo.append(t)
    return parents

def chain(parents,target):
    if target not in parents:return []
    out=[target]
    while parents[out[-1]] is not None:out.append(parents[out[-1]])
    return out[::-1]

def classify_record(channels,incoming,assets):
    # A positive static association prevents a cut classification. It does not
    # assert the player can acquire the object in a particular playthrough.
    if any(channels.values()):return 'HAS_USE_LINK','證據不足'
    if incoming:return 'INDIRECT_REFERENCES_ONLY','證據不足'
    if assets:return 'ISOLATED_DEFINED_CONTENT','證據不足'
    return 'DEFINITION_ONLY','證據不足'

def main():
    core=sqlite3.connect('file:'+str(ROOT/'data/archive.db').replace('\\','/')+'?mode=ro',uri=True);core.row_factory=sqlite3.Row
    db=sqlite3.connect('file:'+str(OUT/'evidence.db').replace('\\','/')+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
    assets={r['hash']:dict(r) for r in core.execute('SELECT * FROM assets')}
    ag=collections.defaultdict(set)
    for table in ('refs','semantic_refs'):
        for s,t in core.execute('SELECT source_hash,target_hash FROM '+table):ag[s].add(t)
    for h,v in db.execute("SELECT hash,value FROM resource_fields WHERE red_type='ResourcePath'"):
        if v not in ('','0','None'):ag[h].add(asset_id(v))
    root_hashes=[h for h,a in assets.items() if a['path'] in ROOT_PATHS]
    # Flow-only reachability is recorded separately from all-resource references.
    flowtypes={'.gamedef','.quest','.questphase','.scene'}
    fg={s:{t for t in ts if assets.get(t,{}).get('extension') in flowtypes} for s,ts in ag.items() if assets.get(s,{}).get('extension') in flowtypes}
    flow=bfs(fg,root_hashes)
    records={r['id']:dict(r) for r in db.execute('SELECT * FROM records WHERE source=?',(SNAPSHOT,))}
    rg=collections.defaultdict(set);incoming=collections.defaultdict(list);edge_fields={}
    for s,t,f,ptr in db.execute('SELECT owner,target,field,pointer FROM tweak_edges WHERE source=?',(SNAPSHOT,)):
        rg[s].add(t);incoming[t].append((s,f,ptr));edge_fields.setdefault((s,t),(f,ptr))
        ag['T:'+s].add('T:'+t)
    for owner,target in db.execute('SELECT owner,target FROM asset_refs WHERE source=?',(SNAPSHOT,)):ag['T:'+owner].add(target)
    for table in ('core_fields','resource_fields'):
        for h,v in db.execute(f"SELECT hash,value FROM {table} WHERE red_type='TweakDBID'"):
            # The global journal is a catalogue, not an activation root.
            if assets.get(h,{}).get('extension')=='.journal':continue
            ag[h].add('T:'+tweak_id(v))
    full=bfs(ag,root_hashes)
    # Streaming activation/sector masks are not reconstructed. Over-approximate
    # every installed sector as a possible root instead of declaring it unused.
    possible_world=bfs(ag,{h for h,a in assets.items() if a['extension']=='.streamingsector'})
    channels={};seed_evidence={}
    for label,types in CHANNEL_TYPES.items():
        seeds={rid for rid,r in records.items() if r['type'] in types}
        channels[label]=bfs(rg,seeds)
        seed_evidence[label]={s:{'record':records[s]['name'],'type':records[s]['type']} for s in seeds}
    channels['script_literal']=bfs(rg,{r[0] for r in db.execute('SELECT DISTINCT target FROM script_refs')})
    seed_evidence['script_literal']={}
    for target,line,owner,literal in db.execute('SELECT target,line,owner,literal FROM script_refs ORDER BY line'):
        seed_evidence['script_literal'].setdefault(target,{'line':line,'function':owner,'literal':literal,'path':'r6/cache/final.redscripts','decoded_file':'data/phase2/scripts/final.reds'})
    resource_seeds=collections.defaultdict(dict);detached=collections.defaultdict(list)
    queries=[('core_fields','archive_id'),('resource_fields','archive')]
    for table,archivecol in queries:
        for h,arc,ptr,v in db.execute(f"SELECT hash,{archivecol},pointer,value FROM {table} WHERE red_type='TweakDBID'"):
            if assets.get(h,{}).get('extension')=='.journal':continue
            rid=tweak_id(v)
            if rid not in records:continue
            entry={'hash':h,'archive':arc,'path':assets.get(h,{}).get('path',h),'pointer':ptr,'value':v}
            if h in full or h in possible_world:
                label='quest_or_scene' if assets.get(h,{}).get('extension') in flowtypes else 'world_or_entity'
                if h not in full:entry['activation']='possible world sector; activation masks not evaluated'
                resource_seeds[label].setdefault(rid,entry)
            elif assets.get(h,{}).get('extension')=='.community':resource_seeds['community_definition'].setdefault(rid,entry)
            else:detached[rid].append(entry)
    for label in ('quest_or_scene','world_or_entity','community_definition'):
        seed_evidence[label]=resource_seeds[label];channels[label]=bfs(rg,resource_seeds[label])
    ar=collections.defaultdict(list)
    for row in db.execute('SELECT owner,target,path,field,pointer FROM asset_refs WHERE source=?',(SNAPSHOT,)):ar[row['owner']].append(dict(row))
    results=[]
    for rid,r in sorted(records.items(),key=lambda x:(x[1]['name'] or '',x[0])):
        if not r['category']:continue
        paths={label:chain(parents,rid) for label,parents in channels.items()}
        if r['category']=='角色' and len(paths['equipment'])==1:paths['equipment']=[]
        observations={}
        for label,ids in paths.items():
            if not ids:continue
            observations[label]={'seed':seed_evidence[label].get(ids[0],{}),'chain':[{'id':x,'name':records.get(x,{}).get('name',x)} for x in ids], 'edges':[{'source':s,'target':t,'field':edge_fields.get((s,t),('',''))[0],'pointer':edge_fields.get((s,t),('',''))[1]} for s,t in zip(ids,ids[1:])]}
        status,confidence=classify_record(paths,incoming.get(rid,[]),ar.get(rid,[]))
        rows=[{'id':s,'name':records.get(s,{}).get('name',s),'field':f,'pointer':p} for s,f,p in sorted(set(incoming.get(rid,[])))]
        results.append(dict(id='NCA-REC-'+rid,record_id=rid,name=r['name'],type=r['type'],category=r['category'],rule_status=status,classification=confidence,classification_origin='rule',channels=observations,incoming=rows,detached_resources=detached.get(rid,[]),asset_refs=ar.get(rid,[]),checks={'evaluated':len(channels),'total':len(channels),'formula':'evaluated / total channels; static coverage only, not confidence'},reproduce=f'python -X utf8 scripts/phase2_query.py --record {rid}'))
    # Generic orphan quest groups: never upgrade by quest identifier or community label.
    groups=collections.defaultdict(list)
    for h,a in assets.items():
        m=re.match(r'((?:base|ep1)\\quest\\(?:minor_quests|side_quests|main_quests)\\[^\\]+\\)',a['path'])
        if m:groups[m[1]].append(h)
    quests=[]
    for prefix,hs in sorted(groups.items()):
        structural=[h for h in hs if assets[h]['extension'] in ('.quest','.questphase','.scene') and not re.search(r'\\(?:test|tests|versions)\\',assets[h]['path'])]
        if not structural:continue
        missing=collections.defaultdict(list)
        for h in structural:
            for row in core.execute("SELECT target_hash,target_path,field,archive_id FROM semantic_refs WHERE source_hash=? AND target_path LIKE '%.scene'",(h,)):
                if row['target_hash'] not in assets:missing[row['target_path']].append(dict(source_hash=h,source_path=assets[h]['path'],**dict(row)))
        reachable=sorted(set(structural)&set(flow));all_reach=sorted(set(structural)&set(full))
        status='HAS_FLOW_LINK' if reachable else 'DETACHED_WITH_MISSING_SCENES' if missing else 'DETACHED_FLOW'
        confidence='疑似刪除內容' if not reachable and missing else '證據不足'
        quests.append({'prefix':prefix,'members':sorted(hs),'structural':structural,'flow_reached':reachable,'all_resource_reached':all_reach,'missing_scenes':dict(missing),'rule_status':status,'classification':confidence,'classification_origin':'rule','decision':{'no_formal_flow_entry':not bool(reachable),'missing_scene_payload':bool(missing),'rule':'no_formal_flow_entry AND missing_scene_payload => suspected_cut; static evidence cannot prove confirmed_unused'}})
    coverage={r['source']:json.loads(r['report']) for r in db.execute('SELECT * FROM coverage')}
    output={'schema':'nca.phase2.rules/v1','snapshot':SNAPSHOT,'root_paths':ROOT_PATHS,'roots':root_hashes,'asset_reached':sum(h in assets for h in full),'hybrid_nodes_reached':len(full),'flow_reached':len(flow),'flow_assets':sorted(flow),'resource_scanned':db.execute('SELECT count(*) FROM resource_scan').fetchone()[0],'coverage':coverage,'records':results,'quests':quests,'limits':['Archive variants are unioned; runtime precedence is not inferred.','Native code, dynamic record construction, conditions and actual save-state execution are not resolved.','Vendor/loot/reward definition chains establish potential use, not player acquisition.','Unresolved flat names/owners and modded-cache activation remain coverage gaps.'],'rule_source_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()}
    (OUT/'rules.json').write_text(json.dumps(output,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    (OUT/'asset-reachability.json').write_text(json.dumps(full,separators=(',',':')),encoding='utf-8')
    (OUT/'possible-world-reachability.json').write_text(json.dumps(possible_world,separators=(',',':')),encoding='utf-8')
    print(json.dumps({k:v for k,v in output.items() if k not in ('records','quests','coverage','flow_assets')},ensure_ascii=False));print(collections.Counter(r['rule_status'] for r in results));print(collections.Counter(q['rule_status'] for q in quests))

if __name__=='__main__':main()
