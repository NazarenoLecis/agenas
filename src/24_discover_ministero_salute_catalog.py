"""
Script: 24_discover_ministero_salute_catalog.py

Discovery mirata del portale Open Data del Ministero della Salute.
La prima versione raccoglie link candidati dalla pagina configurata.
"""

from urllib.parse import urljoin
import pandas as pd

from utils_paths import get_configured_path, ensure_project_folders, load_project_config
from utils_io import write_csv_json_pair
from utils_web import get_public_url, is_http_url, parse_html, should_skip_href, REQUEST_TIMEOUT_SECONDS


FILE_EXTENSIONS = [".csv", ".json", ".xml", ".xlsx", ".zip"]


def is_candidate(url):
    clean = url.split("?")[0].split("#")[0].lower()
    return any(clean.endswith(ext) for ext in FILE_EXTENSIONS)


def discover_page(source_url):
    if not source_url or not is_http_url(source_url):
        return pd.DataFrame([{"found_url": "", "link_text": "", "error": "missing_or_invalid_url"}])
    response = get_public_url(source_url, timeout_seconds=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    soup = parse_html(response.text)
    rows = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if should_skip_href(href):
            continue
        absolute = urljoin(source_url, href)
        if is_http_url(absolute) and is_candidate(absolute):
            rows.append({"found_url": absolute, "link_text": link.get_text(" ", strip=True), "error": ""})
    return pd.DataFrame(rows)


def main():
    ensure_project_folders()
    config = load_project_config()
    sources = [s for s in config.SOURCES if s.get("provider") == "Ministero della Salute"]
    frames = []
    for source in sources:
        try:
            df = discover_page(source.get("source_page_url"))
            df["source_id"] = source.get("source_id")
            df["provider"] = source.get("provider")
            frames.append(df)
        except Exception as error:
            frames.append(pd.DataFrame([{"source_id": source.get("source_id"), "provider": source.get("provider"), "found_url": "", "link_text": "", "error": str(error)}]))
    output = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    output_path = get_configured_path("outputs_tables") / "ministero_salute_discovery.csv"
    write_csv_json_pair(output, output_path.parent, output_path.stem)
    print(f"Ministero discovery written to {output_path}")


if __name__ == "__main__":
    main()
