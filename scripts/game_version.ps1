param([Parameter(Mandatory=$true)][string]$GameRoot)
$ErrorActionPreference='Stop'
$ncExe=Join-Path $GameRoot 'bin\x64\Cyberpunk2077.exe'
$ncVersion=[Diagnostics.FileVersionInfo]::GetVersionInfo($ncExe)
$ncResult=[ordered]@{game_product_version=$ncVersion.ProductVersion;game_file_version=$ncVersion.FileVersion;gog_version='UNKNOWN';gog_build='UNKNOWN'}
$ncGog=Get-ChildItem -LiteralPath $GameRoot -Filter 'goggame-*.info' | Select-Object -First 1
if($ncGog){
    $ncInfo=Get-Content -LiteralPath $ncGog.FullName -Raw | ConvertFrom-Json
    if($ncInfo.buildId){$ncResult.gog_build=[string]$ncInfo.buildId}
    if($ncInfo.version){$ncResult.gog_version=[string]$ncInfo.version}
}
$ncResult | ConvertTo-Json -Compress
