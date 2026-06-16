import unittest
from pathlib import Path

from main import (
    AppSettings,
    app_icon_path,
    canonical_country_name,
    canonical_theme_name,
    canonical_ui_size_name,
    default_country_for_language,
    rate_by_country_name,
    resource_path,
    settings_bool,
)


class AppSettingsTest(unittest.TestCase):
    def test_writes_and_reads_ini_file(self):
        settings_path = Path(__file__).parent / "tmp" / "Lucio" / "IVA Calculator.ini"
        settings = AppSettings(settings_path)
        settings.setValue("theme", "Blue")
        settings.setValue("ui_size", "Small")
        settings.setValue("show_decimals", "true")
        settings.sync()

        loaded = AppSettings(settings_path)

        self.assertEqual(loaded.value("theme"), "Blue")
        self.assertEqual(loaded.value("ui_size"), "Small")
        self.assertTrue(settings_bool(loaded.value("show_decimals")))

    def test_bool_parser_accepts_common_values(self):
        self.assertTrue(settings_bool("true"))
        self.assertTrue(settings_bool("1"))
        self.assertFalse(settings_bool("false"))
        self.assertFalse(settings_bool(None))

    def test_language_default_country_mapping(self):
        self.assertEqual(default_country_for_language("de"), "Germany")
        self.assertEqual(default_country_for_language("pt"), "Portugal")
        self.assertEqual(rate_by_country_name("Germany").rate, 19)
        self.assertEqual(rate_by_country_name("Alemania").rate, 19)

    def test_legacy_saved_values_remain_supported(self):
        self.assertEqual(canonical_theme_name("Azul"), "Blue")
        self.assertEqual(canonical_ui_size_name("Pequeno"), "Small")
        self.assertEqual(canonical_country_name("Estados Unidos"), "United States")

    def test_geometry_values_round_trip(self):
        settings_path = Path(__file__).parent / "tmp" / "Lucio" / "Geometry.ini"
        settings = AppSettings(settings_path)
        settings.setValue("window_x", 120)
        settings.setValue("window_y", 80)
        settings.setValue("window_width", 360)
        settings.setValue("window_height", 640)
        settings.sync()

        loaded = AppSettings(settings_path)

        self.assertEqual(int(loaded.value("window_x")), 120)
        self.assertEqual(int(loaded.value("window_y")), 80)
        self.assertEqual(int(loaded.value("window_width")), 360)
        self.assertEqual(int(loaded.value("window_height")), 640)

    def test_resource_path_resolves_project_resources(self):
        icon_path = resource_path("assets", "app-icon.svg")
        self.assertTrue(icon_path.exists())
        self.assertEqual(icon_path, app_icon_path())


if __name__ == "__main__":
    unittest.main()
