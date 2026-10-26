# Adapted from spuddeh/cp2077-ink-archive build.py (MIT).
# Copyright (c) spuddeh. Full notice: research/ink-archive-LICENSE.txt.
def depot(v):
    if isinstance(v, dict):
        p=v.get('DepotPath')
        if isinstance(p, dict):p=p.get('$v',p.get('$value'))
        if p=='0':return None
        return p if isinstance(p,str) else None
    return v if isinstance(v,str) else None

def iter_paths(node, field='', out=None):
    if out is None:out=[]
    if isinstance(node,list):
        for i,v in enumerate(node):
            if isinstance(v,dict) and 'DepotPath' in v:
                p=depot(v)
                if p is not None:out.append((p,field,i))
            else:iter_paths(v,field,out)
    elif isinstance(node,dict):
        for k,v in node.items():
            fname=field if k in ('$v','$value') else k
            if isinstance(v,dict) and 'DepotPath' in v:
                p=depot(v)
                if p is not None:out.append((p,fname,0))
            else:iter_paths(v,fname,out)
    return out
