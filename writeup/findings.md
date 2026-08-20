# Colonization Pressure vs. Antibiotic Exposure: What Predicts Hospital-Onset MRSA?

**TL;DR:** In this dataset, a patient's own demographics and exposure history predict
hospital-onset MRSA acquisition meaningfully better than their ward's colonization
pressure does (test AUC 0.637 vs. 0.534) — but most of that edge comes from **age and
sex**, not from the antibiotic classes themselves. Ward-level MRSA colonization pressure
has a real, adjusted effect (OR 1.069, p = 0.010), just a small one, and it doesn't show
up at all in a naive bivariate comparison.

[**Interactive dashboard →**](https://claude.ai/code/artifact/2c83acbb-eea5-44ab-9bc5-a63d1d79a2dd) · [Notebooks](../notebooks/) · [Data source](../DATA_ACCESS.md)

---

## The question

Two things are commonly proposed as drivers of hospital-onset MRSA acquisition:

1. **Environmental exposure** — the microbiome of the ward a patient is admitted to,
   proxied by *colonization pressure*: how much MRSA carriage exists among recent
   co-occupants of the same ward.
2. **Patient exposure** — the patient's own recent antibiotic use, which can select for
   or otherwise predispose toward colonization by resistant organisms.

The PhysioNet [Predictors of Hospital Onset Infection](https://doi.org/10.13026/k70x-0m81)
dataset (Wei, Sagers, McKenna et al. 2025) is built specifically to separate these two
effects: it provides **two matched case-control cohorts** drawn from the same Mass
General Brigham inpatient population (May 2015–July 2024), each designed to isolate one
factor by matching away the other.

| | Environmental cohort | Patient cohort |
|---|---|---|
| Matched on | age (±5y), sex, prior surgery, room length-of-stay, antibiotic history | hospital ward, admission month/year, room length-of-stay |
| Isolates | ward colonization pressure | antibiotic exposure history |
| Leaves unmatched | — | **age, sex** |
| MRSA cases / controls | 1,101 / 2,397 | 1,102 / 2,656 |

Because the patient cohort isn't matched on age or sex, any model built on it needs to
adjust for those explicitly, or its antibiotic-exposure coefficients will be confounded.
That turned out to matter a lot (see below).

## Method

Standard matched case-control analysis pipeline, each step in its own notebook:

1. **[EDA](../notebooks/01_eda.ipynb)** — load and clean the data (ages ≥90 are censored
   as the literal string `'>90'` for privacy; recoded to numeric with a flag column),
   filter to the two MRSA subsets, and directly check the matching assumption above.
2. **[Correlation analysis](../notebooks/02_correlation_analysis.ipynb)** — point-biserial
   correlations of each candidate predictor against case/control status, and
   multicollinearity screening within each predictor set.
3. **[Hypothesis testing](../notebooks/03_hypothesis_testing.ipynb)** — Mann-Whitney U
   tests per predictor, Benjamini-Hochberg corrected across the many colonization-pressure
   and antibiotic-class comparisons.
4. **Logistic regression**, one model per arm:
   - **[Environmental](../notebooks/04a_logreg_environmental.ipynb)**: MRSA acquisition ~
     9 colonization-pressure variables + prior surgery + Elixhauser comorbidity index.
     No age/sex terms needed — the matching already balances them.
   - **[Patient](../notebooks/04b_logreg_patient.ipynb)**: MRSA acquisition ~ 12
     antibiotic-class exposure counts + Elixhauser index, fit **twice** — once without and
     once with age/sex — to make the confounding concrete rather than assumed.
5. **[Model comparison](../notebooks/05_model_comparison.ipynb)** — 80/20 train/test AUC
   for each arm's full model.
6. **[Dashboard](../notebooks/06_tableau_prep.ipynb)** — aggregate exports, visualized in
   the [interactive dashboard](https://claude.ai/code/artifact/2c83acbb-eea5-44ab-9bc5-a63d1d79a2dd).

Two data issues surfaced during the regression step, both worth naming because they'd
silently distort results if missed: `carbapenem_0_60` has zero variance in the patient
MRSA subset (no one in it received a carbapenem), and `anti_staph_beta_lactam_0_60` has
zero variance *within the case group specifically* (only ~5 exposed controls, zero
exposed cases) — which drove a logistic regression coefficient to −217 with a standard
error of 1.2×10⁴⁷ while statsmodels still reported "converged." Both were dropped before
fitting, with the reasoning logged in `src/data_loading.py`.

## Findings

### 1. Ward colonization pressure is a real predictor — but only once you adjust for confounders

In the raw bivariate comparison, **no** colonization-pressure variable — including
`MRSA_cp` itself — is significant after correcting for multiple comparisons (lowest
adjusted p = 0.068, for *drug-susceptible Enterobacterales* CP; `MRSA_cp` sits at
p = 0.875). Taken alone, that comparison would say colonization pressure doesn't matter.

But in the adjusted logistic regression — controlling for the other eight
colonization-pressure variables, prior surgery, and comorbidity burden — **`MRSA_cp` is
significant**: OR 1.069 (95% CI 1.016–1.124, p = 0.010). The unadjusted comparison was
masking a real effect, likely because the colonization-pressure variables are correlated
with each other (a ward with high MRSA pressure often has elevated pressure for other
organisms too) and the univariate test can't separate MRSA-specific pressure from that
shared "how colonized is this ward generally" signal.

The effect is real but small: pseudo-R² for the full environmental model is **0.007** —
colonization pressure and the other covariates together explain very little of who
acquires MRSA. All variance inflation factors were low (< 3), so this isn't a
multicollinearity artifact.

### 2. In the patient cohort, sex and age dominate — individual antibiotics mostly don't

The adjusted patient model's strongest terms by a wide margin:

| Predictor | Adjusted OR | 95% CI | p |
|---|---|---|---|
| Sex: male | **1.836** | 1.589–2.121 | < 0.001 |
| Age (per year) | 0.989 | 0.986–0.993 | < 0.001 |
| Sulfonamides (folate inhibitors) | 0.245 | 0.094–0.637 | 0.004 |

Everything else — penicillins, cephalosporins, fluoroquinolones, glycopeptides,
macrolides, tetracyclines, and the rest of the twelve antibiotic classes tested — was not
statistically significant on its own.

Sulfonamide exposure's *protective* direction (lower odds of MRSA with prior exposure) is
counterintuitive if you expect antibiotics to select for resistant organisms, and it
showed up the same way in the raw hypothesis test. The likely explanation is **indication
bias**: sulfonamides are prescribed for specific infections, and whatever population
receives them differs from the general patient population in ways this model doesn't
fully capture. This is a matched observational design, not a randomized one — it can
describe association, not establish that sulfonamides causally protect against MRSA.

Fitting the model **without** age/sex first, then adding them, makes the confounding
concrete: pseudo-R² goes from **0.0067** (antibiotics + comorbidity index alone) to
**0.0296** (adding age and sex) — a roughly 4.4x increase from two variables the
antibiotics-only model didn't have access to. That's the direct empirical confirmation
that this cohort's lack of age/sex matching was a live issue, not a theoretical one.

### 3. The patient model out-predicts the environmental model, but mostly for demographic reasons

| Model | Predictor set | Test AUC | n |
|---|---|---|---|
| Environmental | Colonization pressure + surgery + comorbidity | **0.534** | 3,498 |
| Patient | Antibiotics + comorbidity + age + sex (adjusted) | **0.637** | 3,758 |

The environmental model is barely better than a coin flip. The patient model is
meaningfully predictive by comparison — but given finding #2, most of that gap is
attributable to age and sex being present in one model's feature set and absent
(structurally, by design) from the other's, not to antibiotic exposure being a
fundamentally stronger signal than colonization pressure.

Two caveats belong on this comparison specifically:

- **The cohorts aren't apples-to-apples.** They differ in matching design and sample
  composition, so part of the AUC gap could reflect the underlying cohorts rather than
  the predictor classes in isolation.
- **Both pseudo-R² values are small.** Even the better-performing patient model explains
  only a modest share of the variance in MRSA acquisition. Most of what determines
  whether a given hospitalized patient acquires MRSA in this dataset is not captured by
  either colonization pressure or the recorded antibiotic/demographic variables.

## Bottom line

Framed narrowly as "antibiotic exposure vs. colonization pressure," the antibiotic-history
model wins on predictive performance. Framed more precisely, the honest answer is:
**patient demographics (age, sex) carry more signal than either ward-level colonization
pressure or the specific antibiotic classes tested** — and colonization pressure's one
genuine, MRSA-specific effect is real but modest, and invisible unless you control for
the other organisms' colonization pressure at the same time.

For infection control purposes, this suggests demographic risk stratification and
general colonization-pressure monitoring (not attribution to any single antibiotic class)
are where the signal in this dataset actually is — consistent with the source paper's
framing of colonization pressure and antibiotic exposure as complementary, not competing,
risk factors.

## Limitations

- **Observational, matched case-control design.** Associations here, including the
  sulfonamide finding, are not evidence of causal effects; indication bias is a live
  concern for any exposure that's itself a response to a clinical presentation.
- **Single health system.** All data comes from Mass General Brigham; ward architecture,
  antibiotic stewardship practices, and patient mix at other institutions may differ.
- **Small subgroups.** Several antibiotic classes had single-digit exposure counts within
  the MRSA subset (e.g. 4 patients exposed to anti-staphylococcal beta-lactams, 7 to
  anti-anaerobes) — those estimates, where they survived at all, are noisy.
- **Low pseudo-R² throughout.** Neither model explains most of the variance in
  acquisition; there are evidently other drivers (individual ward architecture, specific
  care unit, unmeasured clinical factors) not captured by either predictor set.

## Reproducing this

Raw data is PhysioNet credentialed-access and isn't included in this repo — see
[DATA_ACCESS.md](../DATA_ACCESS.md). With `data/raw/HO_infxn_analysis.csv` in place, the
notebooks in [`notebooks/`](../notebooks/) run in numbered order end to end.
