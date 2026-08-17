# Data Access

This project uses **Predictors of Hospital Onset Infection: A Matched Retrospective
Cohort Dataset (v1.0.0)**, published on PhysioNet:
https://doi.org/10.13026/k70x-0m81

## Why the data isn't in this repo

This is a **credentialed-access** PhysioNet resource, released under the
PhysioNet Credentialed Health Data License 1.5.0 and Data Use Agreement 1.5.0.
The DUA prohibits redistributing the raw data outside the approved access
mechanism, so `HO_infxn_analysis.csv` is git-ignored (`data/raw/`, see
[.gitignore](.gitignore)) and must never be pushed to this or any public repo.

## Getting access

1. Become a credentialed PhysioNet user (requires institutional affiliation
   and completion of CITI "Data or Specimens Only Research" training).
2. Sign the Data Use Agreement for this specific project.
3. Download `HO_infxn_analysis.csv` from
   https://physionet.org/content/hospital-onset-infection/1.0.0/
4. Place it at `data/raw/HO_infxn_analysis.csv` in your local clone.

## Dataset summary (from the PhysioNet data dictionary, `docs/data_dictionary.pdf`)

One CSV (`HO_infxn_analysis.csv`) contains **both** cohorts, distinguished by
the `analysis` column:

- **`environmental`** — cases/controls matched on age (±5y), sex, prior
  surgery, room LOS, and antibiotic exposure history. Primary predictors are
  ward-level colonization pressure columns (`{pathogen}_cp`).
- **`patient`** — cases/controls matched on hospital ward, admission
  month/year, and room LOS — **not** age or sex. Primary predictors are
  antibiotic class exposure counts (`{abx_class}_0_60`).

Each row is one hospitalization; `run` gives the target pathogen (11 total,
this project filters to `run == "MRSA"`); `group_binary` is the case (1) /
control (0) label.

Key columns needing cleanup before analysis:

- `age`: numeric except patients ≥90, recorded as the string `">90"` for
  privacy — must be handled before treating age as numeric (see
  [notebooks/01_eda.ipynb](notebooks/01_eda.ipynb)).
- `time_to_infxn`, `matching_duration`: `N/A` for controls.

Full column-by-column definitions are in `docs/data_dictionary.pdf`
(the public PhysioNet project page — not restricted).
