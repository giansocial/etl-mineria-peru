import pytest
import pandas as pd
from src.transform.cleaner import (
    normalize_columns, parse_numeric_values, clean_production_data, add_period_column,
)


def test_normalize_columns():
    df = pd.DataFrame({"Metal ": [1], " Region": [2], "Anio.": [3]})
    result = normalize_columns(df)
    assert list(result.columns) == ["metal", "region", "anio"]


def test_parse_numeric():
    df = pd.DataFrame({"produccion": ["1,234.5", "5 678", "abc"]})
    result = parse_numeric_values(df, ["produccion"])
    assert result["produccion"].iloc[0] == 1234.5
    assert pd.isna(result["produccion"].iloc[2])


def test_clean_removes_dupes():
    df = pd.DataFrame({
        "metal": ["cobre", "cobre"],
        "region": ["Ancash", "Ancash"],
        "anio": [2023, 2023],
        "mes": [1, 1],
        "produccion": ["42150.5", "42150.5"],
    })
    cleaned = clean_production_data(df)
    assert len(cleaned) == 1


def test_clean_drops_null_production():
    df = pd.DataFrame({
        "metal": ["cobre", "oro"],
        "region": ["Ancash", "Cajamarca"],
        "anio": [2023, 2023],
        "mes": [1, 1],
        "produccion": ["42150.5", "abc"],
    })
    cleaned = clean_production_data(df)
    assert len(cleaned) == 1


def test_clean_normalizes_metal():
    df = pd.DataFrame({
        "metal": [" Cobre ", "ORO"],
        "region": ["Ancash", "Cajamarca"],
        "anio": [2023, 2023],
        "mes": [1, 2],
        "produccion": ["100", "200"],
    })
    cleaned = clean_production_data(df)
    assert cleaned["metal"].iloc[0] == "cobre"
    assert cleaned["metal"].iloc[1] == "oro"


def test_clean_normalizes_region():
    df = pd.DataFrame({
        "metal": ["cobre"],
        "region": ["la libertad"],
        "anio": [2023],
        "mes": [1],
        "produccion": ["100"],
    })
    cleaned = clean_production_data(df)
    assert cleaned["region"].iloc[0] == "La Libertad"


def test_add_period():
    df = pd.DataFrame({"anio": [2023, 2023], "mes": [1, 12]})
    result = add_period_column(df)
    assert result["periodo"].iloc[0] == "2023-01"
    assert result["periodo"].iloc[1] == "2023-12"
