"""
Script: 41_iss_source_notes.py

Crea una nota tabellare su come usare le fonti ISS nel progetto.
"""

import pandas as pd

from utils_paths import get_configured_path, ensure_project_folders


ROWS = [
    {"source_group": "ISS", "use_case": "sorveglianze", "main_modules": "surveillance;risk_factors"},
    {"source_group": "ISS", "use_case": "prevenzione", "main_modules": "risk_factors;territorial_care"},
    {"source_group": "ISS", "use_case": "infezioni respiratorie", "main_modules": "surveillance;emergency"},
]


def main():
    ensure_project_folders()
    output_path = get_configured_path("outputs_tables") / "iss_source_notes.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(ROWS).to_csv(output_path, index=False)
    print(f"ISS source notes written to {output_path}")


if __name__ == "__main__":
    main()
