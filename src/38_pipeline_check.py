"""
Script: 38_pipeline_check.py

Controlla che i file principali della pipeline esistano.
"""

from pathlib import Path
import pandas as pd

from utils_paths import get_project_root, get_configured_path, ensure_project_folders


EXPECTED_FILES = [
    "README.md",
    "config/project_config.py",
    "src/00_discover_sources.py",
    "src/20_run_all.py",
    "src/23_source_audit.py",
    "src/24_discover_ministero_salute_catalog.py",
    "src/25_build_duckdb.py",
    "src/31_build_dimensions.py",
]


def main():
    ensure_project_folders()
    root = get_project_root()
    rows = []
    for relative_path in EXPECTED_FILES:
        rows.append({"path": relative_path, "exists": (root / relative_path).exists()})
    output_path = get_configured_path("outputs_tables") / "pipeline_check.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output_path, index=False)
    print(f"Pipeline check written to {output_path}")


if __name__ == "__main__":
    main()
