"""
Script: 11_costs.py

Modulo iniziale per costi e spesa.
"""

import pandas as pd


def aggregate_costs(df, group_cols, cost_col):
    return df.groupby(group_cols, dropna=False)[cost_col].sum().reset_index()


def add_cost_per_capita(df, cost_col, population_col, output_col):
    df = df.copy()
    df[output_col] = df[cost_col] / df[population_col]
    return df
