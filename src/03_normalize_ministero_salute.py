"""
Script: 03_normalize_ministero_salute.py

Obiettivo
Normalizzare i file grezzi del Ministero presenti in data/raw e salvare versioni
pulite in data/processed.
"""

from pathlib import Path

from utils_paths import get_configured_path, ensure_project_folders, load_project_config
from utils_io import read_table, write_table, write_csv_json_pair
from utils_cleaning import normalize_table


SUPPORTED_INPUTS = [".csv", ".json", ".xlsx", ".xls", ".parquet"]


def find_raw_files(raw_folder):
    files = []
    for path in Path(raw_folder).rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_INPUTS:
            files.append(path)
    return files


def normalize_file(input_path, raw_root, processed_root, export_parquet=False):
    df = read_table(input_path)
    df = normalize_table(df)
    relative_path = input_path.relative_to(raw_root)
    output_base = processed_root / relative_path.with_suffix("")
    write_csv_json_pair(df, output_base.parent, output_base.name)
    if export_parquet:
        write_table(df, output_base.with_suffix(".parquet"))
    return output_base


def main():
    ensure_project_folders()
    config = load_project_config()
    export_parquet = bool(getattr(config, "ANALYSIS_SETTINGS", {}).get("export_parquet", False))
    raw_root = get_configured_path("data_raw") / "ministero_salute"
    processed_root = get_configured_path("data_processed") / "ministero_salute"
    files = find_raw_files(raw_root)
    for input_path in files:
        normalize_file(input_path, raw_root, processed_root, export_parquet=export_parquet)
    print(f"Normalized {len(files)} Ministry files")


if __name__ == "__main__":
    main()
