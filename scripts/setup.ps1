param(
    [string]$PythonExe
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$VenvPath = Join-Path $ProjectRoot ".venv"
$RequirementsPath = Join-Path $ProjectRoot "requirements.txt"

function Resolve-BasePython {
    param([string]$RequestedPython)

    if ($RequestedPython) {
        if (-not (Test-Path $RequestedPython)) {
            throw "Requested Python executable was not found: $RequestedPython"
        }
        return (Resolve-Path $RequestedPython).Path
    }

    $candidates = @()

    try {
        $candidates += (Get-Command python.exe -All -ErrorAction Stop | Select-Object -ExpandProperty Source)
    } catch {
    }

    $commonPaths = @(
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe"
    )
    $candidates += $commonPaths

    $normalizedProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)

    foreach ($candidate in ($candidates | Select-Object -Unique)) {
        if (-not $candidate) {
            continue
        }
        if (-not (Test-Path $candidate)) {
            continue
        }

        $fullCandidate = [System.IO.Path]::GetFullPath($candidate)
        if ($fullCandidate.StartsWith($normalizedProjectRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
            continue
        }

        return $fullCandidate
    }

    throw "Unable to find a working base Python interpreter. Pass -PythonExe explicitly."
}

$ResolvedPython = Resolve-BasePython -RequestedPython $PythonExe

Write-Host "Using base Python: $ResolvedPython"

& $ResolvedPython -m venv --upgrade $VenvPath

$VenvPython = Join-Path $VenvPath "Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    throw "Virtual environment repair failed. Missing interpreter at $VenvPython"
}

& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r $RequirementsPath

Write-Host "Environment is ready."
