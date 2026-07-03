# Agenas data analysis

Repository per catalogare, scaricare, normalizzare e analizzare dati pubblici del Servizio sanitario nazionale da fonti istituzionali.

Il progetto parte da Agenas e integra Ministero della Salute, ISTAT, OpenBDAP, AIFA e fonti regionali ufficiali.

## Obiettivo

Costruire una base dati riproducibile per ottenere e analizzare tutto cio che e disponibile dalle fonti pubbliche sanitarie, con dettaglio nazionale, regionale, aziendale, territoriale, di struttura, di prestazione e di periodo quando la fonte lo consente.

Il repository non parte da una singola analisi prioritaria. L'obiettivo e costruire un'infrastruttura dati ampia, estendibile e documentata.

## Ambiti coperti

Il progetto deve mappare tutte le fonti disponibili su mobilita sanitaria, personale, tempi di attesa, costi, spesa, prestazioni, emergenza, ricoveri, attivita ospedaliera, assistenza territoriale, dotazioni, strutture, accreditamento, farmaci, demografia e indicatori di esito.

## Metodologia

Ogni analisi deve riportare fonte, anno, livello territoriale, definizione dell'indicatore e limiti del dato.

Gli indicatori non devono essere letti come giudizi automatici. Le differenze tra territori e strutture possono dipendere da codifiche, volumi, composizione dei casi, disponibilita dei dati e criteri di inclusione.

Il PNE deve essere usato come fonte di indicatori comparativi. Il repository non deve trasformarlo in una classifica secca di strutture.

## Regole del codice

- usare file utils per le funzioni riutilizzabili;
- non usare classi;
- non usare argparse;
- non creare file __init__.py;
- scrivere commenti estensivi;
- usare config/project_config.py per la configurazione;
- non usare file YAML per la configurazione;
- creare script per download CSV e JSON;
- creare notebook per analisi e grafici.

## Uso

Installare le dipendenze.

```bash
pip install -r requirements.txt
```

Per analisi geografiche:

```bash
pip install -r requirements-geo.txt
```

Eseguire tutta la pipeline.

```bash
python src/18_full_pipeline.py
```

Oppure eseguire i passaggi singoli.

```bash
python src/15_build_catalogs.py
python src/00_discover_sources.py
python src/01_download_ministero_salute.py
python src/02_download_Agenas.py
python src/03_normalize_ministero_salute.py
python src/04_normalize_Agenas.py
python src/05_build_indicators.py
python src/06_export_json.py
python src/07_build_charts.py
python src/16_data_requirements.py
python src/17_module_inventory.py
```

## Output

- data_catalog/data_catalog.csv
- data_catalog/analysis_modules.csv
- data_catalog/discovered_links.csv
- metadata/downloads_log.csv
- data/processed/
- outputs/figures/
- outputs/tables/
- outputs/dashboard_data/
