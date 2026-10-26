"""Download only pinned official tools, verify SHA-256, extract inside this project."""
import argparse,hashlib,json,os,urllib.request,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def configure_mesh_export(settings):
    # Upstream appsettings.json includes a UTF-8 BOM in the official release.
    data=json.loads(settings.read_text(encoding='utf-8-sig'))
    data['MeshExportArgs']={'withMaterials':False,'isGLBinary':True,'LodFilter':True}
    settings.write_text(json.dumps(data,indent=2),encoding='utf-8')

def safe_members(archive,target):
    for item in archive.infolist():
        dest=(target/item.filename).resolve()
        if not dest.is_relative_to(target.resolve()):raise ValueError('Archive path traversal rejected')
        if (item.external_attr>>16)&0o170000==0o120000:raise ValueError('Archive symlinks rejected')
    return archive.infolist()

def main():
    p=argparse.ArgumentParser();p.add_argument('--list',action='store_true');args=p.parse_args()
    lock=json.loads((ROOT/'scripts/tools.lock.json').read_text())
    if args.list:print(json.dumps(lock,indent=2));return
    config=json.loads((ROOT/'config.json').read_text())
    if not config.get('storage_approved'):raise SystemExit('Set an explicit storage cap with initialize.py first.')
    target=ROOT/'tools';target.mkdir(exist_ok=True)
    for item in lock:
        used=sum(f.stat().st_size for f in ROOT.rglob('*') if f.is_file())
        if used+item['bytes']*8>config['storage_limit_bytes']:raise SystemExit('Approved storage cap would be approached; download stopped.')
        package=target/item['file']
        if not package.exists():
            req=urllib.request.Request(item['url'],headers={'User-Agent':'NightCityArchive/0.1'})
            with urllib.request.urlopen(req,timeout=60) as response,package.with_suffix('.partial').open('wb') as output:
                total=0
                while chunk:=response.read(1024*1024):
                    total+=len(chunk)
                    if total>item['bytes']:raise RuntimeError('Download exceeded pinned length')
                    output.write(chunk)
            package.with_suffix('.partial').replace(package)
        if package.stat().st_size!=item['bytes'] or hashlib.sha256(package.read_bytes()).hexdigest()!=item['sha256']:
            raise RuntimeError('Tool package checksum mismatch: '+item['file'])
        destination=target/item['directory'];destination.mkdir(exist_ok=True)
        with zipfile.ZipFile(package) as archive:archive.extractall(destination,members=safe_members(archive,destination))
        print('Verified:',item['name'],flush=True)
    settings=target/'wolvenkit-9.1.0/appsettings.json'
    configure_mesh_export(settings)

if __name__=='__main__':main()
