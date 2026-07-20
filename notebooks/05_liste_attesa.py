# %%
# Liste di attesa
#
# Analisi di readiness per tempi di attesa, PNLA e fonti regionali.

from pathlib import Path
import sys
import pandas as pd
from IPython.display import display

for path in [Path.cwd(), *Path.cwd().parents]:
    helper_path = path / "notebooks" / "utils_notebooks.py"
    if helper_path.exists():
        sys.path.insert(0, str(helper_path.parent))
        break

from utils_notebooks import contains_any, get_project_paths, plot_barh, read_clean_csv

pd.set_option("display.max_columns", 80)
pd.set_option("display.max_colwidth", 140)

PATHS = get_project_paths()
ROOT = PATHS["root"]
CATALOG_DIR = PATHS["catalog"]
TABLES = PATHS["tables"]
PROCESSED = PATHS["processed"]
print("Project root:", ROOT)

# %% [markdown]
# ## Scopo
#
# Le liste di attesa richiedono granularita per regione, prestazione, classe di
# priorita e periodo. Questo notebook non inventa indicatori dove il dato manca:
# misura invece quanto la pipeline e' pronta a produrli.

# %%
catalog = read_clean_csv(CATALOG_DIR / "data_catalog.csv")
regional_seed = read_clean_csv(CATALOG_DIR / "regional_sources_seed.csv")
discovered = read_clean_csv(CATALOG_DIR / "discovered_links.csv")
validated = read_clean_csv(TABLES / "validated_discovered_links.csv")
registry = read_clean_csv(TABLES / "dataset_registry.csv")
recursive = read_clean_csv(TABLES / "recursive_public_discovery.csv")
quality = read_clean_csv(TABLES / "quality_overview.csv")

waiting_pattern = "attesa|pnla|priorita|priorita|prestazion|tempo|tempi|classe"

waiting_sources = catalog[
    (catalog.get("theme", pd.Series("", index=catalog.index)) == "waiting_times")
    | contains_any(catalog, ["source_id", "dataset_name", "source_page_url", "output_subfolder"], waiting_pattern)
].copy() if not catalog.empty else pd.DataFrame()

waiting_seed = regional_seed[regional_seed.get("module_id", pd.Series("", index=regional_seed.index)) == "waiting_times"].copy() if not regional_seed.empty else pd.DataFrame()
waiting_registry = registry[contains_any(registry, ["theme", "dataset_name", "link_text", "candidate_url", "final_url"], waiting_pattern)].copy() if not registry.empty else pd.DataFrame()
waiting_validated = validated[contains_any(validated, ["source_id", "link_text", "found_url", "final_url"], waiting_pattern)].copy() if not validated.empty else pd.DataFrame()
waiting_recursive = recursive[contains_any(recursive, ["source_id", "link_text", "found_url", "page_url"], waiting_pattern)].copy() if not recursive.empty else pd.DataFrame()

summary = pd.DataFrame(
    [
        {"area": "fonti catalogo waiting_times", "value": len(waiting_sources)},
        {"area": "regioni nel seed waiting_times", "value": waiting_seed["region"].nunique() if "region" in waiting_seed.columns else 0},
        {"area": "link registry pertinenti", "value": len(waiting_registry)},
        {"area": "link validati pertinenti", "value": len(waiting_validated)},
        {"area": "link ricorsivi pertinenti", "value": len(waiting_recursive)},
    ]
)
display(summary)
display(waiting_sources.head(20))

# %% [markdown]
# ## Fonti nazionali e PNLA
#
# La fonte Agenas PNLA e' catalogata come dashboard. Questo e' importante:
# una dashboard puo' essere molto informativa, ma non equivale automaticamente a
# un dataset tabellare scaricabile.

# %%
if not waiting_sources.empty:
    columns = ["provider", "source_id", "dataset_name", "access_type", "license", "redistribution_allowed", "download_status", "source_page_url"]
    display(waiting_sources[[column for column in columns if column in waiting_sources.columns]])
    source_counts = waiting_sources.groupby(["provider", "access_type"], dropna=False).size().reset_index(name="sources")
    plot_barh(source_counts, "access_type", "sources", "Fonti liste attesa per tipo accesso", color="#0f766e")
else:
    print("Nessuna fonte waiting_times nel catalogo.")

# %% [markdown]
# ## Copertura regionale
#
# Le liste di attesa sono fortemente regionali. Il seed indica le regioni da
# mappare, ma molte possono non avere ancora URL ufficiali salvati.

# %%
if not waiting_seed.empty:
    waiting_seed["has_source_url"] = waiting_seed.get("source_page_url", "").fillna("").astype(str).str.strip() != ""
    waiting_seed["has_download_url"] = waiting_seed.get("download_url", "").fillna("").astype(str).str.strip() != ""
    status_counts = waiting_seed.groupby("status", dropna=False).size().reset_index(name="regions")
    url_counts = pd.DataFrame(
        [
            {"url_type": "source_page_url", "regions": int(waiting_seed["has_source_url"].sum())},
            {"url_type": "download_url", "regions": int(waiting_seed["has_download_url"].sum())},
            {"url_type": "missing_any_url", "regions": int((~(waiting_seed["has_source_url"] | waiting_seed["has_download_url"])).sum())},
        ]
    )
    display(status_counts)
    display(url_counts)
    plot_barh(status_counts, "status", "regions", "Stato mapping regionale liste attesa", color="#b45309")
    plot_barh(url_counts, "url_type", "regions", "URL regionali disponibili", color="#7c3aed")
    display(waiting_seed.sort_values(["status", "region"]).head(40))
else:
    print("Seed regionale waiting_times non disponibile.")

# %% [markdown]
# ## Link candidati
#
# Questa sezione cerca link pertinenti a liste di attesa in registry, validazione
# e discovery ricorsiva. L'obiettivo e' separare report/documentazione da file
# dati scaricabili.

# %%
if not waiting_registry.empty:
    if "file_extension" in waiting_registry.columns:
        extension_counts = waiting_registry.groupby("file_extension", dropna=False).size().reset_index(name="links")
        plot_barh(extension_counts, "file_extension", "links", "Formati candidati liste attesa", color="#2563eb")
    columns = ["provider", "source_id", "dataset_name", "file_extension", "validation_status_code", "license", "candidate_url"]
    display(waiting_registry[[column for column in columns if column in waiting_registry.columns]].head(30))
else:
    print("Nessun candidato waiting_times nel registry.")

if not waiting_validated.empty:
    status_counts = waiting_validated.groupby("validation_status_code", dropna=False).size().reset_index(name="links")
    status_counts["validation_status_code"] = status_counts["validation_status_code"].astype(str)
    plot_barh(status_counts, "validation_status_code", "links", "Validazione link liste attesa", color="#be123c")
    display(status_counts)

if not waiting_recursive.empty:
    recursive_counts = waiting_recursive.groupby("link_type", dropna=False).size().reset_index(name="links")
    plot_barh(recursive_counts, "link_type", "links", "Link ricorsivi pertinenti per tipo", color="#0f766e")
    display(waiting_recursive[["source_id", "page_url", "found_url", "link_text", "link_type", "error"]].head(30))

# %% [markdown]
# ## Schema analitico minimo
#
# Un dataset utilizzabile per tempi di attesa dovrebbe arrivare almeno a:
# regione, prestazione, classe priorita, periodo, volume, tempo atteso o quota
# entro soglia. Questa cella rende esplicito lo schema prima della normalizzazione.

# %%
expected_columns = [
    "region_code",
    "region_name",
    "provider",
    "service_code",
    "service_name",
    "priority_class",
    "period",
    "year",
    "waiting_time_days",
    "within_threshold_share",
    "bookings_or_cases",
    "source_id",
]
display(pd.DataFrame({"expected_column": expected_columns}))

processed_files = list(PROCESSED.rglob("*.csv")) if PROCESSED.exists() else []
waiting_processed = [path for path in processed_files if "waiting" in str(path).lower() or "attesa" in str(path).lower()]
display(pd.DataFrame({"processed_waiting_file": [str(path.relative_to(ROOT)) for path in waiting_processed]}))

# %% [markdown]
# ## Readiness e prossime priorita
#
# La readiness combina fonte catalogata, mappa regionale, link validati e dataset
# processati. Il risultato e' una check-list di lavoro, non un giudizio clinico.

# %%
has_data_candidate = False
if not waiting_registry.empty and "is_data_file" in waiting_registry.columns:
    has_data_candidate = waiting_registry["is_data_file"].fillna(False).astype(bool).any()

rows = [
    {"check": "fonte nazionale catalogata", "passed": not waiting_sources.empty, "note": f"{len(waiting_sources)} fonti"},
    {"check": "seed regionale presente", "passed": not waiting_seed.empty, "note": f"{len(waiting_seed)} righe"},
    {"check": "link pertinente validato", "passed": not waiting_validated.empty, "note": f"{len(waiting_validated)} link"},
    {"check": "file dati candidato", "passed": bool(has_data_candidate), "note": "richiede formato tabellare validato"},
    {"check": "dataset processato", "passed": len(waiting_processed) > 0, "note": f"{len(waiting_processed)} file"},
]
readiness = pd.DataFrame(rows)
display(readiness)
plot_barh(readiness.assign(value=readiness["passed"].astype(int)), "check", "value", "Readiness liste attesa", xlabel="0/1", color="#9333ea")

# %% [markdown]
# ## Tabella candidati per analisi
#
# Questa tabella mette insieme i link piu' pertinenti e i campi necessari per
# decidere cosa aprire, scaricare o normalizzare.

# %%
if not waiting_registry.empty:
    candidate_columns = [
        "provider",
        "source_id",
        "dataset_name",
        "file_extension",
        "validation_status_code",
        "is_data_file",
        "is_report_file",
        "license",
        "candidate_url",
    ]
    candidate_columns = [column for column in candidate_columns if column in waiting_registry.columns]
    waiting_candidates = waiting_registry[candidate_columns].copy()
    if "validation_status_code" in waiting_candidates.columns:
        waiting_candidates["validation_status_code"] = pd.to_numeric(waiting_candidates["validation_status_code"], errors="coerce")
        waiting_candidates = waiting_candidates.sort_values(["validation_status_code", "provider", "source_id"], na_position="last")
    display(waiting_candidates.head(80))
else:
    print("Nessun candidato liste attesa da filtrare.")
