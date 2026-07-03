"""
Script: 45_ministero_all_links.py

Estrae link e candidati dataset dal portale Open Data del Ministero della Salute.
"""

from urllib.parse import urljoin
from datetime import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup

from utils_paths import get_configured_path, ensure_project_folders


URL = "https://www.dati.salute.gov.it/"
HEADERS = {"User-Agent": "Agenas-data-analysis/0.1"}
KEYWORDS = ["dataset", "csv", "json", "xml", "download", "scarica", "dati", "open"]


def main():
    ensure_project_folders()
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    rows = []
    for link in soup.find_all("a"):
        href = link.get("href")
        text = link.get_text(" ", strip=True)
        if not href:
            continue
        absolute = urljoin(URL, href)
        marker = f"{absolute} {text}".lower()
        if any(keyword in marker for keyword in KEYWORDS):
            rows.append({"url": absolute, "link_text": text, "checked_at": datetime.now().isoformat(timespec="seconds")})
    output_path = get_configured_path("outputs_tables") / "ministero_all_links.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).drop_duplicates().to_csv(output_path, index=False)
    print(f"Ministero links written to {output_path}")


if __name__ == "__main__":
    main()
