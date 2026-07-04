"""
Script: 22_quality_overview_v2.py

Costruisce un riepilogo qualita sui dataset processati.
"""

from pathlib import Path
import pandas as pd

from utils_paths import get_configured_path, ensure_project_folders
from utils_io import read_table, write_csv_json_pair
from utils_quality import run_basic_quality_checks


SUPPORTED_INPUTS = [".csv", ".json", ".parquet"]


def iter_processed_files(processed_root):
    for file_path in Path(processed_root).rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() in SUPPORTED_INPUTS:
            yield file_path


def add_csv_json_pair_checks(processed_root, rows):
    stems = {}
    for file_path in iter_processed_files(processed_root):
        key = str(file_path.with_suffix("").relative_to(processed_root))
        stems.setdefault(key, set()).add(file_path.suffix.lower())
    for key, suffixes in sorted(stems.items()):
        if ".csv" in suffixes or ".json" in suffixes:
            rows.append({
                "dataset_path": key,
                "check_name": "csv_json_pair",
                "passed": ".csv" in suffixes and ".json" in suffixes,
                "value": ";".join(sorted(suffixes)),
                "message": "ok" if ".csv" in suffixes and ".json" in suffixes else "missing_csv_or_json",
            })


def main():
    ensure_project_folders()
    processed_root = get_configured_path("data_processed")
    tables_root = get_configured_path("outputs_tables")
    rows = []
    for file_path in iter_processed_files(processed_root):
        try:
            df = read_table(file_path)
            checks = run_basic_quality_checks(df)
            for check in checks:
                check["dataset_path"] = str(file_path.relative_to(processed_root))
                rows.append(check)
        except Exception as error:
            rows.append({"dataset_path": str(file_path), "check_name": "read_error", "passed": False, "value": "", "message": str(error)})
    add_csv_json_pair_checks(processed_root, rows)
    output_path = tables_root / "quality_overview.csv"
    write_csv_json_pair(pd.DataFrame(rows), output_path.parent, output_path.stem)
    print("Quality overview completed")


if __name__ == "__main__":
    main()
