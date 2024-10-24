import argparse
import json
import logging
import time

from src.config.settings import RAW_DIR, PROCESSED_DIR, METALES
from src.extract.minem_loader import load_all_raw
from src.transform.cleaner import clean_production_data, add_period_column
from src.transform.enricher import (
    add_yoy_variation,
    add_mom_variation,
    add_moving_average,
    rank_regions_by_metal,
    concentration_index,
)
from src.quality.validators import run_quality_report
from src.load.warehouse import init_db, load_to_warehouse
from src.utils.logger import setup_logging

log = logging.getLogger(__name__)


def run_etl(raw_dir=None, metals: list[str] = None) -> dict:
    t0 = time.time()
    raw_dir = raw_dir or RAW_DIR

    import pandas as pd
    rows = load_all_raw(raw_dir)
    if not rows:
        log.error("sin datos para procesar")
        return {"error": "sin datos"}

    df = pd.DataFrame(rows)
    df = clean_production_data(df)
    df = add_period_column(df)

    if metals:
        df = df[df["metal"].isin(metals)]
        log.info("filtrado a %d filas para metales: %s", len(df), metals)

    quality = run_quality_report(df)
    log.info("calidad: %.1f%%", quality["score_total"])

    df = add_yoy_variation(df)
    df = add_mom_variation(df)
    df = add_moving_average(df, window=6)

    conn = init_db()
    loaded = load_to_warehouse(df, conn)

    ranking = rank_regions_by_metal(df)
    ranking.to_csv(PROCESSED_DIR / "ranking_regiones.csv", index=False)

    hhi = concentration_index(df)
    hhi.to_csv(PROCESSED_DIR / "concentracion_hhi.csv", index=False)

    df.to_csv(PROCESSED_DIR / "produccion_enriquecida.csv", index=False)

    conn.close()
    elapsed = round(time.time() - t0, 1)
    log.info("ETL completado en %.1fs", elapsed)

    return {
        "filas_procesadas": len(df),
        "filas_cargadas": loaded,
        "calidad_pct": quality["score_total"],
        "metales": sorted(df["metal"].unique().tolist()),
        "regiones": sorted(df["region"].unique().tolist()),
        "duracion_seg": elapsed,
    }


def main():
    parser = argparse.ArgumentParser(description="ETL produccion minera Peru")
    parser.add_argument("--metals", nargs="+", help="metales a procesar")
    args = parser.parse_args()

    setup_logging()
    result = run_etl(metals=args.metals)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
