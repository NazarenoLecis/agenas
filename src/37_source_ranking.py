"""
Script: 37_source_ranking.py

Crea una graduatoria operativa delle fonti da lavorare prima.
"""

import pandas as pd

from utils_paths import get_configured_path, ensure_project_folders


def score_source(row):
    score = 0
    if row.get("redistribution_allowed") == "yes":
        score += 3
    if row.get("access_type") in ["web_page", "api"]:
        score += 2
    if row.get("theme") in ["all", "workforce", "waiting_times", "hospital_activity", "emergency", "costs"]:
        score += 2
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
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Source ranking written to {output_path}")


if __name__ == "__main__":
    main()
