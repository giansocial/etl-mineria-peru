# ETL Producción Minera - Perú

¿Sabías que Perú es el segundo productor mundial de cobre, plata y zinc, y que la minería representa el 60% de sus exportaciones? Sin embargo, la producción está tan concentrada que solo 3 regiones generan más del 70% del cobre nacional, y una caída en Arequipa o Áncash puede mover los indicadores de todo el sector.

Soy Gian Cruz. Construí este pipeline ETL para procesar los datos de producción minera publicados por el MINEM. Analiza 8 metales en 15 regiones, calcula variaciones interanuales, promedios móviles y el índice de concentración Herfindahl-Hirschman (HHI) para medir qué tan dependiente es cada metal de pocas regiones productoras.

## Qué hace

- Carga datos de producción desde archivos CSV (exportaciones del boletín MINEM)
- Limpia y normaliza nombres de metales, regiones y valores numéricos
- Calcula variación interanual y mensual de producción
- Genera promedios móviles de 6 meses
- Rankea regiones por volumen de producción
- Calcula índice de concentración Herfindahl-Hirschman (HHI)
- Ejecuta validación de calidad (completitud, unicidad, rango)
- Carga a warehouse SQLite con esquema dimensional

## Esquema del warehouse

```
dim_metal (id, nombre, unidad, factor_lb)
dim_region (id, nombre)
dim_tiempo (id, año, mes, periodo, trimestre)
fact_produccion (metal_id, region_id, tiempo_id, produccion, var_interanual, var_mensual, ma_6m)
```

## Instalación

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Uso

```bash
# Colocar CSVs de producción en data/raw/
# Formato: metal, region, año, mes, produccion

# Ejecutar ETL completo
python -m src.pipeline

# Filtrar por metales
python -m src.pipeline --metals cobre oro
```

## Tests

```bash
pytest tests/ -v
pytest tests/ --cov=src --cov-report=term-missing
```

## Stack

- Python 3.10+
- pandas + numpy
- SQLite (warehouse)
- pytest

## Estructura

```
etl-mineria-peru/
├── src/
│   ├── config/
│   │   └── settings.py          # Metales, regiones, rutas
│   ├── extract/
│   │   └── minem_loader.py      # Carga y validación de CSVs
│   ├── transform/
│   │   ├── cleaner.py           # Normalización y limpieza
│   │   └── enricher.py          # Variaciones, MA, ranking, HHI
│   ├── quality/
│   │   └── validators.py        # Scoring de calidad ponderado
│   ├── load/
│   │   └── warehouse.py         # Esquema estrella SQLite
│   ├── utils/
│   │   └── logger.py
│   └── pipeline.py              # Orquestador (CLI)
├── tests/
│   ├── fixtures/
│   │   └── produccion_sample.csv
│   ├── test_loader.py
│   ├── test_cleaner.py
│   ├── test_enricher.py
│   ├── test_validators.py
│   └── test_warehouse.py
└── requirements.txt
```

---

## What it does

ETL pipeline for Peruvian mining production data by metal, region, and period. Data comes from MINEM statistical bulletins and loads into a SQLite star schema warehouse.

Peru is the world's second largest producer of copper, silver, and zinc. This project analyzes monthly production of 8 metals across 15 mining regions, computing year-over-year changes, moving averages, and regional concentration (HHI index).

---

## Fuentes de datos

| Fuente | Descripción | Enlace |
|--------|-------------|--------|
| MINEM - Boletín Estadístico de Minería | Producción mensual por metal y región | [https://www.minem.gob.pe/_estadisticaSector.php?idSector=1&idEstadistica=12501](https://www.minem.gob.pe/_estadisticaSector.php?idSector=1&idEstadistica=12501) |
| MINEM - Datos abiertos | Portal de datos abiertos del sector minero | [https://www.minem.gob.pe/_estadistica.php?idSector=1&idEstadistica=12544](https://www.minem.gob.pe/_estadistica.php?idSector=1&idEstadistica=12544) |
| Datos Abiertos Perú | Portal nacional de datos abiertos | [https://www.datosabiertos.gob.pe/](https://www.datosabiertos.gob.pe/) |
