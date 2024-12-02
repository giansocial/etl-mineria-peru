import logging
import sqlite3
from pathlib import Path
import pandas as pd

from src.config.settings import DB_PATH

log = logging.getLogger(__name__)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS dim_metal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    unidad TEXT,
    factor_lb REAL
);

CREATE TABLE IF NOT EXISTS dim_region (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_tiempo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    anio INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    periodo TEXT NOT NULL,
    trimestre INTEGER NOT NULL,
    UNIQUE(anio, mes)
);

CREATE TABLE IF NOT EXISTS fact_produccion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metal_id INTEGER NOT NULL,
    region_id INTEGER NOT NULL,
    tiempo_id INTEGER NOT NULL,
    produccion REAL NOT NULL,
    var_interanual_pct REAL,
    var_mensual_pct REAL,
    ma_6m REAL,
    FOREIGN KEY (metal_id) REFERENCES dim_metal(id),
    FOREIGN KEY (region_id) REFERENCES dim_region(id),
    FOREIGN KEY (tiempo_id) REFERENCES dim_tiempo(id),
    UNIQUE(metal_id, region_id, tiempo_id)
);
"""


def init_db(db_path: Path = None) -> sqlite3.Connection:
    db_path = db_path or DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    log.info("esquema inicializado en %s", db_path.name)
    return conn


def _get_or_create_id(conn, table: str, col: str, value: str) -> int:
    cur = conn.execute(f"SELECT id FROM {table} WHERE {col} = ?", (value,))
    row = cur.fetchone()
    if row:
        return row[0]
    conn.execute(f"INSERT INTO {table} ({col}) VALUES (?)", (value,))
    conn.commit()
    cur = conn.execute(f"SELECT id FROM {table} WHERE {col} = ?", (value,))
    return cur.fetchone()[0]


def _get_or_create_tiempo(conn, anio: int, mes: int) -> int:
    periodo = f"{anio}-{str(mes).zfill(2)}"
    trimestre = (mes - 1) // 3 + 1
    cur = conn.execute(
        "SELECT id FROM dim_tiempo WHERE anio = ? AND mes = ?", (anio, mes)
    )
    row = cur.fetchone()
    if row:
        return row[0]
    conn.execute(
        "INSERT INTO dim_tiempo (anio, mes, periodo, trimestre) VALUES (?, ?, ?, ?)",
        (anio, mes, periodo, trimestre),
    )
    conn.commit()
    cur = conn.execute(
        "SELECT id FROM dim_tiempo WHERE anio = ? AND mes = ?", (anio, mes)
    )
    return cur.fetchone()[0]


def load_to_warehouse(df: pd.DataFrame, conn: sqlite3.Connection = None) -> int:
    own_conn = conn is None
    if own_conn:
        conn = init_db()

    loaded = 0
    for _, row in df.iterrows():
        metal_id = _get_or_create_id(conn, "dim_metal", "nombre", row["metal"])
        region_id = _get_or_create_id(conn, "dim_region", "nombre", row["region"])
        tiempo_id = _get_or_create_tiempo(conn, int(row["anio"]), int(row["mes"]))

        conn.execute(
            """INSERT OR REPLACE INTO fact_produccion
               (metal_id, region_id, tiempo_id, produccion, var_interanual_pct, var_mensual_pct, ma_6m)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                metal_id,
                region_id,
                tiempo_id,
                row.get("produccion"),
                row.get("var_interanual_pct"),
                row.get("var_mensual_pct"),
                row.get("ma_6m"),
            ),
        )
        loaded += 1

    conn.commit()
    log.info("cargadas %d filas al warehouse", loaded)

    if own_conn:
        conn.close()
    return loaded
