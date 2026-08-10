[CmdletBinding()]
param(
    [switch]$Launch
)

$ErrorActionPreference = "Stop"
$PackageRoot = $PSScriptRoot
$AppRoot = Join-Path $PackageRoot "app"
$RuntimeRoot = Join-Path $PackageRoot ".runtime"
$CondaRoot = Join-Path $RuntimeRoot "miniforge"
$EnvironmentRoot = Join-Path $RuntimeRoot "unisharp"
$Python = Join-Path $EnvironmentRoot "python.exe"
$Checkpoint = Join-Path $AppRoot "checkpoints\pretained_model.pt"
$Guide = Join-Path $PackageRoot "GPU-Setup-Guide.md"

function Write-Step([string] $Message) {
    Write-Host "[UniSHARP] $Message" -ForegroundColor Cyan
}

function Invoke-Checked([string] $Executable, [string[]] $Arguments) {
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed ($LASTEXITCODE): $Executable $($Arguments -join ' ')"
    }
}

function Test-BlenderInstallation {
    if ($env:BLENDER_EXE -and (Test-Path -LiteralPath $env:BLENDER_EXE)) {
        return $true
    }
    foreach ($programFiles in @($env:ProgramFiles, $env:ProgramW6432) | Select-Object -Unique) {
        if ($programFiles) {
            $blenderRoot = Join-Path $programFiles "Blender Foundation"
            if (Get-ChildItem -Path $blenderRoot -Filter "blender.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1) {
                return $true
            }
        }
    }
    return $false
}

function Confirm-Install([string] $Component) {
    $answer = Read-Host "$Component is not installed. Download and start its installer now? [Y/n]"
    return [string]::IsNullOrWhiteSpace($answer) -or $answer -match "^[Yy]"
}

function Install-Blender {
    $Installer = Join-Path $RuntimeRoot "blender-5.2.0-windows-x64.msi"
    New-Item -ItemType Directory -Force -Path $RuntimeRoot | Out-Null
    if (-not (Test-Path -LiteralPath $Installer)) {
        Write-Step "Downloading Blender 5.2 LTS..."
        Invoke-WebRequest -Uri "https://download.blender.org/release/Blender5.2/blender-5.2.0-windows-x64.msi" -OutFile $Installer
    }
    Write-Step "Starting the Blender installer..."
    $process = Start-Process -FilePath "msiexec.exe" -ArgumentList @("/i", $Installer) -Wait -PassThru
    if ($process.ExitCode -ne 0) {
        throw "Blender installation failed with exit code $($process.ExitCode)."
    }
}

function Install-CudaToolkit {
    $Installer = Join-Path $RuntimeRoot "cuda_12.8.0_windows_network.exe"
    New-Item -ItemType Directory -Force -Path $RuntimeRoot | Out-Null
    if (-not (Test-Path -LiteralPath $Installer)) {
        Write-Step "Downloading the NVIDIA CUDA 12.8 installer..."
        Invoke-WebRequest -Uri "https://developer.download.nvidia.com/compute/cuda/12.8.0/network_installers/cuda_12.8.0_windows_network.exe" -OutFile $Installer
    }
    Write-Step "Launching the NVIDIA CUDA installer. Install the NVIDIA driver and CUDA Toolkit, then restart Windows."
    Start-Process -FilePath $Installer -Wait
}

if (-not (Test-Path -LiteralPath $AppRoot)) {
    throw "The app folder is missing: $AppRoot"
}
if (-not (Test-Path -LiteralPath $Checkpoint)) {
    throw "The UniSHARP checkpoint is missing: $Checkpoint"
}
if (-not (Test-BlenderInstallation)) {
    if (-not (Confirm-Install "Blender 5.2 LTS")) {
        Write-Host "Blender is required. Install it, then run Run-UniSHARP.cmd again." -ForegroundColor Yellow
        Start-Process $Guide
        exit 1
    }
    Install-Blender
    if (-not (Test-BlenderInstallation)) {
        throw "Blender installation finished but Blender was not detected. Restart Windows, then run Run-UniSHARP.cmd again."
    }
}

$nvidiaSmi = Get-Command nvidia-smi.exe -ErrorAction SilentlyContinue
if (-not $nvidiaSmi) {
    if (-not (Confirm-Install "NVIDIA driver / CUDA")) {
        Write-Host "An NVIDIA driver is required. Install it, then run Run-UniSHARP.cmd again." -ForegroundColor Yellow
        Start-Process $Guide
        exit 1
    }
    Install-CudaToolkit
    Write-Host "Restart Windows after installation, then run Run-UniSHARP.cmd again." -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path -LiteralPath $Python)) {
    $Installer = Join-Path $RuntimeRoot "Miniforge3-Windows-x86_64.exe"
    New-Item -ItemType Directory -Force -Path $RuntimeRoot | Out-Null
    if (-not (Test-Path -LiteralPath $Installer)) {
        Write-Step "Downloading the Python environment installer..."
        Invoke-WebRequest -Uri "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe" -OutFile $Installer
    }
    Write-Step "Installing a local Python environment..."
    $process = Start-Process -FilePath $Installer -ArgumentList @("/S", "/D=$CondaRoot") -Wait -PassThru
    if ($process.ExitCode -ne 0) {
        throw "Miniforge installation failed with exit code $($process.ExitCode)."
    }
    $Conda = Join-Path $CondaRoot "condabin\conda.bat"
    if (-not (Test-Path -LiteralPath $Conda)) {
        throw "Miniforge was installed but conda.bat was not found: $Conda"
    }
    Write-Step "Creating the UniSHARP environment..."
    Invoke-Checked $Conda @("create", "--prefix", $EnvironmentRoot, "python=3.11", "pip", "-c", "conda-forge", "-y")
}

$TorchCheck = & $Python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())" 2>$null
if ($LASTEXITCODE -ne 0 -or ($TorchCheck -notmatch "True")) {
    Write-Step "Installing PyTorch with CUDA 12.8 support..."
    Invoke-Checked $Python @("-m", "pip", "install", "--upgrade", "pip")
    Invoke-Checked $Python @("-m", "pip", "install", "torch==2.8.0", "torchvision==0.23.0", "torchaudio==2.8.0", "--index-url", "https://download.pytorch.org/whl/cu128")
    Write-Step "Installing the remaining UniSHARP dependencies..."
    Invoke-Checked $Python @("-m", "pip", "install", "-r", (Join-Path $AppRoot "requirements-portable.txt"))
}

& $Python -c "import torch; assert torch.cuda.is_available(), 'PyTorch cannot access the NVIDIA GPU'; print(f'PyTorch {torch.__version__} / CUDA {torch.version.cuda}')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "PyTorch could not access the GPU. Open the guide for driver/CUDA troubleshooting." -ForegroundColor Yellow
    Start-Process $Guide
    exit 1
}

if ($Launch) {
    Write-Step "Starting UniSHARP..."
    $env:UNISHARP_APP_ROOT = $PackageRoot
    & $Python (Join-Path $AppRoot "scripts\blender_gui.py")
}
