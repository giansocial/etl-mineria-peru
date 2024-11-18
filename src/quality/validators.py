import logging
import pandas as pd

log = logging.getLogger(__name__)


def check_completeness(df: pd.DataFrame, required_cols: list[str]) -> dict:
    total = len(df)
    if total == 0:
        return {"score": 0.0, "detalles": {}}
    detalles = {}
    for col in required_cols:
        if col in df.columns:
            nulls = df[col].isnull().sum()
            detalles[col] = round((1 - nulls / total) * 100, 1)
        else:
            detalles[col] = 0.0
    score = sum(detalles.values()) / len(detalles) if detalles else 0.0
    return {"score": round(score, 1), "detalles": detalles}


def check_uniqueness(df: pd.DataFrame, key_cols: list[str]) -> dict:
    total = len(df)
    if total == 0:
        return {"score": 100.0, "duplicados": 0}
    dupes = df.duplicated(subset=key_cols).sum()
    score = (1 - dupes / total) * 100
    return {"score": round(score, 1), "duplicados": int(dupes)}


def check_range(df: pd.DataFrame, col: str, min_val: float, max_val: float) -> dict:
    if col not in df.columns:
        return {"score": 0.0, "fuera_rango": 0}
    valid = df[col].between(min_val, max_val)
    total = valid.count()
    if total == 0:
        return {"score": 0.0, "fuera_rango": 0}
    score = valid.sum() / total * 100
    return {"score": round(score, 1), "fuera_rango": int(total - valid.sum())}


def run_quality_report(df: pd.DataFrame) -> dict:
    required = ["metal", "region", "anio", "mes", "produccion"]
    completeness = check_completeness(df, required)
    uniqueness = check_uniqueness(df, ["metal", "region", "anio", "mes"])
    range_check = check_range(df, "produccion", 0, 1e9)

    weights = {"completeness": 0.4, "uniqueness": 0.3, "range": 0.3}
    total = (
        completeness["score"] * weights["completeness"]
        + uniqueness["score"] * weights["uniqueness"]
        + range_check["score"] * weights["range"]
    )

    report = {
        "score_total": round(total, 1),
        "completitud": completeness,
        "unicidad": uniqueness,
        "rango_produccion": range_check,
        "filas_evaluadas": len(df),
    }

    log.info("calidad total: %.1f%% (%d filas)", total, len(df))
    return report
