"""Open the museum, or run a foreground local server until its window is closed."""
import json,subprocess,sys,threading,urllib.request,webbrowser
from pathlib import Path
root=Path(__file__).resolve().parent
config=json.loads((root/'config.json').read_text())
url=f'http://127.0.0.1:{config["port"]}'
try:
    with urllib.request.urlopen(url+'/api/health',timeout=3) as r:
        if not r.headers.get('Server','').startswith('NightCityArchive/'):
            raise RuntimeError('This port is used by another application.')
        stats=json.load(r)
    webbrowser.open(url)
except (OSError,ValueError):
    if not (root/'data/archive.db').exists():raise SystemExit('The archive database is missing. Run Rebuild.ps1 -FromCache.')
    threading.Timer(2,lambda:webbrowser.open(url)).start()
    print('NIGHT CITY // ARCHIVE  '+url+'\nClose this window to stop this local server.',flush=True)
    try:subprocess.run([sys.executable,'-X','utf8',str(root/'server.py')],cwd=root,check=True)
    except KeyboardInterrupt:pass
