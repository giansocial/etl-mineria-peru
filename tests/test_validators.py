import pytest
import pandas as pd
from src.quality.validators import (
    check_completeness, check_uniqueness, check_range, run_quality_report,
)


def _df():
    return pd.DataFrame({
        "metal": ["cobre", "oro", "plata"],
        "region": ["Ancash", "Cajamarca", "Junin"],
        "anio": [2023, 2023, 2023],
        "mes": [1, 2, 3],
        "produccion": [42000.0, 130.5, 1850.0],
    })


def test_completeness_full():
    df = _df()
    result = check_completeness(df, ["metal", "region", "produccion"])
    assert result["score"] == 100.0


def test_completeness_with_nulls():
    df = _df()
    df.loc[0, "produccion"] = None
    result = check_completeness(df, ["produccion"])
    assert result["score"] < 100
    assert result["detalles"]["produccion"] < 100


def test_completeness_empty():
    result = check_completeness(pd.DataFrame(), ["metal"])
    assert result["score"] == 0.0


def test_uniqueness_no_dupes():
    df = _df()
    result = check_uniqueness(df, ["metal", "region", "anio", "mes"])
    assert result["score"] == 100.0
    assert result["duplicados"] == 0


def test_uniqueness_with_dupes():
    df = pd.concat([_df(), _df().iloc[:1]], ignore_index=True)
    result = check_uniqueness(df, ["metal", "region", "anio", "mes"])
    assert result["duplicados"] == 1


def test_range_valid():
    df = _df()
    result = check_range(df, "produccion", 0, 1e9)
    assert result["score"] == 100.0


def test_range_out():
    df = _df()
    df.loc[0, "produccion"] = -500
    result = check_range(df, "produccion", 0, 1e9)
    assert result["fuera_rango"] == 1


def test_quality_report():
    df = _df()
    report = run_quality_report(df)
    assert report["score_total"] > 90
    assert "completitud" in report
    assert "unicidad" in report
