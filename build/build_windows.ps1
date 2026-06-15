$ErrorActionPreference = "Stop"
Set-Item Env:PYTHONIOENCODING UTF-8

$workspaceRoot = Split-Path -Parent "$PSScriptRoot"
$distDir = Join-Path $workspaceRoot "build\dist"
$tmpDir = Join-Path $workspaceRoot "build\tmp"
$outputDir = Join-Path $workspaceRoot "build\output"

New-Item -ItemType Directory -Force -Path $distDir, $tmpDir, $outputDir | Out-Null

& powershell -NoProfile -ExecutionPolicy Bypass -File "$workspaceRoot\scripts\compile_translations.ps1"

& pyinstaller -w -D -y `
  --name LucioIVACalculator `
  --hidden-import=PyQt6.QtCore `
  --hidden-import=PyQt6.QtGui `
  --hidden-import=PyQt6.QtWidgets `
  --hidden-import=PyQt6.QtSvg `
  "--add-data=$workspaceRoot\assets;assets" `
  "--add-data=$workspaceRoot\translations;translations" `
  --distpath "$distDir" `
  --specpath "$tmpDir" `
  --workpath "$tmpDir" `
  "$workspaceRoot\main.py"

Copy-Item "$workspaceRoot\LICENSE" "$distDir\" -Force
$version = Get-Content "$workspaceRoot\VERSION" -Raw
$version = $version.Trim()
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
    $zipPath = Join-Path $outputDir "LucioIVACalculator-$version-Windows-x64.zip"
    if (Test-Path $zipPath) {
        Remove-Item $zipPath -Force
    }
    Compress-Archive -Path "$distDir\LucioIVACalculator", "$distDir\LICENSE" -DestinationPath $zipPath
}
