"""
Script: 45_ministero_all_links.py

Estrae link e candidati dataset dal portale Open Data del Ministero della Salute.
"""

from urllib.parse import urljoin
from datetime import datetime
import pandas as pd

from utils_paths import get_configured_path, ensure_project_folders
from utils_io import write_csv_json_pair
from utils_web import get_public_url, is_http_url, parse_html, should_skip_href, REQUEST_TIMEOUT_SECONDS


URL = "https://www.dati.salute.gov.it/"
KEYWORDS = ["dataset", "csv", "json", "xml", "download", "scarica", "dati", "open"]


def main():
    ensure_project_folders()
    rows = []
    try:
        response = get_public_url(URL, timeout_seconds=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        soup = parse_html(response.text)
        for link in soup.find_all("a"):
            href = link.get("href")
            text = link.get_text(" ", strip=True)
            if should_skip_href(href):
                continue
            absolute = urljoin(URL, href)
            if not is_http_url(absolute):
                continue
            marker = f"{absolute} {text}".lower()
            if any(keyword in marker for keyword in KEYWORDS):
                rows.append({"url": absolute, "link_text": text, "checked_at": datetime.now().isoformat(timespec="seconds"), "error": ""})
    except Exception as error:
        rows.append({"url": URL, "link_text": "", "checked_at": datetime.now().isoformat(timespec="seconds"), "error": str(error)})
    output_path = get_configured_path("outputs_tables") / "ministero_all_links.csv"
    output = pd.DataFrame(rows).drop_duplicates()
    write_csv_json_pair(output, output_path.parent, output_path.stem)
    print(f"Ministero links written to {output_path}")


if __name__ == "__main__":
    main()
