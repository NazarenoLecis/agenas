"""
Script: 00_discover_sources.py

Obiettivo
Leggere le fonti indicate in config/project_config.py, aprire le pagine pubbliche
e cercare link a file scaricabili.

Come usare
1. Aggiornare config/project_config.py.
2. Eseguire python src/00_discover_sources.py dalla radice del repository.
3. Controllare data_catalog/discovered_links.csv.

Regole
Lo script usa solo pagine pubbliche. Non accede ad aree riservate.
"""

from datetime import datetime
from urllib.parse import urljoin
import pandas as pd
import requests
from bs4 import BeautifulSoup

from utils_paths import get_project_root, get_configured_path, load_project_config


FILE_EXTENSIONS = [".csv", ".json", ".xml", ".xlsx", ".xls", ".zip", ".pdf"]
HEADERS = {"User-Agent": "Agenas-data-analysis/0.1"}


def is_download_link(url):
    clean_url = url.split("?")[0].split("#")[0].lower()
    return any(clean_url.endswith(extension) for extension in FILE_EXTENSIONS)


def fetch_public_page(url, timeout_seconds=30):
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout_seconds)
        return response.status_code, response.headers.get("content-type", ""), response.text, ""
    except Exception as error:
        return None, "", "", str(error)


def extract_links(source):
    source_url = source.get("source_page_url", "")
    checked_at = datetime.now().isoformat(timespec="seconds")
    status_code, content_type, html, error_message = fetch_public_page(source_url)
    rows = []
    if error_message:
        rows.append({
            "source_id": source.get("source_id"),
            "provider": source.get("provider"),
            "source_page_url": source_url,
            "found_url": "",
            "file_extension": "",
            "link_text": "",
            "checked_at": checked_at,
            "status_code": status_code,
            "content_type": content_type,
            "status": "error",
            "error_message": error_message,
        })
        return rows
    soup = BeautifulSoup(html, "lxml")
    for link in soup.find_all("a"):
        href = link.get("href")
        if not href:
            continue
        absolute_url = urljoin(source_url, href)
        if not is_download_link(absolute_url):
            continue
        clean_url = absolute_url.split("?")[0].split("#")[0]
        extension = clean_url.lower().split(".")[-1]
        rows.append({
            "source_id": source.get("source_id"),
            "provider": source.get("provider"),
            "source_page_url": source_url,
            "found_url": absolute_url,
            "file_extension": extension,
            "link_text": link.get_text(" ", strip=True),
            "checked_at": checked_at,
            "status_code": status_code,
            "content_type": content_type,
            "status": "candidate_download",
            "error_message": "",
        })
    if not rows:
        rows.append({
            "source_id": source.get("source_id"),
            "provider": source.get("provider"),
            "source_page_url": source_url,
            "found_url": "",
            "file_extension": "",
            "link_text": "",
            "checked_at": checked_at,
            "status_code": status_code,
            "content_type": content_type,
            "status": "no_download_link_found",
            "error_message": "",
        })
    return rows


def main():
    root = get_project_root()
    config = load_project_config()
    output_path = get_configured_path("discovered_links")
    rows = []
    for source in config.SOURCES:
        rows.extend(extract_links(source))
    df = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Discovery table written to {output_path.relative_to(root)}")


if __name__ == "__main__":
    main()
