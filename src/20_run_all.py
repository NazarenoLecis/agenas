"""
Script: 20_run_all.py

Esegue la pipeline principale del progetto.
"""

import subprocess
import sys


STEPS = [
    "src/15_build_catalogs.py",
    "src/35_regional_sources_seed.py",
    "src/36_clean_column_aliases.py",
    "src/38_pipeline_check.py",
    "src/39_publication_rules.py",
    "src/00_discover_sources.py",
    "src/43_recursive_public_discovery.py",
    "src/44_agenas_links.py",
    "src/45_ministero_all_links.py",
    "src/46_iss_links.py",
    "src/47_openbdap_ckan_health_expenditure.py",
    "src/48_istat_demography_discovery.py",
    "src/49_siope_discovery.py",
    "src/33_validate_discovered_links.py",
    "src/34_dataset_registry.py",
    "src/50_health_expenditure_registry.py",
    "src/51_health_expenditure_resource_plan.py",
    "src/24_discover_ministero_salute_catalog.py",
    "src/37_source_ranking.py",
    "src/01_download_ministero_salute.py",
    "src/02_download_Agenas.py",
    "src/03_normalize_ministero_salute.py",
    "src/04_normalize_Agenas.py",
    "src/05_build_indicators.py",
    "src/52_build_health_expenditure_framework.py",
    "src/06_export_json.py",
    "src/07_build_charts.py",
    "src/16_data_requirements.py",
    "src/17_module_inventory.py",
    "src/22_quality_overview_v2.py",
    "src/23_source_audit.py",
    "src/40_readme_outputs.py",
    "src/54_project_audit.py",
    "src/25_build_duckdb.py",
    "src/31_build_dimensions.py",
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
