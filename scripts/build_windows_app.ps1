$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $ProjectRoot

if (-not $IsWindows -and $env:OS -ne "Windows_NT") {
    throw "This script builds the native Windows app and must run on Windows."
}

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    py -3.12 -m venv (Join-Path $ProjectRoot ".venv")
    if ($LASTEXITCODE -ne 0) { throw "Could not create the Python virtual environment." }
}

& $Python -m pip install -e ".[desktop]"
if ($LASTEXITCODE -ne 0) { throw "Could not install desktop build dependencies." }

$BuildRoot = Join-Path $ProjectRoot "build\windows"
$env:PYINSTALLER_CONFIG_DIR = Join-Path $BuildRoot "pyinstaller-config"
New-Item -ItemType Directory -Force -Path $BuildRoot | Out-Null

$WebPath = Join-Path $ProjectRoot "src\trading_helper\web"
$DefaultsPath = Join-Path $ProjectRoot "src\trading_helper\defaults"
$PyInstallerArgs = @(
    "-m", "PyInstaller", "--noconfirm", "--windowed",
    "--name", "TradingHelper",
    "--collect-all", "webview",
    "--hidden-import", "webview.platforms.winforms",
    "--add-data", "$WebPath;trading_helper\web",
    "--add-data", "$DefaultsPath;trading_helper\defaults",
    "--add-data", "$(Join-Path $ProjectRoot 'config\settings.example.yaml');config",
    "--add-data", "$(Join-Path $ProjectRoot '.env.example');.",
    "--specpath", $BuildRoot,
    "--distpath", (Join-Path $ProjectRoot "dist\windows"),
    "--workpath", $BuildRoot,
    (Join-Path $ProjectRoot "src\trading_helper\desktop_app.py")
)
& $Python @PyInstallerArgs
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed to build TradingHelper.exe." }

$OutputDir = Join-Path $ProjectRoot "dist\windows"
$AppDir = Join-Path $OutputDir "TradingHelper"
$Archive = Join-Path $OutputDir "TradingHelper-windows-x64.zip"
if (Test-Path $Archive) { Remove-Item $Archive -Force }
Compress-Archive -Path (Join-Path $AppDir "*") -DestinationPath $Archive
Write-Output "Built: $AppDir\TradingHelper.exe"
Write-Output "Packaged: $Archive"
