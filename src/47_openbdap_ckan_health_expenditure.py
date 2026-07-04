"""
Script: 47_openbdap_ckan_health_expenditure.py

Discovery mirata del catalogo OpenBDAP tramite API CKAN.

Cerca dataset e risorse collegati a spesa sanitaria, Conto Economico degli enti
del SSN, SIOPE e finanza sanitaria. Non scarica i file dati. Produce un registry
operativo delle risorse candidate.
"""

from datetime import datetime
import re
import pandas as pd
import requests

from utils_paths import get_configured_path, ensure_project_folders
from utils_io import write_csv_json_pair, write_json_object


CKAN_ACTION_BASE = "https://bdap-opendata.rgs.mef.gov.it/SpodCkanApi/api/3/action"
HEADERS = {"User-Agent": "Agenas-data-analysis/0.1"}
TIMEOUT_SECONDS = 45

SEARCH_QUERIES = [
    "SSN",
    "spesa sanitaria",
    "Conto Economico enti SSN",
    "conto economico regionale sanita",
    "modello rilevazione conto economico enti ssn",
    "livello regionale enti ssn",
    "movimenti di cassa enti ssn",
    "siope sanita",
]

HEALTH_KEYWORDS = [
    "ssn", "sanita", "sanitario", "sanitaria", "salute",
    "conto economico", "modello ce", "enti del ssn", "livello regionale",
    "spesa sanitaria", "finanza sanitaria", "movimenti di cassa", "siope",
]

DATA_FORMATS = {"csv", "json", "xml", "xlsx", "xls", "zip", "ods"}


def normalize_text(value):
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def ckan_action(action, params=None):
    url = f"{CKAN_ACTION_BASE}/{action}"
    response = requests.get(url, params=params or {}, headers=HEADERS, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    payload = response.json()
    if not payload.get("success", False):
        raise RuntimeError(f"CKAN action failed: {action}")
    return payload.get("result")


def package_search(query, rows=100):
    try:
        result = ckan_action("package_search", {"q": query, "rows": rows})
        return result.get("results", [])
    except Exception:
        return []


def package_show(package_id):
    return ckan_action("package_show", {"id": package_id})


def fallback_package_list(limit=500):
    try:
        packages = ckan_action("package_list")
    except Exception:
        return []
    selected = []
    for package_id in packages[:limit]:
        try:
            package = package_show(package_id)
        except Exception:
            continue
        text = normalize_text(" ".join([package.get("title", ""), package.get("name", ""), package.get("notes", "")]))
        if any(keyword in text for keyword in HEALTH_KEYWORDS):
            selected.append(package)
    return selected


def collect_packages():
    packages_by_id = {}
    errors = []
    for query in SEARCH_QUERIES:
        try:
            for package in package_search(query):
                package_id = package.get("id") or package.get("name")
                if package_id:
                    packages_by_id[package_id] = package
        except Exception as error:
            errors.append({"query": query, "error": str(error)})
    if not packages_by_id:
        for package in fallback_package_list():
            package_id = package.get("id") or package.get("name")
            if package_id:
                packages_by_id[package_id] = package
    return list(packages_by_id.values()), errors


def score_resource(package, resource):
    text = normalize_text(" ".join([
        package.get("title", ""), package.get("name", ""), package.get("notes", ""),
        resource.get("name", ""), resource.get("description", ""), resource.get("url", ""), resource.get("format", ""),
    ]))
    score = 0
    for keyword in HEALTH_KEYWORDS:
        if keyword in text:
            score += 1
    resource_format = normalize_text(resource.get("format", "")).replace(".", "")
    if resource_format in DATA_FORMATS:
        score += 2
    if "region" in text or "regionale" in text:
        score += 2
    if "conto economico" in text or "modello ce" in text:
        score += 3
    if "siope" in text or "movimenti di cassa" in text:
        score += 2
    return score


def package_to_rows(package):
    resources = package.get("resources") or []
    if not resources:
        resources = [{}]
    rows = []
    for resource in resources:
        row = {
            "source_id": "openbdap_ckan",
            "provider": "OpenBDAP / RGS",
            "package_id": package.get("id", ""),
            "package_name": package.get("name", ""),
            "package_title": package.get("title", ""),
            "package_notes": package.get("notes", ""),
            "license_id": package.get("license_id", ""),
            "license_title": package.get("license_title", ""),
            "resource_id": resource.get("id", ""),
            "resource_name": resource.get("name", ""),
            "resource_description": resource.get("description", ""),
            "resource_format": resource.get("format", ""),
            "resource_url": resource.get("url", ""),
            "resource_created": resource.get("created", ""),
            "resource_last_modified": resource.get("last_modified", ""),
            "resource_size": resource.get("size", ""),
            "discovered_at": datetime.now().isoformat(timespec="seconds"),
        }
        row["relevance_score"] = score_resource(package, resource)
        rows.append(row)
    return rows


def main():
    ensure_project_folders()
    packages, errors = collect_packages()
    rows = []
    for package in packages:
        rows.extend(package_to_rows(package))
    output = pd.DataFrame(rows)
    if not output.empty:
        output = output.sort_values(["relevance_score", "package_title", "resource_name"], ascending=[False, True, True])
    output_path = get_configured_path("outputs_tables") / "openbdap_health_expenditure_resources.csv"
    write_csv_json_pair(output, output_path.parent, output_path.stem)
    write_json_object({"errors": errors, "queries": SEARCH_QUERIES, "packages_found": len(packages)}, output_path.parent / "openbdap_health_expenditure_discovery_log.json")
    print(f"OpenBDAP health expenditure resources written to {output_path}")


if __name__ == "__main__":
    main()
