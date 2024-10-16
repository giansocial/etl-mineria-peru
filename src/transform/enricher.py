import pandas as pd
import numpy as np


def add_yoy_variation(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.sort_values(["metal", "region", "anio", "mes"])
    df["prod_anterior"] = df.groupby(["metal", "region", "mes"])["produccion"].shift(1)
    mask = df["prod_anterior"] > 0
    df.loc[mask, "var_interanual_pct"] = (
        (df.loc[mask, "produccion"] - df.loc[mask, "prod_anterior"])
        / df.loc[mask, "prod_anterior"]
        * 100
    ).round(2)
    df = df.drop(columns=["prod_anterior"])
    return df


def add_mom_variation(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.sort_values(["metal", "region", "anio", "mes"])
    df["prod_mes_ant"] = df.groupby(["metal", "region"])["produccion"].shift(1)
    mask = df["prod_mes_ant"] > 0
    df.loc[mask, "var_mensual_pct"] = (
        (df.loc[mask, "produccion"] - df.loc[mask, "prod_mes_ant"])
        / df.loc[mask, "prod_mes_ant"]
        * 100
    ).round(2)
    df = df.drop(columns=["prod_mes_ant"])
    return df


def add_moving_average(df: pd.DataFrame, window: int = 6) -> pd.DataFrame:
    df = df.copy()
    df = df.sort_values(["metal", "region", "anio", "mes"])
    col = f"ma_{window}m"
    df[col] = (
        df.groupby(["metal", "region"])["produccion"]
        .transform(lambda x: x.rolling(window, min_periods=window).mean())
        .round(2)
    )
    return df


def rank_regions_by_metal(df: pd.DataFrame) -> pd.DataFrame:
    annual = (
        df.groupby(["metal", "region", "anio"])["produccion"]
        .sum()
        .reset_index()
    )
    annual["rank"] = (
        annual.groupby(["metal", "anio"])["produccion"]
        .rank(ascending=False, method="min")
        .astype(int)
    )
    return annual.sort_values(["metal", "anio", "rank"])


def concentration_index(df: pd.DataFrame) -> pd.DataFrame:
    annual = (
        df.groupby(["metal", "region", "anio"])["produccion"]
        .sum()
        .reset_index()
    )
    total = annual.groupby(["metal", "anio"])["produccion"].transform("sum")
    annual["participacion_pct"] = (annual["produccion"] / total * 100).round(2)

    hhi = (
        annual.groupby(["metal", "anio"])
        .apply(lambda g: (g["participacion_pct"] ** 2).sum())
        .reset_index(name="hhi")
    )
    hhi["hhi"] = hhi["hhi"].round(0).astype(int)
    return hhi
