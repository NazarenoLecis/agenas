"""
Script: 23_source_audit.py

Crea report sintetici sullo stato delle fonti configurate e sui link scoperti.
"""

import pandas as pd

from utils_paths import get_configured_path, ensure_project_folders


def read_csv_if_exists(path):
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def main():
    ensure_project_folders()
    catalog_path = get_configured_path("data_catalog")
    discovered_path = get_configured_path("discovered_links")
    tables_root = get_configured_path("outputs_tables")
    reports_root = get_configured_path("outputs_reports")
    catalog = read_csv_if_exists(catalog_path)
    discovered = read_csv_if_exists(discovered_path)
    tables_root.mkdir(parents=True, exist_ok=True)
    reports_root.mkdir(parents=True, exist_ok=True)
    if not catalog.empty:
        by_provider = catalog.groupby(["provider", "access_type"], dropna=False).size().reset_index(name="sources")
        by_theme = catalog.groupby(["theme", "access_type"], dropna=False).size().reset_index(name="sources")
        by_provider.to_csv(tables_root / "source_audit_by_provider.csv", index=False)
        by_theme.to_csv(tables_root / "source_audit_by_theme.csv", index=False)
    if not discovered.empty and "status" in discovered.columns:
        discovery_status = discovered.groupby(["provider", "status"], dropna=False).size().reset_index(name="links")
        discovery_status.to_csv(tables_root / "source_audit_discovery_status.csv", index=False)
    with (reports_root / "source_audit.md").open("w", encoding="utf-8") as file:
        file.write("# Source audit\n\n")
        file.write(f"Configured sources: {len(catalog)}\n\n")
        file.write(f"Discovered rows: {len(discovered)}\n")
    print("Source audit completed")


if __name__ == "__main__":
    main()
