from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
WAREHOUSE_DIR = DATA_DIR / "warehouse"
LOG_DIR = PROJECT_ROOT / "logs"

for _d in (RAW_DIR, PROCESSED_DIR, WAREHOUSE_DIR, LOG_DIR):
    _d.mkdir(parents=True, exist_ok=True)

DB_PATH = WAREHOUSE_DIR / "mineria.db"

MINEM_BOLETIN_URL = (
    "https://www.minem.gob.pe/_estadisticaSector.php?"
    "idSector=1&idEstadistica=12501"
)
DATOS_ABIERTOS_URL = "https://www.datosabiertos.gob.pe/"

ANIO_INICIO = 2020
ANIO_FIN = 2024

METALES = {
    "cobre": {"unidad": "TMF", "factor_lb": 2204.62},
    "oro": {"unidad": "Oz.f.", "factor_lb": None},
    "plata": {"unidad": "Oz.f.", "factor_lb": None},
    "zinc": {"unidad": "TMF", "factor_lb": 2204.62},
    "plomo": {"unidad": "TMF", "factor_lb": 2204.62},
    "hierro": {"unidad": "TLF", "factor_lb": None},
    "estano": {"unidad": "TMF", "factor_lb": 2204.62},
    "molibdeno": {"unidad": "TMF", "factor_lb": 2204.62},
}

REGIONES_MINERAS = [
    "Ancash", "Arequipa", "Cajamarca", "Cusco", "Apurimac",
    "Junin", "La Libertad", "Lima", "Moquegua", "Pasco",
    "Puno", "Tacna", "Ica", "Huancavelica", "Ayacucho",
]
