Param(
    [string]$Version = "0.1.0",
    [string]$VenvPath = ".venv",
    [string]$DistDir = "dist",
    [switch]$SkipInstaller
)

$ErrorActionPreference = "Stop"

function Step($msg) {
    Write-Host "`n==> $msg" -ForegroundColor Cyan
}

$python = Join-Path $VenvPath "Scripts\python.exe"
$pip = Join-Path $VenvPath "Scripts\pip.exe"

if (-not (Test-Path $python)) {
    throw "Python venv not found at $python. Run scripts/dev-setup-windows.ps1 first."
}

Step "Installing PyInstaller"
& $pip install pyinstaller

Step "Building standalone executable"
& $python -m PyInstaller --noconfirm --clean --name DJSelector --windowed main.py

$bundleDir = Join-Path $DistDir "DJSelector"
if (-not (Test-Path $bundleDir)) {
    throw "Expected bundle not found at $bundleDir"
}

Step "Copying runtime docs"
Copy-Item README.md -Destination $bundleDir -Force

if ($SkipInstaller) {
    Write-Host "Skipping installer build by request (-SkipInstaller)."
    exit 0
}

$iss = "installer/windows/DJSelector.iss"
if (-not (Test-Path $iss)) {
    throw "Inno Setup script not found at $iss"
}

$innoCandidates = @(
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles}\Inno Setup 6\ISCC.exe"
)

$inno = $innoCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $inno) {
    throw "ISCC.exe not found. Install Inno Setup 6 and retry."
}

Step "Building installer via Inno Setup"
& $inno "/DAppVersion=$Version" $iss

Step "Build complete"
Write-Host "Portable app: dist/DJSelector/"
Write-Host "Installer: installer/windows/output/"
