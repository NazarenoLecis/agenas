"""
Script: 19_data_source_notes.py

Obiettivo
Creare una tabella sintetica delle aree informative da cercare nelle fonti.
"""

import pandas as pd

from utils_paths import get_configured_path, ensure_project_folders


AREAS = [
    "mobilita sanitaria",
    "mobilita economica",
    "personale sanitario",
    "medici per disciplina",
    "infermieri",
    "operatori socio sanitari",
    "tempi di attesa",
    "costi e spesa",
    "prestazioni",
    "pronto soccorso",
    "ricoveri",
    "posti letto",
    "strutture",
    "accreditamento",
    "grandi apparecchiature",
    "assistenza territoriale",
    "farmaci",
    "demografia",
]


def main():
    ensure_project_folders()
    output_path = get_configured_path("outputs_tables") / "data_source_areas.csv"
    pd.DataFrame({"area": AREAS}).to_csv(output_path, index=False)
    print(f"Data source areas written to {output_path}")


if __name__ == "__main__":
    main()
