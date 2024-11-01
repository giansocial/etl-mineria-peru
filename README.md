# ETL Produccion Minera - Peru

Soy Gian Cruz.

Pipeline ETL que procesa datos de produccion minera del Peru por metal, region y periodo. Los datos provienen del Boletin Estadistico de Mineria del Ministerio de Energia y Minas (MINEM) y se cargan a un warehouse SQLite con esquema estrella.

Peru es el segundo productor mundial de cobre, plata y zinc. Este proyecto analiza la produccion mensual de 8 metales en 15 regiones mineras, calculando variaciones interanuales, promedios moviles y concentracion regional (indice HHI).

## Que hace

- Carga datos de produccion desde archivos CSV (exportaciones del boletin MINEM)
- Limpia y normaliza nombres de metales, regiones y valores numericos
- Calcula variacion interanual y mensual de produccion
- Genera promedios moviles de 6 meses
- Rankea regiones por volumen de produccion
- Calcula indice de concentracion Herfindahl-Hirschman (HHI)
- Ejecuta validacion de calidad (completitud, unicidad, rango)
- Carga a warehouse SQLite con esquema dimensional

## Esquema del warehouse

```
dim_metal (id, nombre, unidad, factor_lb)
dim_region (id, nombre)
dim_tiempo (id, anio, mes, periodo, trimestre)
fact_produccion (metal_id, region_id, tiempo_id, produccion, var_interanual, var_mensual, ma_6m)
```

## Instalacion

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Uso

```bash
# Colocar CSVs de produccion en data/raw/
# Formato: metal, region, anio, mes, produccion

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
│   │   └── minem_loader.py      # Carga y validacion de CSVs
│   ├── transform/
│   │   ├── cleaner.py           # Normalizacion y limpieza
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

| Fuente | Descripcion | Enlace |
|--------|-------------|--------|
| MINEM - Boletin Estadistico de Mineria | Produccion mensual por metal y region | [https://www.minem.gob.pe/_estadisticaSector.php?idSector=1&idEstadistica=12501](https://www.minem.gob.pe/_estadisticaSector.php?idSector=1&idEstadistica=12501) |
| MINEM - Datos abiertos | Portal de datos abiertos del sector minero | [https://www.minem.gob.pe/_estadistica.php?idSector=1&idEstadistica=12544](https://www.minem.gob.pe/_estadistica.php?idSector=1&idEstadistica=12544) |
| Datos Abiertos Peru | Portal nacional de datos abiertos | [https://www.datosabiertos.gob.pe/](https://www.datosabiertos.gob.pe/) |
