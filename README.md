# Lucio IVA Calculator

Calculadora de IVA hecha con PyQt6 e inspirada en VAT Calculator.

## Funciones

- Tres pantallas sincronizadas: IVA excluido, IVA e IVA incluido.
- Teclado numerico con operaciones basicas, borrar, limpiar y cambio de signo.
- Seleccion de pais/tasa con tasas de Ecuador, Union Europea y otros paises.
- Tasas personalizadas persistentes.
- Configuracion de formato numerico: separadores, decimales y agrupacion.
- Temas de color.
- Tamano de interfaz seleccionable: muy pequeno, pequeno, mediano, grande y muy grande.

## Ejecutar

```bash
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
# .venv\Scripts\activate       # Windows PowerShell
pip install -r requirements.txt
python main.py
```

## Configuracion

La app guarda sus preferencias en un archivo INI dentro de la carpeta de configuracion del usuario:

- Windows: `%AppData%\Lucio\IVA Calculator.ini`
- Linux: `~/.config/Lucio/IVA Calculator.ini`
- macOS: `~/Library/Application Support/Lucio/IVA Calculator.ini`
