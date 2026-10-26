"""Generic quest operation evidence. No community fixtures or named exceptions.

Local graph traversal over-approximates all conditional outputs. It is not a
runtime executor: external events and native/script dispatch remain unknown.
"""
import collections,json,sqlite3,zlib
from phase2_index import ROOT,OUT,tweak_id
from phase2_mq027 import graph_summary

def walk_anc(node,pointer='',anc=()):
    yield pointer,node,anc
    if isinstance(node,dict):
        for k,v in node.items():yield from walk_anc(v,pointer+'/'+k,anc+((pointer,node),))
    elif isinstance(node,list):
        for i,v in enumerate(node):yield from walk_anc(v,pointer+'/'+str(i),anc+((pointer,node),))

def main():
    c=sqlite3.connect('file:'+str(ROOT/'data/archive.db').replace('\\','/')+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
    e=sqlite3.connect('file:'+str(OUT/'evidence.db').replace('\\','/')+'?mode=ro',uri=True)
    hashes=[r[0] for r in e.execute("SELECT DISTINCT hash FROM core_fields WHERE red_type='TweakDBID' AND value LIKE 'Items.%'")];e.close()
    result=[]
    for index,h in enumerate(hashes):
        if index%100==0:print('item operation resources',index,'/',len(hashes),flush=True)
        a=c.execute('SELECT path,extension FROM assets WHERE hash=?',(h,)).fetchone()
        if a['extension'] not in ('.quest','.questphase','.scene'):continue
        for r in c.execute('SELECT archive_id,json_zlib FROM resources WHERE hash=? ORDER BY archive_id',(h,)):
            data=json.loads(zlib.decompress(r['json_zlib']));gs=graph_summary(data);graphs={}
            for g in gs:
                edges=collections.defaultdict(set)
                for edge in g['edges']:edges[edge['source_node']].add(edge['target_node'])
                starts={n['handle'] for n in g['nodes'] if n['type'] in ('questInputNodeDefinition','questStartNodeDefinition')}
                reached=set(starts);todo=list(starts)
                while todo:
                    for target in edges[todo.pop()]:
                        if target not in reached:reached.add(target);todo.append(target)
                graphs[g['pointer']]={'nodes':{n['handle']:n for n in g['nodes']},'starts':starts,'reached':reached}
            for ptr,n,anc in walk_anc(data):
                if not isinstance(n,dict) or n.get('$type')!='TweakDBID' or not n.get('$value'):continue
                value=str(n['$value'])
                if not value.startswith('Items.'):continue
                types=[(p,x) for p,x in anc if isinstance(x,dict) and '$type' in x]
                operation=next(((p,x) for p,x in reversed(types) if x.get('$type','').endswith('Params')),None)
                if not operation:operation=next(((p,x) for p,x in reversed(types) if x.get('$type','').startswith('quest')),None)
                if not operation:continue
                optr,op=operation;graph_chain=[]
                for gp,g in graphs.items():
                    prefix=gp+'/nodes/'
                    if not ptr.startswith(prefix):continue
                    nodepath=prefix+ptr[len(prefix):].split('/')[0]
                    wrapper=next((x for p,x in anc if p==nodepath),{})
                    handle=str(wrapper.get('HandleId',wrapper.get('HandleRefId','')))
                    nd=g['nodes'].get(handle,{})
                    graph_chain.append({'graph_pointer':gp,'node_handle':handle,'node_id':nd.get('node_id'),'node_type':nd.get('type'),'entry_handles':sorted(g['starts']),'local_entry_reached':handle in g['reached'] if g['starts'] else None})
                scalar={k:v for k,v in op.items() if isinstance(v,(str,int,float,bool)) and k!='$type'}
                flags=[]
                for p,x,_ in walk_anc(op):
                    if isinstance(x,dict) and x.get('$type')=='questUniversalRef':flags.append({'pointer':optr+p,'refLocalPlayer':x.get('refLocalPlayer'),'mainPlayerObject':x.get('mainPlayerObject')})
                result.append({'hash':h,'archive_id':r['archive_id'],'path':a['path'],'pointer':ptr+'/$value','record':value,'record_id':tweak_id(value),'operation_type':op['$type'],'operation_pointer':optr,'parameters':scalar,'target_flags':flags,'graph_chain':graph_chain,'local_input_path':all(x['local_entry_reached'] is True for x in graph_chain) if graph_chain else None})
    dest=OUT/'quest-operations.json';dest.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print(json.dumps({'operations':len(result),'resources':len({r['hash'] for r in result}),'local_input_path':dict(collections.Counter(str(r['local_input_path']) for r in result))}))

if __name__=='__main__':main()
