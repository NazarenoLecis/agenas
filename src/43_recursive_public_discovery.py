"""
Script: 43_recursive_public_discovery.py

Discovery controllata delle pagine pubbliche configurate.

Lo script segue link interni allo stesso dominio fino a una profondita limitata e
salva tutti i link candidati a dataset, report o pagine di dati. Non accede ad
aree riservate e non usa credenziali.
"""

from collections import deque
from urllib.parse import urljoin, urlparse
from datetime import datetime
import pandas as pd

from utils_paths import get_configured_path, ensure_project_folders, load_project_config
from utils_io import write_csv_json_pair
from utils_web import get_public_url, is_http_url, normalize_url, parse_html, should_skip_href, REQUEST_TIMEOUT_SECONDS


FILE_EXTENSIONS = [".csv", ".json", ".xml", ".xlsx", ".xls", ".zip", ".pdf", ".ods"]
KEYWORDS = ["download", "scarica", "dataset", "dati", "csv", "json", "xlsx", "open-data", "open data"]
MAX_DEPTH = 1
MAX_PAGES_PER_SOURCE = 5


def same_domain(url, base_url):
    return urlparse(url).netloc == urlparse(base_url).netloc


def classify_link(url, text):
    clean = url.split("?")[0].split("#")[0].lower()
    text_l = str(text).lower()
    if any(clean.endswith(ext) for ext in FILE_EXTENSIONS):
        return "file_candidate"
    if any(keyword in clean or keyword in text_l for keyword in KEYWORDS):
        return "page_candidate"
    return "other"


def fetch_links(page_url):
    response = get_public_url(page_url, timeout_seconds=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    soup = parse_html(response.text)
    links = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if should_skip_href(href):
            continue
        absolute = normalize_url(urljoin(page_url, href))
        if not is_http_url(absolute):
            continue
        links.append((absolute, link.get_text(" ", strip=True)))
    return links


def discover_source(source):
    start_url = normalize_url(source.get("source_page_url", ""))
    checked_at = datetime.now().isoformat(timespec="seconds")
    if not start_url or not is_http_url(start_url):
        return [{"source_id": source.get("source_id"), "provider": source.get("provider"), "page_url": start_url, "found_url": "", "link_text": "", "link_type": "error", "depth": 0, "checked_at": checked_at, "error": "missing_or_invalid_url"}]

    queue = deque([(start_url, 0)])
    visited = set()
    rows = []
    while queue and len(visited) < MAX_PAGES_PER_SOURCE:
        page_url, depth = queue.popleft()
        page_url = normalize_url(page_url)
        if page_url in visited:
            continue
        visited.add(page_url)
        try:
            links = fetch_links(page_url)
        except Exception as error:
            rows.append({"source_id": source.get("source_id"), "provider": source.get("provider"), "page_url": page_url, "found_url": "", "link_text": "", "link_type": "error", "depth": depth, "checked_at": checked_at, "error": str(error)})
            continue
        for found_url, text in links:
            link_type = classify_link(found_url, text)
            if link_type != "other":
                rows.append({"source_id": source.get("source_id"), "provider": source.get("provider"), "page_url": page_url, "found_url": found_url, "link_text": text, "link_type": link_type, "depth": depth, "checked_at": checked_at, "error": ""})
            if depth < MAX_DEPTH and same_domain(found_url, start_url) and found_url not in visited:
                queue.append((found_url, depth + 1))
    return rows


def main():
    ensure_project_folders()
    config = load_project_config()
    rows = []
    for source in config.SOURCES:
        rows.extend(discover_source(source))
    output_path = get_configured_path("outputs_tables") / "recursive_public_discovery.csv"
    output = pd.DataFrame(rows).drop_duplicates()
    write_csv_json_pair(output, output_path.parent, output_path.stem)
    print(f"Recursive discovery written to {output_path}")


if __name__ == "__main__":
    main()
