"""
Script: 18_full_pipeline.py

Obiettivo
Eseguire in sequenza i passaggi principali della pipeline.

Questo script non usa argparse e non usa classi.
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
]


def run_step(step):
    print(f"Running {step}", flush=True)
    return subprocess.run([sys.executable, step], check=False)


def main():
    for step in STEPS:
        result = run_step(step)
        if result.returncode != 0:
            print(f"Step failed: {step}")
            return result.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
