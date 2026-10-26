"""Requested MQ027 case study, separate from automatic discovery rules."""
import collections,hashlib,json,re,sqlite3,zlib
from phase2_index import ROOT,OUT
from phase2_context import walk

def graph_summary(data):
    handles={str(n['HandleId']):n.get('Data') for _,n in walk(data) if isinstance(n,dict) and 'HandleId' in n}
    def resolve(h):return (h.get('Data') or handles.get(str(h.get('HandleRefId','')),{})) if isinstance(h,dict) else {}
    def hid(h):return str(h.get('HandleId',h.get('HandleRefId',''))) if isinstance(h,dict) else ''
    graphs=[]
    for ptr,node in walk(data):
        if not isinstance(node,dict) or not isinstance(node.get('nodes'),list):continue
        owners={};nodes=[]
        for wrapper in node['nodes']:
            n=resolve(wrapper)
            if not n:continue
            identity=hid(wrapper);sockets=[]
            for s in n.get('sockets',[]):
                sd=resolve(s);owners[hid(s)]=identity
                sockets.append({'handle':hid(s),'name':sd.get('name',{}).get('$value'),'type':sd.get('type')})
            scene=n.get('sceneFile',{}).get('DepotPath',{}).get('$value')
            nodes.append({'handle':identity,'node_id':n.get('id'),'type':n.get('$type'),'sockets':sockets,'scene':scene})
        edges=[]
        for handle,n in handles.items():
            if not isinstance(n,dict) or n.get('$type')!='graphGraphConnectionDefinition':continue
            s=hid(n.get('source',{}));t=hid(n.get('destination',{}))
            if s in owners and t in owners:edges.append({'handle':handle,'source_node':owners[s],'source_socket':s,'target_node':owners[t],'target_socket':t})
        graphs.append({'pointer':ptr,'nodes':nodes,'edges':edges})
    return graphs

def main():
    c=sqlite3.connect('file:'+str(ROOT/'data/archive.db').replace('\\','/')+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
    e=sqlite3.connect('file:'+str(OUT/'evidence.db').replace('\\','/')+'?mode=ro',uri=True);e.row_factory=sqlite3.Row
    rule=json.loads((OUT/'rules.json').read_text(encoding='utf-8'))
    q=next(x for x in rule['quests'] if x['prefix']== 'base\\quest\\minor_quests\\mq027\\')
    assets=[]
    for a in c.execute("SELECT * FROM assets WHERE path LIKE '%mq027%' ORDER BY path"):
        a=dict(a);a['archives']=[dict(x) for x in c.execute('SELECT r.path,r.sha256,e.sha1 entry_sha1 FROM entries e JOIN archives r ON r.id=e.archive_id WHERE e.hash=? ORDER BY r.path',(a['hash'],))];assets.append(a)
    structured=[]
    for a in assets:
        if a['extension'] not in ('.gamedef','.quest','.questphase','.scene'):continue
        for r in c.execute('SELECT archive_id,json_zlib FROM resources WHERE hash=? ORDER BY archive_id',(a['hash'],)):
            data=json.loads(zlib.decompress(r['json_zlib']));observations=[]
            for ptr,n in walk(data):
                if isinstance(n,dict) and n.get('$type','') in ('questSetVar_NodeType','questVarComparison_ConditionType','questJournalEntry_NodeType','questJournalQuestEntry_NodeType','questPhoneManagerNodeDefinition'):
                    observations.append({'pointer':ptr,'value':n})
            structured.append({'hash':a['hash'],'path':a['path'],'archive_id':r['archive_id'],'graphs':graph_summary(data),'observations':observations})
    journal=[dict(r) for r in e.execute("SELECT * FROM journal_nodes WHERE path LIKE '%mq027%' ORDER BY archive_id,pointer")]
    keys=set()
    for row in journal:keys.update(re.findall(r'LocKey#(\d+)',row['node']));row['node']=json.loads(row['node'])
    characters=[]
    for r in e.execute("SELECT * FROM records WHERE source=? AND name LIKE '%mq027%' ORDER BY name",(rule['snapshot'],)):
        row=dict(r);row['flats']=[dict(f) for f in e.execute('SELECT id,field,type,value FROM flats WHERE source=? AND owner=? ORDER BY field',(r['source'],r['id']))]
        for f in row['flats']:
            f['value']=json.loads(f['value'])
            if f['type']=='gamedataLocKeyWrapper':keys.add(str(f['value']['key']))
        row['usage']=next((x for x in rule['records'] if x['record_id']==r['id']),None);characters.append(row)
    localized=[dict(r) for r in e.execute('SELECT * FROM localization WHERE key IN ('+','.join('?'*len(keys))+') OR secondary LIKE \'%mq027%\' ORDER BY key,language,hash,archive_id',sorted(keys))]
    voice=json.loads((OUT/'audio/inventory.json').read_text(encoding='utf-8'))
    for a in voice:a['transcription']=json.loads((OUT/'audio'/(a['hash']+'.asr.json')).read_text(encoding='utf-8'))
    voiceids=sorted({str(m['string_id']) for a in voice for m in a['voice_map']})
    subtitle_matches=[dict(r) for r in e.execute('SELECT hash,archive_id,key,language,pointer FROM localization WHERE kind=\'localizationPersistenceSubtitleEntries\' AND key IN ('+','.join('?'*len(voiceids))+')',voiceids)]
    world=[dict(r) for r in e.execute("SELECT f.*,s.path FROM resource_fields f JOIN resource_scan s ON s.hash=f.hash AND s.archive=f.archive WHERE lower(f.value) LIKE '%mq027%' ORDER BY s.path,f.pointer")]
    data={'id':'NCA-AB6DD4DA3FB3','quest':'MQ027','rule':q,'assets':assets,'structures':structured,'journal':journal,'localization':localized,'records':characters,'world_matches':world,'audio':voice,'subtitle_matches':subtitle_matches,'subtitle_search_languages':['en-us','zh-tw'],'voice_ids':voiceids}
    dest=OUT/'mq027-private.json';dest.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    summary={'asset_count':len(assets),'extensions':dict(collections.Counter(a['extension'] for a in assets)),'records':[r['name'] for r in characters],'journal_nodes_with_variants':len(journal),'world_fields':len(world),'world_resources':len({r['hash'] for r in world}),'audio_files':len(voice),'audio_ids':len(voiceids),'audio_seconds':round(sum(a['seconds'] for a in voice),4),'subtitle_matches':len(subtitle_matches),'missing_scenes':list(q['missing_scenes']),'flow_reached':q['flow_reached'],'all_resource_reached':q['all_resource_reached'],'classification':q['classification'],'private_file_sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}
    (ROOT/'reports/phase2/mq027-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
