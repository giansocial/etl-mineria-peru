import pytest
from pathlib import Path
from src.extract.minem_loader import load_production_csv, load_all_raw, validate_metal_column

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_csv():
    rows = load_production_csv(FIXTURES / "produccion_sample.csv")
    assert len(rows) > 0
    assert "metal" in rows[0]
    assert "produccion" in rows[0]


def test_load_csv_not_found():
    with pytest.raises(FileNotFoundError):
        load_production_csv(FIXTURES / "no_existe.csv")


def test_load_all_raw():
    rows = load_all_raw(FIXTURES)
    assert len(rows) > 40


def test_load_all_empty_dir(tmp_path):
    rows = load_all_raw(tmp_path)
    assert rows == []


def test_validate_metals():
    rows = load_production_csv(FIXTURES / "produccion_sample.csv")
    result = validate_metal_column(rows, ["cobre", "oro", "plata", "zinc"])
    assert len(result["metales_encontrados"]) == 4
    assert result["metales_faltantes"] == []


def test_validate_missing_metal():
    rows = load_production_csv(FIXTURES / "produccion_sample.csv")
    result = validate_metal_column(rows, ["cobre", "oro", "litio"])
    assert "litio" in result["metales_faltantes"]
