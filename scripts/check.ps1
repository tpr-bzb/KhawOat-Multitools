$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$SmokeCheck = Join-Path $PSScriptRoot "smoke_check.py"
$HandlerSmokeCheck = Join-Path $PSScriptRoot "handler_smoke.py"
$ServicesUnitCheck = Join-Path $PSScriptRoot "services_unit.py"
$ReleaseMetadataUnitCheck = Join-Path $PSScriptRoot "release_metadata_unit.py"
$UpdaterE2ECheck = Join-Path $PSScriptRoot "updater_e2e.py"

function Invoke-CheckedCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Executable,
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$Arguments
    )

    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $Executable $($Arguments -join ' ')"
    }
}

if (-not (Test-Path $VenvPython)) {
    throw "Missing virtual environment. Run scripts/setup.ps1 first."
}

Set-Location $ProjectRoot

Invoke-CheckedCommand $VenvPython -m py_compile main.py app_release.py app_runtime.py handlers_basic.py handlers_tools.py ui_views.py services.py ui_config.py generate_manifest.py check_file.py
Invoke-CheckedCommand $VenvPython $SmokeCheck
Invoke-CheckedCommand $VenvPython $HandlerSmokeCheck
Invoke-CheckedCommand $VenvPython $ServicesUnitCheck
Invoke-CheckedCommand $VenvPython $ReleaseMetadataUnitCheck
Invoke-CheckedCommand $VenvPython $UpdaterE2ECheck

Write-Host "Project checks passed."
