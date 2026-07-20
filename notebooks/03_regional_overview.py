# %%
# Regional overview
#
# Questo notebook in formato Python usa le celle Jupyter percent.
# L'analisi misura copertura regionale, gap di mapping e priorita operative.

from pathlib import Path
import sys
import pandas as pd
from IPython.display import display

for path in [Path.cwd(), *Path.cwd().parents]:
    helper_path = path / "notebooks" / "utils_notebooks.py"
    if helper_path.exists():
        sys.path.insert(0, str(helper_path.parent))
        break

from utils_notebooks import get_project_paths, has_any_value, plot_barh, plot_matrix, read_clean_csv

pd.set_option("display.max_columns", 80)
pd.set_option("display.max_colwidth", 120)

PATHS = get_project_paths()
ROOT = PATHS["root"]
CATALOG_DIR = PATHS["catalog"]
TABLES = PATHS["tables"]
print("Project root:", ROOT)

# %% [markdown]
# ## Caricamento dati
#
# Il notebook usa soprattutto `regional_sources_seed.csv`: e' la mappa di lavoro
# delle regioni per modulo. La confrontiamo con catalogo, registry e ranking per
# capire dove ci sono fonti nazionali, dove servono portali regionali e dove
# manca ancora dato scaricabile.

# %%
regional_seed = read_clean_csv(CATALOG_DIR / "regional_sources_seed.csv")
catalog = read_clean_csv(CATALOG_DIR / "data_catalog.csv")
modules = read_clean_csv(CATALOG_DIR / "analysis_modules.csv")
registry = read_clean_csv(TABLES / "dataset_registry.csv")
source_ranking = read_clean_csv(TABLES / "source_ranking.csv")
quality = read_clean_csv(TABLES / "quality_overview.csv")

summary = pd.DataFrame(
    [
        {"area": "righe seed regionali", "value": len(regional_seed)},
        {"area": "regioni nel seed", "value": regional_seed["region"].nunique() if "region" in regional_seed.columns else 0},
        {"area": "moduli nel seed", "value": regional_seed["module_id"].nunique() if "module_id" in regional_seed.columns else 0},
        {"area": "fonti catalogate", "value": len(catalog)},
        {"area": "righe registry", "value": len(registry)},
    ]
)
display(summary)
display(regional_seed.head(20))

# %% [markdown]
# ## Copertura regionale per modulo
#
# Una copertura regionale seria richiede due letture: ampiezza geografica e
# ampiezza tematica. La matrice seguente mostra dove il seed prevede una ricerca
# fonte per ciascun modulo.

# %%
if not regional_seed.empty and {"region", "module_id"}.issubset(regional_seed.columns):
    region_counts = regional_seed.groupby("region", dropna=False).size().reset_index(name="module_slots")
    module_counts = regional_seed.groupby("module_id", dropna=False).size().reset_index(name="regions")
    plot_barh(region_counts, "region", "module_slots", "Slot analitici per regione", color="#0f766e")
    plot_barh(module_counts, "module_id", "regions", "Regioni coperte per modulo", color="#7c3aed")

    matrix = regional_seed.pivot_table(index="region", columns="module_id", values="status", aggfunc="count", fill_value=0)
    display(matrix)
    plot_matrix(matrix, "Matrice regione x modulo")
else:
    print("Seed regionale non disponibile o incompleto.")

# %% [markdown]
# ## Stato mapping e gap operativo
#
# Il campo `status` segnala se una fonte regionale e' ancora da mappare. Questo
# e' il backlog concreto: una regione/modulo senza URL non va trattata come dato
# mancante sanitario, ma come fonte ancora da identificare o verificare.

# %%
if not regional_seed.empty:
    status_counts = regional_seed.groupby("status", dropna=False).size().reset_index(name="items")
    plot_barh(status_counts, "status", "items", "Stato mapping regionale", color="#b45309")

    url_columns = [column for column in ["source_page_url", "download_url"] if column in regional_seed.columns]
    gap = regional_seed.copy()
    if url_columns:
        gap["has_any_url"] = gap[url_columns].apply(has_any_value, axis=1)
    else:
        gap["has_any_url"] = False
    gap_summary = gap.groupby(["module_id", "status", "has_any_url"], dropna=False).size().reset_index(name="items")
    display(gap_summary.sort_values(["module_id", "status", "has_any_url"]))

    missing_urls = gap[~gap["has_any_url"]].copy()
    display(missing_urls[["region", "module_id", "status", "license", "notes"]].head(40))
else:
    print("Nessun seed regionale da analizzare.")

# %% [markdown]
# ## Connessione con fonti nazionali e registry
#
# Il seed regionale non vive da solo: alcuni temi possono essere coperti meglio
# da fonti nazionali o da registry gia' validati. Qui confrontiamo moduli
# regionali e catalogo per evitare duplicazioni di lavoro.

# %%
if not catalog.empty and not regional_seed.empty:
    national_by_theme = catalog.groupby("theme", dropna=False).size().reset_index(name="national_sources")
    regional_by_theme = regional_seed.groupby("module_id", dropna=False).size().reset_index(name="regional_slots")
    coverage = regional_by_theme.merge(national_by_theme, left_on="module_id", right_on="theme", how="left")
    coverage["national_sources"] = pd.to_numeric(coverage["national_sources"], errors="coerce").fillna(0).astype(int)
    display(coverage[["module_id", "regional_slots", "national_sources"]].sort_values("regional_slots", ascending=False))
    plot_barh(coverage, "module_id", "national_sources", "Fonti nazionali disponibili per modulo regionale", color="#2563eb")

if not registry.empty and "theme" in registry.columns:
    registry_theme = registry.groupby("theme", dropna=False).size().reset_index(name="candidate_links")
    display(registry_theme.sort_values("candidate_links", ascending=False))
    plot_barh(registry_theme, "theme", "candidate_links", "Link candidati nel registry per tema", color="#be123c")

# %% [markdown]
# ## Priorita pratica
#
# La priorita non e' solo il numero di regioni: conta se esistono fonti nazionali
# riusabili, se i link sono validati e se la licenza e' chiara. La tabella sotto
# mette in fila i moduli con piu' lavoro regionale ancora aperto.

# %%
if not regional_seed.empty:
    priority = regional_seed.groupby("module_id", dropna=False).agg(
        regional_slots=("region", "count"),
        regions=("region", "nunique"),
        statuses=("status", lambda values: ";".join(sorted(set(values)))),
    ).reset_index()
    if not registry.empty and "theme" in registry.columns:
        candidate_counts = registry.groupby("theme", dropna=False).size().reset_index(name="candidate_links")
        priority = priority.merge(candidate_counts, left_on="module_id", right_on="theme", how="left")
    priority["candidate_links"] = pd.to_numeric(priority.get("candidate_links", 0), errors="coerce").fillna(0).astype(int)
    priority["regional_gap_score"] = priority["regional_slots"] - priority["candidate_links"].clip(upper=priority["regional_slots"])
    display(priority.sort_values(["regional_gap_score", "regional_slots"], ascending=False))
    plot_barh(priority, "module_id", "regional_gap_score", "Moduli con maggiore gap regionale", color="#9333ea")

# %% [markdown]
# ## Workplan regionale
#
# Questa tabella e' pensata per essere filtrata dall'utente: regione, modulo,
# stato mapping, presenza URL e priorita del modulo.

# %%
if not regional_seed.empty:
    workplan = regional_seed.copy()
    if "priority" in locals():
        workplan = workplan.merge(
            priority[["module_id", "regional_gap_score", "candidate_links"]],
            on="module_id",
            how="left",
        )
    url_columns = [column for column in ["source_page_url", "download_url"] if column in workplan.columns]
    workplan["has_any_url"] = workplan[url_columns].apply(has_any_value, axis=1) if url_columns else False
    display(workplan.sort_values(["regional_gap_score", "region", "module_id"], ascending=[False, True, True]).head(80))
