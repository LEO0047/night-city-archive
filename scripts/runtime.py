"""Discover an optional PowerShell runtime without embedding a machine-specific path."""
import json,os,shutil
from pathlib import Path

def find_pwsh(required=True):
    root=Path(__file__).resolve().parents[1]
    cfg=root/'config.json';config=json.loads(cfg.read_text()) if cfg.exists() else {}
    candidates=[os.environ.get('NCA_PWSH'),config.get('pwsh_path'),shutil.which('pwsh')]
    if os.name=='nt':candidates.append(str(Path(os.environ.get('ProgramFiles','C:/Program Files'))/'PowerShell/7/pwsh.exe'))
    for candidate in candidates:
        if candidate and Path(candidate).is_file():return str(Path(candidate).resolve())
    if required:raise RuntimeError('PowerShell 7.6 required. Install it or set NCA_PWSH / config.json pwsh_path.')
    return None
