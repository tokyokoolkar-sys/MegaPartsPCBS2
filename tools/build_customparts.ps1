# One-shot build for the CustomParts mod: model bundles (Unity batchmode), the mod DLL, then stage
# everything to out\customparts\ laid out like the game folder. Nothing is written to the game.
#   -SkipUnity   reuse the bundles already in out\bundles (the Unity build is slow on a fresh Library)
param([switch]$SkipUnity)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$unity = 'E:\Unity\6000.2.6f2\Editor\Unity.exe'
$bundles = Join-Path $root 'out\bundles'
$stage = Join-Path $root 'out\customparts'

if (-not $SkipUnity) {
    $log = Join-Path $root 'out\unity_build.log'
    Write-Host "Unity batchmode build (log: $log)..."
    $p = Start-Process $unity -Wait -PassThru -NoNewWindow -ArgumentList @(
        '-batchmode', '-quit', '-projectPath', (Join-Path $root 'unity\ModelBundles'),
        '-executeMethod', 'BuildModelBundles.Build', '-logFile', $log)
    if ($p.ExitCode -ne 0 -or -not (Select-String -Path $log -SimpleMatch '[ModelBundles] done' -Quiet)) {
        throw "Unity build failed (exit $($p.ExitCode)); see $log"
    }
    Select-String -Path $log -SimpleMatch '[ModelBundles]' | ForEach-Object { $_.Line }
}

Write-Host 'dotnet build...'
dotnet build (Join-Path $root 'mod\CustomParts\CustomParts.csproj') -c Release --nologo -v q
if ($LASTEXITCODE -ne 0) { throw 'dotnet build failed' }

# Read the bundle names the config needs, so the stage holds exactly what parts.txt uses.
$cfg = Join-Path $root 'mod\CustomParts\parts.txt'
$need = Get-Content $cfg | Where-Object { $_.Trim() -and -not $_.Trim().StartsWith('#') } |
    ForEach-Object { ($_ -split '\|')[3].Trim() } | Sort-Object -Unique

if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
$modsDir = New-Item -ItemType Directory -Force (Join-Path $stage 'Mods\CustomParts')
$xmlDir = New-Item -ItemType Directory -Force (Join-Path $stage 'mods')
Copy-Item (Join-Path $root 'mod\CustomParts\bin\Release\net6.0\CustomParts.dll') (Join-Path $stage 'Mods')
Copy-Item $cfg $modsDir
foreach ($b in $need) {
    $f = Join-Path $bundles $b
    if (-not (Test-Path $f)) { throw "Bundle $b not found in $bundles" }
    Copy-Item $f $modsDir
}
Copy-Item (Join-Path $root 'mod\CustomParts\parts\*.xml') $xmlDir
Write-Host "Staged to $stage :"
Get-ChildItem $stage -Recurse -File | ForEach-Object { '  ' + $_.FullName.Substring($stage.Length + 1) }
