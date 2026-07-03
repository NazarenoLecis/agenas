"""
Script: 04_normalize_Agenas.py

Obiettivo
Normalizzare i file Agenas scaricati in data/raw e salvare versioni pulite in
data/processed.

Uso
Eseguire python src/04_normalize_Agenas.py dopo il download.
"""

from pathlib import Path

from utils_paths import get_configured_path, ensure_project_folders
from utils_io import read_table, write_table
from utils_cleaning import normalize_table


SUPPORTED_INPUTS = [".csv", ".json", ".xlsx", ".xls", ".parquet"]


def find_raw_files(raw_folder):
    files = []
    for path in Path(raw_folder).rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_INPUTS:
            files.append(path)
    return files


def normalize_file(input_path, raw_root, processed_root):
    df = read_table(input_path)
    df = normalize_table(df)
    relative_path = input_path.relative_to(raw_root)
    output_base = processed_root / relative_path.with_suffix("")
    write_table(df, output_base.with_suffix(".csv"))
    write_table(df, output_base.with_suffix(".json"))
    write_table(df, output_base.with_suffix(".parquet"))
    return output_base


def main():
    ensure_project_folders()
    raw_root = get_configured_path("data_raw") / "Agenas"
    processed_root = get_configured_path("data_processed") / "Agenas"
    files = find_raw_files(raw_root)
    for input_path in files:
        normalize_file(input_path, raw_root, processed_root)
    print(f"Normalized {len(files)} Agenas files")


if __name__ == "__main__":
    main()
