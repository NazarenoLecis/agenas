"""
Utility per indicatori sanitari.

Le funzioni calcolano indicatori generici e mantengono numeratore e denominatore
quando possibile. Questo aiuta a controllare ogni trasformazione nei notebook.
"""

import pandas as pd


def add_rate_per_population(df, numerator_col, population_col, output_col, multiplier=100000):
    """
    Calcola un indicatore per abitanti.

    Esempio: posti letto per 100.000 abitanti.
    """
    df = df.copy()
    if numerator_col not in df.columns or population_col not in df.columns:
        df[output_col] = pd.NA
        return df
    df[output_col] = df[numerator_col] / df[population_col] * multiplier
    return df


def aggregate_sum(df, group_cols, value_cols):
    """
    Aggrega per somma le colonne numeriche indicate.
    """
    available_values = [column for column in value_cols if column in df.columns]
    available_groups = [column for column in group_cols if column in df.columns]
    if not available_groups or not available_values:
        return pd.DataFrame()
    return df.groupby(available_groups, dropna=False)[available_values].sum().reset_index()


def add_source_metadata(df, source):
    """
    Aggiunge metadati di fonte a una tabella derivata.
    """
    df = df.copy()
    df["source_id"] = source.get("source_id", "")
    df["provider"] = source.get("provider", "")
    df["source_page_url"] = source.get("source_page_url", "")
    df["license"] = source.get("license", "")
    return df
