"""
Utility DuckDB.

Il modulo crea un database locale a partire dai file CSV e Parquet presenti in
cartelle del progetto. Serve per interrogare molti dataset senza caricarli tutti
in memoria con pandas.
"""

from pathlib import Path
import re
import duckdb


def connect_database(database_path):
    database_path = Path(database_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(database_path))


def safe_table_name(path, root=None):
    """
    Crea un nome tabella stabile usando il percorso relativo.

    Usare solo lo stem del file causa collisioni quando due cartelle contengono
    file con lo stesso nome, per esempio diversi dataset `data.csv`.
    """
    path = Path(path)
    if root is not None:
        try:
            name = str(path.relative_to(root).with_suffix(""))
        except ValueError:
            name = str(path.with_suffix(""))
    else:
        name = str(path.with_suffix(""))
    name = name.lower().replace("\\", "_").replace("/", "_")
    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name or "table"


def quote_identifier(identifier):
    """
    Quota un identificatore DuckDB in modo sicuro.
    """
    return '"' + str(identifier).replace('"', '""') + '"'


def register_file(connection, file_path, table_name=None, root=None):
    file_path = Path(file_path)
    table_name = table_name or safe_table_name(file_path, root=root)
    quoted_table_name = quote_identifier(table_name)
    if file_path.suffix.lower() == ".csv":
        connection.execute(
            f"CREATE OR REPLACE VIEW {quoted_table_name} AS SELECT * FROM read_csv_auto(?)",
            [str(file_path)],
        )
    elif file_path.suffix.lower() == ".parquet":
        connection.execute(
            f"CREATE OR REPLACE VIEW {quoted_table_name} AS SELECT * FROM read_parquet(?)",
            [str(file_path)],
        )
    else:
        return None
    return table_name


def register_folder(connection, folder_path):
    folder_path = Path(folder_path)
    tables = []
    seen = set()
    for file_path in sorted(list(folder_path.rglob("*.csv")) + list(folder_path.rglob("*.parquet"))):
        table_name = safe_table_name(file_path, root=folder_path)
        if table_name in seen:
            continue
        seen.add(table_name)
        registered = register_file(connection, file_path, table_name=table_name, root=folder_path)
        if registered:
            tables.append(registered)
    return tables
