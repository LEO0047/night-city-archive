"""Create local-only settings after explicit selection of the source game and storage cap."""
import argparse,json,subprocess
from pathlib import Path
from runtime import find_pwsh
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser();p.add_argument('--game-root',type=Path,required=True);p.add_argument('--storage-gb',type=float,required=True);p.add_argument('--pwsh');args=p.parse_args()
    game=args.game_root.resolve()
    if not (game/'bin/x64/Cyberpunk2077.exe').is_file():raise SystemExit('Expected an existing Windows Cyberpunk installation; no game files will be installed.')
    if ROOT.is_relative_to(game):raise SystemExit('Place the project outside the game directory.')
    if (ROOT/'config.json').exists():raise SystemExit('config.json already exists. Review it manually instead of overwriting it.')
    if args.storage_gb<=0:raise SystemExit('Storage limit must be positive.')
    config=json.loads((ROOT/'config.example.json').read_text());config.update(game_root=str(game),storage_limit_bytes=int(args.storage_gb*1_000_000_000),storage_approved=True)
    if args.pwsh:config['pwsh_path']=str(Path(args.pwsh).resolve())
    pwsh=args.pwsh or find_pwsh()
    result=subprocess.run([pwsh,'-NoProfile','-File',str(ROOT/'scripts/game_version.ps1'),'-GameRoot',str(game)],capture_output=True,text=True,encoding='utf-8',check=True)
    config.update(json.loads(result.stdout))
    for name in ('data','reports','tools'):(ROOT/name).mkdir(exist_ok=True)
    (ROOT/'config.json').write_text(json.dumps(config,indent=2),encoding='utf-8')
    print('Local configuration created. Game files were read only.')

if __name__=='__main__':main()
