from __future__ import annotations

import os
import sys
import ctypes
from configparser import ConfigParser
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from ctypes import wintypes

try:
    import winreg
except ImportError:
    winreg = None

from PyQt6.QtCore import QEvent, QTimer, Qt, QLocale, QSettings, QSize, QTranslator, QUrl
from PyQt6.QtGui import QAction, QFont, QFontDatabase, QIcon, QKeySequence, QPainter, QPainterPath, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


APP_ORG = "Lucio"
APP_NAME = "IVA Calculator"
CONFIG_FILE_NAME = "IVA Calculator.ini"
APP_EXECUTABLE_NAME = "LucioIVACalculator"
DEFAULT_LANGUAGE = "es"
DEFAULT_LANGUAGE_SETTING = "system"
SYSTEM_FONT_SETTING = "system"
LANGUAGES = {
    "system": "Sistema",
    "es": "Español",
    "en": "English",
    "de": "Deutsch",
    "fr": "Français",
    "it": "Italiano",
    "pt": "Português",
    "nl": "Nederlands",
    "pl": "Polski",
    "ro": "Română",
    "bg": "Български",
    "hr": "Hrvatski",
    "cs": "Čeština",
    "sk": "Slovenčina",
    "sl": "Slovenščina",
    "et": "Eesti",
    "fi": "Suomi",
    "sv": "Svenska",
    "da": "Dansk",
    "el": "Ελληνικά",
    "hu": "Magyar",
    "lv": "Latviešu",
    "lt": "Lietuvių",
    "mt": "Malti",
    "no": "Norsk",
    "ja": "日本語",
    "ko": "한국어",
    "zh": "中文",
    "hi": "हिन्दी",
}
LANGUAGE_DEFAULT_COUNTRIES = {
    "es": "Ecuador",
    "en": "Reino Unido",
    "de": "Alemania",
    "fr": "Francia",
    "it": "Italia",
    "pt": "Portugal",
    "nl": "Paises Bajos",
    "pl": "Polonia",
    "ro": "Rumania",
    "bg": "Bulgaria",
    "hr": "Croacia",
    "cs": "Republica Checa",
    "sk": "Eslovaquia",
    "sl": "Eslovenia",
    "et": "Estonia",
    "fi": "Finlandia",
    "sv": "Suecia",
    "da": "Dinamarca",
    "el": "Grecia",
    "hu": "Hungria",
    "lv": "Letonia",
    "lt": "Lituania",
    "mt": "Malta",
    "no": "Noruega",
    "ja": "Japon",
    "ko": "Corea del Sur",
    "zh": "China",
    "hi": "India GST",
}
LOCALE_DEFAULT_COUNTRIES = {
    "es_EC": "Ecuador",
    "es_ES": "Espana",
    "es_MX": "Mexico",
    "es_AR": "Argentina",
    "es_CL": "Chile",
    "es_CO": "Colombia",
    "es_PE": "Peru",
    "es_UY": "Uruguay",
    "es_PY": "Paraguay",
    "es_BO": "Bolivia",
    "pt_BR": "Brasil",
    "pt_PT": "Portugal",
    "en_US": "Estados Unidos",
    "en_GB": "Reino Unido",
    "en_CA": "Canada GST",
    "en_AU": "Australia",
    "en_NZ": "Nueva Zelanda",
    "fr_FR": "Francia",
    "fr_CA": "Canada GST",
    "de_DE": "Alemania",
    "de_AT": "Austria",
    "de_CH": "Suiza",
    "it_IT": "Italia",
    "it_CH": "Suiza",
    "nl_NL": "Paises Bajos",
}
DEFAULT_UI_SIZE = "Mediano"
UI_SIZE_PRESETS = {
    "Muy pequeno": {"scale": 0.82, "width": 330, "height": 570, "min_width": 290, "min_height": 500},
    "Pequeno": {"scale": 0.92, "width": 360, "height": 630, "min_width": 310, "min_height": 530},
    "Mediano": {"scale": 1.0, "width": 392, "height": 690, "min_width": 330, "min_height": 560},
    "Grande": {"scale": 1.16, "width": 455, "height": 790, "min_width": 380, "min_height": 640},
    "Muy grande": {"scale": 1.32, "width": 520, "height": 900, "min_width": 430, "min_height": 720},
}
KEYBOARD_SHORTCUTS = [
    ("0-9", "Escribir numeros"),
    (". / ,", "Escribir separador decimal"),
    ("+  -  *  /", "Operaciones basicas"),
    ("Enter", "Calcular operacion pendiente"),
    ("Backspace / Delete", "Borrar el ultimo digito"),
    ("Esc", "Limpiar todo"),
    ("Ctrl+1", "Editar IVA excluido"),
    ("Ctrl+2", "Editar IVA"),
    ("Ctrl+3", "Editar IVA incluido"),
    ("Ctrl+Tab", "Cambiar al siguiente valor"),
    ("Ctrl+Shift+Tab", "Cambiar al valor anterior"),
    ("Ctrl+P", "Seleccionar pais"),
    ("Ctrl+R", "Abrir tasas personalizadas"),
    ("Ctrl+,", "Abrir configuracion"),
    ("F1", "Abrir ayuda"),
]


def scaled(value: int | float, factor: float) -> int:
    return max(1, round(value * factor))


def system_font_family() -> str:
    app = QApplication.instance()
    if app is not None:
        return app.font().family()
    return QFont().defaultFamily()


def effective_font_family(font_family: str | None) -> str:
    if not font_family or font_family == SYSTEM_FONT_SETTING:
        return system_font_family()
    return font_family


def css_font_family(font_family: str) -> str:
    return font_family.replace("\\", "\\\\").replace('"', '\\"')


def user_config_dir() -> Path:
    if sys.platform.startswith("win"):
        base_dir = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base_dir = Path.home() / "Library" / "Application Support"
    else:
        base_dir = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base_dir / APP_ORG


def settings_file_path() -> Path:
    config_dir = user_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / CONFIG_FILE_NAME


class AppSettings:
    section_name = "settings"

    def __init__(self, path: Path):
        self.path = path
        self.values: dict[str, str] = {}
        self.load()

    def load(self):
        if not self.path.exists():
            return
        parser = ConfigParser()
        parser.read(self.path, encoding="utf-8")
        if parser.has_section(self.section_name):
            self.values.update(dict(parser.items(self.section_name)))

    def value(self, key: str, default=None):
        return self.values.get(key, default)

    def setValue(self, key: str, value):  # noqa: N802
        self.values[key] = str(value)

    def allKeys(self):  # noqa: N802
        return list(self.values.keys())

    def sync(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        parser = ConfigParser()
        parser[self.section_name] = self.values
        try:
            with self.path.open("w", encoding="utf-8") as file:
                parser.write(file)
        except OSError as error:
            print(f"No se pudo guardar la configuracion en {self.path}: {error}", file=sys.stderr)


def app_settings() -> AppSettings:
    settings = AppSettings(settings_file_path())
    migrate_legacy_settings(settings)
    return settings


def migrate_legacy_settings(settings: AppSettings):
    if settings.allKeys():
        return
    legacy_settings = QSettings(APP_ORG, APP_NAME)
    for key in legacy_settings.allKeys():
        settings.setValue(key, legacy_settings.value(key))
    settings.sync()


def settings_bool(value, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def windows_apps_dark_theme() -> bool:
    if not sys.platform.startswith("win") or winreg is None:
        return False
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        ) as key:
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return int(value) == 0
    except OSError:
        return False


def set_windows_title_bar_dark(window, enabled: bool):
    if not sys.platform.startswith("win"):
        return
    try:
        hwnd = int(window.winId())
        value = wintypes.BOOL(1 if enabled else 0)
        for attribute in (20, 19):
            result = ctypes.windll.dwmapi.DwmSetWindowAttribute(
                wintypes.HWND(hwnd),
                wintypes.DWORD(attribute),
                ctypes.byref(value),
                ctypes.sizeof(value),
            )
            if result == 0:
                break
    except (AttributeError, OSError, ValueError):
        return


def translations_dir() -> Path:
    return application_root() / "translations"


def app_icon_path() -> Path:
    return application_root() / "assets" / "app-icon.svg"


def photos_dir() -> Path:
    return application_root() / "assets" / "Photos"


def docs_dir() -> Path:
    return application_root() / "docs"


def help_file_path(language_code: str) -> Path:
    code = effective_language_code(language_code)
    if code != "en":
        code = DEFAULT_LANGUAGE
    help_path = docs_dir() / f"help_{code}.html"
    if help_path.exists():
        return help_path
    return docs_dir() / "help_es.html"


def application_root() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def load_translation(app: QApplication, language_code: str) -> QTranslator | None:
    language_code = effective_language_code(language_code)
    if language_code == DEFAULT_LANGUAGE:
        return None
    translator = QTranslator(app)
    translation_file = translations_dir() / f"iva_calculator_{language_code}.qm"
    if translator.load(str(translation_file)):
        app.installTranslator(translator)
        return translator
    return None


def system_locale_name() -> str:
    return QLocale.system().name()


def effective_language_code(language_code: str) -> str:
    if language_code == "system":
        code = system_locale_name().split("_", 1)[0].lower()
        return code if code in LANGUAGES and code != "system" else DEFAULT_LANGUAGE
    return language_code if language_code in LANGUAGES else DEFAULT_LANGUAGE


def default_country_for_language(language_code: str) -> str | None:
    if language_code == "system":
        locale_name = system_locale_name()
        if locale_name in LOCALE_DEFAULT_COUNTRIES:
            return LOCALE_DEFAULT_COUNTRIES[locale_name]
        language_code = effective_language_code(language_code)
    return LANGUAGE_DEFAULT_COUNTRIES.get(language_code)


def rate_by_country_name(country_name: str | None) -> TaxRate | None:
    if not country_name:
        return None
    for rate in COUNTRY_RATES:
        if rate.name == country_name:
            return rate
    return None


def combo_set_data(combo: QComboBox, data):
    index = combo.findData(data)
    if index >= 0:
        combo.setCurrentIndex(index)


def combo_data(combo: QComboBox, default):
    data = combo.currentData()
    return data if data is not None else default


@dataclass(frozen=True)
class TaxRate:
    name: str
    rate: Decimal
    flag: str = ""
    custom: bool = False

    @property
    def label(self) -> str:
        return f"{self.flag} {self.name}".strip()


COUNTRY_RATES = [
    TaxRate("Ecuador", Decimal("15"), "EC"),
    TaxRate("Espana", Decimal("21"), "ES"),
    TaxRate("Islas Canarias", Decimal("7"), "IC"),
    TaxRate("Alemania", Decimal("19"), "DE"),
    TaxRate("Austria", Decimal("20"), "AT"),
    TaxRate("Belgica", Decimal("21"), "BE"),
    TaxRate("Bulgaria", Decimal("20"), "BG"),
    TaxRate("Croacia", Decimal("25"), "HR"),
    TaxRate("Chipre", Decimal("19"), "CY"),
    TaxRate("Dinamarca", Decimal("25"), "DK"),
    TaxRate("Eslovaquia", Decimal("20"), "SK"),
    TaxRate("Eslovenia", Decimal("22"), "SI"),
    TaxRate("Estonia", Decimal("22"), "EE"),
    TaxRate("Finlandia", Decimal("24"), "FI"),
    TaxRate("Francia", Decimal("20"), "FR"),
    TaxRate("Grecia", Decimal("24"), "GR"),
    TaxRate("Hungria", Decimal("27"), "HU"),
    TaxRate("Irlanda", Decimal("23"), "IE"),
    TaxRate("Italia", Decimal("22"), "IT"),
    TaxRate("Letonia", Decimal("21"), "LV"),
    TaxRate("Lituania", Decimal("21"), "LT"),
    TaxRate("Luxemburgo", Decimal("17"), "LU"),
    TaxRate("Malta", Decimal("18"), "MT"),
    TaxRate("Paises Bajos", Decimal("21"), "NL"),
    TaxRate("Polonia", Decimal("23"), "PL"),
    TaxRate("Portugal", Decimal("23"), "PT"),
    TaxRate("Republica Checa", Decimal("21"), "CZ"),
    TaxRate("Rumania", Decimal("19"), "RO"),
    TaxRate("Suecia", Decimal("25"), "SE"),
    TaxRate("Reino Unido", Decimal("20"), "GB"),
    TaxRate("Noruega", Decimal("25"), "NO"),
    TaxRate("Suiza", Decimal("8.1"), "CH"),
    TaxRate("Canada GST", Decimal("5"), "CA"),
    TaxRate("Mexico", Decimal("16"), "MX"),
    TaxRate("Argentina", Decimal("21"), "AR"),
    TaxRate("Chile", Decimal("19"), "CL"),
    TaxRate("Colombia", Decimal("19"), "CO"),
    TaxRate("Peru", Decimal("18"), "PE"),
    TaxRate("Brasil", Decimal("17"), "BR"),
    TaxRate("Uruguay", Decimal("22"), "UY"),
    TaxRate("Paraguay", Decimal("10"), "PY"),
    TaxRate("Bolivia", Decimal("13"), "BO"),
    TaxRate("Estados Unidos", Decimal("0"), "US"),
    TaxRate("Australia", Decimal("10"), "AU"),
    TaxRate("Nueva Zelanda", Decimal("15"), "NZ"),
    TaxRate("Japon", Decimal("10"), "JP"),
    TaxRate("Corea del Sur", Decimal("10"), "KR"),
    TaxRate("India GST", Decimal("18"), "IN"),
    TaxRate("China", Decimal("13"), "CN"),
    TaxRate("Sudafrica", Decimal("15"), "ZA"),
]

THEMES = {
    "Rojo": "#ef5350",
    "Azul": "#42a5f5",
    "Indigo": "#7986cb",
    "Cian": "#4dd0e1",
    "Verde azulado": "#4db6ac",
    "Verde": "#81c784",
    "Lima": "#dce775",
    "Ambar": "#ffb74d",
    "Purpura": "#ba68c8",
    "Rosa": "#f06292",
    "Oscuro": "#3d3d3d",
}


def dec(value: str | int | float | Decimal) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return Decimal("0")


def clean_decimal_text(text: str, decimal_separator: str) -> str:
    text = text.strip().replace(" ", "")
    alternate = "," if decimal_separator == "." else "."
    text = text.replace(alternate, decimal_separator)
    return text.replace(decimal_separator, ".")


class NumberFormatter:
    def __init__(
        self,
        decimals: int = 2,
        decimal_separator: str = ",",
        thousands_separator: str = ".",
        grouping: int = 3,
        show_decimals: bool = True,
    ):
        self.decimals = decimals
        self.decimal_separator = decimal_separator
        self.thousands_separator = thousands_separator
        self.grouping = grouping
        self.show_decimals = show_decimals

    def parse(self, text: str) -> Decimal:
        if not text:
            return Decimal("0")
        cleaned = text.replace(self.thousands_separator, "")
        cleaned = clean_decimal_text(cleaned, self.decimal_separator)
        return dec(cleaned)

    def format(self, value: Decimal) -> str:
        precision = Decimal("1") if not self.show_decimals else Decimal("1").scaleb(-self.decimals)
        value = value.quantize(precision, rounding=ROUND_HALF_UP)
        raw = f"{value:f}"
        negative = raw.startswith("-")
        if negative:
            raw = raw[1:]
        whole, _, fraction = raw.partition(".")
        whole = self._group(whole)
        if self.show_decimals and self.decimals > 0:
            fraction = fraction.ljust(self.decimals, "0")[: self.decimals]
            raw = f"{whole}{self.decimal_separator}{fraction}"
        else:
            raw = whole
        return f"-{raw}" if negative else raw

    def _group(self, whole: str) -> str:
        if not self.thousands_separator or self.grouping <= 0:
            return whole
        parts = []
        while whole:
            parts.append(whole[-self.grouping :])
            whole = whole[: -self.grouping]
        return self.thousands_separator.join(reversed(parts))


class DisplayPanel(QFrame):
    def __init__(self, key: str, title: str):
        super().__init__()
        self.key = key
        self.setObjectName("displayPanel")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.panel_layout = QVBoxLayout(self)
        self.title = QLabel(title)
        self.title.setObjectName("displayTitle")
        self.value = QLabel("0,00")
        self.value.setObjectName("displayValue")
        self.value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.value.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.panel_layout.addWidget(self.title)
        self.panel_layout.addWidget(self.value, 1)
        self.apply_size(1.0)

    def apply_size(self, factor: float):
        self.setMinimumHeight(scaled(82, factor))
        self.panel_layout.setContentsMargins(
            scaled(16, factor),
            scaled(8, factor),
            scaled(16, factor),
            scaled(8, factor),
        )
        self.panel_layout.setSpacing(scaled(2, factor))

    def set_active(self, active: bool):
        self.setProperty("active", active)
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event):  # noqa: N802
        self.window().set_active_panel(self.key)
        super().mousePressEvent(event)


class CountryDialog(QDialog):
    def __init__(self, rates: list[TaxRate], parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Paises"))
        self.setMinimumSize(430, 560)
        layout = QVBoxLayout(self)
        title = QLabel(self.tr("Paises"))
        title.setObjectName("dialogTitle")
        self.list_widget = QListWidget()
        for rate in rates:
            item = QListWidgetItem(f"{rate.label}    {rate.rate}%")
            item.setData(Qt.ItemDataRole.UserRole, rate)
            self.list_widget.addItem(item)
        self.list_widget.itemDoubleClicked.connect(self.accept)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(title)
        layout.addWidget(self.list_widget, 1)
        layout.addWidget(buttons)

    def selected_rate(self) -> TaxRate | None:
        item = self.list_widget.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None


class CustomRatesDialog(QDialog):
    def __init__(self, rates: list[Decimal], parent=None):
        super().__init__(parent)
        self.rates = rates
        self.setWindowTitle(self.tr("Tasas personalizadas"))
        self.setMinimumSize(360, 470)
        layout = QVBoxLayout(self)
        header = QHBoxLayout()
        title = QLabel(self.tr("Tasas personalizadas"))
        title.setObjectName("dialogTitle")
        add = QPushButton("+")
        add.setObjectName("roundButton")
        add.clicked.connect(self.add_rate)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(add)
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.accept)
        remove = QPushButton(self.tr("Eliminar seleccionada"))
        remove.clicked.connect(self.remove_rate)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close | QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addLayout(header)
        layout.addWidget(self.list_widget, 1)
        layout.addWidget(remove)
        layout.addWidget(buttons)
        self.refresh()

    def refresh(self):
        self.list_widget.clear()
        for value in self.rates:
            item = QListWidgetItem(f"{value.normalize()}%")
            item.setData(Qt.ItemDataRole.UserRole, value)
            self.list_widget.addItem(item)

    def add_rate(self):
        value, ok = QInputDialog.getDouble(
            self,
            self.tr("Nueva tasa"),
            self.tr("Porcentaje"),
            12.0,
            0.0,
            999.0,
            3,
        )
        if ok:
            new_value = dec(value).quantize(Decimal("0.001")).normalize()
            if new_value not in self.rates:
                self.rates.append(new_value)
                self.rates.sort()
            self.refresh()

    def remove_rate(self):
        item = self.list_widget.currentItem()
        if item:
            self.rates.remove(item.data(Qt.ItemDataRole.UserRole))
            self.refresh()

    def selected_rate(self) -> Decimal | None:
        item = self.list_widget.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None


class AboutDialog(QDialog):
    def __init__(self, dark_theme: bool = False, settings: AppSettings | None = None, parent=None):
        super().__init__(parent)
        self.dark_theme = dark_theme
        self.settings = settings
        self.setWindowTitle(self.tr("Acerca de..."))
        self.setWindowIcon(QIcon(str(app_icon_path())))
        self.setMinimumSize(780, 520)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        left = QVBoxLayout()
        left.setSpacing(14)
        left.addStretch()
        icon_label = QLabel()
        icon_label.setObjectName("aboutIcon")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setMinimumWidth(190)
        icon_label.setPixmap(QPixmap(str(app_icon_path())).scaled(
            180,
            180,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        ))
        title = QLabel(self.tr("Calculadora de IVA"))
        title.setObjectName("aboutAppTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left.addWidget(icon_label)
        left.addWidget(title)
        left.addStretch()

        right = QVBoxLayout()
        right.setSpacing(12)
        developers_title = QLabel(self.tr("Desarrolladores"))
        developers_title.setObjectName("dialogTitle")
        right.addWidget(developers_title)
        right.addWidget(
            self.developer_card(
                "Washington Indacochea Delgado",
                "linuxfrontier@proton.me",
                "https://www.facebook.com/wachin.id",
                photos_dir() / "Washington_Indacochea_FB_IMG.jpg",
            )
        )
        right.addWidget(
            self.developer_card(
                "Joseph Lucio Guerrero",
                "josephsteveng@gmail.com",
                "https://www.facebook.com/jose.guerrero.718689",
                photos_dir() / "Joseph_Lucio_FB_IMG.jpg",
            )
        )

        details = QLabel()
        details.setObjectName("aboutText")
        details.setTextFormat(Qt.TextFormat.RichText)
        details.setOpenExternalLinks(True)
        details.setWordWrap(True)
        details.setText(
            self.styled_links(
                self.tr(
                    "<p><b>Licencia</b><br>GNU GPL v3</p>"
                    "<p><b>Tecnologías usadas</b><br>Python, PyQt6, Qt Linguist, QtSvg</p>"
                    "<p>Calculadora de IVA de escritorio con tasas por país, tasas personalizadas, "
                    "formatos numéricos, temas, tamaños de interfaz e internacionalización.</p>"
                    '<p><b>Sitio web</b><br><a href="https://wachin.github.io/lucio-iva-calculator/">'
                    "https://wachin.github.io/lucio-iva-calculator/</a></p>"
                    "<p>Jipijapa, Manabí, Ecuador</p>"
                )
            )
        )
        right.addWidget(details, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)

        right.addWidget(buttons)

        layout.addLayout(left)
        layout.addLayout(right, 1)
        self.restore_or_center()

    def developer_card(self, name: str, email: str, facebook: str, photo_path: Path) -> QFrame:
        card = QFrame()
        card.setObjectName("developerCard")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(14)

        photo = QLabel()
        photo.setObjectName("developerPhoto")
        photo.setFixedSize(104, 104)
        photo.setPixmap(self.rounded_photo(photo_path, 104, 12))
        photo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        info = QLabel()
        info.setObjectName("aboutText")
        info.setTextFormat(Qt.TextFormat.RichText)
        info.setOpenExternalLinks(True)
        info.setWordWrap(True)
        info.setText(
            self.styled_links(
                f"<p><b>© 2026 {name}</b><br>"
                f'<a href="mailto:{email}">{email}</a><br>'
                f'<a href="{facebook}">{facebook.replace("https://www.", "")}</a></p>'
            )
        )

        layout.addWidget(photo)
        layout.addWidget(info, 1)
        return card

    def styled_links(self, html: str) -> str:
        link_color = "#8ec5ff" if self.dark_theme else "#0645ad"
        link_style = f'style="color:{link_color}; text-decoration: underline; font-weight: 600;"'
        return html.replace("<a href=", f"<a {link_style} href=")

    def rounded_photo(self, photo_path: Path, size: int, radius: int) -> QPixmap:
        source = QPixmap(str(photo_path))
        if source.isNull():
            source = QPixmap(size, size)
            source.fill(Qt.GlobalColor.transparent)
        scaled_photo = source.scaled(
            size,
            size,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        x = max(0, (scaled_photo.width() - size) // 2)
        y = max(0, (scaled_photo.height() - size) // 2)
        cropped = scaled_photo.copy(x, y, size, size)
        result = QPixmap(size, size)
        result.fill(Qt.GlobalColor.transparent)
        painter = QPainter(result)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        path = QPainterPath()
        path.addRoundedRect(0, 0, size, size, radius, radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, cropped)
        painter.end()
        return result

    def restore_or_center(self):
        if self.settings is not None and self.restore_saved_geometry():
            return
        self.center_on_parent_or_screen()

    def restore_saved_geometry(self) -> bool:
        if self.settings is None:
            return False
        try:
            x = int(self.settings.value("about_window_x"))
            y = int(self.settings.value("about_window_y"))
            width = int(self.settings.value("about_window_width"))
            height = int(self.settings.value("about_window_height"))
        except (TypeError, ValueError):
            return False
        if width <= 0 or height <= 0:
            return False
        screens = QApplication.screens()
        if screens:
            screen = next(
                (
                    candidate
                    for candidate in screens
                    if candidate.availableGeometry().adjusted(-40, -40, 40, 40).contains(x, y)
                ),
                QApplication.primaryScreen() or screens[0],
            )
            available = screen.availableGeometry()
            width = min(max(width, self.minimumWidth()), available.width())
            height = min(max(height, self.minimumHeight()), available.height())
            x = min(max(x, available.left()), available.right() - width + 1)
            y = min(max(y, available.top()), available.bottom() - height + 1)
        self.setGeometry(x, y, width, height)
        return True

    def center_on_parent_or_screen(self):
        self.adjustSize()
        parent = self.parentWidget()
        if parent is not None:
            center = parent.frameGeometry().center()
            frame = self.frameGeometry()
            frame.moveCenter(center)
            self.move(frame.topLeft())
            return
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        frame = self.frameGeometry()
        frame.moveCenter(screen.availableGeometry().center())
        self.move(frame.topLeft())

    def save_window_geometry(self):
        if self.settings is None or self.isMinimized():
            return
        geometry = self.geometry()
        self.settings.setValue("about_window_x", geometry.x())
        self.settings.setValue("about_window_y", geometry.y())
        self.settings.setValue("about_window_width", geometry.width())
        self.settings.setValue("about_window_height", geometry.height())
        self.settings.sync()

    def closeEvent(self, event):  # noqa: N802
        self.save_window_geometry()
        super().closeEvent(event)


class HelpDialog(QDialog):
    def __init__(self, language_code: str, dark_theme: bool = False, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Ayuda"))
        self.setWindowIcon(QIcon(str(app_icon_path())))
        self.setMinimumSize(680, 560)

        layout = QVBoxLayout(self)
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(self.help_html(language_code, dark_theme))

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)

        layout.addWidget(browser, 1)
        layout.addWidget(buttons)

    def help_html(self, language_code: str, dark_theme: bool) -> str:
        html = help_file_path(language_code).read_text(encoding="utf-8")
        if dark_theme:
            help_css = """
              body { background: #242424; color: #f2f2f2; font-size: 15px; line-height: 1.55; }
              h1 { color: #ff6b6b; font-size: 28px; }
              h2 { color: #ffffff; font-size: 21px; }
              table { font-size: 15px; }
              th, td { border-bottom: 1px solid #555555; padding: 9px 8px; }
              th { background: #343434; color: #ffffff; }
              kbd { background: #3d3d3d; border: 1px solid #777777; color: #ffffff; }
            """
        else:
            help_css = """
              body { font-size: 15px; line-height: 1.55; }
              h1 { font-size: 28px; }
              h2 { font-size: 21px; }
              table { font-size: 15px; }
              th, td { padding: 9px 8px; }
            """
        return html.replace("</style>", f"{help_css}</style>")


class SettingsDialog(QDialog):
    def __init__(
        self,
        formatter: NumberFormatter,
        theme_name: str,
        ui_size_name: str,
        font_family: str,
        language_code: str,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Configuracion"))
        self.setMinimumSize(500, 560)
        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        form = QFormLayout()
        self.thousands = QComboBox()
        self.thousands.addItems([".", ",", " ", ""])
        self.thousands.setCurrentText(formatter.thousands_separator)
        self.decimal = QComboBox()
        self.decimal.addItems([",", "."])
        self.decimal.setCurrentText(formatter.decimal_separator)
        self.decimals = QComboBox()
        self.decimals.addItems(["0", "1", "2", "3", "4"])
        self.decimals.setCurrentText(str(formatter.decimals))
        self.show_decimals = QCheckBox(self.tr("Mostrar"))
        self.show_decimals.setChecked(formatter.show_decimals)
        self.grouping = QComboBox()
        self.grouping.addItems(["3", "4"])
        self.grouping.setCurrentText(str(formatter.grouping))
        self.theme = QComboBox()
        for theme in THEMES:
            self.theme.addItem(self.theme_label(theme), theme)
        combo_set_data(self.theme, theme_name)
        self.ui_size = QComboBox()
        for ui_size in UI_SIZE_PRESETS:
            self.ui_size.addItem(self.ui_size_label(ui_size), ui_size)
        combo_set_data(self.ui_size, ui_size_name if ui_size_name in UI_SIZE_PRESETS else DEFAULT_UI_SIZE)
        self.font_family = QComboBox()
        self.font_family.addItem(self.tr("Sistema"), SYSTEM_FONT_SETTING)
        font_families = QFontDatabase.families() or [system_font_family()]
        for family in font_families:
            self.font_family.addItem(family, family)
        combo_set_data(self.font_family, font_family if font_family else SYSTEM_FONT_SETTING)
        self.language = QComboBox()
        for code, label in LANGUAGES.items():
            self.language.addItem(self.language_label(code, label), code)
        combo_set_data(self.language, language_code if language_code in LANGUAGES else DEFAULT_LANGUAGE_SETTING)
        form.addRow(self.tr("Separador de miles"), self.thousands)
        form.addRow(self.tr("Separador decimal"), self.decimal)
        form.addRow(self.tr("Lugares decimales"), self.decimals)
        form.addRow("", self.show_decimals)
        form.addRow(self.tr("Agrupacion de cifras"), self.grouping)
        form.addRow(self.tr("Tema"), self.theme)
        form.addRow(self.tr("Tamano de interfaz"), self.ui_size)
        form.addRow(self.tr("Fuente"), self.font_family)
        form.addRow(self.tr("Idioma"), self.language)
        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumHeight(86)
        self.preview.setObjectName("preview")
        for widget in [self.thousands, self.decimal, self.decimals, self.grouping]:
            widget.currentTextChanged.connect(self.update_preview)
        self.show_decimals.toggled.connect(self.update_preview)
        self.theme.currentTextChanged.connect(self.update_preview)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        general_layout.addLayout(form)
        general_layout.addWidget(QLabel(self.tr("Vista previa")))
        general_layout.addWidget(self.preview)
        general_layout.addStretch()
        tabs.addTab(general_tab, self.tr("General"))
        tabs.addTab(self.build_shortcuts_tab(), self.tr("Atajos de teclado"))
        layout.addWidget(tabs, 1)
        layout.addWidget(buttons)
        self.update_preview()

    def build_shortcuts_tab(self) -> QWidget:
        tab = QWidget()
        layout = QGridLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setHorizontalSpacing(18)
        layout.setVerticalSpacing(8)
        shortcut_header = QLabel(self.tr("Atajo"))
        action_header = QLabel(self.tr("Accion"))
        shortcut_header.setStyleSheet("font-weight: 700;")
        action_header.setStyleSheet("font-weight: 700;")
        layout.addWidget(shortcut_header, 0, 0)
        layout.addWidget(action_header, 0, 1)
        for row, (shortcut, description) in enumerate(KEYBOARD_SHORTCUTS, start=1):
            shortcut_label = QLabel(shortcut)
            shortcut_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            description_label = QLabel(self.shortcut_description(description))
            description_label.setWordWrap(True)
            layout.addWidget(shortcut_label, row, 0)
            layout.addWidget(description_label, row, 1)
        layout.setColumnStretch(1, 1)
        layout.setRowStretch(len(KEYBOARD_SHORTCUTS) + 1, 1)
        return tab

    def shortcut_description(self, description: str) -> str:
        labels = {
            "Escribir numeros": self.tr("Escribir numeros"),
            "Escribir separador decimal": self.tr("Escribir separador decimal"),
            "Operaciones basicas": self.tr("Operaciones basicas"),
            "Calcular operacion pendiente": self.tr("Calcular operacion pendiente"),
            "Borrar el ultimo digito": self.tr("Borrar el ultimo digito"),
            "Limpiar todo": self.tr("Limpiar todo"),
            "Editar IVA excluido": self.tr("Editar IVA excluido"),
            "Editar IVA": self.tr("Editar IVA"),
            "Editar IVA incluido": self.tr("Editar IVA incluido"),
            "Cambiar al siguiente valor": self.tr("Cambiar al siguiente valor"),
            "Cambiar al valor anterior": self.tr("Cambiar al valor anterior"),
            "Seleccionar pais": self.tr("Seleccionar pais"),
            "Abrir tasas personalizadas": self.tr("Abrir tasas personalizadas"),
            "Abrir configuracion": self.tr("Abrir configuracion"),
            "Abrir ayuda": self.tr("Abrir ayuda"),
        }
        return labels.get(description, description)

    def theme_label(self, theme_name: str) -> str:
        labels = {
            "Rojo": self.tr("Rojo"),
            "Azul": self.tr("Azul"),
            "Indigo": self.tr("Indigo"),
            "Cian": self.tr("Cian"),
            "Verde azulado": self.tr("Verde azulado"),
            "Verde": self.tr("Verde"),
            "Lima": self.tr("Lima"),
            "Ambar": self.tr("Ambar"),
            "Purpura": self.tr("Purpura"),
            "Rosa": self.tr("Rosa"),
            "Oscuro": self.tr("Oscuro"),
        }
        return labels.get(theme_name, theme_name)

    def ui_size_label(self, ui_size_name: str) -> str:
        labels = {
            "Muy pequeno": self.tr("Muy pequeno"),
            "Pequeno": self.tr("Pequeno"),
            "Mediano": self.tr("Mediano"),
            "Grande": self.tr("Grande"),
            "Muy grande": self.tr("Muy grande"),
        }
        return labels.get(ui_size_name, ui_size_name)

    def language_label(self, code: str, label: str) -> str:
        if code == "system":
            return self.tr("Sistema")
        return label

    def formatter(self) -> NumberFormatter:
        return NumberFormatter(
            decimals=int(self.decimals.currentText()),
            decimal_separator=self.decimal.currentText(),
            thousands_separator=self.thousands.currentText(),
            grouping=int(self.grouping.currentText()),
            show_decimals=self.show_decimals.isChecked(),
        )

    def update_preview(self):
        formatter = self.formatter()
        theme_name = combo_data(self.theme, "Rojo")
        preview_text = "#f7f7f7" if theme_name == "Oscuro" else "rgba(0,0,0,0.75)"
        self.preview.setText(formatter.format(Decimal("1234567890.12")))
        self.preview.setStyleSheet(f"background:{THEMES[theme_name]}; color:{preview_text};")


class CalculatorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = app_settings()
        self.formatter = NumberFormatter(
            decimals=int(self.settings.value("decimals", 2)),
            decimal_separator=self.settings.value("decimal_separator", ","),
            thousands_separator=self.settings.value("thousands_separator", "."),
            grouping=int(self.settings.value("grouping", 3)),
            show_decimals=settings_bool(self.settings.value("show_decimals", "true"), True),
        )
        self.theme_name = self.settings.value("theme", "Rojo")
        stored_language = self.settings.value("language", DEFAULT_LANGUAGE_SETTING)
        self.language_code = stored_language if stored_language in LANGUAGES else DEFAULT_LANGUAGE_SETTING
        should_apply_language_rate = "rate_name" not in self.settings.allKeys()
        stored_ui_size = self.settings.value("ui_size", DEFAULT_UI_SIZE)
        self.ui_size_name = stored_ui_size if stored_ui_size in UI_SIZE_PRESETS else DEFAULT_UI_SIZE
        self.font_family = self.settings.value("font_family", SYSTEM_FONT_SETTING)
        self.key_buttons: list[QPushButton] = []
        self.custom_rates = self.load_custom_rates()
        self.current_rate = TaxRate(
            self.settings.value("rate_name", "Ecuador"),
            dec(self.settings.value("rate_value", "15")),
            self.settings.value("rate_flag", "EC"),
            settings_bool(self.settings.value("rate_custom", "false")),
        )
        self.active_key = "net"
        self.input_buffer = ""
        self.pending_operator: str | None = None
        self.pending_value: Decimal | None = None
        self.values = {"net": Decimal("0"), "tax": Decimal("0"), "gross": Decimal("0")}
        self.panels: dict[str, DisplayPanel] = {}
        self.last_system_dark_theme = windows_apps_dark_theme()
        self.system_theme_timer: QTimer | None = None
        self.setWindowTitle(self.tr("Calculadora de IVA"))
        self.setWindowIcon(QIcon(str(app_icon_path())))
        self.build_ui()
        QApplication.instance().installEventFilter(self)
        self.apply_app_font()
        self.apply_ui_size(resize_window=False)
        self.apply_theme()
        self.restore_or_place_window()
        if should_apply_language_rate:
            self.apply_default_rate_for_language()
        self.sync_from_active()
        self.start_system_theme_monitor()

    @property
    def ui_preset(self) -> dict[str, float | int]:
        return UI_SIZE_PRESETS.get(self.ui_size_name, UI_SIZE_PRESETS[DEFAULT_UI_SIZE])

    @property
    def ui_scale(self) -> float:
        return float(self.ui_preset["scale"])

    def resize_to_available_screen(self):
        screen = QApplication.primaryScreen()
        preset = self.ui_preset
        if screen is None:
            self.resize(int(preset["width"]), int(preset["height"]))
            return
        available = screen.availableGeometry()
        width = min(int(preset["width"]), max(280, available.width() - 48))
        height = min(int(preset["height"]), max(460, available.height() - 48))
        self.resize(width, height)

    def restore_or_place_window(self):
        if self.restore_saved_geometry():
            return
        self.resize_to_available_screen()
        self.center_on_screen()

    def restore_saved_geometry(self) -> bool:
        try:
            x = int(self.settings.value("window_x"))
            y = int(self.settings.value("window_y"))
            width = int(self.settings.value("window_width"))
            height = int(self.settings.value("window_height"))
        except (TypeError, ValueError):
            return False
        if width <= 0 or height <= 0:
            return False
        rect = self.clamp_window_geometry(x, y, width, height)
        self.setGeometry(rect[0], rect[1], rect[2], rect[3])
        return True

    def clamp_window_geometry(self, x: int, y: int, width: int, height: int) -> tuple[int, int, int, int]:
        screens = QApplication.screens()
        if not screens:
            return x, y, width, height
        screen = next(
            (
                candidate
                for candidate in screens
                if candidate.availableGeometry().adjusted(-40, -40, 40, 40).contains(x, y)
            ),
            QApplication.primaryScreen() or screens[0],
        )
        available = screen.availableGeometry()
        width = min(max(width, self.minimumWidth()), available.width())
        height = min(max(height, self.minimumHeight()), available.height())
        x = min(max(x, available.left()), available.right() - width + 1)
        y = min(max(y, available.top()), available.bottom() - height + 1)
        return x, y, width, height

    def center_on_screen(self):
        screen = self.screen() or QApplication.primaryScreen()
        if screen is None:
            return
        available = screen.availableGeometry()
        frame = self.frameGeometry()
        frame.moveCenter(available.center())
        self.move(frame.topLeft())

    def save_window_geometry(self):
        if self.isMinimized():
            return
        geometry = self.normalGeometry() if self.isMaximized() else self.geometry()
        self.settings.setValue("window_x", geometry.x())
        self.settings.setValue("window_y", geometry.y())
        self.settings.setValue("window_width", geometry.width())
        self.settings.setValue("window_height", geometry.height())
        self.settings.sync()

    def apply_app_font(self):
        app = QApplication.instance()
        if app is None:
            return
        font = QFont(app.font())
        selected_family = effective_font_family(self.font_family)
        if selected_family:
            font.setFamily(selected_family)
        app.setFont(font)

    def apply_ui_size(self, resize_window: bool = True):
        factor = self.ui_scale
        preset = self.ui_preset
        screen = QApplication.primaryScreen()
        if screen is not None:
            available = screen.availableGeometry()
            min_width = min(int(preset["min_width"]), max(280, available.width() - 80))
            min_height = min(int(preset["min_height"]), max(460, available.height() - 80))
        else:
            min_width = int(preset["min_width"])
            min_height = int(preset["min_height"])
        self.setMinimumSize(min_width, min_height)
        for panel in self.panels.values():
            panel.apply_size(factor)
        for button in self.key_buttons:
            button.setMinimumSize(QSize(scaled(54, factor), scaled(58, factor)))
        if hasattr(self, "toolbar_layout"):
            self.toolbar_layout.setContentsMargins(
                scaled(10, factor),
                scaled(6, factor),
                scaled(10, factor),
                scaled(6, factor),
            )
        if hasattr(self, "displays_layout"):
            self.displays_layout.setContentsMargins(
                scaled(10, factor),
                scaled(10, factor),
                scaled(10, factor),
                scaled(10, factor),
            )
            self.displays_layout.setSpacing(scaled(7, factor))
        if hasattr(self, "keypad_grid"):
            self.keypad_grid.setContentsMargins(
                scaled(7, factor),
                scaled(7, factor),
                scaled(7, factor),
                scaled(7, factor),
            )
            self.keypad_grid.setHorizontalSpacing(scaled(7, factor))
            self.keypad_grid.setVerticalSpacing(scaled(7, factor))
        self.apply_theme()
        if resize_window:
            self.resize_to_available_screen()

    def start_system_theme_monitor(self):
        if not sys.platform.startswith("win"):
            return
        self.system_theme_timer = QTimer(self)
        self.system_theme_timer.setInterval(1500)
        self.system_theme_timer.timeout.connect(self.handle_system_theme_change)
        self.system_theme_timer.start()

    def handle_system_theme_change(self):
        system_dark = windows_apps_dark_theme()
        if system_dark == self.last_system_dark_theme:
            return
        was_light = not self.last_system_dark_theme
        self.last_system_dark_theme = system_dark
        if was_light and system_dark and self.theme_name != "Oscuro":
            self.theme_name = "Oscuro"
            self.save_settings()
            self.apply_theme()

    def build_ui(self):
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setCentralWidget(central)

        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        self.toolbar_layout = QHBoxLayout(toolbar)
        bar = self.toolbar_layout
        bar.setContentsMargins(10, 6, 10, 6)
        menu_button = QToolButton()
        menu_button.setText("☰")
        menu_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        menu = QMenu(menu_button)
        select_country_action = QAction(self.tr("Seleccionar pais"), self, triggered=self.select_country)
        select_country_action.setShortcut(QKeySequence("Ctrl+P"))
        custom_rates_action = QAction(self.tr("Tasas personalizadas"), self, triggered=self.manage_custom_rates)
        custom_rates_action.setShortcut(QKeySequence("Ctrl+R"))
        settings_action = QAction(self.tr("Configuracion"), self, triggered=self.open_settings)
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        help_action = QAction(self.tr("Ayuda"), self, triggered=self.open_help)
        help_action.setShortcut(QKeySequence("F1"))
        menu.addAction(select_country_action)
        menu.addAction(custom_rates_action)
        menu.addAction(settings_action)
        menu.addSeparator()
        menu.addSection(self.tr("Ayuda"))
        menu.addAction(help_action)
        about_action = QAction(self.tr("Acerca de..."), self, triggered=self.open_about)
        menu.addAction(about_action)
        self.addActions([select_country_action, custom_rates_action, settings_action, help_action, about_action])
        menu_button.setMenu(menu)
        self.country_button = QPushButton()
        self.country_button.setObjectName("countryButton")
        self.country_button.clicked.connect(self.select_country)
        self.rate_button = QPushButton()
        self.rate_button.setObjectName("rateButton")
        self.rate_button.clicked.connect(self.manage_custom_rates)
        bar.addWidget(menu_button)
        bar.addWidget(self.country_button, 1)
        bar.addWidget(self.rate_button)
        root.addWidget(toolbar)

        displays = QFrame()
        displays.setObjectName("displayArea")
        self.displays_layout = QVBoxLayout(displays)
        displays_layout = self.displays_layout
        displays_layout.setContentsMargins(10, 10, 10, 10)
        displays_layout.setSpacing(7)
        for key, title in [
            ("net", self.tr("IVA EXCLUIDO")),
            ("tax", self.tr("IVA")),
            ("gross", self.tr("IVA INCLUIDO")),
        ]:
            panel = DisplayPanel(key, title)
            self.panels[key] = panel
            displays_layout.addWidget(panel)
        root.addWidget(displays, 1)

        keypad = QFrame()
        keypad.setObjectName("keypad")
        self.keypad_grid = QGridLayout(keypad)
        grid = self.keypad_grid
        grid.setContentsMargins(7, 7, 7, 7)
        grid.setHorizontalSpacing(7)
        grid.setVerticalSpacing(7)
        buttons = [
            ["7", "8", "9", "DEL", "CA"],
            ["4", "5", "6", "×", "÷"],
            ["1", "2", "3", "+", "-"],
            ["0", ".", "±", "=", "rate"],
        ]
        for row, row_values in enumerate(buttons):
            for col, text in enumerate(row_values):
                label = self.current_rate.flag if text == "rate" else text
                button = QPushButton(label)
                button.setMinimumSize(QSize(54, 58))
                button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                self.key_buttons.append(button)
                button.setObjectName("dangerButton" if text in {"DEL", "CA"} else "keyButton")
                if col >= 3 and text not in {"DEL", "CA"}:
                    button.setObjectName("operationButton")
                if text == "rate":
                    button.setObjectName("rateKey")
                    button.clicked.connect(self.select_country)
                else:
                    button.clicked.connect(lambda checked=False, value=text: self.handle_key(value))
                grid.addWidget(button, row, col)
        root.addWidget(keypad)
        self.update_header()
        self.set_active_panel(self.active_key)

    def eventFilter(self, watched, event):  # noqa: N802
        if event.type() == QEvent.Type.KeyPress and QApplication.activeWindow() is self:
            if self.handle_keyboard_event(event):
                return True
        return super().eventFilter(watched, event)

    def handle_keyboard_event(self, event) -> bool:
        modifiers = event.modifiers() & ~Qt.KeyboardModifier.KeypadModifier
        key = event.key()

        if modifiers == Qt.KeyboardModifier.ControlModifier:
            if key == Qt.Key.Key_1:
                self.set_active_panel("net")
                return True
            if key == Qt.Key.Key_2:
                self.set_active_panel("tax")
                return True
            if key == Qt.Key.Key_3:
                self.set_active_panel("gross")
                return True
            if key == Qt.Key.Key_Tab:
                self.cycle_active_panel(1)
                return True

        if modifiers == (
            Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier
        ) and key == Qt.Key.Key_Tab:
            self.cycle_active_panel(-1)
            return True

        if modifiers not in {
            Qt.KeyboardModifier.NoModifier,
            Qt.KeyboardModifier.ShiftModifier,
        }:
            return False

        text = event.text()
        if text and text in "0123456789":
            self.handle_key(text)
            return True

        key_map = {
            Qt.Key.Key_Comma: ".",
            Qt.Key.Key_Period: ".",
            Qt.Key.Key_Backspace: "DEL",
            Qt.Key.Key_Delete: "DEL",
            Qt.Key.Key_Escape: "CA",
            Qt.Key.Key_Return: "=",
            Qt.Key.Key_Enter: "=",
            Qt.Key.Key_Plus: "+",
            Qt.Key.Key_Minus: "-",
            Qt.Key.Key_Asterisk: "×",
            Qt.Key.Key_Slash: "÷",
        }
        if key in key_map:
            self.handle_key(key_map[key])
            return True

        text_map = {"*": "×", "/": "÷", "x": "×", "X": "×", "=": "="}
        if text in text_map:
            self.handle_key(text_map[text])
            return True

        return False

    def cycle_active_panel(self, direction: int = 1):
        panel_order = ["net", "tax", "gross"]
        current_index = panel_order.index(self.active_key)
        self.set_active_panel(panel_order[(current_index + direction) % len(panel_order)])

    def set_active_panel(self, key: str):
        self.active_key = key
        self.input_buffer = ""
        for panel_key, panel in self.panels.items():
            panel.set_active(panel_key == key)

    def handle_key(self, key: str):
        if key in "0123456789":
            self.input_buffer = "0" if self.input_buffer == "0" else self.input_buffer + key
            self.values[self.active_key] = self.formatter.parse(self.input_buffer)
            self.sync_from_active()
        elif key == ".":
            decimal_separator = self.formatter.decimal_separator
            if decimal_separator not in self.input_buffer:
                self.input_buffer = self.input_buffer or "0"
                self.input_buffer += decimal_separator
                self.panels[self.active_key].value.setText(self.input_buffer)
        elif key == "DEL":
            self.input_buffer = self.input_buffer[:-1]
            self.values[self.active_key] = self.formatter.parse(self.input_buffer or "0")
            self.sync_from_active()
        elif key == "CA":
            self.input_buffer = ""
            self.pending_operator = None
            self.pending_value = None
            self.values = {"net": Decimal("0"), "tax": Decimal("0"), "gross": Decimal("0")}
            self.sync_from_active()
        elif key == "±":
            self.values[self.active_key] = -self.values[self.active_key]
            self.input_buffer = self.formatter.format(self.values[self.active_key])
            self.sync_from_active()
        elif key in {"+", "-", "×", "÷"}:
            self.pending_value = self.values[self.active_key]
            self.pending_operator = key
            self.input_buffer = ""
        elif key == "=":
            self.calculate_pending()

    def calculate_pending(self):
        if self.pending_operator is None or self.pending_value is None:
            return
        current = self.values[self.active_key]
        if self.pending_operator == "+":
            result = self.pending_value + current
        elif self.pending_operator == "-":
            result = self.pending_value - current
        elif self.pending_operator == "×":
            result = self.pending_value * current
        else:
            result = Decimal("0") if current == 0 else self.pending_value / current
        self.values[self.active_key] = result
        self.pending_operator = None
        self.pending_value = None
        self.input_buffer = self.formatter.format(result)
        self.sync_from_active()

    def sync_from_active(self):
        rate = self.current_rate.rate / Decimal("100")
        if rate == 0:
            if self.active_key == "tax":
                self.values["net"] = Decimal("0")
                self.values["gross"] = self.values["tax"]
            else:
                source = self.values[self.active_key]
                self.values["net"] = source
                self.values["tax"] = Decimal("0")
                self.values["gross"] = source
        elif self.active_key == "net":
            self.values["tax"] = self.values["net"] * rate
            self.values["gross"] = self.values["net"] + self.values["tax"]
        elif self.active_key == "tax":
            self.values["net"] = self.values["tax"] / rate
            self.values["gross"] = self.values["net"] + self.values["tax"]
        elif self.active_key == "gross":
            self.values["net"] = self.values["gross"] / (Decimal("1") + rate)
            self.values["tax"] = self.values["gross"] - self.values["net"]
        self.refresh_displays()

    def refresh_displays(self):
        for key, panel in self.panels.items():
            panel.value.setText(self.formatter.format(self.values[key]))

    def select_country(self):
        rates = COUNTRY_RATES + [TaxRate(self.tr("Personalizado"), rate, "*", True) for rate in self.custom_rates]
        dialog = CountryDialog(rates, self)
        self.apply_dialog_window_theme(dialog)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected = dialog.selected_rate()
            if selected:
                self.current_rate = selected
                self.save_current_rate()
                self.update_header()
                self.sync_from_active()

    def manage_custom_rates(self):
        dialog = CustomRatesDialog(self.custom_rates.copy(), self)
        self.apply_dialog_window_theme(dialog)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.custom_rates = dialog.rates
            selected = dialog.selected_rate()
            if selected is not None:
                self.current_rate = TaxRate("Personalizado", selected, "*", True)
            self.save_custom_rates()
            self.save_current_rate()
            self.update_header()
            self.sync_from_active()

    def open_settings(self):
        dialog = SettingsDialog(
            self.formatter,
            self.theme_name,
            self.ui_size_name,
            self.font_family,
            self.language_code,
            self,
        )
        self.apply_dialog_window_theme(dialog)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            previous_language = self.language_code
            self.formatter = dialog.formatter()
            self.theme_name = combo_data(dialog.theme, "Rojo")
            self.ui_size_name = combo_data(dialog.ui_size, DEFAULT_UI_SIZE)
            self.font_family = combo_data(dialog.font_family, SYSTEM_FONT_SETTING)
            self.language_code = combo_data(dialog.language, DEFAULT_LANGUAGE_SETTING)
            self.save_settings()
            self.apply_app_font()
            self.apply_ui_size()
            self.apply_theme()
            self.refresh_displays()
            if self.language_code != previous_language:
                self.apply_default_rate_for_language()
                QMessageBox.information(
                    self,
                    self.tr("Idioma"),
                    self.tr("El idioma se aplicara al reiniciar la aplicacion."),
                )

    def open_about(self):
        dialog = AboutDialog(self.theme_name == "Oscuro", self.settings, self)
        self.apply_dialog_window_theme(dialog)
        dialog.exec()

    def open_help(self):
        dialog = HelpDialog(self.language_code, self.theme_name == "Oscuro", self)
        self.apply_dialog_window_theme(dialog)
        dialog.exec()

    def apply_default_rate_for_language(self):
        rate = rate_by_country_name(default_country_for_language(self.language_code))
        if rate is None:
            return
        self.current_rate = rate
        self.save_current_rate()
        self.update_header()
        self.sync_from_active()

    def update_header(self):
        self.country_button.setText(self.rate_display_name(self.current_rate))
        self.rate_button.setText(f"{self.current_rate.rate.normalize()} %")
        for button in self.findChildren(QPushButton, "rateKey"):
            button.setText(self.current_rate.flag or "%")

    def rate_display_name(self, rate: TaxRate) -> str:
        if rate.custom or rate.name in {"Personalizado", "Custom"}:
            return self.tr("Personalizado")
        return rate.name

    def load_custom_rates(self) -> list[Decimal]:
        raw = self.settings.value("custom_rates", "7.5,9.25,14.28,32.1")
        return sorted(dec(part) for part in str(raw).split(",") if part.strip())

    def save_custom_rates(self):
        self.settings.setValue("custom_rates", ",".join(str(rate) for rate in self.custom_rates))
        self.settings.sync()

    def save_current_rate(self):
        self.settings.setValue("rate_name", self.current_rate.name)
        self.settings.setValue("rate_value", str(self.current_rate.rate))
        self.settings.setValue("rate_flag", self.current_rate.flag)
        self.settings.setValue("rate_custom", "true" if self.current_rate.custom else "false")
        self.settings.sync()

    def save_settings(self):
        self.settings.setValue("decimals", self.formatter.decimals)
        self.settings.setValue("decimal_separator", self.formatter.decimal_separator)
        self.settings.setValue("thousands_separator", self.formatter.thousands_separator)
        self.settings.setValue("grouping", self.formatter.grouping)
        self.settings.setValue("show_decimals", "true" if self.formatter.show_decimals else "false")
        self.settings.setValue("theme", self.theme_name)
        self.settings.setValue("ui_size", self.ui_size_name)
        self.settings.setValue("font_family", self.font_family)
        self.settings.setValue("language", self.language_code)
        self.settings.sync()

    def apply_theme(self):
        color = THEMES[self.theme_name]
        dark_theme = self.theme_name == "Oscuro"
        set_windows_title_bar_dark(self, dark_theme)
        header_text = "#ffffff" if dark_theme else "#111111"
        display_title_color = "rgba(255,255,255,0.78)" if dark_theme else "rgba(0,0,0,0.62)"
        display_value_color = "rgba(255,255,255,0.94)" if dark_theme else "rgba(0,0,0,0.78)"
        panel_background = "#2f2f2f" if dark_theme else "rgba(255,255,255,0.16)"
        active_panel_background = "#383838" if dark_theme else "rgba(255,255,255,0.31)"
        panel_border = "#666666" if dark_theme else "rgba(255,255,255,0.28)"
        active_panel_border = "rgba(255,255,255,0.78)" if dark_theme else "rgba(255,255,255,0.72)"
        app_background = "#202124" if dark_theme else "#eeeeee"
        dialog_background = "#2b2b2b" if dark_theme else "#f7f7f7"
        dialog_text = "#f2f2f2" if dark_theme else "#202020"
        link_color = "#8ec5ff" if dark_theme else "#0b57d0"
        field_background = "#3a3a3a" if dark_theme else "#ffffff"
        field_border = "#5a5a5a" if dark_theme else "#b8b8b8"
        tab_background = "#242424" if dark_theme else "#eeeeee"
        tab_selected = "#464646" if dark_theme else "#ffffff"
        tab_text = "#bdbdbd" if dark_theme else dialog_text
        tab_selected_text = "#ffffff" if dark_theme else dialog_text
        tab_selected_border = "#e53935" if dark_theme else field_border
        button_background = "#3a3a3a" if dark_theme else "#f3f3f3"
        button_hover = "#4a4a4a" if dark_theme else "#e6e6e6"
        menu_background = "#2b2b2b" if dark_theme else "#ffffff"
        menu_selection = "#444444" if dark_theme else "#e8f0fe"
        preview_text = "#f7f7f7" if dark_theme else "rgba(0,0,0,0.75)"
        about_icon_background = "#333333" if dark_theme else "#f7f7f7"
        about_icon_border = "#555555" if dark_theme else "#dddddd"
        developer_card_background = "#333333" if dark_theme else "#ffffff"
        developer_card_border = "#555555" if dark_theme else "#dddddd"
        keypad_background = "#191919" if dark_theme else "#f7f7f7"
        number_key_background = "#323232" if dark_theme else "#ffffff"
        number_key_text = "#ffffff" if dark_theme else "#111111"
        operation_key_background = "#3d3d3d" if dark_theme else "#cfcfcf"
        operation_key_text = "#ffffff" if dark_theme else "#111111"
        key_hover_background = "#454545" if dark_theme else "#f5f5f5"
        operation_hover_background = "#4a4a4a" if dark_theme else "#d8d8d8"
        ui_font_family = css_font_family(effective_font_family(self.font_family))
        factor = self.ui_scale
        display_title_font = scaled(17, factor)
        display_value_font = scaled(36, factor)
        key_font = scaled(27, factor)
        danger_font = scaled(24, factor)
        header_font = scaled(18, factor)
        menu_font = scaled(25, factor)
        menu_item_font = scaled(15, factor)
        dialog_font = scaled(14, factor)
        list_font = scaled(15, factor)
        tab_font = scaled(14, factor)
        dialog_button_font = scaled(14, factor)
        dialog_title_font = scaled(24, factor)
        round_button_font = scaled(24, factor)
        round_button_size = scaled(36, factor)
        preview_font = scaled(34, factor)
        style = (
            f"""
            QApplication, QDialog, QMessageBox {{
                background: {dialog_background};
                color: {dialog_text};
                font-family: "{ui_font_family}";
                font-size: {dialog_font}px;
            }}
            QMainWindow {{
                background: {app_background};
                color: {dialog_text};
            }}
            QLabel, QCheckBox, QRadioButton, QGroupBox {{
                color: {dialog_text};
                font-size: {dialog_font}px;
            }}
            QTabWidget::pane {{
                border: 1px solid {field_border};
                background: {dialog_background};
                top: -1px;
            }}
            QTabBar::tab {{
                background: {tab_background};
                color: {tab_text};
                border: 1px solid {field_border};
                border-bottom-color: {field_border};
                font-size: {tab_font}px;
                padding: {scaled(8, factor)}px {scaled(12, factor)}px;
            }}
            QTabBar::tab:selected {{
                background: {tab_selected};
                color: {tab_selected_text};
                border-top: 3px solid {tab_selected_border};
                border-bottom-color: {tab_selected};
                font-weight: 700;
            }}
            QTabBar::tab:!selected {{
                margin-top: {scaled(3, factor)}px;
            }}
            QTabBar::tab:hover {{
                background: {button_hover};
                color: {tab_selected_text};
            }}
            QComboBox, QSpinBox, QLineEdit, QTextEdit, QTextBrowser, QListWidget {{
                background: {field_background};
                color: {dialog_text};
                border: 1px solid {field_border};
                font-size: {dialog_font}px;
                selection-background-color: {menu_selection};
                selection-color: {dialog_text};
            }}
            QListWidget {{
                font-size: {list_font}px;
            }}
            QComboBox {{
                padding: {scaled(3, factor)}px {scaled(6, factor)}px;
            }}
            QComboBox::drop-down {{
                border-left: 1px solid {field_border};
            }}
            QPushButton {{
                background: {button_background};
                color: {dialog_text};
                border: 1px solid {field_border};
                font-size: {dialog_button_font}px;
                padding: {scaled(6, factor)}px {scaled(14, factor)}px;
            }}
            QPushButton:hover {{
                background: {button_hover};
            }}
            QMenu {{
                background: {menu_background};
                color: {dialog_text};
                border: 1px solid {field_border};
                font-size: {menu_item_font}px;
            }}
            QMenu::item {{
                padding: {scaled(8, factor)}px {scaled(28, factor)}px {scaled(8, factor)}px {scaled(18, factor)}px;
            }}
            QMenu::item:selected {{
                background: {menu_selection};
            }}
            #toolbar {{
                background: {color};
            }}
            #displayArea {{
                background: {color};
            }}
            #displayPanel {{
                background: {panel_background};
                border: 1px solid {panel_border};
                border-radius: 6px;
            }}
            #displayPanel[active="true"] {{
                background: {active_panel_background};
                border: 2px solid {active_panel_border};
            }}
            #displayTitle {{
                color: {display_title_color};
                font: 700 {display_title_font}px "Consolas";
                letter-spacing: 0;
            }}
            #displayValue {{
                color: {display_value_color};
                font: 600 {display_value_font}px "Segoe UI";
            }}
            #keypad {{
                background: {keypad_background};
            }}
            #keyButton, #operationButton, #rateKey {{
                background: {number_key_background};
                border: none;
                border-radius: 3px;
                color: {number_key_text};
                font-size: {key_font}px;
            }}
            #keyButton:hover {{
                background: {key_hover_background};
            }}
            #operationButton, #rateKey {{
                background: {operation_key_background};
                color: {operation_key_text};
            }}
            #operationButton:hover, #rateKey:hover {{
                background: {operation_hover_background};
            }}
            #dangerButton {{
                background: #e53935;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: {danger_font}px;
                font-weight: 700;
            }}
            #countryButton, #rateButton {{
                background: transparent;
                border: none;
                color: {header_text};
                font-size: {header_font}px;
                font-weight: 700;
            }}
            QToolButton {{
                background: transparent;
                border: none;
                color: {header_text};
                font-size: {menu_font}px;
                padding: {scaled(2, factor)}px {scaled(8, factor)}px;
            }}
            #dialogTitle {{
                font-size: {dialog_title_font}px;
                font-weight: 700;
                padding: 6px;
            }}
            #roundButton {{
                background: #2196f3;
                color: white;
                border-radius: 18px;
                font-size: {round_button_font}px;
                min-width: {round_button_size}px;
                min-height: {round_button_size}px;
            }}
            #preview {{
                font-size: {preview_font}px;
                color: {preview_text};
                border-radius: 2px;
            }}
            #aboutIcon {{
                background: {about_icon_background};
                border: 1px solid {about_icon_border};
                border-radius: 8px;
                padding: 16px;
            }}
            #aboutAppTitle {{
                color: {dialog_text};
                font-size: {scaled(18, factor)}px;
                font-weight: 700;
            }}
            #developerCard {{
                background: {developer_card_background};
                border: 1px solid {developer_card_border};
                border-radius: 8px;
            }}
            #developerPhoto {{
                border: 2px solid {developer_card_border};
                border-radius: 12px;
            }}
            #aboutText {{
                color: {dialog_text};
                font-size: {scaled(14, factor)}px;
                line-height: 1.35;
            }}
            #aboutText a {{
                color: {link_color};
            }}
            """
        )
        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(style)
        self.setStyleSheet(style)

    def apply_dialog_window_theme(self, dialog: QDialog):
        set_windows_title_bar_dark(dialog, self.theme_name == "Oscuro")

    def closeEvent(self, event):  # noqa: N802
        self.save_window_geometry()
        super().closeEvent(event)


def main() -> int:
    if "--pyinstaller-test" in sys.argv:
        return 0
    QApplication.setOrganizationName(APP_ORG)
    QApplication.setApplicationName(APP_NAME)
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(app_icon_path())))
    settings = app_settings()
    translator = load_translation(app, settings.value("language", DEFAULT_LANGUAGE_SETTING))
    window = CalculatorWindow()
    window.translator = translator
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
