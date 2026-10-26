param([switch]$FromCache,[switch]$Keep)
$ErrorActionPreference='Stop'
Push-Location $PSScriptRoot
try {
    $ncArgs=@('-X','utf8','scripts\rebuild.py')
    if($FromCache){$ncArgs+='--from-cache'}
    if($Keep){$ncArgs+='--keep'}
    & python @ncArgs
    if($LASTEXITCODE -ne 0){throw 'Rebuild did not pass; see reports/rebuild.json or the preceding error.'}
} finally { Pop-Location }
