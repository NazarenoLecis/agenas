"""
Script: 31_build_dimensions.py

Crea tabelle dimensionali vuote o derivate dai dataset processati.
"""

import pandas as pd

from utils_paths import get_configured_path, ensure_project_folders


DIMENSIONS = {
    "dim_region": ["region_code", "region_name"],
    "dim_asl": ["asl_code", "asl_name", "region_code"],
    "dim_structure": ["structure_code", "structure_name", "asl_code", "region_code"],
    "dim_service": ["service_code", "service_name"],
    "dim_profession": ["profession_code", "profession_name"],
    "dim_source": ["source_id", "provider", "dataset_name", "license"],
}


def main():
    ensure_project_folders()
    tables_root = get_configured_path("outputs_tables")
    tables_root.mkdir(parents=True, exist_ok=True)
    for name, columns in DIMENSIONS.items():
        pd.DataFrame(columns=columns).to_csv(tables_root / f"{name}.csv", index=False)
    print("Dimension table templates written")


if __name__ == "__main__":
    main()
