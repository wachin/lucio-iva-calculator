$ErrorActionPreference = "Stop"

$workspaceRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$translationsDir = Join-Path $workspaceRoot "translations"

function Get-LRelease {
    $command = Get-Command lrelease -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $pyqtLrelease = & python -c "import pathlib, PyQt6; print(pathlib.Path(PyQt6.__file__).parent / 'Qt6' / 'bin' / 'lrelease.exe')" 2>$null
    if ($LASTEXITCODE -eq 0 -and (Test-Path "$pyqtLrelease")) {
        return "$pyqtLrelease"
    }

    $qtToolsLrelease = & python -c "import importlib.util, pathlib; spec = importlib.util.find_spec('qt5_applications'); print(pathlib.Path(next(iter(spec.submodule_search_locations))) / 'Qt' / 'bin' / 'lrelease.exe' if spec and spec.submodule_search_locations else '')" 2>$null
    if ($LASTEXITCODE -eq 0 -and (Test-Path "$qtToolsLrelease")) {
        return "$qtToolsLrelease"
    }

    $searchRoots = @()
    if ($env:QTDIR) {
        $searchRoots += $env:QTDIR
    }
    $searchRoots += "C:\Qt"
    if ($env:USERPROFILE) {
        $searchRoots += (Join-Path $env:USERPROFILE "Qt")
    }

    foreach ($root in ($searchRoots | Select-Object -Unique)) {
        if (!(Test-Path $root)) {
            continue
        }
        $matches = Get-ChildItem -Path $root -Recurse -Filter lrelease.exe -ErrorAction SilentlyContinue |
            Sort-Object FullName -Descending
        if ($matches) {
            return $matches[0].FullName
        }
    }

    throw "No se encontro lrelease.exe. Instala un kit de escritorio de Qt, agrega lrelease al PATH o instala qt5_applications."
}

if (!(Test-Path $translationsDir)) {
    New-Item -ItemType Directory -Force -Path $translationsDir | Out-Null
}

$lrelease = Get-LRelease
Write-Output "Compilando traducciones con: $lrelease"

Get-ChildItem -Path $translationsDir -Filter *.ts | ForEach-Object {
    $qmPath = [System.IO.Path]::ChangeExtension($_.FullName, ".qm")
    & $lrelease $_.FullName -qm $qmPath
}
