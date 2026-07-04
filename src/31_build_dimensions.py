"""
Script: 31_build_dimensions.py

Crea tabelle dimensionali vuote o derivate dai dataset processati.
"""

import pandas as pd

from utils_paths import get_configured_path, ensure_project_folders
from utils_io import write_csv_json_pair


DIMENSIONS = {
    "dim_region": ["region_code", "region_name"],
    "dim_asl": ["asl_code", "asl_name", "region_code"],
    "dim_structure": ["structure_code", "structure_name", "asl_code", "region_code"],
    "dim_service": ["service_code", "service_name"],
    "dim_profession": ["profession_code", "profession_name"],
    "dim_source": ["source_id", "provider", "dataset_name", "license"],
    "dim_demographic_denominator": ["denominator_id", "description", "preferred_use"],
    "dim_accounting_basis": ["accounting_basis", "description"],
}

ACCOUNTING_BASIS_ROWS = [
    {"accounting_basis": "competenza_ce", "description": "Costi e ricavi di competenza da Conto Economico"},
    {"accounting_basis": "cassa_siope", "description": "Incassi e pagamenti di cassa da SIOPE"},
]


def build_dimension(name, columns):
    if name == "dim_accounting_basis":
        return pd.DataFrame(ACCOUNTING_BASIS_ROWS, columns=columns)
    return pd.DataFrame(columns=columns)


def main():
    ensure_project_folders()
    tables_root = get_configured_path("outputs_tables")
    for name, columns in DIMENSIONS.items():
        write_csv_json_pair(build_dimension(name, columns), tables_root, name)
    print("Dimension table templates written")


if __name__ == "__main__":
    main()
