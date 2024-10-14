import logging
import pandas as pd
import numpy as np

log = logging.getLogger(__name__)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    col_map = {}
    for c in df.columns:
        clean = c.strip().lower().replace(" ", "_").replace(".", "")
        col_map[c] = clean
    df = df.rename(columns=col_map)
    return df


def parse_numeric_values(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    df = df.copy()
    for col in cols:
        if col not in df.columns:
            continue
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace(" ", "", regex=False)
            .str.strip()
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def clean_production_data(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)

    if "anio" in df.columns:
        df["anio"] = pd.to_numeric(df["anio"], errors="coerce")
        df = df.dropna(subset=["anio"])
        df["anio"] = df["anio"].astype(int)

    if "mes" in df.columns:
        df["mes"] = pd.to_numeric(df["mes"], errors="coerce")
        df = df.dropna(subset=["mes"])
        df["mes"] = df["mes"].astype(int)

    if "produccion" in df.columns:
        df = parse_numeric_values(df, ["produccion"])
        df = df.dropna(subset=["produccion"])

    if "metal" in df.columns:
        df["metal"] = df["metal"].str.strip().str.lower()

    if "region" in df.columns:
        df["region"] = df["region"].str.strip().str.title()

    before = len(df)
    df = df.drop_duplicates()
    dupes = before - len(df)
    if dupes > 0:
        log.info("eliminados %d duplicados", dupes)

    return df.reset_index(drop=True)


def add_period_column(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "anio" in df.columns and "mes" in df.columns:
        df["periodo"] = df["anio"].astype(str) + "-" + df["mes"].astype(str).str.zfill(2)
    return df
