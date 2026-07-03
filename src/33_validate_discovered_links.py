"""
Script: 33_validate_discovered_links.py

Valida i link scoperti con richieste leggere e produce una tabella di priorita.
"""

import pandas as pd
import requests

from utils_paths import get_configured_path, ensure_project_folders


HEADERS = {"User-Agent": "Agenas-data-analysis/0.1"}
DATA_EXTENSIONS = ["csv", "json", "xml", "xlsx", "xls", "zip"]


def validate_url(url):
    try:
        response = requests.head(url, headers=HEADERS, timeout=20, allow_redirects=True)
        return response.status_code, response.headers.get("content-type", ""), response.headers.get("content-length", ""), response.url, ""
    except Exception as error:
        return None, "", "", url, str(error)


def main():
    ensure_project_folders()
    discovered_path = get_configured_path("discovered_links")
    output_path = get_configured_path("outputs_tables") / "validated_discovered_links.csv"
    if not discovered_path.exists():
        print("No discovered links found")
        return
    df = pd.read_csv(discovered_path)
    rows = []
    for _, row in df.iterrows():
        url = row.get("found_url", "")
        if not isinstance(url, str) or not url:
            continue
        status, content_type, content_length, final_url, error = validate_url(url)
        item = row.to_dict()
        item["validation_status_code"] = status
        item["validation_content_type"] = content_type
        item["validation_content_length"] = content_length
        item["final_url"] = final_url
        item["validation_error"] = error
        item["is_data_file"] = str(row.get("file_extension", "")).lower() in DATA_EXTENSIONS
        rows.append(item)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output_path, index=False)
    print(f"Validated links written to {output_path}")


if __name__ == "__main__":
    main()
