"""
Script: 39_publication_rules.py

Definisce regole minime per pubblicare output aggregati.
"""

import pandas as pd

from utils_paths import get_configured_path, ensure_project_folders
from utils_io import write_csv_json_pair


RULES = [
    {"output_type": "cell_count", "minimum_value": 5, "rule": "do_not_publish_small_cells"},
    {"output_type": "regional_indicator", "minimum_value": 1, "rule": "ok_if_aggregated"},
    {"output_type": "structure_indicator", "minimum_value": 5, "rule": "review_if_low_volume"},
    {"output_type": "public_table_format", "minimum_value": 2, "rule": "publish_csv_and_json"},
    {"output_type": "accounting_basis", "minimum_value": 1, "rule": "keep_accrual_ce_and_siope_cash_separate"},
    {"output_type": "demographic_denominator", "minimum_value": 1, "rule": "declare_relevant_population_type"},
]


def main():
    ensure_project_folders()
    output_path = get_configured_path("outputs_tables") / "publication_rules.csv"
    write_csv_json_pair(pd.DataFrame(RULES), output_path.parent, output_path.stem)
    print(f"Publication rules written to {output_path}")


if __name__ == "__main__":
    main()
