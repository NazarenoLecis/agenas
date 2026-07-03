"""
Utility per grafici statici.
"""

from pathlib import Path
import matplotlib.pyplot as plt


def save_bar_chart(df, x_col, y_col, output_path, title=""):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plot_df = df[[x_col, y_col]].dropna().copy().sort_values(y_col)
    plt.figure(figsize=(12, 7))
    plt.barh(plot_df[x_col].astype(str), plot_df[y_col])
    plt.title(title)
    plt.xlabel(y_col)
    plt.ylabel(x_col)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    return output_path


def save_line_chart(df, x_col, y_col, output_path, title=""):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plot_df = df[[x_col, y_col]].dropna().copy().sort_values(x_col)
    plt.figure(figsize=(12, 7))
    plt.plot(plot_df[x_col], plot_df[y_col], marker="o")
    plt.title(title)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    return output_path
