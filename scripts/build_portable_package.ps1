[CmdletBinding()]
param(
    [string] $Destination = (Join-Path (Split-Path $PSScriptRoot -Parent) "UniSHARP_Blender_Portable")
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path $PSScriptRoot -Parent
$AppDestination = Join-Path $Destination "app"
New-Item -ItemType Directory -Force -Path $Destination, $AppDestination | Out-Null

$RobocopyArguments = @(
    $RepoRoot,
    $AppDestination,
    "/E",
    "/XD", ".git", "build", "outputs", "checkpoints", "__pycache__", "UniSHARP_Blender_Portable",
    "/XF", "launch_blender_gui.bat",
    "/NFL", "/NDL", "/NJH", "/NJS", "/NP"
)
& robocopy @RobocopyArguments
if ($LASTEXITCODE -gt 7) {
    throw "App copy failed (robocopy exit code $LASTEXITCODE)."
}

New-Item -ItemType Directory -Force -Path (Join-Path $AppDestination "checkpoints") | Out-Null
Copy-Item -LiteralPath (Join-Path $RepoRoot "portable\Run-UniSHARP.cmd") -Destination $Destination -Force
Copy-Item -LiteralPath (Join-Path $RepoRoot "portable\Setup-UniSHARP.ps1") -Destination $Destination -Force
Copy-Item -LiteralPath (Join-Path $RepoRoot "portable\GPU-Setup-Guide.md") -Destination $Destination -Force
New-Item -ItemType Directory -Force -Path (Join-Path $Destination "Blender_Output") | Out-Null

@"
UniSHARP Blender portable package

1. Install Blender 3.6 or newer on this PC, or let the launcher install Blender 5.2 LTS as its default.
2. Read GPU-Setup-Guide.md if this is the first run.
3. Double-click Run-UniSHARP.cmd.

The first run downloads the official UniSHARP checkpoint (about 4.7 GB) when it is missing, then creates a private Miniforge/PyTorch CUDA environment in .runtime.
Keep the app folder together.
"@ | Set-Content -LiteralPath (Join-Path $Destination "README.txt") -Encoding utf8

Write-Host "Portable package created: $Destination" -ForegroundColor Green
