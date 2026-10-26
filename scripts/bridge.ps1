param([ValidateSet('index','extract','decode')][string]$Mode='index',[string]$RequestFile='', [string]$Output='data\raw', [long]$MaxBytes=4000000000)
$ErrorActionPreference='Stop'
$ncRoot=Split-Path $PSScriptRoot -Parent
$ncConfig=Get-Content -LiteralPath (Join-Path $ncRoot 'config.json') -Raw | ConvertFrom-Json
$ncGame=$ncConfig.game_root
$ncTool=Join-Path $ncRoot 'tools\wolvenkit-9.1.0'
Get-ChildItem -LiteralPath $ncTool -Filter 'WolvenKit*.dll' | ForEach-Object { [System.Reflection.Assembly]::LoadFrom($_.FullName) | Out-Null }
$ncBridge=Join-Path $ncRoot 'tools\NCA.Bridge.dll'
if(!(Test-Path $ncBridge) -or (Get-Item "$PSScriptRoot\WolvenBridge.cs").LastWriteTime -gt (Get-Item $ncBridge).LastWriteTime){
  $ncRuntime=Get-ChildItem 'C:\Program Files\dotnet\shared\Microsoft.NETCore.App' -Directory | Where-Object Name -Like '10.*' | Sort-Object Name -Descending | Select-Object -First 1
  $ncDlls=@(Get-ChildItem $ncRuntime.FullName -Filter '*.dll')+@(Get-ChildItem $ncTool -Filter 'WolvenKit*.dll')
  $ncRefs=foreach($ncDll in $ncDlls){try{[Reflection.AssemblyName]::GetAssemblyName($ncDll.FullName)|Out-Null; '/reference:"'+$ncDll.FullName+'"'}catch{}}
  $ncResponse=@('/nostdlib+','/target:library','/langversion:latest',('/out:"'+$ncBridge+'"'))+$ncRefs+@(('"'+$PSScriptRoot+'\WolvenBridge.cs"'))
  $ncRsp=Join-Path $ncRoot 'data\bridge.rsp'; $ncResponse | Set-Content $ncRsp -Encoding utf8
  $ncSdk=Get-ChildItem 'C:\Program Files\dotnet\sdk' -Directory | Sort-Object Name -Descending | Select-Object -First 1
  & dotnet (Join-Path $ncSdk.FullName 'Roslyn\bincore\csc.dll') ('@'+$ncRsp)
  if($LASTEXITCODE -ne 0){throw 'Bridge compilation failed'}
}
[Reflection.Assembly]::LoadFrom($ncBridge)|Out-Null
if($Mode -eq 'index'){ [WolvenBridge]::Index($ncGame,(Join-Path $ncRoot 'data')) }
elseif($Mode -eq 'decode'){ [WolvenBridge]::Decode($ncGame,$RequestFile,(Join-Path $ncRoot $Output),$MaxBytes) }
else { [WolvenBridge]::Extract($ncGame,$RequestFile,(Join-Path $ncRoot $Output),$MaxBytes) }
