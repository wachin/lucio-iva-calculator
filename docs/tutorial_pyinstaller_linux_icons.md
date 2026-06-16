# Tutorial: Linux icons with PyInstaller

This guide explains a practical solution for PyQt6 or Qt for Python applications packaged with PyInstaller on Linux.

## The problem

On Linux, this alone is not enough:

```python
app.setWindowIcon(QIcon("app-icon.svg"))
```

It may work for some windows, but it does not guarantee that the icon will appear correctly in:

* the Dock
* the taskbar
* the application menu
* launchers
* in some cases Alt+Tab

It is also important to understand this:

* on Windows and macOS, `PyInstaller --icon` often works for embedding the main application icon
* on Linux, `PyInstaller --icon` does not solve the desktop icon for the ELF binary by itself

## What usually works

On Linux, the most robust solution usually combines:

* the Qt runtime icon
* correct paths for packaged resources
* a `.desktop` file
* a coherent `StartupWMClass`
* `QApplication.setDesktopFileName(...)`

## 1. Store the project icons

It is recommended to have at least:

* `assets/app-icon.svg`
* optionally `assets/app-icon.ico`

The SVG file is especially useful when installing it into `~/.local/share/icons/...`.

## 2. Resolve resources correctly

If the application is packaged with PyInstaller `--onefile`, resources are extracted into a temporary directory available through `sys._MEIPASS`.

Recommended pattern:

```python
from pathlib import Path
import os
import sys

def resource_path(*relative_parts: str | os.PathLike[str]) -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent
    return base_path.joinpath(*map(os.fspath, relative_parts))
```

## 3. Load the icon with fallback support

```python
from PyQt6.QtGui import QIcon

def app_icon_candidates():
    return (
        resource_path("assets", "app-icon.svg"),
        resource_path("assets", "app-icon.ico"),
    )

def load_app_icon() -> QIcon:
    icon = QIcon()
    for candidate in app_icon_candidates():
        if candidate.exists():
            icon.addFile(str(candidate))
    return icon
```

## 4. Apply the icon to both the application and the main window

Use both:

```python
app.setWindowIcon(load_app_icon())
window.setWindowIcon(load_app_icon())
```

If the application opens important dialogs, it is also recommended to use:

```python
dialog.setWindowIcon(load_app_icon())
```

## 5. Configure the Linux desktop identity

It is recommended to keep the application base name aligned:

```python
LINUX_DESKTOP_FILE_BASENAME = "MyApplication"

app = QApplication(sys.argv)
app.setApplicationDisplayName("My Application")
app.setApplicationName(LINUX_DESKTOP_FILE_BASENAME)
app.setDesktopFileName(LINUX_DESKTOP_FILE_BASENAME)
```

It also helps if the main window has a coherent name:

```python
window.setObjectName(LINUX_DESKTOP_FILE_BASENAME)
```

## 6. Create a `.desktop` file

Many Linux desktop environments need a `.desktop` file to associate the window correctly with its icon and launcher.

Example:

```ini
[Desktop Entry]
Type=Application
Name=My Application
Comment=Desktop application built with PyQt6
Exec=MyApplication
TryExec=MyApplication
Icon=MyApplication
Categories=Utility;Office;
Terminal=false
StartupWMClass=MyApplication
```

These values should stay coherent with each other:

* executable name
* `Exec=`
* `Icon=`
* `StartupWMClass=`
* `app.setDesktopFileName(...)`

## 7. Package resources with PyInstaller

Recommended pattern:

```bash
pyinstaller -w -F -y \
  --name MyApplication \
  --add-data "assets:assets" \
  --add-data "translations:translations" \
  --add-data "docs:docs" \
  main.py
```

You may keep `--icon` for cross-platform consistency, but on Linux you should not depend on it for the taskbar or Dock icon.

## 8. Verify that the resources are really inside the one-file binary

If `pyi-archive_viewer` is available:

```bash
pyi-archive_viewer -l build/dist/MyApplication
```

It is a good idea to verify that entries such as these are present:

* `assets/app-icon.svg`
* `assets/app-icon.ico`
* `.qm` translation files
* HTML help files

## 9. Distribute the `.desktop` file and SVG icon as well

Even if the `one-file` binary already contains internal resources, for real Linux desktop integration it is better to distribute:

* the executable
* the `.desktop` file
* the SVG icon

For example:

```bash
cp build/MyApplication.desktop build/dist/
cp assets/app-icon.svg build/dist/
```

## 10. Per-user local installation

To test real desktop integration:

```bash
mkdir -p ~/.local/bin ~/.local/share/applications ~/.local/share/icons/hicolor/scalable/apps
cp build/dist/MyApplication ~/.local/bin/
cp build/dist/MyApplication.desktop ~/.local/share/applications/
cp build/dist/app-icon.svg ~/.local/share/icons/hicolor/scalable/apps/MyApplication.svg
chmod +x ~/.local/bin/MyApplication
```

If `~/.local/bin` is not in `PATH`, there are two options:

* add it to `PATH`
* or use an absolute path in `Exec=`

## 11. Real differences between desktop environments

Not all Linux desktop environments behave the same way.

It is possible that:

* GNOME or Ubuntu show a generic icon when launching a portable binary directly
* XFCE shows the correct icon
* Fluxbox also shows the correct icon

That is why it is useful to test at least on:

* Debian or MX Linux with XFCE
* a recent Ubuntu release

## 12. GitHub Actions and Linux artifacts

If the workflow uploads only this:

```yaml
path: build/dist/MyApplication
```

then the artifact will not include:

* `MyApplication.desktop`
* `app-icon.svg`

If you want all three files, upload the whole `build/dist/` directory or multiple paths:

```yaml
path: build/dist/
```

or:

```yaml
path: |
  build/dist/MyApplication
  build/dist/MyApplication.desktop
  build/dist/app-icon.svg
```

## Short summary

For Linux with PyInstaller:

* `--icon` is not enough
* `resource_path(...)` matters
* you should use `QApplication.setWindowIcon(...)`
* you should use `setWindowIcon(...)` on the main window
* a properly configured `.desktop` file is often the key to real desktop integration
