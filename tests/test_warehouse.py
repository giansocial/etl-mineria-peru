import pytest
import sqlite3
import pandas as pd
from pathlib import Path
from src.load.warehouse import init_db, load_to_warehouse


@pytest.fixture
def db(tmp_path):
    conn = init_db(tmp_path / "test.db")
    yield conn
    conn.close()


def _sample_df():
    return pd.DataFrame({
        "metal": ["cobre", "oro"],
        "region": ["Ancash", "Cajamarca"],
        "anio": [2023, 2023],
        "mes": [1, 1],
        "produccion": [42000.0, 130.5],
        "var_interanual_pct": [None, None],
        "var_mensual_pct": [None, None],
        "ma_6m": [None, None],
    })


def test_init_creates_tables(db):
    cur = db.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cur.fetchall()}
    assert "dim_metal" in tables
    assert "dim_region" in tables
    assert "dim_tiempo" in tables
    assert "fact_produccion" in tables


def test_load_inserts_rows(db):
    df = _sample_df()
    loaded = load_to_warehouse(df, db)
    assert loaded == 2
    cur = db.execute("SELECT COUNT(*) FROM fact_produccion")
    assert cur.fetchone()[0] == 2


def test_load_creates_dimensions(db):
    df = _sample_df()
    load_to_warehouse(df, db)
    cur = db.execute("SELECT nombre FROM dim_metal ORDER BY nombre")
    metals = [r[0] for r in cur.fetchall()]
    assert "cobre" in metals
    assert "oro" in metals


def test_load_upsert_idempotent(db):
    df = _sample_df()
    load_to_warehouse(df, db)
    load_to_warehouse(df, db)
    cur = db.execute("SELECT COUNT(*) FROM fact_produccion")
    assert cur.fetchone()[0] == 2


def test_load_tiempo_trimestre(db):
    df = _sample_df()
    load_to_warehouse(df, db)
    cur = db.execute("SELECT trimestre FROM dim_tiempo WHERE mes = 1")
    assert cur.fetchone()[0] == 1
