"""
Script: 34_dataset_registry.py

Crea un registry operativo dei dataset a partire da fonti configurate, discovery e validazione.
"""

import pandas as pd

from utils_paths import get_configured_path, ensure_project_folders


def read_if_exists(path):
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def main():
    ensure_project_folders()
    catalog = read_if_exists(get_configured_path("data_catalog"))
    validated = read_if_exists(get_configured_path("outputs_tables") / "validated_discovered_links.csv")
    output_path = get_configured_path("outputs_tables") / "dataset_registry.csv"
    if validated.empty:
        registry = catalog.copy()
        registry["candidate_url"] = ""
        registry["is_data_file"] = False
    else:
        registry = validated.copy()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    registry.to_csv(output_path, index=False)
    print(f"Dataset registry written to {output_path}")


if __name__ == "__main__":
    main()
