"""Shared loading/cleaning helpers for HO_infxn_analysis.csv.

Used by every notebook in notebooks/ so the age '>90' fix and MRSA
filtering logic live in exactly one place.
"""
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "HO_infxn_analysis.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

AGE_OVER_90_SENTINEL = 90  # conservative numeric stand-in for the censored ">90" bucket


def load_raw(path: Path = RAW_PATH) -> pd.DataFrame:
    return pd.read_csv(path)


def clean_age(df: pd.DataFrame, age_col: str = "age") -> pd.DataFrame:
    """Make `age` numeric.

    The source data censors ages >=90 as the literal string '>90' for
    privacy. We flag those rows in `age_over_90` (so they can be excluded
    or modeled separately if the censoring matters) and recode the value
    to AGE_OVER_90_SENTINEL so `age` is uniformly numeric.
    """
    df = df.copy()
    is_censored = df[age_col].astype(str).str.strip().eq(">90")
    df["age_over_90"] = is_censored
    df[age_col] = df[age_col].astype(str).str.strip().replace(">90", str(AGE_OVER_90_SENTINEL))
    df[age_col] = pd.to_numeric(df[age_col], errors="raise")
    return df


def load_mrsa_subset(analysis: str, path: Path = RAW_PATH) -> pd.DataFrame:
    """Load HO_infxn_analysis.csv filtered to MRSA rows for one analysis arm.

    analysis: 'environmental' or 'patient'
    """
    df = load_raw(path)
    df = df[df["analysis"].str.lower() == analysis.lower()].copy()
    df = df[df["run"].astype(str).str.contains("MRSA", case=False, na=False)].copy()
    df = clean_age(df)
    return df


def save_processed(df: pd.DataFrame, name: str) -> Path:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / name
    df.to_csv(out_path, index=False)
    return out_path


def load_processed(name: str) -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DIR / name)


def drop_zero_variance(
    df: pd.DataFrame, cols: list, outcome_col: str = None, verbose: bool = True
) -> list:
    """Return `cols` minus any that are constant overall, or constant within
    one level of `outcome_col`.

    In the MRSA subsets, some antibiotic classes (e.g. carbapenem) have no
    exposed patients at all -- constant overall, which produces undefined
    correlations and singular design matrices if left in.

    Others (e.g. anti_staph_beta_lactam) aren't constant overall but *are*
    constant within the case group (zero exposed cases, a handful of exposed
    controls) -- this still causes quasi-complete separation in a logistic
    regression: the MLE coefficient runs off to +/-infinity with an enormous
    standard error even though the optimizer may report "converged". Pass
    `outcome_col` to catch this too.
    """
    kept = []
    for c in cols:
        if df[c].var() == 0:
            if verbose:
                print(f"Dropping '{c}': zero variance in this subset (no exposed cases).")
            continue
        if outcome_col is not None:
            group_vars = df.groupby(outcome_col)[c].var()
            if (group_vars == 0).any():
                if verbose:
                    print(f"Dropping '{c}': constant within one outcome group (separation risk).")
                continue
        kept.append(c)
    return kept
