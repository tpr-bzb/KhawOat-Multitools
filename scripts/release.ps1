param(
    [switch]$SkipChecks,
    [switch]$SkipExeBuild,
    [switch]$SkipInstallerBuild
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PowerShellExe = (Get-Process -Id $PID).Path
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$LogDir = Join-Path $ProjectRoot "logs"
$ReleaseLogFile = Join-Path $LogDir "release.log"
$ReleaseLogMaxBytes = 524288
$ReleaseLogBackupCount = 5
$CheckScript = Join-Path $PSScriptRoot "check.ps1"
$VersionFile = Join-Path $ProjectRoot "version.json"
$ManifestFile = Join-Path $ProjectRoot "manifest.json"
$SpecFile = Join-Path $ProjectRoot "KhawOat_MultiTools_Pro.spec"
$InstallerFile = Join-Path $ProjectRoot "setting.iss"
$DistExe = Join-Path $ProjectRoot "dist\KhawOat_MultiTools_Pro.exe"
$ReleaseMetadataTest = Join-Path $PSScriptRoot "release_metadata_unit.py"
$ReleaseSummaryFile = Join-Path $LogDir "release-summary.txt"

function Invoke-CheckedCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Executable,
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$Arguments
    )

    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) {
        Write-ReleaseLog "ERROR" "command_failed executable=$Executable arguments=$($Arguments -join ' ') exit_code=$LASTEXITCODE"
        throw "Command failed with exit code ${LASTEXITCODE}: $Executable $($Arguments -join ' ')"
    }
}

function Write-ReleaseLog {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Level,
        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    if (-not (Test-Path $LogDir)) {
        New-Item -ItemType Directory -Path $LogDir | Out-Null
    }

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $ReleaseLogFile -Value "$timestamp | $Level | $Message"
}

function Rotate-ReleaseLogIfNeeded {
    if (-not (Test-Path $ReleaseLogFile)) {
        return
    }

    $logItem = Get-Item $ReleaseLogFile
    if ($logItem.Length -lt $ReleaseLogMaxBytes) {
        return
    }

    for ($index = $ReleaseLogBackupCount - 1; $index -ge 1; $index--) {
        $source = "$ReleaseLogFile.$index"
        $destination = "$ReleaseLogFile." + ($index + 1)
        if (Test-Path $source) {
            Move-Item -Force $source $destination
        }
    }

    Move-Item -Force $ReleaseLogFile "$ReleaseLogFile.1"
}

function Find-ISCC {
    $candidates = @(
        (Get-Command ISCC.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -ErrorAction SilentlyContinue),
        (Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 7\ISCC.exe"),
        "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        "C:\Program Files\Inno Setup 6\ISCC.exe",
        "C:\Program Files (x86)\Inno Setup 7\ISCC.exe",
        "C:\Program Files\Inno Setup 7\ISCC.exe"
    ) | Where-Object { $_ }

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    return $null
}

function Get-ReleaseVersion {
    if (-not (Test-Path $VersionFile)) {
        throw "Missing version.json"
    }

    $versionData = Get-Content $VersionFile -Raw | ConvertFrom-Json
    if (-not $versionData.version) {
        throw "version.json does not contain a version value"
    }

    return [string]$versionData.version
}

function Get-ManifestVersion {
    if (-not (Test-Path $ManifestFile)) {
        throw "Missing manifest.json"
    }

    $manifestData = Get-Content $ManifestFile -Raw | ConvertFrom-Json
    if (-not $manifestData.version) {
        throw "manifest.json does not contain a version value"
    }

    return [string]$manifestData.version
}

function Get-InstallerArtifactPath {
    $installerText = Get-Content $InstallerFile -Raw

    $outputBaseMatch = [regex]::Match($installerText, "OutputBaseFilename=([^\r\n]+)")
    if (-not $outputBaseMatch.Success) {
        throw "Unable to resolve OutputBaseFilename from setting.iss"
    }

    $outputDirMatch = [regex]::Match($installerText, "OutputDir=([^\r\n]+)")
    $outputDir = if ($outputDirMatch.Success) { $outputDirMatch.Groups[1].Value.Trim() } else { "Output" }
    if (-not [System.IO.Path]::IsPathRooted($outputDir)) {
        $outputDir = Join-Path $ProjectRoot $outputDir
    }
    $baseName = $outputBaseMatch.Groups[1].Value.Trim()

    return (Join-Path $outputDir ($baseName + ".exe"))
}

function Get-InstallerConfiguredVersion {
    $installerText = Get-Content $InstallerFile -Raw
    $versionMatch = [regex]::Match($installerText, '#define MyAppVersion "([^"]+)"')
    if (-not $versionMatch.Success) {
        throw "Unable to resolve MyAppVersion from setting.iss"
    }

    return $versionMatch.Groups[1].Value.Trim()
}

function Format-ArtifactSummary {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $item = Get-Item $Path
    return "{0} ({1} bytes)" -f $item.FullName, $item.Length
}

function Assert-ArtifactFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [Parameter(Mandatory = $true)]
        [string]$Label
    )

    if (-not (Test-Path $Path)) {
        throw "$Label artifact not found: $Path"
    }

    $item = Get-Item $Path
    if ($item.Length -le 0) {
        throw "$Label artifact is empty: $Path"
    }
}

function Write-ReleaseSummary {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Version,
        [Parameter(Mandatory = $true)]
        [string]$ManifestVersion,
        [Parameter(Mandatory = $true)]
        [string]$InstallerConfiguredVersion,
        [Parameter(Mandatory = $true)]
        [bool]$ForceSetup,
        [string]$ExecutablePath,
        [string]$InstallerPath
    )

    $summaryLines = @(
        "Release Checklist",
        "Version: $Version",
        "Manifest Version: $ManifestVersion",
        "Installer Version: $InstallerConfiguredVersion",
        "Force Setup: $ForceSetup",
        "Manifest: $ManifestFile"
    )

    if ($ExecutablePath) {
        $summaryLines += "Executable: $(Format-ArtifactSummary -Path $ExecutablePath)"
    } else {
        $summaryLines += "Executable: skipped"
    }

    if ($InstallerPath) {
        $summaryLines += "Installer: $(Format-ArtifactSummary -Path $InstallerPath)"
    } else {
        $summaryLines += "Installer: skipped"
    }

    Set-Content -Path $ReleaseSummaryFile -Value $summaryLines -Encoding UTF8
}

if (-not (Test-Path $VenvPython)) {
    throw "Missing virtual environment. Run scripts/setup.ps1 first."
}

if (-not (Test-Path $SpecFile)) {
    throw "Missing PyInstaller spec file: $SpecFile"
}

if (-not (Test-Path $InstallerFile)) {
    throw "Missing installer script: $InstallerFile"
}

Set-Location $ProjectRoot
Rotate-ReleaseLogIfNeeded

$releaseVersion = Get-ReleaseVersion
$versionData = Get-Content $VersionFile -Raw | ConvertFrom-Json
$forceSetup = [bool]$versionData.force_setup
$installerArtifact = Get-InstallerArtifactPath
$installerConfiguredVersion = Get-InstallerConfiguredVersion
$builtExePath = $null
$builtInstallerPath = $null

Write-Host "Preparing release for version $releaseVersion"
Write-ReleaseLog "INFO" "release_start version=$releaseVersion force_setup=$forceSetup skip_checks=$SkipChecks skip_exe=$SkipExeBuild skip_installer=$SkipInstallerBuild"

if (-not $SkipChecks) {
    Write-Host "Running project checks..."
    Write-ReleaseLog "INFO" "checks_start"
    Invoke-CheckedCommand $PowerShellExe "-ExecutionPolicy" "Bypass" "-File" $CheckScript
    Write-ReleaseLog "INFO" "checks_complete"
}

Write-Host "Regenerating manifest..."
Write-ReleaseLog "INFO" "manifest_regenerate_start"
Invoke-CheckedCommand $VenvPython "generate_manifest.py"

if (-not (Test-Path $ManifestFile)) {
    Write-ReleaseLog "ERROR" "manifest_missing_after_regeneration"
    throw "Manifest generation failed: manifest.json not found"
}

$manifestVersion = Get-ManifestVersion
if ($manifestVersion -ne $releaseVersion) {
    Write-ReleaseLog "ERROR" "manifest_version_mismatch release_version=$releaseVersion manifest_version=$manifestVersion"
    throw "Manifest version mismatch after regeneration. version.json=$releaseVersion manifest.json=$manifestVersion"
}
Write-ReleaseLog "INFO" "manifest_regenerate_complete manifest_version=$manifestVersion"

if ($installerConfiguredVersion -ne $releaseVersion) {
    Write-ReleaseLog "ERROR" "installer_version_mismatch release_version=$releaseVersion installer_version=$installerConfiguredVersion"
    throw "Installer version mismatch. version.json=$releaseVersion setting.iss=$installerConfiguredVersion"
}
Write-ReleaseLog "INFO" "installer_version_validated installer_version=$installerConfiguredVersion"

Write-Host "Re-validating release metadata..."
Write-ReleaseLog "INFO" "release_metadata_validation_start"
Invoke-CheckedCommand $VenvPython $ReleaseMetadataTest
Write-ReleaseLog "INFO" "release_metadata_validation_complete"

if (-not $SkipChecks) {
    Write-Host "Running project checks again after manifest refresh..."
    Write-ReleaseLog "INFO" "checks_post_manifest_start"
    Invoke-CheckedCommand $PowerShellExe "-ExecutionPolicy" "Bypass" "-File" $CheckScript
    Write-ReleaseLog "INFO" "checks_post_manifest_complete"
}

if (-not $SkipExeBuild) {
    Write-Host "Building executable with PyInstaller..."
    Write-ReleaseLog "INFO" "exe_build_start"
    Invoke-CheckedCommand $VenvPython "-m" "PyInstaller" "--noconfirm" $SpecFile

    Assert-ArtifactFile -Path $DistExe -Label "Executable"
    $builtExePath = $DistExe
    Write-ReleaseLog "INFO" "exe_build_complete path=$builtExePath"
}

if (-not $SkipInstallerBuild) {
    $isccPath = Find-ISCC
    if (-not $isccPath) {
        Write-ReleaseLog "ERROR" "iscc_not_found"
        throw "Inno Setup compiler (ISCC.exe) not found. Install Inno Setup or rerun with -SkipInstallerBuild."
    }

    Assert-ArtifactFile -Path $DistExe -Label "Executable required for installer build"

    Write-Host "Building installer with Inno Setup..."
    Write-ReleaseLog "INFO" "installer_build_start compiler=$isccPath"
    Invoke-CheckedCommand $isccPath $InstallerFile
    Assert-ArtifactFile -Path $installerArtifact -Label "Installer"
    if ([System.IO.Path]::GetFileNameWithoutExtension($installerArtifact) -notmatch [regex]::Escape($releaseVersion)) {
        Write-ReleaseLog "ERROR" "installer_filename_version_mismatch path=$installerArtifact version=$releaseVersion"
        throw "Installer filename does not include expected version: $installerArtifact"
    }
    $builtInstallerPath = $installerArtifact
    Write-ReleaseLog "INFO" "installer_build_complete path=$builtInstallerPath"
}

Write-ReleaseSummary `
    -Version $releaseVersion `
    -ManifestVersion $manifestVersion `
    -InstallerConfiguredVersion $installerConfiguredVersion `
    -ForceSetup $forceSetup `
    -ExecutablePath $builtExePath `
    -InstallerPath $builtInstallerPath

Write-Host ""
Write-Host "Release workflow completed successfully."
Write-Host "Version: $releaseVersion"
Write-Host "Manifest: $ManifestFile"
Write-Host "Force Setup: $forceSetup"
if ($builtExePath) {
    Write-Host "Executable: $builtExePath"
}
if ($builtInstallerPath) {
    Write-Host "Installer: $builtInstallerPath"
}
Write-Host "Summary: $ReleaseSummaryFile"
Write-ReleaseLog "INFO" "release_complete manifest=$ManifestFile executable=$builtExePath installer=$builtInstallerPath"
