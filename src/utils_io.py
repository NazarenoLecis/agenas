"""
Utility di input e output.

Queste funzioni leggono e salvano tabelle in CSV, JSON, XLSX e Parquet.
Gli script principali usano queste funzioni per mantenere un comportamento
coerente tra download, normalizzazione, indicatori e notebook.

Per gli output pubblici del progetto, CSV e JSON sono i formati obbligatori.
"""

from pathlib import Path
import json
import pandas as pd


def read_table(path):
    """
    Legge una tabella in base all'estensione del file.
    """
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix == ".json":
        return pd.read_json(path)
    if suffix in [".xlsx", ".xls"]:
        return pd.read_excel(path)
    if suffix == ".parquet":
        return pd.read_parquet(path)
    raise ValueError(f"Unsupported table format: {suffix}")


def write_table(df, path):
    """
    Salva una tabella in base all'estensione del file.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        df.to_csv(path, index=False)
        return path
    if suffix == ".json":
        df.to_json(path, orient="records", force_ascii=False, indent=2)
        return path
    if suffix == ".parquet":
        df.to_parquet(path, index=False)
        return path
    if suffix == ".xlsx":
        df.to_excel(path, index=False)
        return path
    raise ValueError(f"Unsupported output format: {suffix}")


def write_csv_json_pair(df, folder, stem):
    """
    Salva una tabella nello stesso folder in CSV e JSON.
    """
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    csv_path = write_table(df, folder / f"{stem}.csv")
    json_path = write_table(df, folder / f"{stem}.json")
    return {"csv": csv_path, "json": json_path}


def write_json_object(data, path):
    """
    Salva un oggetto Python come JSON leggibile.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    return path
