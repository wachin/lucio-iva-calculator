# Tutorial: iconos Linux con PyInstaller

Esta guia explica una solucion practica para aplicaciones PyQt6 o Qt for Python empaquetadas con PyInstaller en Linux.

## El problema

En Linux no basta con hacer esto:

```python
app.setWindowIcon(QIcon("app-icon.svg"))
```

Eso puede funcionar en algunas ventanas, pero no garantiza que el icono aparezca correctamente en:

* Dock
* barra de tareas
* menu de aplicaciones
* lanzadores
* en algunos casos Alt+Tab

Tambien es importante entender esto:

* en Windows y macOS, `PyInstaller --icon` si suele servir para incrustar el icono principal
* en Linux, `PyInstaller --icon` no resuelve por si solo el icono del ELF para el escritorio

## Lo que si suele funcionar

En Linux, la solucion mas robusta suele combinar:

* icono Qt en tiempo de ejecucion
* rutas correctas para recursos empaquetados
* archivo `.desktop`
* `StartupWMClass` coherente
* `QApplication.setDesktopFileName(...)`

## 1. Guardar los iconos del proyecto

Se recomienda tener al menos:

* `assets/app-icon.svg`
* opcionalmente `assets/app-icon.ico`

El SVG es muy util para instalarlo en `~/.local/share/icons/...`.

## 2. Resolver recursos correctamente

Si la app se empaqueta con PyInstaller `--onefile`, los recursos se extraen en una carpeta temporal accesible con `sys._MEIPASS`.

Patron recomendado:

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

## 3. Cargar el icono con fallback

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

## 4. Aplicar el icono tanto a la app como a la ventana principal

Hay que usar ambos:

```python
app.setWindowIcon(load_app_icon())
window.setWindowIcon(load_app_icon())
```

Si la app abre dialogos importantes, tambien conviene:

```python
dialog.setWindowIcon(load_app_icon())
```

## 5. Configurar la identidad de escritorio en Linux

Se recomienda alinear el nombre base de la aplicacion:

```python
LINUX_DESKTOP_FILE_BASENAME = "MiAplicacion"

app = QApplication(sys.argv)
app.setApplicationDisplayName("Mi Aplicacion")
app.setApplicationName(LINUX_DESKTOP_FILE_BASENAME)
app.setDesktopFileName(LINUX_DESKTOP_FILE_BASENAME)
```

Tambien ayuda que la ventana principal tenga un nombre coherente:

```python
window.setObjectName(LINUX_DESKTOP_FILE_BASENAME)
```

## 6. Crear un archivo `.desktop`

Muchos escritorios Linux necesitan un `.desktop` para asociar bien la ventana con su icono y su lanzador.

Ejemplo:

```ini
[Desktop Entry]
Type=Application
Name=Mi Aplicacion
Comment=Aplicacion de escritorio hecha con PyQt6
Exec=MiAplicacion
TryExec=MiAplicacion
Icon=MiAplicacion
Categories=Utility;Office;
Terminal=false
StartupWMClass=MiAplicacion
```

Es importante que estos valores sean coherentes entre si:

* nombre del ejecutable
* `Exec=`
* `Icon=`
* `StartupWMClass=`
* `app.setDesktopFileName(...)`

## 7. Empaquetar recursos con PyInstaller

Patron recomendado:

```bash
pyinstaller -w -F -y \
  --name MiAplicacion \
  --add-data "assets:assets" \
  --add-data "translations:translations" \
  --add-data "docs:docs" \
  main.py
```

Se puede mantener `--icon` por coherencia entre plataformas, pero en Linux no hay que depender de el para la barra de tareas o el Dock.

## 8. Verificar que los recursos si quedaron dentro del one-file

Si esta disponible `pyi-archive_viewer`:

```bash
pyi-archive_viewer -l build/dist/MiAplicacion
```

Conviene revisar que aparezcan recursos como:

* `assets/app-icon.svg`
* `assets/app-icon.ico`
* archivos `.qm`
* ayuda HTML

## 9. Distribuir tambien `.desktop` e icono SVG

Aunque el binario `one-file` ya lleve recursos internos, para integracion real en Linux es mejor distribuir tambien:

* el ejecutable
* el archivo `.desktop`
* el icono SVG

Por ejemplo:

```bash
cp build/MiAplicacion.desktop build/dist/
cp assets/app-icon.svg build/dist/
```

## 10. Instalacion local por usuario

Para probar integracion de escritorio real:

```bash
mkdir -p ~/.local/bin ~/.local/share/applications ~/.local/share/icons/hicolor/scalable/apps
cp build/dist/MiAplicacion ~/.local/bin/
cp build/dist/MiAplicacion.desktop ~/.local/share/applications/
cp build/dist/app-icon.svg ~/.local/share/icons/hicolor/scalable/apps/MiAplicacion.svg
chmod +x ~/.local/bin/MiAplicacion
```

Si `~/.local/bin` no esta en `PATH`, hay dos opciones:

* agregarlo al `PATH`
* o usar una ruta absoluta en `Exec=`

## 11. Diferencias reales entre escritorios

No todos los escritorios Linux se comportan igual.

Es posible que:

* GNOME o Ubuntu muestren icono generico con un binario portable lanzado directamente
* XFCE muestre el icono correctamente
* Fluxbox tambien lo muestre correctamente

Por eso conviene probar al menos en:

* Debian o MX Linux con XFCE
* Ubuntu reciente

## 12. GitHub Actions y artefactos Linux

Si el workflow sube solo esto:

```yaml
path: build/dist/MiAplicacion
```

entonces el artefacto no llevara:

* `MiAplicacion.desktop`
* `app-icon.svg`

Si se quieren los tres archivos, hay que subir `build/dist/` completo o varias rutas:

```yaml
path: build/dist/
```

o:

```yaml
path: |
  build/dist/MiAplicacion
  build/dist/MiAplicacion.desktop
  build/dist/app-icon.svg
```

## Resumen corto

Para Linux con PyInstaller:

* `--icon` no basta
* `resource_path(...)` es importante
* hay que usar `QApplication.setWindowIcon(...)`
* hay que usar `setWindowIcon(...)` en la ventana principal
* un `.desktop` bien hecho suele ser la clave para el escritorio
