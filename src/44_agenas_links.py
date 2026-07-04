"""
Script: 44_agenas_links.py

Estrae link dal Portale Statistico Agenas, inclusi report e pagine collegate.
"""

from urllib.parse import urljoin, urlparse
from datetime import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup

from utils_paths import get_configured_path, ensure_project_folders, load_project_config
from utils_io import write_csv_json_pair


HEADERS = {"User-Agent": "Agenas-data-analysis/0.1"}
SKIP_SCHEMES = {"mailto", "tel", "javascript", "data"}


def is_http_url(url):
    return urlparse(str(url)).scheme in {"http", "https"}


def fetch_links(url):
    if not url or not is_http_url(url):
        return pd.DataFrame([{"link_text": "", "url": "", "error": "missing_or_invalid_url"}])
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    rows = []
    for link in soup.find_all("a"):
        text = link.get_text(" ", strip=True)
        href = link.get("href")
        if not href or urlparse(href).scheme in SKIP_SCHEMES:
            continue
        absolute = urljoin(url, href)
        if not is_http_url(absolute):
            continue
        if text or "agenas" in absolute.lower():
            rows.append({"link_text": text, "url": absolute, "error": ""})
    return pd.DataFrame(rows).drop_duplicates()


def main():
    ensure_project_folders()
    config = load_project_config()
    sources = [s for s in config.SOURCES if s.get("provider") == "Agenas"]
    frames = []
    for source in sources:
        try:
            df = fetch_links(source.get("source_page_url"))
            df["source_id"] = source.get("source_id")
            df["provider"] = source.get("provider")
            df["checked_at"] = datetime.now().isoformat(timespec="seconds")
            frames.append(df)
        except Exception as error:
            frames.append(pd.DataFrame([{"source_id": source.get("source_id"), "provider": source.get("provider"), "link_text": "", "url": "", "checked_at": datetime.now().isoformat(timespec="seconds"), "error": str(error)}]))
    output = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    output_path = get_configured_path("outputs_tables") / "agenas_links.csv"
    write_csv_json_pair(output, output_path.parent, output_path.stem)
    print(f"Agenas links written to {output_path}")


if __name__ == "__main__":
    main()
