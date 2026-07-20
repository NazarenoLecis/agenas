# %%
# Strutture sanitarie
#
# Analisi di readiness per fonti e dataset sulle strutture sanitarie.
# Il notebook usa metadati, link validati e dimensioni prodotte dalla pipeline.

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
# Per le strutture sanitarie non basta sapere che esiste una pagina: servono
# identificativi stabili di struttura, territorio, tipo, accreditamento e periodo.
# Questo notebook valuta quanto siamo vicini a quella base dati.

# %%
catalog = read_clean_csv(CATALOG_DIR / "data_catalog.csv")
registry = read_clean_csv(TABLES / "dataset_registry.csv")
validated = read_clean_csv(TABLES / "validated_discovered_links.csv")
recursive = read_clean_csv(TABLES / "recursive_public_discovery.csv")
agenas_links = read_clean_csv(TABLES / "agenas_links.csv")
dim_structure = read_clean_csv(TABLES / "dim_structure.csv")
dim_region = read_clean_csv(TABLES / "dim_region.csv")

structure_pattern = "struttur|ospedal|presidio|accredit|stabiliment|casa di cura|asl|azienda"

structure_sources = catalog[
    (catalog.get("theme", pd.Series("", index=catalog.index)) == "structures")
    | contains_any(catalog, ["dataset_name", "output_subfolder", "source_page_url"], structure_pattern)
].copy() if not catalog.empty else pd.DataFrame()

registry_mask = contains_any(registry, ["theme", "dataset_name", "link_text", "candidate_url", "final_url"], structure_pattern)
structure_registry = registry[registry_mask].copy() if not registry.empty else pd.DataFrame()

validated_mask = contains_any(validated, ["source_id", "link_text", "found_url", "final_url"], structure_pattern)
structure_validated = validated[validated_mask].copy() if not validated.empty else pd.DataFrame()

summary = pd.DataFrame(
    [
        {"area": "fonti catalogo strutture", "value": len(structure_sources)},
        {"area": "link registry pertinenti", "value": len(structure_registry)},
        {"area": "link validati pertinenti", "value": len(structure_validated)},
        {"area": "righe dim_structure", "value": len(dim_structure)},
        {"area": "righe dim_region", "value": len(dim_region)},
    ]
)
display(summary)
display(structure_sources.head(20))

# %% [markdown]
# ## Fonti e copertura
#
# La prima verifica e' se il tema strutture ha fonti dedicate, oppure se dipende
# da link indiretti trovati in portali generali.

# %%
if not structure_sources.empty:
    source_counts = structure_sources.groupby(["provider", "access_type"], dropna=False).size().reset_index(name="sources")
    display(source_counts)
    plot_barh(source_counts.groupby("provider")["sources"].sum().reset_index(), "provider", "sources", "Fonti strutture per provider", color="#0f766e")
else:
    print("Nessuna fonte strutture esplicita nel catalogo.")

if not agenas_links.empty:
    agenas_structure_links = agenas_links[contains_any(agenas_links, ["link_text", "url"], structure_pattern)].copy()
    print("Link Agenas pertinenti:", len(agenas_structure_links))
    display(agenas_structure_links.head(30))

# %% [markdown]
# ## Link candidati e validazione
#
# I candidati migliori sono file tabellari validati; i PDF sono utili per
# metodologia o definizioni, ma non bastano per costruire una dimensione
# struttura analitica.

# %%
if not structure_registry.empty:
    if "file_extension" in structure_registry.columns:
        ext_counts = structure_registry.groupby("file_extension", dropna=False).size().reset_index(name="links")
        plot_barh(ext_counts, "file_extension", "links", "Formati candidati per strutture", color="#7c3aed")
    if "provider" in structure_registry.columns:
        provider_counts = structure_registry.groupby("provider", dropna=False).size().reset_index(name="links")
        plot_barh(provider_counts, "provider", "links", "Link strutture per provider", color="#2563eb")
    columns = ["provider", "source_id", "dataset_name", "file_extension", "validation_status_code", "license", "candidate_url"]
    display(structure_registry[[column for column in columns if column in structure_registry.columns]].head(30))
else:
    print("Nessun link strutture nel registry.")

if not structure_validated.empty:
    status_counts = structure_validated.groupby("validation_status_code", dropna=False).size().reset_index(name="links")
    status_counts["validation_status_code"] = status_counts["validation_status_code"].astype(str)
    plot_barh(status_counts, "validation_status_code", "links", "Validazione link strutture", color="#b45309")
    display(status_counts)

# %% [markdown]
# ## Schema dimensionale atteso
#
# La dimensione `dim_structure` e' oggi un template. Questo e' utile: consente di
# sapere quali campi devono esistere quando una fonte viene normalizzata.

# %%
if not dim_structure.empty:
    display(dim_structure.head(20))
else:
    expected_columns = ["structure_code", "structure_name", "asl_code", "region_code"]
    display(pd.DataFrame({"expected_column": expected_columns}))

processed_files = list(PROCESSED.rglob("*.csv")) if PROCESSED.exists() else []
structure_processed = [path for path in processed_files if "structure" in str(path).lower() or "struttur" in str(path).lower()]
display(pd.DataFrame({"processed_structure_file": [str(path.relative_to(ROOT)) for path in structure_processed]}))

# %% [markdown]
# ## Gap analysis
#
# Qui trasformiamo la readiness in una lista di lavoro. Le priorita sono:
# fonte con licenza chiara, formato tabellare, identificativi struttura e
# granularita territoriale.

# %%
rows = []
rows.append({"check": "fonte catalogo dedicata", "passed": not structure_sources.empty, "note": f"{len(structure_sources)} fonti trovate"})
rows.append({"check": "link registry pertinente", "passed": not structure_registry.empty, "note": f"{len(structure_registry)} link trovati"})
rows.append({"check": "link dati tabellare", "passed": bool(not structure_registry.empty and structure_registry.get("is_data_file", pd.Series(False, index=structure_registry.index)).fillna(False).astype(bool).any()), "note": "richiede file dati validato"})
rows.append({"check": "dimensione struttura popolata", "passed": len(dim_structure) > 0, "note": f"{len(dim_structure)} righe"})
rows.append({"check": "dataset strutture processato", "passed": len(structure_processed) > 0, "note": f"{len(structure_processed)} file"})
readiness = pd.DataFrame(rows)
display(readiness)
plot_barh(readiness.assign(value=readiness["passed"].astype(int)), "check", "value", "Readiness strutture", xlabel="0/1", color="#be123c")

# %% [markdown]
# ## Tabella candidati per analisi
#
# La tabella sotto e' il punto di partenza per scegliere le fonti da aprire,
# scaricare o normalizzare.

# %%
if not structure_registry.empty:
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
    candidate_columns = [column for column in candidate_columns if column in structure_registry.columns]
    structure_candidates = structure_registry[candidate_columns].copy()
    if "validation_status_code" in structure_candidates.columns:
        structure_candidates["validation_status_code"] = pd.to_numeric(structure_candidates["validation_status_code"], errors="coerce")
        structure_candidates = structure_candidates.sort_values(["validation_status_code", "provider", "source_id"], na_position="last")
    display(structure_candidates.head(80))
else:
    print("Nessun candidato strutture da filtrare.")
