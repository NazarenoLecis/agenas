"""
Script: 38_pipeline_check.py

Controlla che i file principali della pipeline esistano.
"""

from pathlib import Path
import pandas as pd

from utils_paths import get_project_root, get_configured_path, ensure_project_folders
from utils_io import write_csv_json_pair


EXPECTED_FILES = [
    "README.md",
    "requirements.txt",
    "config/project_config.py",
    "config/health_expenditure_config.py",
    "src/00_discover_sources.py",
    "src/20_run_all.py",
    "src/23_source_audit.py",
    "src/24_discover_ministero_salute_catalog.py",
    "src/25_build_duckdb.py",
    "src/31_build_dimensions.py",
    "src/52_build_health_expenditure_framework.py",
]

EXPECTED_OUTPUT_PAIRS = [
    "data_catalog/data_catalog",
    "data_catalog/analysis_modules",
    "data_catalog/discovered_links",
    "outputs/tables/dataset_registry",
    "outputs/tables/source_ranking",
    "outputs/tables/quality_overview",
    "outputs/tables/regional_health_expenditure_demographic_adjusted",
]


def check_expected_files(root):
    rows = []
    for relative_path in EXPECTED_FILES:
        rows.append({"check_type": "file_exists", "path": relative_path, "exists": (root / relative_path).exists(), "passed": (root / relative_path).exists()})
    return rows


def check_output_pairs(root):
    rows = []
    for relative_stem in EXPECTED_OUTPUT_PAIRS:
        csv_path = root / f"{relative_stem}.csv"
        json_path = root / f"{relative_stem}.json"
        passed = csv_path.exists() == json_path.exists()
        rows.append({
            "check_type": "csv_json_pair",
            "path": relative_stem,
            "exists": csv_path.exists() or json_path.exists(),
            "csv_exists": csv_path.exists(),
            "json_exists": json_path.exists(),
            "passed": passed,
        })
    return rows


def main():
    ensure_project_folders()
    root = get_project_root()
    rows = check_expected_files(root) + check_output_pairs(root)
    output_path = get_configured_path("outputs_tables") / "pipeline_check.csv"
    write_csv_json_pair(pd.DataFrame(rows), output_path.parent, output_path.stem)
    print(f"Pipeline check written to {output_path}")


if __name__ == "__main__":
    main()
