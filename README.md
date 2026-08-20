# MRSA Hospital-Onset Infection: Environmental vs. Patient Risk Factors

Portfolio project analyzing hospital-onset MRSA acquisition using the PhysioNet
[Predictors of Hospital Onset Infection](https://doi.org/10.13026/k70x-0m81)
matched retrospective cohort dataset.

## Research question

Does **ward-level colonization pressure** (environmental exposure) or
**antibiotic exposure history** (patient exposure) better predict
hospital-onset MRSA acquisition?

The source dataset provides two complementary matched case-control cohorts to
study this:

| | Environmental analysis | Patient analysis |
|---|---|---|
| Matched on | age, sex, prior surgery, room LOS, antibiotic history | ward, admission month/year, room LOS |
| Primary predictor | ward colonization pressure (`MRSA_cp`, etc.) | antibiotic class exposure counts |
| Not matched on | — | age, sex |

Because the patient-analysis cohort is **not** matched on age/sex, the
patient-analysis logistic regression model controls for age and sex
explicitly as covariates; the environmental-analysis model does not need to
(matching already balances them).

## Findings

Patient demographics and exposure history predict MRSA acquisition meaningfully
better than ward colonization pressure (test AUC 0.637 vs. 0.534) — but most of
that edge is age/sex, not the antibiotics themselves. Colonization pressure has
a real, adjusted effect (OR 1.069, p = 0.010) that's invisible in a naive
bivariate comparison. **[Full write-up →](writeup/findings.md)**

## Dashboard

**[Live interactive dashboard →](https://claude.ai/code/artifact/2c83acbb-eea5-44ab-9bc5-a63d1d79a2dd)**
(also at [reports/dashboard.html](reports/dashboard.html)) — the headline AUC
comparison, the colonization-pressure and antibiotic-exposure charts, and the
adjusted odds-ratio forest plot for both models, built from the aggregate
exports in `tableau/`. A step-by-step guide for rebuilding the same views in
Tableau Public is at [tableau/DASHBOARD_GUIDE.md](tableau/DASHBOARD_GUIDE.md).

## Data

Not included in this repo — see [DATA_ACCESS.md](DATA_ACCESS.md) for why
(PhysioNet credentialed access / DUA) and how to obtain it. Expected at
`data/raw/HO_infxn_analysis.csv`.

## Project structure

```
data/raw/            HO_infxn_analysis.csv (git-ignored, see DATA_ACCESS.md)
data/processed/      cleaned/derived datasets (git-ignored)
docs/                data dictionary (public PhysioNet project page PDF)
notebooks/
  01_eda.ipynb                        exploration, age '>90' cleanup, MRSA subset
  02_correlation_analysis.ipynb       correlation structure of candidate predictors
  03_hypothesis_testing.ipynb         case vs. control group comparisons
  04a_logreg_environmental.ipynb      MRSA ~ colonization pressure
  04b_logreg_patient.ipynb            MRSA ~ antibiotic exposure, controlling for age/sex
  05_model_comparison.ipynb           compare the two models' predictive performance
  06_tableau_prep.ipynb               export aggregated tables for the dashboard
src/                 shared helper functions imported by notebooks
reports/figures/     exported static figures
reports/dashboard.html  self-contained interactive dashboard (see Dashboard above)
tableau/             aggregate CSV exports + Tableau Public build guide
writeup/             final written summary of findings
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook
```

## Workflow

Each pipeline stage is a checkpointed commit: EDA → correlation analysis →
hypothesis testing → logistic regression (per analysis type) → model
comparison → dashboard → write-up.
