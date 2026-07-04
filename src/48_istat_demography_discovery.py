"""
Script: 48_istat_demography_discovery.py

Discovery mirata delle pagine ISTAT Demo utili per denominatori demografici.

Estrae link a pagine, ZIP e CSV collegati a popolazione residente, nascite e
struttura per eta. Non scarica i file dati.
"""

from datetime import datetime
from urllib.parse import urljoin, urlparse
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup

from utils_paths import get_configured_path, ensure_project_folders
from utils_io import write_csv_json_pair


HEADERS = {"User-Agent": "Agenas-data-analysis/0.1"}
URLS = [
    {"source_id": "istat_population_age_region", "source_page_url": "https://demo.istat.it/app/?i=POS&l=it", "source_role": "population_by_age_sex"},
    {"source_id": "istat_demo_home", "source_page_url": "https://demo.istat.it/", "source_role": "demography_index"},
]
KEYWORDS = ["popolazione", "eta", "sesso", "nasc", "nati", "csv", "zip", "download", "scarica", "regione", "ripartizioni"]
SKIP_SCHEMES = {"mailto", "tel", "javascript", "data"}


def is_http_url(url):
    return urlparse(str(url)).scheme in {"http", "https"}


def normalize_text(value):
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def classify_url(url, text):
    marker = normalize_text(f"{url} {text}")
    clean = str(url).split("?")[0].split("#")[0].lower()
    if clean.endswith(".zip"):
        return "zip_candidate"
    if clean.endswith(".csv"):
        return "csv_candidate"
    if any(keyword in marker for keyword in KEYWORDS):
        return "page_candidate"
    return "other"


def fetch_links(source):
    url = source["source_page_url"]
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    rows = []
    checked_at = datetime.now().isoformat(timespec="seconds")
    for link in soup.find_all("a"):
        href = link.get("href")
        text = link.get_text(" ", strip=True)
        title = link.get("title", "") or link.get("aria-label", "")
        marker_text = " ".join([text, title])
        if not href or urlparse(href).scheme in SKIP_SCHEMES:
            continue
        absolute = urljoin(url, href)
        if not is_http_url(absolute):
            continue
        link_type = classify_url(absolute, marker_text)
        if link_type == "other":
            continue
        rows.append({
            "source_id": source["source_id"],
            "provider": "ISTAT",
            "source_role": source["source_role"],
            "source_page_url": url,
            "url": absolute,
            "link_text": marker_text,
            "link_type": link_type,
            "checked_at": checked_at,
            "error": "",
        })
    if not rows:
        rows.append({"source_id": source["source_id"], "provider": "ISTAT", "source_role": source["source_role"], "source_page_url": url, "url": "", "link_text": "", "link_type": "no_candidate", "checked_at": checked_at, "error": ""})
    return rows


def main():
    ensure_project_folders()
    rows = []
    for source in URLS:
        try:
            rows.extend(fetch_links(source))
        except Exception as error:
            rows.append({"source_id": source["source_id"], "provider": "ISTAT", "source_role": source["source_role"], "source_page_url": source["source_page_url"], "url": "", "link_text": "", "link_type": "error", "checked_at": datetime.now().isoformat(timespec="seconds"), "error": str(error)})
    output = pd.DataFrame(rows).drop_duplicates()
    output_path = get_configured_path("outputs_tables") / "istat_demography_links.csv"
    write_csv_json_pair(output, output_path.parent, output_path.stem)
    print(f"ISTAT demography links written to {output_path}")


if __name__ == "__main__":
    main()
