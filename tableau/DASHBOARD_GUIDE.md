# Tableau Dashboard Build Guide

Tableau Public 2023.1 is installed, but I can only drive browser-based tools, not native
desktop apps — so this is a guide for you to follow rather than something I can build
directly. It's written against the exact columns in the four CSVs in this folder
(regenerate them by re-running `notebooks/06_tableau_prep.ipynb` if the analysis
changes).

Connect each CSV as its own data source in one workbook (File → New, then "Text file" four
times) — they don't need to be joined or related; each sheet below uses only one of them.

---

## Sheet 1 — Environmental: acquisition rate by colonization-pressure decile

**Data source:** `env_mrsa_cp_by_decile.csv`
**Columns:** `mrsa_cp_decile`, `n`, `acquisition_rate`, `mean_mrsa_cp`

1. Drag `mrsa_cp_decile` to **Columns**. Right-click it → **Discrete** (so it's treated as
   an ordered category, 0–7, not a continuous axis).
2. Drag `acquisition_rate` to **Rows**. Right-click → **Format** → number format
   **Percentage**.
3. Marks type: **Line**, then add **Bar** as a secondary reference if you want — a plain
   line is enough to make the point.
4. Drag `n` to **Tooltip**, and `mean_mrsa_cp` to **Tooltip** too, so hovering a decile
   shows sample size and the actual mean colonization-pressure value, not just the
   decile number.
5. Title: *"MRSA Acquisition Rate by Ward Colonization Pressure Decile"*.

**What you'll see:** the line is close to flat (~29–34% across all deciles) — it does
**not** show a strong monotonic climb. This matches the regression finding: `MRSA_cp`'s
adjusted odds ratio was only 1.069. Worth a caption on the dashboard saying so explicitly,
so the chart doesn't read as "no relationship" when the adjusted model did find a small
real one — a chart is not equivalent to the adjusted model, since it's an unadjusted
bivariate view.

---

## Sheet 2 — Patient: acquisition rate by antibiotic class, exposed vs. unexposed

**Data source:** `pat_mrsa_rate_by_abx_class.csv`
**Columns:** `antibiotic_class`, `n_exposed`, `acquisition_rate_exposed`, `n_unexposed`,
`acquisition_rate_unexposed`

1. Drag `antibiotic_class` to **Rows**.
2. Drag `acquisition_rate_exposed` **and** `acquisition_rate_unexposed` both onto
   **Columns**. Tableau will auto-create a **Measure Names** / **Measure Values** pair and
   draw a bar per measure — this gives you the exposed-vs-unexposed grouped bar without
   any manual pivoting.
3. Drag the **Measure Names** pill to **Color** so the two bars are visually distinct
   (e.g. exposed = teal, unexposed = grey).
4. Sort rows by `acquisition_rate_exposed` descending (click the sort icon on that axis).
5. **`carbapenem`** has `n_exposed = 0` (nobody in this subset got a carbapenem course) —
   its exposed-rate is blank. Either filter that row out, or leave it with a text
   annotation ("no exposed patients") so it doesn't look like a data error.
6. Add `n_exposed` to **Tooltip** — several classes here have single-digit exposed counts
   (`anti_staph_beta_lactam`: 4, `anti_anaerobe`/`extended_spectrum_cephalosporin`: 7),
   so the tooltip should make clear those bars are noisy, not reliable signal.
7. Title: *"MRSA Acquisition Rate by Prior Antibiotic Class Exposure (60 Days)"*.

---

## Sheet 3 — Forest plot: odds ratios across both models

**Data source:** `model_odds_ratios.csv`
**Columns:** `OR`, `ci_low`, `ci_high`, `source`, `variable`

This is the most involved one — it's a classic "forest plot" built as a Gantt-style range
plus a point marker, which Tableau doesn't have as a built-in chart type.

1. Drag `variable` to **Rows**. Drag `source` to **Rows** too (above `variable`) so
   environmental and patient predictors are grouped separately — or use `source` as a
   **Filter** and build the sheet once per arm if you'd rather keep it simpler.
2. Drag `ci_low` to **Columns**. Change the mark type to **Gantt Bar**.
3. Create a calculated field `ci_width` = `[ci_high] - [ci_low]`, and drag it onto
   **Size** on the Marks card — this stretches each Gantt bar from `ci_low` to
   `ci_high`, drawing the confidence interval as a horizontal bar.
4. Right-click the `ci_low` axis (now the x-axis) → **Dual Axis**, then drag `OR` onto
   that second axis. Change its mark type to **Circle** — this overlays a point at the
   OR estimate on top of the CI bar. Right-click the second axis → **Synchronize Axis**.
5. Sort `variable` within each `source` by `OR` descending.
6. Add a reference line at **x = 1** (Analytics pane → drag "Reference Line" onto the
   axis, constant value 1, label "No effect") — anything whose CI bar doesn't cross this
   line is a statistically distinguishable effect.
7. Given `sex_male`'s OR (1.84, CI 1.59–2.12) sits far to the right of the colonization-
   pressure ORs (all clustered near 1.0), consider a **logarithmic x-axis** (right-click
   axis → Logarithmic) so both scales are readable in one chart, or facet by `source`
   into two side-by-side panels with independent axes instead of forcing one shared
   scale.
8. Title: *"Adjusted Odds Ratios: Environmental vs. Patient Model"*.

**What you'll see:** in the environmental arm, only `MRSA_cp`'s CI clears 1 (barely,
1.016–1.124). In the patient arm, `sex_male` and `age` clear it clearly; `sulfonamide_0_60`
clears it on the *protective* side (CI entirely below 1, 0.094–0.637); everything else
straddles 1.

---

## Sheet 4 — Cohort summary

**Data source:** `cohort_summary.csv`
**Columns:** `analysis`, `group`, `n`, `mean_age`, `mean_duration`

Simplest sheet: drag all five columns onto the view as a **Text Table** (Show Me → table).
This gives dashboard viewers the sample-size and demographic context (e.g. that the
patient cohort's mean age differs by ~4 years between case and control — 62.3 vs.
66.3 — visible confirmation of the age imbalance the write-up discusses) without needing
to read the notebooks.

---

## Assembling the dashboard

1. **Dashboard → New Dashboard**, size "Automatic" or a fixed 1200×900.
2. Drag Sheets 1–4 onto the canvas — a 2×2 grid works well (CP-decile top-left,
   antibiotic-class top-right, forest plot spanning the bottom, cohort summary as a small
   panel or tooltip-accessible detail).
3. Add a **Text** object at the top as a title/summary caption, e.g.:
   > "Which predicts hospital-onset MRSA better: ward colonization pressure or antibiotic
   > exposure history? The patient (antibiotic + demographic) model achieves AUC 0.637 vs.
   > 0.534 for the environmental (colonization pressure) model — but most of that gap
   > traces to age/sex, not the antibiotics themselves."
4. **File → Save to Tableau Public** (or Save as `.twbx` locally first if you want a
   private draft before publishing) — a `.twbx` packages the workbook with its data, so
   it's self-contained.

**DUA note:** everything in these four CSVs is already aggregated (deciles, group means,
model coefficients, class-level rates) — no row-level patient data — so publishing the
finished dashboard publicly on Tableau Public should be fine under the PhysioNet DUA. If
you add any new sheet later, keep it built from an aggregate export like these, not from
`data/processed/*.csv` directly.
