"""
Configurazione centrale del progetto.

Il repository usa un file Python per la configurazione, senza YAML.
Gli script importano queste variabili per sapere dove leggere e salvare dati,
quali fonti trattare e quali regole applicare alle analisi.
"""

PROJECT_NAME = "agenas"

PATHS = {
    "data_raw": "data/raw",
    "data_interim": "data/interim",
    "data_processed": "data/processed",
    "data_external": "data/external",
    "metadata": "metadata",
    "downloads_log": "metadata/downloads_log.csv",
    "checksums": "metadata/checksums",
    "data_catalog": "data_catalog/data_catalog.csv",
    "discovered_links": "data_catalog/discovered_links.csv",
    "outputs_figures": "outputs/figures",
    "outputs_tables": "outputs/tables",
    "outputs_reports": "outputs/reports",
    "outputs_dashboard": "outputs/dashboard_data",
}

ANALYSIS_SETTINGS = {
    "default_year": None,
    "min_cell_count": 5,
    "export_csv": True,
    "export_json": True,
    "export_parquet": True,
    "overwrite_existing_files": False,
}

CHART_SETTINGS = {
    "figure_width": 12,
    "figure_height": 7,
    "dpi": 150,
    "default_top_n": 20,
}

QUALITY_SETTINGS = {
    "fail_on_missing_required_columns": False,
    "fail_on_empty_dataset": True,
    "write_quality_reports": True,
}

SOURCES = [
    {
        "source_id": "agenas_portale_statistico",
        "provider": "AGENAS",
        "dataset_name": "Portale Statistico AGENAS",
        "theme": "portale_statistico",
        "source_page_url": "https://stat.agenas.it/web/index.php?r=site%2Fpublic",
        "download_url_csv": "",
        "download_url_json": "",
        "download_url_xml": "",
        "access_type": "dashboard",
        "license": "da_verificare",
        "redistribution_allowed": "unclear",
        "output_subfolder": "agenas/portale_statistico",
        "enabled": False,
    },
    {
        "source_id": "agenas_pne",
        "provider": "AGENAS",
        "dataset_name": "Programma Nazionale Esiti",
        "theme": "pne",
        "source_page_url": "https://www.agenas.gov.it/ricerca-e-sviluppo/758-che-cosa-e-pne",
        "download_url_csv": "",
        "download_url_json": "",
        "download_url_xml": "",
        "access_type": "manual_review",
        "license": "da_verificare",
        "redistribution_allowed": "unclear",
        "output_subfolder": "agenas/pne",
        "enabled": False,
    },
    {
        "source_id": "agenas_pnla",
        "provider": "AGENAS",
        "dataset_name": "Piattaforma Nazionale Liste di Attesa",
        "theme": "liste_attesa",
        "source_page_url": "https://www.portaletrasparenzaservizisanitari.it/piattaforma-nazionale-delle-liste-di-attesa/",
        "download_url_csv": "",
        "download_url_json": "",
        "download_url_xml": "",
        "access_type": "dashboard",
        "license": "da_verificare",
        "redistribution_allowed": "unclear",
        "output_subfolder": "agenas/pnla",
        "enabled": False,
    },
    {
        "source_id": "ministero_salute_open_data",
        "provider": "Ministero della Salute",
        "dataset_name": "Open Data Ministero della Salute",
        "theme": "open_data",
        "source_page_url": "https://www.dati.salute.gov.it/",
        "download_url_csv": "",
        "download_url_json": "",
        "download_url_xml": "",
        "access_type": "web_page",
        "license": "Italian Open Data License v2.0",
        "redistribution_allowed": "yes",
        "output_subfolder": "ministero_salute/open_data",
        "enabled": False,
    },
]
