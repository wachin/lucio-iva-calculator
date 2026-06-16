$ErrorActionPreference = "Stop"
Set-Item Env:PYTHONIOENCODING UTF-8

$workspaceRoot = Split-Path -Parent "$PSScriptRoot"
$distDir = Join-Path $workspaceRoot "build\dist"
$tmpDir = Join-Path $workspaceRoot "build\tmp"
$outputDir = Join-Path $workspaceRoot "build\output"
$version = Get-Content "$workspaceRoot\VERSION" -Raw
$version = $version.Trim()
$versionParts = @($version.Split(".") | ForEach-Object { [int]$_ })
while ($versionParts.Count -lt 4) {
    $versionParts += 0
}
$versionTuple = "$($versionParts[0]), $($versionParts[1]), $($versionParts[2]), $($versionParts[3])"
$versionInfoPath = Join-Path $tmpDir "LucioIVACalculator-version-info.txt"

New-Item -ItemType Directory -Force -Path $distDir, $tmpDir, $outputDir | Out-Null

& powershell -NoProfile -ExecutionPolicy Bypass -File "$workspaceRoot\scripts\compile_translations.ps1"

@"
# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=($versionTuple),
    prodvers=($versionTuple),
    mask=0x3f,
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
          StringStruct('CompanyName', 'Lucio'),
          StringStruct('FileDescription', 'Lucio IVA Calculator'),
          StringStruct('FileVersion', '$version'),
          StringStruct('InternalName', 'LucioIVACalculator'),
          StringStruct('LegalCopyright', 'Copyright (c) 2026 Washington Indacochea Delgado and Joseph Lucio Guerrero'),
          StringStruct('OriginalFilename', 'LucioIVACalculator.exe'),
          StringStruct('ProductName', 'Lucio IVA Calculator'),
          StringStruct('ProductVersion', '$version')
        ]
      )
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"@ | Set-Content -Path $versionInfoPath -Encoding UTF8

& pyinstaller -w -D -y `
  --name LucioIVACalculator `
  --clean `
  --noupx `
  --icon "$workspaceRoot\assets\app-icon.ico" `
  --version-file "$versionInfoPath" `
  --manifest "$workspaceRoot\build\windows_app.manifest" `
  --hidden-import=PyQt6.QtCore `
  --hidden-import=PyQt6.QtGui `
  --hidden-import=PyQt6.QtWidgets `
  --hidden-import=PyQt6.QtSvg `
  "--add-data=$workspaceRoot\assets;assets" `
  "--add-data=$workspaceRoot\translations;translations" `
  "--add-data=$workspaceRoot\docs;docs" `
  --distpath "$distDir" `
  --specpath "$tmpDir" `
  --workpath "$tmpDir" `
  "$workspaceRoot\main.py"

Copy-Item "$workspaceRoot\LICENSE" "$distDir\" -Force
Copy-Item "$workspaceRoot\assets\app-icon.ico" "$distDir\" -Force
Copy-Item "$workspaceRoot\assets\nsis-welcome.bmp" "$distDir\" -Force
Copy-Item "$workspaceRoot\assets\nsis-header.bmp" "$distDir\" -Force

$portableZipPath = Join-Path $outputDir "LucioIVACalculator-$version-Windows-x64-portable.zip"
if (Test-Path $portableZipPath) {
    Remove-Item $portableZipPath -Force
}
Compress-Archive -Path "$distDir\LucioIVACalculator", "$distDir\LICENSE" -DestinationPath $portableZipPath

$nsiContent = Get-Content "$workspaceRoot\build\LucioIVACalculator.nsi" -Raw
$nsiContent = $nsiContent.Replace('!define VERSION "0.1.0.0"', "!define VERSION `"$version.0`"")
$nsiContent = $nsiContent.Replace('!define INSTALLER_NAME "LucioIVACalculator-0.1.0-setup.exe"', "!define INSTALLER_NAME `"LucioIVACalculator-$version-setup.exe`"")
$nsiContent = $nsiContent.Replace('WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "0.1.0"', "WriteRegStr HKCU `"Software\Microsoft\Windows\CurrentVersion\Uninstall\`${APP_NAME}`" `"DisplayVersion`" `"$version`"")
Set-Content -Path "$distDir\LucioIVACalculator.nsi" -Value $nsiContent -Encoding UTF8

$makensis = "C:\Program Files (x86)\NSIS\makensis.exe"
if (Test-Path $makensis) {
    Push-Location $distDir
    & $makensis "$distDir\LucioIVACalculator.nsi"
    Move-Item "LucioIVACalculator-*-setup.exe" "$outputDir" -Force
    Pop-Location
} else {
    Write-Warning "NSIS was not found. Portable ZIP was created, but the installer was not built."
}
