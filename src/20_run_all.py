"""
Script: 20_run_all.py

Obiettivo
Eseguire tutti gli script principali della pipeline, inclusi cataloghi,
discovery, download, normalizzazione, output e inventari.
"""

import subprocess
import sys


STEPS = [
    "src/15_build_catalogs.py",
    "src/00_discover_sources.py",
    "src/01_download_ministero_salute.py",
    "src/02_download_Agenas.py",
    "src/03_normalize_ministero_salute.py",
    "src/04_normalize_Agenas.py",
    "src/05_build_indicators.py",
    "src/06_export_json.py",
    "src/07_build_charts.py",
    "src/16_data_requirements.py",
    "src/17_module_inventory.py",
    "src/19_data_source_notes.py",
]


def main():
    for step in STEPS:
        print(f"Running {step}")
        result = subprocess.run([sys.executable, step], check=False)
        if result.returncode != 0:
            print(f"Step failed: {step}")
            return


if __name__ == "__main__":
    main()
