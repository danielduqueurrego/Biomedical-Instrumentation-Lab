$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..\..")).Path
$entryScript = Join-Path $repoRoot "python\run_student_acquisition_gui.py"
$pyInstallerDistDir = Join-Path $repoRoot "dist\Biomedical Instrumentation Lab"
$pyInstallerBuildDir = Join-Path $repoRoot "build\Biomedical Instrumentation Lab"
$arduinoCliCandidatePaths = @(
    "C:\arduino-cli\arduino-cli.exe",
    (Join-Path $env:ProgramFiles "Arduino CLI\arduino-cli.exe"),
    (Join-Path ${env:ProgramFiles(x86)} "Arduino CLI\arduino-cli.exe")
) | Select-Object -Unique

$arduinoCliPath = $null
foreach ($candidate in $arduinoCliCandidatePaths) {
    if ($candidate -and (Test-Path $candidate)) {
        $arduinoCliPath = (Resolve-Path $candidate).Path
        break
    }
}

if (-not $arduinoCliPath) {
    $whereOutput = & where.exe arduino-cli 2>$null
    if ($LASTEXITCODE -eq 0 -and $whereOutput) {
        $arduinoCliPath = ($whereOutput | Select-Object -First 1).Trim()
    }
}

$installerPayloadDir = Join-Path $repoRoot "dist\installer-payload\arduino-cli"
$installerPayloadParent = Split-Path -Parent $installerPayloadDir
if (Test-Path $installerPayloadDir) {
    Remove-Item -LiteralPath $installerPayloadDir -Recurse -Force
}

if ($arduinoCliPath) {
    if (-not (Test-Path $installerPayloadParent)) {
        New-Item -ItemType Directory -Force -Path $installerPayloadParent | Out-Null
    }
    New-Item -ItemType Directory -Force -Path $installerPayloadDir | Out-Null
    Copy-Item -LiteralPath $arduinoCliPath -Destination (Join-Path $installerPayloadDir "arduino-cli.exe") -Force
    $arduinoCliSourceDir = Split-Path -Parent $arduinoCliPath
    $licensePath = Join-Path $arduinoCliSourceDir "LICENSE.txt"
    if (Test-Path $licensePath) {
        Copy-Item -LiteralPath $licensePath -Destination (Join-Path $installerPayloadDir "LICENSE.txt") -Force
    }
    Write-Host "Bundled Arduino CLI from:"
    Write-Host "  $arduinoCliPath"
}
else {
    Write-Warning "arduino-cli.exe was not found. The installer can still be built, but Arduino CLI will not be bundled."
    if ((Test-Path $installerPayloadParent) -and -not (Get-ChildItem -LiteralPath $installerPayloadParent -Force | Select-Object -First 1)) {
        Remove-Item -LiteralPath $installerPayloadParent -Force
    }
}

$runningBundledApp = Get-Process | Where-Object {
    $_.Path -eq (Join-Path $pyInstallerDistDir "Biomedical Instrumentation Lab.exe")
}
foreach ($process in $runningBundledApp) {
    Stop-Process -Id $process.Id -Force
}

if (Test-Path $pyInstallerDistDir) {
    Remove-Item -LiteralPath $pyInstallerDistDir -Recurse -Force
}

if (Test-Path $pyInstallerBuildDir) {
    Remove-Item -LiteralPath $pyInstallerBuildDir -Recurse -Force
}

$pyInstallerArgs = @(
    "--noconfirm"
    "--clean"
    "--onedir"
    "--windowed"
    "--name"
    "Biomedical Instrumentation Lab"
    "--paths"
    (Join-Path $repoRoot "python")
    "--add-data"
    ((Join-Path $repoRoot "firmware") + ";firmware")
    "--add-data"
    ((Join-Path $repoRoot "python\session_presets") + ";python/session_presets")
    "--hidden-import"
    "matplotlib.backends.backend_tkagg"
    "--hidden-import"
    "serial.tools.list_ports"
    $entryScript
)

Write-Host "Building Windows student GUI bundle with PyInstaller..."
Push-Location $repoRoot
try {
    pyinstaller @pyInstallerArgs
}
finally {
    Pop-Location
}

Write-Host ""
Write-Host "Build finished."
Write-Host "Executable:"
Write-Host "  dist\Biomedical Instrumentation Lab\Biomedical Instrumentation Lab.exe"
if ($arduinoCliPath) {
    Write-Host "Bundled Arduino CLI payload:"
    Write-Host "  dist\installer-payload\arduino-cli\arduino-cli.exe"
}
