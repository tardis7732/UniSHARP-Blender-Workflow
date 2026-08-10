[CmdletBinding()]
param(
    [string] $Destination = (Join-Path (Split-Path $PSScriptRoot -Parent) "UniSHARP_Blender_Portable")
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path $PSScriptRoot -Parent
$AppDestination = Join-Path $Destination "app"
$Checkpoint = Join-Path $RepoRoot "checkpoints\pretained_model.pt"

if (-not (Test-Path -LiteralPath $Checkpoint)) {
    throw "Checkpoint not found: $Checkpoint"
}

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
Copy-Item -LiteralPath $Checkpoint -Destination (Join-Path $AppDestination "checkpoints\pretained_model.pt") -Force
Copy-Item -LiteralPath (Join-Path $RepoRoot "portable\Run-UniSHARP.cmd") -Destination $Destination -Force
Copy-Item -LiteralPath (Join-Path $RepoRoot "portable\Setup-UniSHARP.ps1") -Destination $Destination -Force
Copy-Item -LiteralPath (Join-Path $RepoRoot "portable\GPU-Setup-Guide.md") -Destination $Destination -Force
New-Item -ItemType Directory -Force -Path (Join-Path $Destination "Blender_Output") | Out-Null

@"
UniSHARP Blender portable package

1. Install Blender 5.2 LTS on this PC first.
2. Read GPU-Setup-Guide.md if this is the first run.
3. Double-click Run-UniSHARP.cmd.

The first run downloads a private Miniforge/PyTorch CUDA environment into .runtime.
Keep the app folder and checkpoint together.
"@ | Set-Content -LiteralPath (Join-Path $Destination "README.txt") -Encoding utf8

Write-Host "Portable package created: $Destination" -ForegroundColor Green
