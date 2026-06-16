# Windows Nuitka build experiment

This branch contains an experimental Windows build path using Nuitka.

The regular PyInstaller-based build remains unchanged and is still the official cross-platform pipeline. The Nuitka build exists only to compare Windows antivirus results and packaging behavior.

## GitHub Actions workflow

The workflow is:

```text
.github/workflows/build-nuitka.yml
```

It runs when:

- triggered manually with `workflow_dispatch`;
- pushing to the `test-nuitka` branch.

## Build script

The Windows Nuitka build script is:

```text
build/build_windows_nuitka.ps1
```

It generates:

```text
build/output/LucioIVACalculator-<version>-nuitka-setup.exe
build/output/LucioIVACalculator-<version>-Windows-x64-nuitka-portable.zip
```

## Dependencies

The Windows Nuitka dependencies are:

```text
build/requirements-windows-nuitka.txt
```

The workflow installs Qt separately so `lrelease.exe` is available for translation compilation.

## What to upload to VirusTotal

After the workflow finishes, download the `lucio-iva-windows-nuitka` artifact and test:

```text
LucioIVACalculator-<version>-nuitka-setup.exe
LucioIVACalculator-<version>-Windows-x64-nuitka-portable.zip
LucioIVACalculator.exe extracted from the portable ZIP
```

Compare the results against the PyInstaller artifacts.

## Notes

Nuitka compiles Python modules through a C/C++ compiler and can produce a different binary shape than PyInstaller. This may reduce some heuristic false positives, but it is not guaranteed. Code signing remains the strongest long-term mitigation for Windows reputation and SmartScreen behavior.
