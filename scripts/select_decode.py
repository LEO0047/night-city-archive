import json
from catalog import ROOT,connect
db=connect()
extensions=['.json','.scene','.quest','.questphase','.journal','.gamedef','.inkwidget','.inkanim','.inkatlas','.inkstyle','.inkhud','.inkmenu','.inklayers','.inktypography','.inkfullscreencomposition','.inkenginesettings','.inkgamesettings','.credits','.csv']
rows=db.execute('SELECT e.hash,r.path archive,a.extension,e.size FROM entries e JOIN assets a ON a.hash=e.hash JOIN archives r ON r.id=e.archive_id WHERE a.extension IN ('+','.join('?'*len(extensions))+')',extensions).fetchall()
requests=[dict(hash=r['hash'],archive=r['archive']) for r in rows]
(ROOT/'data/decode-request.json').write_text(json.dumps(requests),encoding='utf-8')
print(json.dumps(dict(files=len(rows),uncompressed_bytes=sum(r['size'] for r in rows))))
