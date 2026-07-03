"""
Script: 40_readme_outputs.py

Crea un breve riepilogo degli output generati dalla pipeline.
"""

from pathlib import Path
import pandas as pd

from utils_paths import get_configured_path, ensure_project_folders


def main():
    ensure_project_folders()
    output_root = get_configured_path("outputs_tables")
    rows = []
    for file_path in Path(output_root).glob("*.csv"):
        rows.append({"output_file": file_path.name, "path": str(file_path)})
    summary_path = output_root / "outputs_summary.csv"
    pd.DataFrame(rows).to_csv(summary_path, index=False)
    print(f"Outputs summary written to {summary_path}")


if __name__ == "__main__":
    main()
