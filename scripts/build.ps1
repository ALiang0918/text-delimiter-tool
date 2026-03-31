param(
    [string]$Python = "python",
    [string]$Name = "TextDelimiterTool",
    [string]$Entry = "run_app.py",
    [string]$IconPath = "assets/app.ico",
    [string]$VersionPath = "VERSION",
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

$pyinstallerCheck = & $Python -m PyInstaller --version 2>$null
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller is not installed. Run: $Python -m pip install pyinstaller"
}

if (-not (Test-Path $VersionPath)) {
    throw "Version file not found: $VersionPath"
}

$versionText = (Get-Content $VersionPath -Raw).Trim()
if ([string]::IsNullOrWhiteSpace($versionText)) {
    throw "Version file is empty: $VersionPath"
}

$versionParts = $versionText.Split('.')
if ($versionParts.Count -ne 3) {
    throw "Version must use semantic format major.minor.patch, got: $versionText"
}

$versionTuple = "{0}, {1}, {2}, 0" -f $versionParts[0], $versionParts[1], $versionParts[2]
$versionQuad = "{0}.{1}.{2}.0" -f $versionParts[0], $versionParts[1], $versionParts[2]
$generatedVersionFile = Join-Path $projectRoot 'build\version-info.generated.txt'
$generatedDir = Split-Path -Parent $generatedVersionFile
New-Item -ItemType Directory -Force -Path $generatedDir | Out-Null

@"
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=($versionTuple),
    prodvers=($versionTuple),
    mask=0x3F,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        '040904B0',
        [
          StringStruct('FileDescription', 'Windows text formatting utility for delimiter-ready output'),
          StringStruct('FileVersion', '$versionQuad'),
          StringStruct('InternalName', 'TextDelimiterTool'),
          StringStruct('OriginalFilename', 'TextDelimiterTool.exe'),
          StringStruct('ProductName', 'Text Delimiter Tool'),
          StringStruct('ProductVersion', '$versionQuad')
        ]
      )
    ]),
    VarFileInfo([
      VarStruct('Translation', [1033, 1200])
    ])
  ]
)
"@ | Set-Content $generatedVersionFile

$command = @(
    "-m", "PyInstaller",
    "--noconfirm",
    "--onefile",
    "--windowed",
    "--name", $Name,
    "--paths", "src",
    "--version-file", $generatedVersionFile,
    "--add-data", "$VersionPath;."
)

if ($Clean) {
    $command += "--clean"
}

if (-not [string]::IsNullOrWhiteSpace($IconPath)) {
    if (Test-Path $IconPath) {
        $resolvedIcon = Resolve-Path $IconPath
        $command += @("--icon", $resolvedIcon.Path)
    } elseif ($IconPath -eq "assets/app.ico") {
        Write-Warning "Default icon not found at assets/app.ico. Building without a custom icon."
    } else {
        throw "Icon file not found: $IconPath"
    }
}

$command += $Entry

Write-Host "Building $Name.exe ..."
Write-Host "Using version $versionText from $VersionPath"
Write-Host "$Python $($command -join ' ')"
& $Python @command

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller build failed."
}

Write-Host "Build finished. Output: dist\$Name.exe"
