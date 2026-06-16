# ROADMAP

## Source Language Migration: Spanish to English

- [x] Create a migration roadmap with tracked progress.
- [x] Audit where Spanish is currently used as the source language in code, translations, docs, and persisted values.
- [x] Migrate the PyQt6 source strings in `main.py` from Spanish to English.
- [x] Change the application base language and default language behavior to English.
- [x] Keep existing Spanish UI available through translations.
- [x] Review persisted configuration values that currently depend on Spanish labels and make them backward compatible.
- [x] Review country and rate labels so the internal model remains stable while the UI becomes English-first.
- [x] Review local help content and decide whether English becomes the source version there as well.
- [x] Rebuild or realign translation files after the source-language migration.
- [x] Run verification passes and update this roadmap with what was completed.
