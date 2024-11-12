import pytest
import pandas as pd
import numpy as np
from src.transform.enricher import (
    add_yoy_variation, add_mom_variation, add_moving_average,
    rank_regions_by_metal, concentration_index,
)


def _sample():
    rows = []
    for anio in [2023, 2024]:
        for mes in range(1, 7):
            rows.append({
                "metal": "cobre",
                "region": "Ancash",
                "anio": anio,
                "mes": mes,
                "produccion": 40000 + np.random.randint(-5000, 5000),
            })
            rows.append({
                "metal": "cobre",
                "region": "Arequipa",
                "anio": anio,
                "mes": mes,
                "produccion": 85000 + np.random.randint(-5000, 5000),
            })
    return pd.DataFrame(rows)


def test_yoy_has_column():
    df = _sample()
    result = add_yoy_variation(df)
    assert "var_interanual_pct" in result.columns


def test_yoy_first_year_is_null():
    df = _sample()
    result = add_yoy_variation(df)
    first_year = result[result["anio"] == 2023]
    assert first_year["var_interanual_pct"].isna().all()


def test_yoy_no_mutation():
    df = _sample()
    cols_before = list(df.columns)
    add_yoy_variation(df)
    assert list(df.columns) == cols_before


def test_mom_has_column():
    df = _sample()
    result = add_mom_variation(df)
    assert "var_mensual_pct" in result.columns


def test_moving_average():
    df = _sample()
    result = add_moving_average(df, window=3)
    assert "ma_3m" in result.columns
    non_null = result["ma_3m"].dropna()
    assert len(non_null) > 0


def test_rank_regions():
    df = _sample()
    ranking = rank_regions_by_metal(df)
    assert "rank" in ranking.columns
    top = ranking[(ranking["anio"] == 2023) & (ranking["rank"] == 1)]
    assert len(top) > 0


def test_concentration_index():
    df = _sample()
    hhi = concentration_index(df)
    assert "hhi" in hhi.columns
    for _, row in hhi.iterrows():
        assert row["hhi"] >= 0
        assert row["hhi"] <= 10000
