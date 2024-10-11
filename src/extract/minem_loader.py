import csv
import logging
from pathlib import Path
from typing import Optional

from src.config.settings import RAW_DIR, METALES

log = logging.getLogger(__name__)


def load_production_csv(filepath: Path) -> list[dict]:
    if not filepath.exists():
        raise FileNotFoundError(f"archivo no encontrado: {filepath}")
    rows = []
    with open(filepath, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    log.info("cargadas %d filas de %s", len(rows), filepath.name)
    return rows


def load_all_raw(raw_dir: Path = None) -> list[dict]:
    raw_dir = raw_dir or RAW_DIR
    all_rows = []
    csv_files = sorted(raw_dir.glob("*.csv"))
    if not csv_files:
        log.warning("no se encontraron CSVs en %s", raw_dir)
        return []
    for f in csv_files:
        rows = load_production_csv(f)
        all_rows.extend(rows)
    return all_rows


def validate_metal_column(rows: list[dict], expected_metals: list[str] = None) -> dict:
    expected = expected_metals or list(METALES.keys())
    found = set()
    for row in rows:
        metal = row.get("metal", "").lower().strip()
        if metal in expected:
            found.add(metal)
    missing = set(expected) - found
    return {
        "total_filas": len(rows),
        "metales_encontrados": sorted(found),
        "metales_faltantes": sorted(missing),
    }
