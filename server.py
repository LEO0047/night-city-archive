"""Loopback-only museum. All asset conversion happens on this machine."""
import concurrent.futures,hashlib,json,mimetypes,os,re,sqlite3,subprocess,threading,time,urllib.parse,zlib,socket
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
import sys
sys.path.insert(0,str(Path(__file__).parent/'scripts'))
from catalog import ROOT,DB,connect

CONFIG=json.loads((ROOT/'config.json').read_text())
POOL=concurrent.futures.ThreadPoolExecutor(max_workers=1)
JOBS={};LOCK=threading.Lock()
from runtime import find_pwsh
PWSH=find_pwsh(required=False)
CLI=ROOT/'tools/wolvenkit-9.1.0/WolvenKit.CLI.exe'

def rows(cursor):return [dict(r) for r in cursor]
def storage():return sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file())
def run(args):
    result=subprocess.run([str(a) for a in args],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=180,creationflags=0x08000000)
    if result.returncode:raise RuntimeError((result.stdout+'\n'+result.stderr)[-2500:])
    return result.stdout

def preview(h):
    db=connect();asset=db.execute('SELECT a.*,r.path archive FROM assets a JOIN archives r ON r.id=a.archive_id WHERE hash=?',(h,)).fetchone()
    if not asset:raise ValueError('Asset not found')
    ext=asset['extension'];output=ROOT/'data/media';output.mkdir(exist_ok=True)
    expected={'.mesh':'.glb','.xbm':'.png','.wem':'.wav'}.get(ext)
    if not expected:return dict(status='unsupported',detail='此類型請使用資源結構與引用檢視。')
    dest=output/(h+expected)
    if not dest.exists():
        if not PWSH:raise RuntimeError("Local extraction requires PowerShell 7.6 on Windows. Cached previews remain available.")
        if asset['size']>100_000_000:raise ValueError('單一資產超過即時預覽 100 MB 限制，請先在本機批次流程審核。')
        used=storage()
        if used+max(asset['size']*40,300_000_000)>CONFIG['storage_limit_bytes']:raise ValueError('已接近核准的 20 GB 上限；停止轉換。')
        request=ROOT/'data'/f'preview-{h}.json'
        request.write_text(json.dumps([dict(hash=h,archive=asset['archive'])]))
        run([PWSH,'-NoProfile','-File',ROOT/'scripts/bridge.ps1','-Mode','extract','-RequestFile',request,'-Output','data/raw','-MaxBytes','1000000000'])
        source=ROOT/'data/raw'/(h+ext)
        if ext=='.wem':run([ROOT/'tools/vgmstream-r2168/vgmstream-cli.exe','-o',dest,source])
        else:run([CLI,'export',source,'-o',output,'--uext','png'])
        if not dest.exists():raise RuntimeError('轉換工具未產生預期檔案；未宣稱預覽成功。')
    result=dict(status='ready',kind={'.mesh':'model','.xbm':'image','.wem':'audio'}[ext],url='/media/'+dest.name,
        detail='原始幾何／中性材質；未重建 REDengine 材質。' if ext=='.mesh' else '由本機遊戲資產轉換。',sha256=hashlib.sha256(dest.read_bytes()).hexdigest())
    db.execute('INSERT OR REPLACE INTO media VALUES(?,?,?,?,?)',(h,result['kind'],dest.name,'ready',json.dumps(result,ensure_ascii=False)));db.commit();db.close()
    return result

def queue_preview(h):
    with LOCK:
        if h not in JOBS:
            JOBS[h]=POOL.submit(preview,h)
        job=JOBS[h]
    if not job.done():return dict(status='working')
    try:return job.result()
    except Exception as e:return dict(status='error',detail=str(e))

class Handler(BaseHTTPRequestHandler):
    server_version='NightCityArchive/1.0'
    def log_message(self,fmt,*args):pass
    def safe_host(self):
        host=self.headers.get('Host','').split(':')[0]
        return host in ('127.0.0.1','localhost')
    def send(self,data,status=200,ctype='application/json; charset=utf-8'):
        body=data if isinstance(data,bytes) else json.dumps(data,ensure_ascii=False).encode('utf-8')
        self.send_response(status);self.send_header('Content-Type',ctype);self.send_header('Content-Length',str(len(body)))
        self.send_header('X-Content-Type-Options','nosniff');self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Cache-Control','no-store')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; media-src 'self' blob:; worker-src 'self' blob:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers();self.wfile.write(body)
    def do_POST(self):
        if not self.safe_host():return self.send({'error':'Loopback host required'},403)
        origin=self.headers.get('Origin')
        if origin and origin not in (f'http://127.0.0.1:{CONFIG["port"]}',f'http://localhost:{CONFIG["port"]}'):return self.send({'error':'Cross-origin request rejected'},403)
        match=re.fullmatch(r'/api/preview/(\d+)',urllib.parse.urlsplit(self.path).path)
        if match:return self.send(queue_preview(match.group(1)))
        self.send({'error':'Not found'},404)
    def do_GET(self):
        if not self.safe_host():return self.send({'error':'Loopback host required'},403)
        parsed=urllib.parse.urlsplit(self.path);path=urllib.parse.unquote(parsed.path);params=urllib.parse.parse_qs(parsed.query)
        p=lambda key,default='':params.get(key,[default])[0]
        try:
            if path.startswith('/api/'):
                if path=='/api/health':return self.send({'name':'NIGHT CITY // ARCHIVE','status':'ready','game_version':CONFIG['game_product_version']})
                with connect() as db:
                    if path=='/api/stats':
                        result={t:db.execute('SELECT count(*) FROM '+t).fetchone()[0] for t in ['assets','entries','archives','refs','documents','semantic_refs','findings']}
                        result['config']={k:CONFIG[k] for k in ['game_product_version','game_file_version','gog_build','wolvenkit_version','storage_limit_bytes']}
                        result['extensions']=rows(db.execute('SELECT extension,count(*) count FROM assets GROUP BY extension ORDER BY count DESC'))
                        result['reports']={}
                        for name in ['game-before-summary','game-after-summary','acceptance','text-coverage']:
                            report=ROOT/'reports'/(name+'.json')
                            if report.exists():result['reports'][name]=json.loads(report.read_text(encoding='utf-8'))
                        return self.send(result)
                    if path=='/api/findings':
                        query='SELECT * FROM findings WHERE 1=1';args=[]
                        for key in ['confidence','community','category']:
                            if p(key):query+=f' AND {key}=?';args.append(p(key))
                        if p('q'):query+=' AND (title LIKE ? OR summary LIKE ? OR id LIKE ?)';args.extend(['%'+p('q')+'%']*3)
                        result=rows(db.execute(query+' ORDER BY score DESC,title',args))
                        for row in result:row['details']=json.loads(row['details'])
                        return self.send(result)
                    if path.startswith('/api/finding/'):
                        fid=path.rsplit('/',1)[-1];row=db.execute('SELECT * FROM findings WHERE id=?',(fid,)).fetchone()
                        if not row:return self.send({'error':'Not found'},404)
                        result=dict(row);result['details']=json.loads(result['details'])
                        result['assets']=rows(db.execute('SELECT a.*,f.role,m.kind media_kind,m.file media_file FROM finding_assets f JOIN assets a ON a.hash=f.hash LEFT JOIN media m ON m.hash=a.hash WHERE f.finding_id=? ORDER BY CASE a.extension WHEN \'.mesh\' THEN 1 WHEN \'.xbm\' THEN 2 WHEN \'.wem\' THEN 3 ELSE 4 END,a.path',(fid,)))
                        return self.send(result)
                    if path=='/api/search':
                        term=p('q').strip()[:300];offset=max(0,min(int(p('offset','0')),100000));kind=p('kind','assets');args=[]
                        where=[]
                        if kind=='text':
                            base='FROM text_search f JOIN documents d ON d.id=f.doc_id JOIN assets a ON a.hash=d.hash'
                            cols='a.hash,a.path,a.extension,d.field,d.language,substr(d.text,1,1800) text'
                            if term:
                                if len(term)>=3:where.append('text_search MATCH ?');args.append('"'+term.replace('"','""')+'"')
                                else:where.append('d.text LIKE ?');args.append('%'+term+'%')
                            if p('language'):where.append('d.language=?');args.append(p('language'))
                        else:
                            base='FROM assets a';cols='a.hash,a.path,a.extension,a.size,a.variants'
                            if term:
                                if term.removeprefix('NCA-ASSET-').isdecimal():where.append('a.hash=?');args.append(term.removeprefix('NCA-ASSET-'))
                                elif len(term)>=3:base+=' JOIN asset_search f ON f.hash=a.hash';where.append('asset_search MATCH ?');args.append('"'+term.replace('"','""')+'"')
                                else:where.append('a.path LIKE ?');args.append('%'+term+'%')
                        if p('extension'):where.append('a.extension=?');args.append(p('extension'))
                        clause=(' WHERE '+' AND '.join(where)) if where else ''
                        results=rows(db.execute('SELECT '+cols+' '+base+clause+' LIMIT 61 OFFSET ?',args+[offset]))
                        return self.send(dict(results=results[:60],more=len(results)>60,offset=offset))
                    if path.startswith('/api/asset/'):
                        h=path.rsplit('/',1)[-1];asset=db.execute('SELECT * FROM assets WHERE hash=?',(h,)).fetchone()
                        if not asset:return self.send({'error':'Not found'},404)
                        result=dict(asset)
                        result['archives']=rows(db.execute('SELECT e.*,r.path,r.sha256 FROM entries e JOIN archives r ON r.id=e.archive_id WHERE e.hash=?',(h,)))
                        result['outgoing']=rows(db.execute('SELECT DISTINCT r.target_hash hash,a.path, r.kind field FROM refs r LEFT JOIN assets a ON a.hash=r.target_hash WHERE r.source_hash=? UNION SELECT r.target_hash hash,r.target_path path,r.field FROM semantic_refs r WHERE source_hash=? LIMIT 100',(h,h)))
                        result['incoming']=rows(db.execute('SELECT DISTINCT r.source_hash hash,a.path,r.kind field FROM refs r JOIN assets a ON a.hash=r.source_hash WHERE r.target_hash=? UNION SELECT r.source_hash hash,a.path,r.field FROM semantic_refs r JOIN assets a ON a.hash=r.source_hash WHERE target_hash=? LIMIT 100',(h,h)))
                        result['documents']=rows(db.execute('SELECT field,language,substr(text,1,6000) text FROM documents WHERE hash=? LIMIT 35',(h,)))
                        result['resource']=db.execute('SELECT 1 FROM resources WHERE hash=?',(h,)).fetchone() is not None
                        result['media']=dict(db.execute('SELECT * FROM media WHERE hash=?',(h,)).fetchone() or {})
                        return self.send(result)
                    if path.startswith('/api/resource/'):
                        h=path.rsplit('/',1)[-1];row=db.execute('SELECT json_zlib FROM resources WHERE hash=? ORDER BY archive_id LIMIT 1',(h,)).fetchone()
                        if row:return self.send(zlib.decompress(row[0]))
                        return self.send({'error':'此資源尚未解析；路徑與封存檔引用已收錄。'},404)
                    if path=='/api/sources':return self.send(json.loads((ROOT/'research/sources.json').read_text(encoding='utf-8')))
                return self.send({'error':'Not found'},404)
            base=ROOT/'data/media' if path.startswith('/media/') else ROOT/'web'
            relative=path[len('/media/'):] if path.startswith('/media/') else (path.lstrip('/') or 'index.html')
            target=(base/relative).resolve()
            if not target.is_relative_to(base.resolve()) or not target.is_file():return self.send({'error':'Not found'},404)
            return self.send(target.read_bytes(),ctype=mimetypes.guess_type(str(target))[0] or 'application/octet-stream')
        except (ValueError,sqlite3.Error) as e:self.send({'error':str(e)},400)
        except (BrokenPipeError,ConnectionResetError):pass

class LocalServer(ThreadingHTTPServer):
    allow_reuse_address=False
    def server_bind(self):
        if hasattr(socket,'SO_EXCLUSIVEADDRUSE'):self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1)
        super().server_bind()

if __name__=='__main__':
    server=LocalServer(('127.0.0.1',CONFIG['port']),Handler)
    print(f'NIGHT CITY // ARCHIVE http://127.0.0.1:{CONFIG["port"]}',flush=True)
    server.serve_forever()
