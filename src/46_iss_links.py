"""
Script: 46_iss_links.py

Estrae link candidati dalle fonti ISS configurate.
"""

from urllib.parse import urljoin, urlparse
from datetime import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup

from utils_paths import get_configured_path, ensure_project_folders, load_project_config
from utils_io import write_csv_json_pair


HEADERS = {"User-Agent": "Agenas-data-analysis/0.1"}
KEYWORDS = ["dati", "dataset", "csv", "xlsx", "pdf", "rapporto", "sorveglianza"]
SKIP_SCHEMES = {"mailto", "tel", "javascript", "data"}


def is_http_url(url):
    return urlparse(str(url)).scheme in {"http", "https"}


def extract(url):
    if not url or not is_http_url(url):
        return pd.DataFrame([{"url": "", "link_text": "", "error": "missing_or_invalid_url"}])
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    rows = []
    for link in soup.find_all("a"):
        href = link.get("href")
        text = link.get_text(" ", strip=True)
        if not href or urlparse(href).scheme in SKIP_SCHEMES:
            continue
        absolute = urljoin(url, href)
        if not is_http_url(absolute):
            continue
        marker = f"{absolute} {text}".lower()
        if any(keyword in marker for keyword in KEYWORDS):
            rows.append({"url": absolute, "link_text": text, "error": ""})
    return pd.DataFrame(rows).drop_duplicates()


def main():
    ensure_project_folders()
    config = load_project_config()
    frames = []
    for source in config.SOURCES:
        if source.get("provider") != "ISS":
            continue
        try:
            df = extract(source.get("source_page_url"))
            df["source_id"] = source.get("source_id")
            df["provider"] = source.get("provider")
            df["checked_at"] = datetime.now().isoformat(timespec="seconds")
            frames.append(df)
        except Exception as error:
            frames.append(pd.DataFrame([{"source_id": source.get("source_id"), "provider": source.get("provider"), "url": "", "link_text": "", "checked_at": datetime.now().isoformat(timespec="seconds"), "error": str(error)}]))
    output = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    output_path = get_configured_path("outputs_tables") / "iss_links.csv"
    write_csv_json_pair(output, output_path.parent, output_path.stem)
    print(f"ISS links written to {output_path}")


if __name__ == "__main__":
    main()
