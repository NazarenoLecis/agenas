"""
Script: 37_source_ranking.py

Crea una graduatoria operativa delle fonti da lavorare prima.
"""

import pandas as pd

from utils_paths import get_configured_path, ensure_project_folders
from utils_io import write_csv_json_pair


def score_source(row):
    score = 0
    if row.get("redistribution_allowed") == "yes":
        score += 3
    if row.get("access_type") in ["web_page", "api", "ckan_api", "download"]:
        score += 2
    if row.get("theme") in ["all", "workforce", "waiting_times", "hospital_activity", "emergency", "costs", "health_expenditure", "demography"]:
        score += 2
    if row.get("download_url_csv") or row.get("download_url_json"):
        score += 2
    if row.get("enabled") is True or str(row.get("enabled")).lower() == "true":
        score += 1
    return score


def main():
    ensure_project_folders()
    catalog_path = get_configured_path("data_catalog")
    output_path = get_configured_path("outputs_tables") / "source_ranking.csv"
    if not catalog_path.exists():
        print("Source catalog not found")
        return
    df = pd.read_csv(catalog_path)
    df["score"] = df.apply(score_source, axis=1)
    df = df.sort_values("score", ascending=False)
    write_csv_json_pair(df, output_path.parent, output_path.stem)
    print(f"Source ranking written to {output_path}")


if __name__ == "__main__":
    main()
