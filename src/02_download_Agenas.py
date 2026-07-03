"""
Script: 02_download_Agenas.py

Obiettivo
Scaricare solo fonti Agenas abilitate e con URL diretto indicato in
config/project_config.py.

Uso
1. Verificare licenza e riuso della fonte.
2. Inserire URL diretti nella configurazione Python.
3. Impostare enabled=True.
4. Eseguire python src/02_download_Agenas.py.
"""

import pandas as pd

from utils_paths import get_project_root, get_configured_path, ensure_project_folders, load_project_config
from utils_catalog import filter_enabled_sources
from utils_download import download_file, infer_extension_from_url


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
        output_folder = get_configured_path("data_raw") / source.get("output_subfolder", "Agenas")
        output_path = output_folder / f"{source.get('source_id')}.{extension}"
        result = download_file(url, output_path)
        result["source_id"] = source.get("source_id")
        result["provider"] = source.get("provider")
        result["file_format"] = extension
        result["url_key"] = url_key
        result["local_path"] = str(output_path.relative_to(root))
        log_rows.append(result)
    return pd.DataFrame(log_rows)


def main():
    ensure_project_folders()
    config = load_project_config()
    sources = filter_enabled_sources(config.SOURCES, provider="Agenas")
    tasks = build_download_tasks(sources)
    log = run_downloads(tasks) if tasks else pd.DataFrame()
    log_path = get_configured_path("downloads_log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if log_path.exists() and not log.empty:
        previous_log = pd.read_csv(log_path)
        log = pd.concat([previous_log, log], ignore_index=True)
    log.to_csv(log_path, index=False)
    print(f"Agenas download log written to {log_path}")


if __name__ == "__main__":
    main()
