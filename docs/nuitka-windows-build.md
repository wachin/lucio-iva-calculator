# Windows Nuitka build

The official Windows package for Lucio IVA Calculator is built with Nuitka and packaged with NSIS.

The older PyInstaller-based Windows build is preserved in the `pyinstaller-old` branch.

## GitHub Actions workflow

The official workflow is:

```text
.github/workflows/build.yml
```

The Windows job:

1. installs Python;
2. installs NSIS;
3. installs Qt translation tools;
4. installs `build/requirements-windows.txt`;
5. runs `build/build_windows.ps1`;
6. uploads the installer and portable ZIP;
7. smoke-tests the installed app and the portable app.

## Build script

The Windows build script is:

```text
build/build_windows.ps1
```

It generates:

```text
build/output/LucioIVACalculator-<version>-setup.exe
build/output/LucioIVACalculator-<version>-Windows-x64-portable.zip
```

## Dependencies

The Windows dependencies are:

```text
build/requirements-windows.txt
```

They include:

- PyQt6
- Nuitka
- ordered-set
- zstandard

The workflow installs Qt separately so `lrelease.exe` is available for translation compilation.

## VirusTotal result for version 0.1.1

The first Windows Nuitka build tested for version `0.1.1` produced clean VirusTotal results:

- installer: `0/68`
- portable ZIP: `0/65`

## Notes

Nuitka compiles Python modules through a C/C++ compiler and produces a different binary shape than PyInstaller. In this project, it reduced the Windows false positives seen with unsigned PyInstaller/NSIS artifacts.

Code signing remains the strongest long-term mitigation for Windows reputation and SmartScreen behavior.
