"""
Script: 15_build_catalogs.py

Obiettivo
Ricostruire i cataloghi CSV e JSON a partire da config/project_config.py.

Questo evita divergenze tra configurazione Python e file in data_catalog.
"""

import pandas as pd

from utils_paths import get_configured_path, load_project_config, ensure_project_folders
from utils_catalog import sources_to_catalog
from utils_io import write_csv_json_pair


def build_analysis_modules_table(modules):
    return pd.DataFrame(modules)


def main():
    ensure_project_folders()
    config = load_project_config()
    sources = sources_to_catalog(config.SOURCES)
    modules = build_analysis_modules_table(config.ANALYSIS_MODULES)
    catalog_path = get_configured_path("data_catalog")
    modules_path = get_configured_path("analysis_modules")
    write_csv_json_pair(sources, catalog_path.parent, catalog_path.stem)
    write_csv_json_pair(modules, modules_path.parent, modules_path.stem)
    print(f"Source catalog written to {catalog_path} and {catalog_path.with_suffix('.json')}")
    print(f"Analysis modules written to {modules_path} and {modules_path.with_suffix('.json')}")


if __name__ == "__main__":
    main()
