"""
Script: 54_project_audit.py

Esegue controlli statici sul progetto senza scaricare dati esterni.

Output:
- outputs/tables/project_audit.csv
- outputs/tables/project_audit.json
- outputs/reports/project_audit.md
"""

from pathlib import Path
import importlib.util
import py_compile
import tempfile
import pandas as pd

from utils_paths import get_project_root, get_configured_path, ensure_project_folders, load_project_config
from utils_io import write_csv_json_pair


SOURCE_REQUIRED_FIELDS = [
    "source_id", "provider", "dataset_name", "theme", "source_page_url",
    "access_type", "license", "redistribution_allowed", "output_subfolder", "enabled",
]

EXPECTED_PUBLIC_OUTPUT_STEMS = [
    "data_catalog/data_catalog",
    "data_catalog/analysis_modules",
    "data_catalog/discovered_links",
    "outputs/tables/dataset_registry",
    "outputs/tables/source_ranking",
    "outputs/tables/quality_overview",
    "outputs/tables/regional_health_expenditure_demographic_adjusted",
]


def audit_row(check_group, check_name, passed, value="", message=""):
    return {
        "check_group": check_group,
        "check_name": check_name,
        "passed": bool(passed),
        "value": value,
        "message": message,
    }


def load_module_from_path(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_python_syntax(root):
    rows = []
    for path in sorted((root / "src").glob("*.py")):
        try:
            py_compile.compile(str(path), doraise=True)
            rows.append(audit_row("python_syntax", str(path.relative_to(root)), True, "", "ok"))
        except Exception as error:
            rows.append(audit_row("python_syntax", str(path.relative_to(root)), False, "", str(error)))
    return rows


def check_config(config):
    rows = []
    source_ids = [source.get("source_id", "") for source in config.SOURCES]
    module_ids = [module.get("module_id", "") for module in config.ANALYSIS_MODULES]
    module_id_set = set(module_ids)

    rows.append(audit_row("config", "unique_source_ids", len(source_ids) == len(set(source_ids)), len(source_ids), "source_id must be unique"))
    rows.append(audit_row("config", "unique_module_ids", len(module_ids) == len(set(module_ids)), len(module_ids), "module_id must be unique"))

    for source in config.SOURCES:
        source_id = source.get("source_id", "missing_source_id")
        missing = [field for field in SOURCE_REQUIRED_FIELDS if field not in source]
        rows.append(audit_row("source_schema", source_id, not missing, ";".join(missing), "missing required source fields" if missing else "ok"))
        theme = source.get("theme")
        theme_ok = theme == "all" or theme in module_id_set
        rows.append(audit_row("source_theme", source_id, theme_ok, theme, "theme not present in ANALYSIS_MODULES" if not theme_ok else "ok"))
    return rows


def check_public_output_pairs(root):
    rows = []
    for stem in EXPECTED_PUBLIC_OUTPUT_STEMS:
        csv_path = root / f"{stem}.csv"
        json_path = root / f"{stem}.json"
        rows.append(audit_row(
            "csv_json_pairs",
            stem,
            csv_path.exists() == json_path.exists(),
            f"csv={csv_path.exists()};json={json_path.exists()}",
            "missing csv/json counterpart" if csv_path.exists() != json_path.exists() else "ok",
        ))
    return rows


def check_health_config(root):
    rows = []
    path = root / "config" / "health_expenditure_config.py"
    if not path.exists():
        return [audit_row("health_config", "file_exists", False, str(path), "missing health expenditure config")]
    try:
        module = load_module_from_path(path, "health_expenditure_config_audit")
        settings = getattr(module, "HEALTH_EXPENDITURE_SETTINGS", {})
        denominators = getattr(module, "DEMOGRAPHIC_DENOMINATORS", [])
        rows.append(audit_row("health_config", "output_formats", set(settings.get("public_output_formats", [])) == {"csv", "json"}, str(settings.get("public_output_formats", [])), "public outputs must be csv and json"))
        rows.append(audit_row("health_config", "denominators_present", len(denominators) >= 5, len(denominators), "demographic denominators should be configured"))
        rows.append(audit_row("health_config", "cash_accrual_separation", bool(settings.get("keep_cash_and_accrual_separate")), settings.get("keep_cash_and_accrual_separate"), "CE and SIOPE must stay separate"))
    except Exception as error:
        rows.append(audit_row("health_config", "import", False, "", str(error)))
    return rows


def write_report(audit, reports_root):
    reports_root.mkdir(parents=True, exist_ok=True)
    failed = audit[audit["passed"] == False]
    with (reports_root / "project_audit.md").open("w", encoding="utf-8") as file:
        file.write("# Project audit\n\n")
        file.write(f"Checks: {len(audit)}\n\n")
        file.write(f"Failed checks: {len(failed)}\n\n")
        if not failed.empty:
            file.write("## Failed checks\n\n")
            for _, row in failed.iterrows():
                file.write(f"- {row['check_group']} / {row['check_name']}: {row['message']} ({row['value']})\n")


def main():
    ensure_project_folders()
    root = get_project_root()
    config = load_project_config()
    rows = []
    rows.extend(check_python_syntax(root))
    rows.extend(check_config(config))
    rows.extend(check_public_output_pairs(root))
    rows.extend(check_health_config(root))

    audit = pd.DataFrame(rows)
    tables_root = get_configured_path("outputs_tables")
    reports_root = get_configured_path("outputs_reports")
    write_csv_json_pair(audit, tables_root, "project_audit")
    write_report(audit, reports_root)
    print(f"Project audit completed with {(audit['passed'] == False).sum()} failed checks")


if __name__ == "__main__":
    main()
