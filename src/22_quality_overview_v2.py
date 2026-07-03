"""
Script: 22_quality_overview_v2.py

Costruisce un riepilogo qualita sui dataset processati.
"""

from pathlib import Path
import pandas as pd

from utils_paths import get_configured_path, ensure_project_folders
from utils_io import read_table
from utils_quality import run_basic_quality_checks


def main():
    ensure_project_folders()
    processed_root = get_configured_path("data_processed")
    tables_root = get_configured_path("outputs_tables")
    tables_root.mkdir(parents=True, exist_ok=True)
    rows = []
    for file_path in Path(processed_root).rglob("*"):
        if file_path.suffix.lower() not in [".csv", ".json", ".parquet"]:
            continue
        try:
            df = read_table(file_path)
            checks = run_basic_quality_checks(df)
            for check in checks:
                check["dataset_path"] = str(file_path.relative_to(processed_root))
                rows.append(check)
        except Exception as error:
            rows.append({"dataset_path": str(file_path), "check_name": "read_error", "passed": False, "value": "", "message": str(error)})
    pd.DataFrame(rows).to_csv(tables_root / "quality_overview.csv", index=False)
    print("Quality overview completed")


if __name__ == "__main__":
    main()
