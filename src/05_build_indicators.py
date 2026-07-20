"""
Script: 05_build_indicators.py

Obiettivo
Creare indicatori iniziali e tabelle di sintesi dai file puliti presenti in
data/processed.

Questa prima versione produce un inventario dei dataset processati. Gli
indicatori sanitari specifici vanno aggiunti quando i dataset ufficiali sono
abilitati nella configurazione Python.
"""

from pathlib import Path
import pandas as pd

from utils_paths import get_configured_path, ensure_project_folders
from utils_io import read_table, write_table


SUPPORTED_INPUTS = [".csv", ".json", ".parquet"]
INVENTORY_COLUMNS = ["dataset_path", "file_format", "rows", "columns", "column_names", "error"]


def find_processed_files(processed_folder):
    files = []
    for path in Path(processed_folder).rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_INPUTS:
            files.append(path)
    return files


def build_dataset_inventory(files, processed_root):
    rows = []
    for path in files:
        try:
            df = read_table(path)
            rows.append({
                "dataset_path": str(path.relative_to(processed_root)),
                "file_format": path.suffix.lower().replace(".", ""),
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": ";".join(df.columns.astype(str)),
                "error": "",
            })
        except Exception as error:
            rows.append({
                "dataset_path": str(path.relative_to(processed_root)),
                "file_format": path.suffix.lower().replace(".", ""),
                "rows": None,
                "columns": None,
                "column_names": "",
                "error": str(error),
            })
    return pd.DataFrame(rows, columns=INVENTORY_COLUMNS)


def main():
    ensure_project_folders()
    processed_root = get_configured_path("data_processed")
    tables_root = get_configured_path("outputs_tables")
    files = find_processed_files(processed_root)
    inventory = build_dataset_inventory(files, processed_root)
    write_table(inventory, tables_root / "processed_dataset_inventory.csv")
    write_table(inventory, tables_root / "processed_dataset_inventory.json")
    print(f"Indicator inventory written for {len(files)} files")


if __name__ == "__main__":
    main()
