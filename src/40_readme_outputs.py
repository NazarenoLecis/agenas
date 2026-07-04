"""
Script: 40_readme_outputs.py

Crea un breve riepilogo degli output generati dalla pipeline.
"""

from pathlib import Path
import pandas as pd

from utils_paths import get_configured_path, ensure_project_folders
from utils_io import write_csv_json_pair


def main():
    ensure_project_folders()
    output_root = get_configured_path("outputs_tables")
    rows = []
    for file_path in sorted(Path(output_root).glob("*")):
        if file_path.suffix.lower() not in [".csv", ".json"]:
            continue
        rows.append({"output_file": file_path.name, "path": str(file_path), "format": file_path.suffix.lower().replace(".", "")})
    summary_path = output_root / "outputs_summary.csv"
    write_csv_json_pair(pd.DataFrame(rows), summary_path.parent, summary_path.stem)
    print(f"Outputs summary written to {summary_path}")


if __name__ == "__main__":
    main()
