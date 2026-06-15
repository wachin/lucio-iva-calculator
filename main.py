from __future__ import annotations

import os
import sys
from configparser import ConfigParser
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

from PyQt6.QtCore import QEvent, Qt, QLocale, QSettings, QSize, QTranslator
from PyQt6.QtGui import QAction, QFont, QIcon, QKeySequence, QPixmap
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
    QVBoxLayout,
    QWidget,
)


APP_ORG = "Lucio"
APP_NAME = "IVA Calculator"
CONFIG_FILE_NAME = "IVA Calculator.ini"
APP_EXECUTABLE_NAME = "LucioIVACalculator"
DEFAULT_LANGUAGE = "es"
DEFAULT_LANGUAGE_SETTING = "system"
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


def scaled(value: int | float, factor: float) -> int:
    return max(1, round(value * factor))


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


def translations_dir() -> Path:
    return application_root() / "translations"


def app_icon_path() -> Path:
    return application_root() / "assets" / "app-icon.svg"


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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Acerca de..."))
        self.setWindowIcon(QIcon(str(app_icon_path())))
        self.setMinimumSize(620, 380)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

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

        text = QLabel()
        text.setObjectName("aboutText")
        text.setTextFormat(Qt.TextFormat.RichText)
        text.setOpenExternalLinks(True)
        text.setWordWrap(True)
        text.setText(
            self.tr(
                "<h2>Calculadora de IVA</h2>"
                "<p><b>Desarrolladores</b></p>"
                "<p>© 2026 Washington Indacochea Delgado<br>"
                '<a href="mailto:linuxfrontier@proton.me">linuxfrontier@proton.me</a></p>'
                "<p>© 2026 Joseph Lucio Guerrero<br>"
                '<a href="mailto:josephsteveng@gmail.com">josephsteveng@gmail.com</a></p>'
                "<p><b>Licencia</b><br>GNU GPL v3</p>"
                "<p><b>Tecnologías usadas</b><br>Python, PyQt6, Qt Linguist, QtSvg</p>"
                "<p>Calculadora de IVA de escritorio con tasas por país, tasas personalizadas, "
                "formatos numéricos, temas, tamaños de interfaz e internacionalización.</p>"
                '<p><b>Sitio web</b><br><a href="https://wachin.github.io/lucio-iva-calculator/">'
                "https://wachin.github.io/lucio-iva-calculator/</a></p>"
                "<p>Jipijapa, Manabí, Ecuador</p>"
            )
        )

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)

        right = QVBoxLayout()
        right.addWidget(text, 1)
        right.addWidget(buttons)

        layout.addWidget(icon_label)
        layout.addLayout(right, 1)


class SettingsDialog(QDialog):
    def __init__(
        self,
        formatter: NumberFormatter,
        theme_name: str,
        ui_size_name: str,
        language_code: str,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Configuracion"))
        self.setMinimumSize(430, 520)
        layout = QVBoxLayout(self)
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
        layout.addLayout(form)
        layout.addWidget(QLabel(self.tr("Vista previa")))
        layout.addWidget(self.preview)
        layout.addStretch()
        layout.addWidget(buttons)
        self.update_preview()

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
        self.preview.setText(formatter.format(Decimal("1234567890.12")))
        self.preview.setStyleSheet(f"background:{THEMES[combo_data(self.theme, 'Rojo')]};")


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
        self.setWindowTitle(self.tr("Calculadora de IVA"))
        self.setWindowIcon(QIcon(str(app_icon_path())))
        self.build_ui()
        QApplication.instance().installEventFilter(self)
        self.apply_ui_size(resize_window=False)
        self.apply_theme()
        self.resize_to_available_screen()
        if should_apply_language_rate:
            self.apply_default_rate_for_language()
        self.sync_from_active()

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
        menu.addAction(select_country_action)
        menu.addAction(custom_rates_action)
        menu.addAction(settings_action)
        menu.addSeparator()
        about_action = QAction(self.tr("Acerca de..."), self, triggered=self.open_about)
        about_action.setShortcut(QKeySequence("F1"))
        menu.addAction(about_action)
        self.addActions([select_country_action, custom_rates_action, settings_action, about_action])
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
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected = dialog.selected_rate()
            if selected:
                self.current_rate = selected
                self.save_current_rate()
                self.update_header()
                self.sync_from_active()

    def manage_custom_rates(self):
        dialog = CustomRatesDialog(self.custom_rates.copy(), self)
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
        dialog = SettingsDialog(self.formatter, self.theme_name, self.ui_size_name, self.language_code, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            previous_language = self.language_code
            self.formatter = dialog.formatter()
            self.theme_name = combo_data(dialog.theme, "Rojo")
            self.ui_size_name = combo_data(dialog.ui_size, DEFAULT_UI_SIZE)
            self.language_code = combo_data(dialog.language, DEFAULT_LANGUAGE_SETTING)
            self.save_settings()
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
        dialog = AboutDialog(self)
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
        self.settings.setValue("language", self.language_code)
        self.settings.sync()

    def apply_theme(self):
        color = THEMES[self.theme_name]
        factor = self.ui_scale
        display_title_font = scaled(12, factor)
        display_value_font = scaled(36, factor)
        key_font = scaled(27, factor)
        danger_font = scaled(24, factor)
        header_font = scaled(18, factor)
        menu_font = scaled(25, factor)
        dialog_title_font = scaled(24, factor)
        round_button_font = scaled(24, factor)
        round_button_size = scaled(36, factor)
        preview_font = scaled(34, factor)
        self.setStyleSheet(
            f"""
            QMainWindow {{
                background: #eeeeee;
            }}
            #toolbar {{
                background: {color};
            }}
            #displayArea {{
                background: {color};
            }}
            #displayPanel {{
                background: rgba(255,255,255,0.16);
                border: 1px solid rgba(255,255,255,0.28);
                border-radius: 6px;
            }}
            #displayPanel[active="true"] {{
                background: rgba(255,255,255,0.31);
                border: 2px solid rgba(255,255,255,0.72);
            }}
            #displayTitle {{
                color: rgba(0,0,0,0.62);
                font: 700 {display_title_font}px "Consolas";
                letter-spacing: 0;
            }}
            #displayValue {{
                color: rgba(0,0,0,0.78);
                font: 300 {display_value_font}px "Segoe UI";
            }}
            #keypad {{
                background: #f7f7f7;
            }}
            #keyButton, #operationButton, #rateKey {{
                background: #ffffff;
                border: none;
                border-radius: 3px;
                color: #111111;
                font-size: {key_font}px;
            }}
            #operationButton, #rateKey {{
                background: #cfcfcf;
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
                color: #111111;
                font-size: {header_font}px;
                font-weight: 700;
            }}
            QToolButton {{
                background: transparent;
                border: none;
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
                color: rgba(0,0,0,0.75);
                border-radius: 2px;
            }}
            #aboutIcon {{
                background: #f7f7f7;
                border: 1px solid #dddddd;
                border-radius: 8px;
                padding: 16px;
            }}
            #aboutText {{
                color: #202020;
                font-size: 13px;
                line-height: 1.35;
            }}
            """
        )


def main() -> int:
    if "--pyinstaller-test" in sys.argv:
        return 0
    QApplication.setOrganizationName(APP_ORG)
    QApplication.setApplicationName(APP_NAME)
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    app.setWindowIcon(QIcon(str(app_icon_path())))
    settings = app_settings()
    translator = load_translation(app, settings.value("language", DEFAULT_LANGUAGE_SETTING))
    window = CalculatorWindow()
    window.translator = translator
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
