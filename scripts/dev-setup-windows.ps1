Param(
    [string]$VenvPath = ".venv",
    [switch]$SkipWinget,
    [switch]$SkipPipInstall
)

$ErrorActionPreference = "Stop"

function Write-Step($msg) {
    Write-Host "`n==> $msg" -ForegroundColor Cyan
}

function Ensure-Command($name, $installHint) {
    if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
        throw "Missing required command '$name'. $installHint"
    }
}

Write-Step "Checking required tools"
Ensure-Command "py" "Install Python 3.10+ from https://www.python.org/downloads/windows/"

if (-not $SkipWinget) {
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Step "Ensuring native audio dependency (libsndfile) via winget"
        winget install --id GnuWin32.Libsndfile --silent --accept-package-agreements --accept-source-agreements | Out-Host
    }
    else {
        Write-Host "winget not found; skipping native dependency install." -ForegroundColor Yellow
        Write-Host "If soundfile fails later, install libsndfile manually." -ForegroundColor Yellow
    }
}

Write-Step "Creating virtual environment at $VenvPath"
py -3 -m venv $VenvPath

$pythonExe = Join-Path $VenvPath "Scripts\python.exe"
$pipExe = Join-Path $VenvPath "Scripts\pip.exe"

Write-Step "Upgrading pip/setuptools/wheel"
& $pythonExe -m pip install --upgrade pip setuptools wheel

if (-not $SkipPipInstall) {
    Write-Step "Installing project dependencies"
    & $pipExe install -r requirements.txt
}

Write-Step "Validating environment"
& $pythonExe -c "import sys; print('Python:', sys.version)"

Write-Step "Done"
Write-Host "Activate env: $VenvPath\Scripts\Activate.ps1"
Write-Host "Run app:    python main.py"
Write-Host "Run tests:  python -m pytest -q"
