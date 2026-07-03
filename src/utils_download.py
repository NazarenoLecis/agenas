"""
Utility per il download di file pubblici.

Le funzioni sono volutamente semplici. Scaricano solo URL diretti indicati nella
configurazione Python o nel catalogo. Ogni download produce metadati utili per
controllare dimensione, stato e checksum del file.
"""

from pathlib import Path
from datetime import datetime
import hashlib
import requests


DEFAULT_HEADERS = {
    "User-Agent": "agenas-health-data-analysis/0.1"
}


def compute_sha256(path):
    """
    Calcola il checksum SHA256 di un file locale.
    """
    path = Path(path)
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def infer_extension_from_url(url):
    """
    Deduce una estensione semplice dall'URL.
    """
    clean_url = url.split("?")[0].split("#")[0]
    suffix = Path(clean_url).suffix.lower().replace(".", "")
    if suffix:
        return suffix
    return "dat"


def download_file(url, output_path, timeout_seconds=60):
    """
    Scarica un file da un URL e lo salva nel percorso indicato.

    La funzione restituisce un dizionario con informazioni sul download.
    In caso di errore, il dizionario contiene success=False e il messaggio.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "download_url": url,
        "local_path": str(output_path),
        "downloaded_at": datetime.now().isoformat(timespec="seconds"),
        "http_status": None,
        "file_size_bytes": None,
        "sha256": None,
        "success": False,
        "error_message": "",
    }
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout_seconds)
        result["http_status"] = response.status_code
        response.raise_for_status()
        output_path.write_bytes(response.content)
        result["file_size_bytes"] = output_path.stat().st_size
        result["sha256"] = compute_sha256(output_path)
        result["success"] = True
    except Exception as error:
        result["error_message"] = str(error)
    return result
