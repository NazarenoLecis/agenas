# %%
# Strutture

from pathlib import Path
import pandas as pd

ROOT = Path.cwd()
processed_root = ROOT / "data" / "processed"
files = list(processed_root.rglob("*.csv")) if processed_root.exists() else []
files[:10]
