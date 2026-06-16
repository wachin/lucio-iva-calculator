# Lucio IVA Calculator

[![Build Lucio IVA Calculator](https://github.com/wachin/lucio-iva-calculator/actions/workflows/build.yml/badge.svg)](https://github.com/wachin/lucio-iva-calculator/actions/workflows/build.yml)
[![GitHub Pages](https://img.shields.io/badge/web-GitHub%20Pages-2ea44f)](https://wachin.github.io/lucio-iva-calculator/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776ab?logo=python&logoColor=white)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-41cd52?logo=qt&logoColor=white)](https://www.riverbankcomputing.com/software/pyqt/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Platforms](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](#ejecutar-desde-el-codigo-fuente)

Calculadora de IVA hecha con PyQt6 e inspirada en VAT Calculator.

## Funciones

- Tres pantallas sincronizadas: IVA excluido, IVA e IVA incluido.
- Teclado numerico con operaciones basicas, borrar, limpiar y cambio de signo.
- Seleccion de pais/tasa con tasas de Ecuador, Union Europea y otros paises.
- Tasas personalizadas persistentes.
- Configuracion de formato numerico: separadores, decimales y agrupacion.
- Temas de color.
- Tamano de interfaz seleccionable: muy pequeno, pequeno, mediano, grande y muy grande.
- Internacionalizacion con Qt Linguist: opcion Sistema y multiples idiomas.
- Al cambiar el idioma, la app propone automaticamente la tasa del pais asociado; el usuario puede cambiarla luego.
- Ayuda local bilingue en espanol e ingles.
- Atajos de teclado y soporte para teclado numerico fisico.

## Idiomas disponibles

La aplicacion incluye la opcion `Sistema`, que usa el idioma del sistema operativo cuando esta soportado. Espanol es el idioma base integrado, y los demas idiomas se cargan desde archivos Qt `.qm` compilados.

Idiomas disponibles para la interfaz:

| Codigo | Idioma |
| --- | --- |
| `system` | Idioma del sistema |
| `es` | Espanol |
| `en` | Ingles |
| `de` | Aleman |
| `fr` | Frances |
| `it` | Italiano |
| `pt` | Portugues |
| `nl` | Neerlandes |
| `pl` | Polaco |
| `ro` | Rumano |
| `bg` | Bulgaro |
| `hr` | Croata |
| `cs` | Checo |
| `sk` | Eslovaco |
| `sl` | Esloveno |
| `et` | Estonio |
| `fi` | Finlandes |
| `sv` | Sueco |
| `da` | Danes |
| `el` | Griego |
| `hu` | Hungaro |
| `lv` | Leton |
| `lt` | Lituano |
| `mt` | Maltes |
| `no` | Noruego |
| `ja` | Japones |
| `ko` | Coreano |
| `zh` | Chino |
| `hi` | Hindi |

## Uso basico

1. Selecciona una tasa desde el nombre del pais, el porcentaje o el menu.
2. Haz clic en `IVA excluido`, `IVA` o `IVA incluido` para decidir que valor quieres escribir.
3. Introduce el importe con el teclado en pantalla o con el teclado fisico.
4. Las otras dos pantallas se actualizan automaticamente con la tasa activa.

Puedes crear tasas personalizadas para descuentos, cargos, comisiones u otros impuestos. En `Configuracion` puedes cambiar idioma, formato numerico, tema visual y tamano de interfaz.

## Atajos de teclado

| Atajo | Accion |
| --- | --- |
| `0-9` | Escribir numeros |
| `. / ,` | Escribir separador decimal |
| `+ - * /` | Operaciones basicas |
| `Enter` | Calcular operacion pendiente |
| `Backspace / Delete` | Borrar el ultimo digito |
| `Esc` | Limpiar todo |
| `Ctrl+1` | Editar IVA excluido |
| `Ctrl+2` | Editar IVA |
| `Ctrl+3` | Editar IVA incluido |
| `Ctrl+Tab` | Cambiar al siguiente valor |
| `Ctrl+Shift+Tab` | Cambiar al valor anterior |
| `Ctrl+P` | Seleccionar pais |
| `Ctrl+R` | Abrir tasas personalizadas |
| `Ctrl+,` | Abrir configuracion |
| `F1` | Abrir ayuda |

## Ejecutar desde el codigo fuente

Lucio IVA Calculator puede ejecutarse directamente desde esta carpeta de codigo fuente. No es obligatorio compilarlo ni crear un instalador para probarlo.

### Windows 10/11 sin venv

Si Python esta instalado y disponible en `PATH`, instala las dependencias y ejecuta:

```powershell
pip install -r requirements.txt
python main.py
```

En muchas instalaciones de Windows tambien funciona:

```powershell
py -m pip install -r requirements.txt
py main.py
```

### Linux sin venv

En Debian, Ubuntu, MX Linux y derivadas puedes usar los paquetes del sistema:

```bash
sudo apt update
sudo apt install python3-pyqt6
python3 main.py
```

Si tu distribucion no tiene `python3-pyqt6` o prefieres usar `pip`, puedes instalar:

```bash
python3 -m pip install -r requirements.txt
python3 main.py
```

### macOS desde el codigo fuente

No dependas del Python antiguo del sistema. Instala Python 3 con Homebrew o desde python.org y luego:

```bash
python3 -m pip install -r requirements.txt
python3 main.py
```

### Windows con venv para desarrollo

Usar `venv` no es obligatorio, pero es recomendable si vas a desarrollar, probar dependencias o empaquetar:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

Si PowerShell bloquea la activacion del entorno, puedes usar:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

### Linux con venv para desarrollo

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

y se lanzará el programa

![Calculadora de IVA](vx_images/01-Calculadora-de-IVA.png)

---

## Compilación en Debian 12 (Recomendado para las versiones Linux)

Para obtener la máxima compatibilidad con distribuciones basadas en Debian, recomendamos compilar los ejecutables Linux en Debian 12 (Bookworm) o MX Linux 23.

### ¿Por qué Debian 12?

PyInstaller incluye el intérprete de Python y enlaza bibliotecas del sistema disponibles en el equipo donde se realiza la compilación. Si la aplicación se compila en una distribución más reciente (por ejemplo Ubuntu 24.04, Ubuntu 26.04, Fedora 40+, etc.), el ejecutable generado puede requerir versiones de GLIBC que no existen en sistemas más antiguos.

Error típico:

```text
Failed to load Python shared library ...
GLIBC_2.38 not found
```

Compilar en Debian 12 evita este problema porque Debian 12 utiliza GLIBC 2.36, compatible con muchas distribuciones Linux actuales.

### Instalar dependencias

```bash
sudo apt update

sudo apt install -y \
    python3 \
    python3-venv \
    python3-pip \
    pyqt6-dev-tools
```

### Crear un entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### Instalar dependencias de Python

```bash
pip install --upgrade pip
pip install -r build/requirements-linux.txt
```

### Compilar la aplicación

```bash
chmod +x build/build_linux.sh
./build/build_linux.sh
```

El ejecutable se generará en:

```text
build/dist/LucioIVACalculator
```

### Verificar la compatibilidad

Después de compilar, puede comprobar las dependencias GLIBC con:

```bash
strings build/dist/LucioIVACalculator | grep GLIBC_
```

El binario generado no debería requerir una versión de GLIBC más nueva que la disponible en Debian 12.

### Entornos recomendados para compilar

* Debian 12 (Bookworm)
* MX Linux 23
* Contenedor Docker basado en Debian 12
* Máquina virtual Debian 12

Si desea distribuir versiones Linux ampliamente compatibles, evite compilar las versiones oficiales en distribuciones demasiado recientes.

### Integracion con el escritorio Linux

`build/build_linux.sh` ahora copia estos archivos adicionales a `build/dist/`:

* `LucioIVACalculator.desktop`
* `app-icon.svg`

El ejecutable ya establece el icono en tiempo de ejecución con `QApplication.setWindowIcon()` y `setWindowIcon()` en la ventana principal, pero muchos entornos de escritorio Linux siguen prefiriendo una entrada `.desktop` coincidente para el Dock, el menú de aplicaciones, los lanzadores y en algunos casos Alt+Tab. Esto es especialmente común con PyInstaller `--onefile`, porque la ruta extraída en tiempo de ejecución es temporal y el escritorio suele depender de una identidad estable de la aplicación en lugar de heurísticas de ruta.

La entrada `.desktop` usa:

* `Exec=LucioIVACalculator`
* `Icon=LucioIVACalculator`
* `StartupWMClass=LucioIVACalculator`

Eso coincide con el nombre de archivo `.desktop` configurado en Qt durante la ejecución y ayuda a que GNOME, KDE, XFCE, Debian 12, MX Linux 23, Ubuntu 24.04+ y Ubuntu 26.04 asocien la ventana con el icono correcto del lanzador.

Para una instalación por usuario, copie los archivos a las rutas estándar:

```bash
mkdir -p ~/.local/bin ~/.local/share/applications ~/.local/share/icons/hicolor/scalable/apps
cp build/dist/LucioIVACalculator ~/.local/bin/
cp build/dist/LucioIVACalculator.desktop ~/.local/share/applications/
cp build/dist/app-icon.svg ~/.local/share/icons/hicolor/scalable/apps/LucioIVACalculator.svg
chmod +x ~/.local/bin/LucioIVACalculator
```

Si `~/.local/bin` todavía no está en `PATH`, agréguelo o edite `Exec=` dentro del archivo `.desktop` con la ruta absoluta del ejecutable.

Después de copiar estos archivos, la aplicación debería aparecer en el menú de programas y usar el icono instalado en lugar de comportarse solamente como un binario portable lanzado desde una carpeta cualquiera.

---

## Configuracion

La app guarda sus preferencias en un archivo INI dentro de la carpeta de configuracion del usuario:

- Windows: `%AppData%\Lucio\IVA Calculator.ini`
- Linux: `~/.config/Lucio/IVA Calculator.ini`
- macOS: `~/Library/Application Support/Lucio/IVA Calculator.ini`

## Personalizar colores

Los colores visuales principales estan en `main.py`.

Para cambiar el color base de cada tema, edita el diccionario `THEMES`. Por ejemplo, el tema oscuro usa:

```python
"Oscuro": "#3d3d3d"
```

Para cambiar especificamente el fondo de las secciones `IVA EXCLUIDO`, `IVA` e `IVA INCLUIDO` en modo oscuro, busca dentro de `apply_theme()` estas variables:

```python
panel_background = "#2f2f2f" if dark_theme else "rgba(255,255,255,0.16)"
active_panel_background = "#383838" if dark_theme else "rgba(255,255,255,0.31)"
panel_border = "#666666" if dark_theme else "rgba(255,255,255,0.28)"
```

`panel_background` controla los paneles normales, `active_panel_background` controla el panel seleccionado y `panel_border` controla el borde.

## Traducciones

Los archivos editables de Qt Linguist estan en:

```text
translations/*.ts
```

La opcion `Sistema` usa el idioma del sistema operativo. Si la configuracion regional incluye pais, tambien intenta escoger la tasa correspondiente, por ejemplo `es_EC` usa Ecuador y `pt_BR` usa Brasil.

Para compilar los `.ts` a `.qm` en Windows:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\compile_translations.ps1
```

El script busca `lrelease.exe` en `PATH`, PyQt6, `qt5_applications`, `QTDIR`, `C:\Qt` y `%USERPROFILE%\Qt`.

### Qt Creator y lrelease en Windows

Para editar o recompilar traducciones en Windows conviene instalar Qt desde el instalador online oficial:

- [Qt Online Installer (Open Source)](https://www.qt.io/development/download-qt-installer-oss)

No basta siempre con instalar solo Qt Creator. Para que exista `lrelease.exe`, instala al menos un kit completo de escritorio desde Qt Maintenance Tool, por ejemplo:

```text
Qt -> Qt 6.x.x -> MinGW 64-bit
```

o:

```text
Qt -> Qt 6.x.x -> MSVC 64-bit
```

Luego `lrelease.exe` suele quedar en rutas como:

```text
C:\Qt\6.x.x\mingw_64\bin\lrelease.exe
C:\Qt\6.x.x\msvc*_64\bin\lrelease.exe
```

Puedes comprobarlo con:

```powershell
Get-ChildItem C:\Qt -Recurse -Filter lrelease.exe
```

Si `lrelease.exe` existe pero no esta en `PATH`, no pasa nada: `scripts\compile_translations.ps1` tambien busca en `QTDIR`, `C:\Qt` y `%USERPROFILE%\Qt`.

## Builds multiplataforma

El proyecto incluye GitHub Actions para compilar artefactos en Windows, Linux y macOS:

```text
.github/workflows/build.yml
```

Los scripts de build estan en:

```text
build/build_windows.ps1
build/build_linux.sh
build/build_macos.sh
```

Para publicar una version, actualiza `VERSION`, crea un tag con formato `v0.1.0` y subelo a GitHub:

```bash
git tag v0.1.0
git push origin v0.1.0
```

El workflow crea una release con los artefactos de Windows, Linux y macOS.
