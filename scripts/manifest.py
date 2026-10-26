"""Read-only, full-content SHA-256 inventory of the original installation."""
import argparse, concurrent.futures, hashlib, json, os, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAME = Path(json.loads((ROOT/'config.json').read_text())['game_root'])

def digest(path):
    before = path.stat()
    h = hashlib.sha256()
    with path.open('rb') as stream:
        while chunk := stream.read(8 * 1024 * 1024):
            h.update(chunk)
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise RuntimeError(f'File changed during hashing: {path}')
    return dict(path=path.relative_to(GAME).as_posix(), size=after.st_size,
                mtime_ns=after.st_mtime_ns, sha256=h.hexdigest())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('label', choices=['before', 'after'])
    args = parser.parse_args()
    files = sorted(p for p in GAME.rglob('*') if p.is_file())
    output = ROOT / 'reports' / f'game-{args.label}.jsonl'
    started = time.time()
    with output.open('w', encoding='utf-8') as target, concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for index, row in enumerate(pool.map(digest, files)):
            target.write(json.dumps(row, ensure_ascii=False) + '\n')
            if index % 500 == 0:
                print(f'{args.label}: {index}/{len(files)} files, {time.time()-started:.0f}s', flush=True)
    summary = dict(root=str(GAME), files=len(files), completed_at_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()), elapsed_seconds=round(time.time()-started, 2),
                   manifest_sha256=hashlib.sha256(output.read_bytes()).hexdigest())
    if args.label == 'after':
        old = {r['path']:r for r in map(json.loads, (ROOT/'reports/game-before.jsonl').read_text(encoding='utf-8').splitlines())}
        new = {r['path']:r for r in map(json.loads, output.read_text(encoding='utf-8').splitlines())}
        summary['added'] = sorted(new.keys()-old.keys())
        summary['removed'] = sorted(old.keys()-new.keys())
        summary['changed'] = [p for p in old.keys() & new.keys() if old[p] != new[p]]
        summary['unchanged'] = not any(summary[k] for k in ['added','removed','changed'])
    (ROOT/'reports'/f'game-{args.label}-summary.json').write_text(json.dumps(summary,indent=2), encoding='utf-8')
    print(json.dumps(summary), flush=True)

if __name__ == '__main__':
    main()
