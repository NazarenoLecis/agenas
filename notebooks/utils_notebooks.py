"""
Utility leggere per i notebook di analisi.
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def find_project_root(start_path=Path.cwd()):
    for path in [start_path, *start_path.parents]:
        if (path / "README.md").exists() and (path / "src").exists():
            return path
    return Path.cwd()


def get_project_paths():
    root = find_project_root()
    return {
        "root": root,
        "catalog": root / "data_catalog",
        "tables": root / "outputs" / "tables",
        "metadata": root / "metadata",
        "processed": root / "data" / "processed",
    }


def read_csv_or_empty(path):
    path = Path(path)
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def clean_text_columns(df):
    output = df.copy()
    for column in output.columns:
        if output[column].dtype == "object":
            output[column] = output[column].fillna("").astype(str).str.strip()
    return output


def read_clean_csv(path):
    return clean_text_columns(read_csv_or_empty(path))


def show_table(df, rows=20):
    if df.empty:
        print("Nessun dato disponibile per questa tabella.")
        return
    try:
        from IPython.display import display

        display(df.head(rows))
    except Exception:
        print(df.head(rows).to_string(index=False))


def plot_barh(df, label_col, value_col, title, xlabel="Conteggio", limit=25, color="#2563eb"):
    if df.empty or label_col not in df.columns or value_col not in df.columns:
        print("Nessun dato sufficiente per il grafico:", title)
        return
    chart = df[[label_col, value_col]].dropna().copy()
    if chart.empty:
        print("Nessun dato sufficiente per il grafico:", title)
        return
    chart = chart.sort_values(value_col, ascending=True).tail(limit)
    fig, ax = plt.subplots(figsize=(10, max(4, 0.35 * len(chart))))
    ax.barh(chart[label_col].astype(str), chart[value_col], color=color)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("")
    plt.tight_layout()
    plt.show()


def plot_matrix(matrix, title, cmap="Blues"):
    if matrix.empty:
        print("Nessun dato sufficiente per il grafico:", title)
        return
    fig, ax = plt.subplots(figsize=(12, max(5, 0.35 * len(matrix))))
    ax.imshow(matrix.values, aspect="auto", cmap=cmap)
    ax.set_xticks(range(len(matrix.columns)))
    ax.set_xticklabels(matrix.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(matrix.index)))
    ax.set_yticklabels(matrix.index)
    ax.set_title(title)
    for y in range(matrix.shape[0]):
        for x in range(matrix.shape[1]):
            value = matrix.iloc[y, x]
            if value:
                ax.text(x, y, str(value), ha="center", va="center", color="black")
    plt.tight_layout()
    plt.show()


def contains_any(df, columns, pattern):
    if df.empty:
        return pd.Series(dtype=bool)
    mask = pd.Series(False, index=df.index)
    for column in columns:
        if column in df.columns:
            mask = mask | df[column].fillna("").astype(str).str.contains(pattern, case=False, regex=True, na=False)
    return mask


def has_any_value(values):
    for value in values:
        if pd.notna(value) and str(value).strip():
            return True
    return False
