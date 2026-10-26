"""Full source integrity check without overwriting the first-phase baseline."""
import concurrent.futures,hashlib,json,sys,time
from pathlib import Path
from manifest import ROOT,GAME,digest

label=sys.argv[1]
assert label in ('before','after')
folder=ROOT/'reports/phase2';folder.mkdir(exist_ok=True)
output=folder/f'game-{label}.jsonl'
started=time.time()
files=sorted(p for p in GAME.rglob('*') if p.is_file())
with output.open('w',encoding='utf-8') as target,concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    for row in pool.map(digest,files):target.write(json.dumps(row,ensure_ascii=False)+'\n')
baseline=ROOT/'reports/game-before.jsonl' if label=='before' else folder/'game-before.jsonl'
old={r['path']:r for r in map(json.loads,baseline.read_text(encoding='utf-8').splitlines())}
new={r['path']:r for r in map(json.loads,output.read_text(encoding='utf-8').splitlines())}
report={'files':len(files),'baseline':str(baseline.relative_to(ROOT)),'added':sorted(new.keys()-old.keys()),'removed':sorted(old.keys()-new.keys()),'changed':sorted(k for k in old.keys()&new.keys() if old[k]!=new[k]),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'elapsed_seconds':round(time.time()-started,2)}
report['unchanged']=not any(report[k] for k in ('added','removed','changed'))
(folder/f'game-{label}.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report),flush=True)
if not report['unchanged']:raise SystemExit(1)
