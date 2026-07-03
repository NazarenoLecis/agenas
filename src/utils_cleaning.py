"""
Utility per pulizia e normalizzazione.

Le funzioni qui sotto applicano regole semplici: nomi colonna standardizzati,
spazi rimossi, codici territoriali trattati come stringhe e valori numerici
convertiti quando possibile.
"""

import re
import pandas as pd


def clean_column_name(column_name):
    """
    Converte un nome colonna in formato semplice snake_case.
    """
    name = str(column_name).strip().lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name


def clean_column_names(df):
    """
    Applica clean_column_name a tutte le colonne del DataFrame.
    """
    df = df.copy()
    df.columns = [clean_column_name(column) for column in df.columns]
    return df


def strip_string_columns(df):
    """
    Rimuove spazi iniziali e finali dalle colonne testuali.
    """
    df = df.copy()
    for column in df.select_dtypes(include="object").columns:
        df[column] = df[column].astype(str).str.strip()
    return df


def convert_numeric_columns(df, columns):
    """
    Converte in numerico le colonne indicate, se presenti.
    """
    df = df.copy()
    for column in columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def normalize_table(df):
    """
    Applica le trasformazioni minime comuni a tutti i dataset.
    """
    df = clean_column_names(df)
    df = strip_string_columns(df)
    return df
