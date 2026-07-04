"""
Script: 34_dataset_registry.py

Crea un registry operativo dei dataset a partire da fonti configurate, discovery
e validazione.
"""

import pandas as pd

from utils_paths import get_configured_path, ensure_project_folders
from utils_io import write_csv_json_pair


def read_if_exists(path):
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def build_registry(catalog, validated):
    if catalog.empty and validated.empty:
        return pd.DataFrame()
    if validated.empty:
        registry = catalog.copy()
        registry["candidate_url"] = ""
        registry["final_url"] = ""
        registry["is_data_file"] = False
        registry["is_report_file"] = False
        registry["validation_status_code"] = ""
        return registry

    registry = validated.copy()
    registry = registry.rename(columns={"found_url": "candidate_url"})
    if not catalog.empty and "source_id" in catalog.columns and "source_id" in registry.columns:
        source_columns = [column for column in catalog.columns if column not in registry.columns or column == "source_id"]
        registry = registry.merge(catalog[source_columns], on="source_id", how="left", suffixes=("", "_catalog"))
    return registry


def main():
    ensure_project_folders()
    catalog = read_if_exists(get_configured_path("data_catalog"))
    validated = read_if_exists(get_configured_path("outputs_tables") / "validated_discovered_links.csv")
    output_path = get_configured_path("outputs_tables") / "dataset_registry.csv"
    registry = build_registry(catalog, validated)
    write_csv_json_pair(registry, output_path.parent, output_path.stem)
    print(f"Dataset registry written to {output_path}")


if __name__ == "__main__":
    main()
