# Windows executable false-positive reduction notes

This document records the Windows packaging changes made to reduce heuristic antivirus false positives for Lucio IVA Calculator while keeping the same application features and the same distribution targets.

## Context

VirusTotal reported a small number of detections for both Windows artifacts:

- `LucioIVACalculator-<version>-setup.exe`
- `LucioIVACalculator-<version>-Windows-x64-portable.zip`

Most major engines reported the files as clean, while a few engines used generic labels such as `Trojan.Generic`, `TR/W64.Malware`, or similar. These labels are commonly triggered by unsigned PyInstaller/NSIS applications, especially when the executable is new and has little download reputation.

These changes do not remove functionality and do not claim to guarantee zero detections. They reduce avoidable suspicious signals in the Windows build.

## Changes Made

## 1. PyInstaller now disables UPX explicitly

File:

```text
build/build_windows.ps1
```

Change:

```text
--noupx
```

Why it helps:

Packed executables are often treated with suspicion by antivirus heuristics. Even if UPX is not intentionally used, passing `--noupx` makes the build explicit and reproducible.

## 2. PyInstaller now performs a clean build

File:

```text
build/build_windows.ps1
```

Change:

```text
--clean
```

Why it helps:

This prevents stale PyInstaller cache data from older builds from being reused. It is especially useful when the previous Windows packaging setup was old or changed over time.

## 3. The Windows executable now has version metadata

File:

```text
build/build_windows.ps1
```

The build script now generates a PyInstaller version resource file dynamically from `VERSION`.

Included metadata:

- `ProductName`
- `CompanyName`
- `FileDescription`
- `LegalCopyright`
- `FileVersion`
- `ProductVersion`
- `InternalName`
- `OriginalFilename`

Why it helps:

Unsigned executables with missing product information look less trustworthy to Windows and antivirus heuristics. Adding normal product metadata makes the file look like a standard desktop application and also improves the Properties dialog in Windows Explorer.

## 4. The Windows executable now has an explicit application manifest

File:

```text
build/windows_app.manifest
```

The manifest declares:

- `requestedExecutionLevel` as `asInvoker`
- Windows compatibility IDs
- per-monitor DPI awareness

Why it helps:

The app does not need administrator privileges. Declaring `asInvoker` makes that explicit in the executable. Compatibility and DPI metadata also make the application resource set more complete and conventional for Windows 10/11 desktop software.

## 5. The NSIS installer declares user-level installation

File:

```text
build/LucioIVACalculator.nsi
```

Change:

```text
RequestExecutionLevel user
```

Why it helps:

The installer writes to the current user's profile under `%LOCALAPPDATA%`, so it does not need elevated privileges. Avoiding unnecessary elevation reduces suspicious installer behavior.

## 6. The NSIS installer now has fuller version metadata

File:

```text
build/LucioIVACalculator.nsi
```

Added/confirmed metadata:

- `VIFileVersion`
- `VIProductVersion`
- `ProductName`
- `CompanyName`
- `FileDescription`
- `FileVersion`
- `ProductVersion`
- `LegalCopyright`
- `InternalName`
- `OriginalFilename`

Why it helps:

The installer itself is an executable and should also look like a normal, identifiable product. This helps users inspect the installer and may reduce generic heuristic suspicion.

## 7. Removed old `qt5_applications` from Windows build dependencies

Files:

```text
build/requirements-windows.txt
scripts/compile_translations.ps1
.github/workflows/build.yml
README.md
README_ES.md
```

Change:

The Windows build no longer installs `qt5_applications`. GitHub Actions now installs Qt explicitly for translation tools, and the translation script searches for `lrelease.exe` in normal Qt locations.

Why it helps:

The application uses PyQt6. `qt5_applications` was only used as a fallback way to find `lrelease.exe`, not as an application runtime dependency. Removing this old build-only package reduces unnecessary packages in the build environment and avoids mixing Qt5 tooling into a PyQt6 project.

## 8. Windows portable ZIP is preserved and tested

Files:

```text
build/build_windows.ps1
.github/workflows/build.yml
README.md
README_ES.md
```

The Windows build continues to generate both:

```text
LucioIVACalculator-<version>-setup.exe
LucioIVACalculator-<version>-Windows-x64-portable.zip
```

GitHub Actions downloads the Windows artifact, installs the installer build, tests the installed executable, then extracts and tests the portable executable with:

```text
--pyinstaller-test
```

Why it helps:

Keeping both distributions lets users choose between an installer and a no-install portable build. Testing both in CI proves that both artifacts are valid.

## 9. GitHub Releases now include SHA256 checksums

File:

```text
.github/workflows/build.yml
```

Tagged releases now upload:

```text
SHA256SUMS.txt
```

Why it helps:

Checksums let users verify that downloaded files match the files produced by GitHub Actions. This does not remove antivirus false positives, but it improves release transparency and trust.

## Files Modified

```text
.github/workflows/build.yml
build/LucioIVACalculator.nsi
build/build_windows.ps1
build/requirements-windows.txt
build/windows_app.manifest
scripts/compile_translations.ps1
README.md
README_ES.md
windows-exe-fixes.md
```

## Remaining Recommendations

These items are outside the source-code changes but are recommended before broad public distribution:

1. Build official Windows artifacts only from GitHub Actions.
2. Publish the generated `SHA256SUMS.txt` with every release.
3. Submit false-positive reports to the antivirus vendors that flag the files.
4. Consider code signing the `.exe` and installer when budget allows.
5. Avoid `--onefile`, UPX, obfuscation, runtime downloading, or unnecessary administrator privileges.
6. Keep dependencies minimal and avoid old build-time packages that are not needed by the app.

## Expected Result

The Windows build should look more like a normal desktop application:

- no UPX packing;
- clean PyInstaller output;
- explicit app manifest;
- product metadata in the executable;
- product metadata in the installer;
- user-level installer;
- no old `qt5_applications` build dependency;
- installer and portable ZIP both generated and tested;
- release checksums published.

VirusTotal results may still vary because unsigned PyInstaller applications can receive heuristic detections. The most effective long-term mitigation is code signing plus enough clean download reputation over time.
