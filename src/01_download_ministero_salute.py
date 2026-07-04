"""
Script: 01_download_ministero_salute.py

Obiettivo
Scaricare le fonti abilitate del Ministero configurate in config/project_config.py.

Output
I file sono salvati in data/raw. Il log viene salvato in metadata/downloads_log.csv
e metadata/downloads_log.json.
"""

import pandas as pd

from utils_paths import get_project_root, get_configured_path, ensure_project_folders, load_project_config
from utils_catalog import filter_enabled_sources
from utils_download import download_file, infer_extension_from_url
from utils_io import write_csv_json_pair


def build_download_tasks(sources):
    tasks = []
    for source in sources:
        for key in ["download_url_csv", "download_url_json", "download_url_xml"]:
            url = source.get(key, "")
            if url:
                tasks.append((source, key, url))
    return tasks


def run_downloads(tasks):
    root = get_project_root()
    log_rows = []
    for source, url_key, url in tasks:
        extension = infer_extension_from_url(url)
        output_folder = get_configured_path("data_raw") / source.get("output_subfolder", "ministero_salute")
        output_path = output_folder / f"{source.get('source_id')}.{extension}"
        result = download_file(url, output_path)
        result["source_id"] = source.get("source_id")
        result["provider"] = source.get("provider")
        result["file_format"] = extension
        result["url_key"] = url_key
        result["local_path"] = str(output_path.relative_to(root))
        log_rows.append(result)
    return pd.DataFrame(log_rows)


def append_previous_log(log, log_path):
    if log_path.exists() and not log.empty:
        previous_log = pd.read_csv(log_path)
        return pd.concat([previous_log, log], ignore_index=True)
    return log


def main():
    ensure_project_folders()
    config = load_project_config()
    sources = filter_enabled_sources(config.SOURCES, provider="Ministero della Salute")
    tasks = build_download_tasks(sources)
    log = run_downloads(tasks) if tasks else pd.DataFrame()
    log_path = get_configured_path("downloads_log")
    log = append_previous_log(log, log_path)
    write_csv_json_pair(log, log_path.parent, log_path.stem)
    print(f"Download log written to {log_path}")


if __name__ == "__main__":
    main()
