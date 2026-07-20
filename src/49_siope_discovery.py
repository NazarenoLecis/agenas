"""
Script: 49_siope_discovery.py

Discovery mirata del sito SIOPE per individuare pagine e link collegati a
download, aggregati, serie storiche e guida.

SIOPE e trattato come fonte di cassa. Il modulo non scarica dati massivi.
"""

from datetime import datetime
from urllib.parse import urljoin
import re
import pandas as pd

from utils_paths import get_configured_path, ensure_project_folders
from utils_io import write_csv_json_pair
from utils_web import get_public_url, is_http_url, parse_html, should_skip_href, REQUEST_TIMEOUT_SECONDS


URLS = [
    "https://www.siope.it/Siope/",
    "https://www.siope.it/Siope/html/help_on_line.pdf",
]
KEYWORDS = ["download", "scarica", "enti", "aggregati", "serie", "storiche", "cassa", "pagamenti", "incassi", "guida", "pdf", "csv", "xls"]


def normalize_text(value):
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def classify_url(url, text):
    marker = normalize_text(f"{url} {text}")
    clean = str(url).split("?")[0].split("#")[0].lower()
    if clean.endswith(".pdf"):
        return "documentation"
    if clean.endswith((".csv", ".xls", ".xlsx", ".zip")):
        return "data_candidate"
    if any(keyword in marker for keyword in KEYWORDS):
        return "page_candidate"
    return "other"


def fetch_source(url):
    checked_at = datetime.now().isoformat(timespec="seconds")
    response = get_public_url(url, timeout_seconds=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    content_type = response.headers.get("content-type", "")
    if "pdf" in content_type.lower() or url.lower().endswith(".pdf"):
        return [{"source_id": "siope", "provider": "SIOPE", "source_page_url": url, "url": url, "link_text": "SIOPE documentation", "link_type": "documentation", "checked_at": checked_at, "error": ""}]
    soup = parse_html(response.text)
    rows = []
    for link in soup.find_all("a"):
        href = link.get("href")
        text = link.get_text(" ", strip=True)
        title = link.get("title", "") or link.get("aria-label", "")
        marker_text = " ".join([text, title])
        if should_skip_href(href):
            continue
        absolute = urljoin(url, href)
        if not is_http_url(absolute):
            continue
        link_type = classify_url(absolute, marker_text)
        if link_type == "other":
            continue
        rows.append({"source_id": "siope", "provider": "SIOPE", "source_page_url": url, "url": absolute, "link_text": marker_text, "link_type": link_type, "checked_at": checked_at, "error": ""})
    if not rows:
        rows.append({"source_id": "siope", "provider": "SIOPE", "source_page_url": url, "url": "", "link_text": "", "link_type": "no_candidate", "checked_at": checked_at, "error": ""})
    return rows


def main():
    ensure_project_folders()
    rows = []
    for url in URLS:
        try:
            rows.extend(fetch_source(url))
        except Exception as error:
            rows.append({"source_id": "siope", "provider": "SIOPE", "source_page_url": url, "url": "", "link_text": "", "link_type": "error", "checked_at": datetime.now().isoformat(timespec="seconds"), "error": str(error)})
    output = pd.DataFrame(rows).drop_duplicates()
    output_path = get_configured_path("outputs_tables") / "siope_links.csv"
    write_csv_json_pair(output, output_path.parent, output_path.stem)
    print(f"SIOPE links written to {output_path}")


if __name__ == "__main__":
    main()
