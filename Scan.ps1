$ErrorActionPreference='Stop'
if($PSVersionTable.PSVersion -lt [version]'7.6'){throw 'Use PowerShell 7.6 or newer with the .NET 10 runtime.'}
Push-Location $PSScriptRoot
try {
    if(Test-Path -LiteralPath 'data\archive.db'){throw 'This scan already has a database. Use Rebuild.ps1, or a separate workspace for another version.'}
    function Invoke-NcaPython { param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Arguments) & python -X utf8 @Arguments; if($LASTEXITCODE -ne 0){throw "Pipeline step failed: $Arguments"} }
    Invoke-NcaPython @('scripts\manifest.py','before')
    & .\scripts\bridge.ps1 -Mode index
    Invoke-NcaPython @('scripts\catalog.py')
    Invoke-NcaPython @('scripts\select_decode.py')
    & .\scripts\bridge.ps1 -Mode decode -RequestFile (Join-Path $PSScriptRoot 'data\decode-request.json') -Output 'data\decoded' -MaxBytes 2000000000
    Invoke-NcaPython @('scripts\text_index.py')
    Invoke-NcaPython @('scripts\discover.py')
    Invoke-NcaPython @('scripts\curate.py')
    Invoke-NcaPython @('scripts\manifest.py','after')
    $ncAudit=Get-Content -LiteralPath 'reports\game-after-summary.json' -Raw | ConvertFrom-Json
    if(!$ncAudit.unchanged){throw 'Source files changed during the scan. Inspect the integrity report.'}
} finally { Pop-Location }
