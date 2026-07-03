"""
Script: 36_clean_column_aliases.py

Crea un dizionario base di alias per colonne sanitarie comuni.
"""

import pandas as pd

from utils_paths import get_configured_path, ensure_project_folders


ALIASES = [
    {"standard_name": "region", "aliases": "regione;regione_nome;region_name"},
    {"standard_name": "year", "aliases": "anno;year;periodo"},
    {"standard_name": "origin", "aliases": "origine;regione_origine;regione_residenza"},
    {"standard_name": "destination", "aliases": "destinazione;regione_destinazione;regione_erogazione"},
    {"standard_name": "structure", "aliases": "struttura;ospedale;presidio;istituto"},
    {"standard_name": "service", "aliases": "prestazione;servizio;specialistica"},
    {"standard_name": "volume", "aliases": "volume;volumi;numero;conteggio;n"},
    {"standard_name": "cost", "aliases": "costo;spesa;importo;valore"},
]


def main():
    ensure_project_folders()
    output_path = get_configured_path("outputs_tables") / "column_aliases.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(ALIASES).to_csv(output_path, index=False)
    print(f"Column aliases written to {output_path}")


if __name__ == "__main__":
    main()
