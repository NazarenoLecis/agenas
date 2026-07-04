# Modulo spesa sanitaria regionale

File aggiunti:

```text
config/health_expenditure_config.py
src/52_build_health_expenditure_framework.py
metadata/health_expenditure_note.md
```

Esecuzione:

```bash
python src/52_build_health_expenditure_framework.py
```

Il modulo produce sempre CSV e JSON.

Output principali:

```text
outputs/tables/health_expenditure_source_plan.csv
outputs/tables/health_expenditure_required_schema.csv
outputs/tables/health_expenditure_denominator_dictionary.csv
outputs/tables/health_expenditure_denominator_rules.csv
outputs/tables/regional_health_expenditure_demographic_adjusted.csv

data/processed/demography/demographic_denominators_region_year.csv
data/processed/prices/price_deflators.csv
data/processed/health_expenditure/regional_health_expenditure_demographic_adjusted.csv
```

I file JSON equivalenti vengono generati negli stessi folder.

Fonti previste:

- OpenBDAP / RGS per Conto Economico degli enti del SSN
- SIOPE / RGS per pagamenti e incassi di cassa
- ISTAT per popolazione, nascite e deflatori

Lo schema finale include spesa nominale, spesa reale, popolazione totale, popolazione per eta, nascite, donne 15-49, popolazione over 65, over 75 e over 80, spesa pro capite e spesa per popolazione rilevante.

Il Conto Economico misura costi e ricavi di competenza. SIOPE misura incassi e pagamenti di cassa. Il campo `accounting_basis` serve a tenere distinti questi due piani.
