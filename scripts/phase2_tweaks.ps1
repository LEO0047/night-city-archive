param([switch]$IncludeModdedCache,[string]$ResourceRequest='', [switch]$SkipBuffers, [string]$ResourceOutput='resource-scans')
$ErrorActionPreference='Stop'
$ncRoot=Split-Path $PSScriptRoot -Parent
$ncConfig=Get-Content -LiteralPath (Join-Path $ncRoot 'config.json') -Raw | ConvertFrom-Json
$ncTool=Join-Path $ncRoot 'tools\wolvenkit-9.1.0'
Get-ChildItem -LiteralPath $ncTool -Filter 'WolvenKit*.dll' | ForEach-Object { [Reflection.Assembly]::LoadFrom($_.FullName) | Out-Null }
$ncCodeHash=(Get-FileHash -LiteralPath "$PSScriptRoot\Phase2Bridge.cs" -Algorithm SHA256).Hash.Substring(0,12)
$ncBridge=Join-Path $ncRoot ('tools\NCA.Phase2.'+$ncCodeHash+'.dll')
if(!(Test-Path $ncBridge) -or (Get-Item "$PSScriptRoot\Phase2Bridge.cs").LastWriteTime -gt (Get-Item $ncBridge).LastWriteTime){
  $ncRuntime=Get-ChildItem 'C:\Program Files\dotnet\shared\Microsoft.NETCore.App' -Directory | Where-Object Name -Like '10.*' | Sort-Object Name -Descending | Select-Object -First 1
  $ncDlls=@(Get-ChildItem $ncRuntime.FullName -Filter '*.dll')+@(Get-ChildItem $ncTool -Filter 'WolvenKit*.dll')
  $ncRefs=foreach($ncDll in $ncDlls){try{[Reflection.AssemblyName]::GetAssemblyName($ncDll.FullName)|Out-Null; '/reference:"'+$ncDll.FullName+'"'}catch{}}
  $ncResponse=@('/nostdlib+','/target:library','/langversion:latest',('/out:"'+$ncBridge+'"'))+$ncRefs+@(('"'+$PSScriptRoot+'\Phase2Bridge.cs"'))
  $ncRsp=Join-Path $ncRoot 'data\phase2\bridge.rsp'; $ncResponse | Set-Content $ncRsp -Encoding utf8
  $ncSdk=Get-ChildItem 'C:\Program Files\dotnet\sdk' -Directory | Sort-Object Name -Descending | Select-Object -First 1
  & dotnet (Join-Path $ncSdk.FullName 'Roslyn\bincore\csc.dll') ('@'+$ncRsp)
  if($LASTEXITCODE -ne 0){throw 'Bridge compilation failed'}
}
[Reflection.Assembly]::LoadFrom($ncBridge)|Out-Null
if($ResourceRequest){
  $ncResourcePath=[IO.Path]::GetFullPath((Join-Path $ncRoot ('data/phase2/'+$ResourceOutput)))
  $ncBound=[IO.Path]::GetFullPath((Join-Path $ncRoot 'data/phase2'))+[IO.Path]::DirectorySeparatorChar
  if(!$ncResourcePath.StartsWith($ncBound,[StringComparison]::OrdinalIgnoreCase)){throw 'Output outside phase2'}
  [Phase2Bridge]::ScanResources($ncConfig.game_root,$ResourceRequest,$ncResourcePath,1500000000,(!$SkipBuffers))
  return
}
$ncRelative=@('r6/cache/tweakdb.bin','r6/cache/tweakdb_ep1.bin')
if($IncludeModdedCache){$ncRelative+=@('r6/cache/modded/tweakdb.bin','r6/cache/modded/tweakdb_ep1.bin')}
foreach($ncPath in $ncRelative){
  $ncInput=Join-Path $ncConfig.game_root $ncPath
  if(!(Test-Path -LiteralPath $ncInput)){continue}
  $ncOutput=Join-Path $ncRoot ('data/phase2/'+$ncPath.Replace('/','_')+'.jsonl.gz')
  $ncManifest=$ncOutput+'.manifest.json'
  $ncSourceHash=(Get-FileHash -LiteralPath $ncInput -Algorithm SHA256).Hash
  $ncParserHash=(Get-FileHash -LiteralPath "$PSScriptRoot\Phase2Bridge.cs" -Algorithm SHA256).Hash
  if((Test-Path -LiteralPath $ncOutput) -and (Test-Path -LiteralPath $ncManifest)){
    $ncPrior=Get-Content -LiteralPath $ncManifest -Raw | ConvertFrom-Json
    if($ncPrior.source_sha256 -eq $ncSourceHash -and $ncPrior.parser_sha256 -eq $ncParserHash){Write-Output "Cached $ncPath";continue}
  }
  $ncBound=[IO.Path]::GetFullPath((Join-Path $ncRoot 'data/phase2'))+[IO.Path]::DirectorySeparatorChar
  if(![IO.Path]::GetFullPath($ncOutput).StartsWith($ncBound,[StringComparison]::OrdinalIgnoreCase)){throw 'Unexpected output directory'}
  [Phase2Bridge]::Tweaks($ncInput,($ncOutput+'.partial'))
  Move-Item -LiteralPath ($ncOutput+'.partial') -Destination $ncOutput -Force
  @{source=$ncPath;source_sha256=$ncSourceHash;parser_sha256=$ncParserHash;output_sha256=(Get-FileHash -LiteralPath $ncOutput -Algorithm SHA256).Hash} | ConvertTo-Json | Set-Content -LiteralPath $ncManifest -Encoding utf8
}
