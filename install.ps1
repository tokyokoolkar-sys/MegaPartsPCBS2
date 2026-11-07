# Install (or -Uninstall) PCBS2 MegaParts: XML Part Loader + generated part files.
param(
    [string]$Game = "E:\Games\PC.Building.Simulator.2.v1.17.02",
    [string]$Loader = "E:\Games\PCBS2-mods-ref\PCBS2 XML Part Loader\version.dll",
    [switch]$Uninstall
)
$ErrorActionPreference = "Stop"
$mods = Join-Path $Game "mods"

# Our files are all tagged in their Notes cell, so uninstall never touches other XML mods.
Get-ChildItem $mods -Filter *.xml -ErrorAction SilentlyContinue |
    Where-Object { Select-String -Path $_.FullName -SimpleMatch "PCBS2 MegaParts", "Ported from " -Quiet } |
    Remove-Item

if ($Uninstall) {
    Write-Host "Removed MegaParts XML files. version.dll left in place (other XML mods may use it)."
    return
}

if (-not (Test-Path (Join-Path $Game "version.dll"))) { Copy-Item $Loader $Game }
New-Item -ItemType Directory -Force $mods | Out-Null
# skip.txt: our parts that a community mod already provides (community version wins).
$skip = @(Get-Content (Join-Path $PSScriptRoot "skip.txt") -ErrorAction SilentlyContinue)
$ours = Get-ChildItem (Join-Path $PSScriptRoot "out\mods") -Filter *.xml | Where-Object { $skip -notcontains $_.Name }
$ours | Copy-Item -Destination $mods
Write-Host ("Installed {0} MegaParts part files into {1} ({2} skipped as community duplicates)" -f $ours.Count, $mods, $skip.Count)
