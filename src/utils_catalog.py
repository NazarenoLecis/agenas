"""
Utility per il catalogo delle fonti.

Il catalogo mantiene una riga per fonte con provider, URL, licenza, stato di
accesso e livello territoriale. Le funzioni in questo file permettono di
costruire il catalogo a partire da config/project_config.py.
"""

from datetime import datetime
import pandas as pd


CATALOG_COLUMNS = [
    "source_id",
    "provider",
    "dataset_name",
    "theme",
    "source_page_url",
    "download_url_csv",
    "download_url_json",
    "download_url_xml",
    "access_type",
    "license",
    "redistribution_allowed",
    "output_subfolder",
    "enabled",
    "last_checked",
    "download_status",
    "notes",
]


def sources_to_catalog(sources):
    """
    Converte la lista SOURCES della configurazione in un DataFrame.
    """
    rows = []
    checked_at = datetime.now().date().isoformat()
    for source in sources:
        row = {column: source.get(column, "") for column in CATALOG_COLUMNS}
        row["last_checked"] = checked_at
        row["download_status"] = "pending" if source.get("enabled") else "manual_review"
        row["notes"] = row.get("notes", "")
        rows.append(row)
    return pd.DataFrame(rows, columns=CATALOG_COLUMNS)


def filter_enabled_sources(sources, provider=None):
    """
    Restituisce solo le fonti abilitate.

    Se provider e valorizzato, mantiene solo le fonti di quel provider.
    """
    enabled = [source for source in sources if source.get("enabled")]
    if provider is None:
        return enabled
    return [source for source in enabled if source.get("provider") == provider]
