import unittest
from pathlib import Path

from main import AppSettings, default_country_for_language, rate_by_country_name, settings_bool


class AppSettingsTest(unittest.TestCase):
    def test_writes_and_reads_ini_file(self):
        settings_path = Path(__file__).parent / "tmp" / "Lucio" / "IVA Calculator.ini"
        settings = AppSettings(settings_path)
        settings.setValue("theme", "Azul")
        settings.setValue("ui_size", "Pequeno")
        settings.setValue("show_decimals", "true")
        settings.sync()

        loaded = AppSettings(settings_path)

        self.assertEqual(loaded.value("theme"), "Azul")
        self.assertEqual(loaded.value("ui_size"), "Pequeno")
        self.assertTrue(settings_bool(loaded.value("show_decimals")))

    def test_bool_parser_accepts_common_values(self):
        self.assertTrue(settings_bool("true"))
        self.assertTrue(settings_bool("1"))
        self.assertFalse(settings_bool("false"))
        self.assertFalse(settings_bool(None))

    def test_language_default_country_mapping(self):
        self.assertEqual(default_country_for_language("de"), "Alemania")
        self.assertEqual(default_country_for_language("pt"), "Portugal")
        self.assertEqual(rate_by_country_name("Alemania").rate, 19)


if __name__ == "__main__":
    unittest.main()
