"""
Script: 25_build_duckdb.py

Registra CSV e Parquet processati in un database DuckDB locale.
"""

from utils_paths import get_configured_path, ensure_project_folders
from utils_duckdb import connect_database, register_folder


def main():
    ensure_project_folders()
    database_path = get_configured_path("data_processed") / "Agenas.duckdb"
    processed_root = get_configured_path("data_processed")
    connection = connect_database(database_path)
    tables = register_folder(connection, processed_root)
    connection.close()
    print(f"Registered {len(tables)} tables in {database_path}")


if __name__ == "__main__":
    main()
