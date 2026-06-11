"""
Orquestacion del Data Warehouse de licitaciones con Dagster.

Idea general
------------
No se reescribe la logica de los scripts ETL existentes. Cada script de
`etl/` y `automation/` se "envuelve" como un *asset* de Dagster que lo ejecuta
como subproceso (igual que hacia `automation/run_pipeline.py`), pero ahora con:

  - grafo de dependencias explicito (linaje del DW visible en la UI),
  - reintentos, logs y estados por paso,
  - un log en archivo por cada paso, guardado en la carpeta `Dagster Logs/`,
  - un chequeo previo de credenciales (.env) con mensaje claro,
  - un sensor que dispara el rebuild cuando cambian las fuentes,
  - un asset final que registra los hashes en `dw.etl_control` para cerrar el
    loop y no re-disparar en falso.

Como correr (desde la raiz del repo, con el venv activado):
    pip install -r requierements.txt
    dagster dev

Luego abrir http://localhost:3000 y "Materialize all".
"""

import datetime
import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from dagster import (
    AssetExecutionContext,
    AssetSelection,
    DefaultScheduleStatus,
    DefaultSensorStatus,
    Definitions,
    RunRequest,
    ScheduleDefinition,
    SkipReason,
    asset,
    define_asset_job,
    sensor,
)

# ---------------------------------------------------------------------------
# Rutas y entorno
# ---------------------------------------------------------------------------
# La raiz del repo es la carpeta que contiene `etl/`, `automation/`, `.env`.
# Se calcula desde la ubicacion de este archivo, asi `dagster dev` puede
# lanzarse desde cualquier directorio sin romper las rutas relativas que usan
# los scripts (p. ej. "data/raw/...").
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Carpeta donde se guardan los logs de cada paso del ETL.
LOG_DIR = PROJECT_ROOT / "Dagster Logs"
LOG_DIR.mkdir(exist_ok=True)

# Cargamos el .env de la raiz para que el sensor y el asset de control tengan
# las credenciales de Neon disponibles en os.environ. Los subprocesos heredan
# este os.environ automaticamente.
load_dotenv(PROJECT_ROOT / ".env")

# Variables que deben estar definidas para poder conectarse a Neon.
REQUIRED_ENV = ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME"]

# IDs de las Google Sheets que actuan como fuente (mismos que en
# automation/check_changes.py). La clave es el nombre logico de la fuente,
# que coincide con la columna `fuente` de dw.etl_control.
SHEETS = {
    "adjudicaciones": "12xT8rHIfRv8BPIG7iTArgD0mztNwZU3GN5Ap66_3sDk",
    "convocatorias": "16OULzb0pizK5PXbYXc3tZDm_JfCJwoNIf-K4YuxLYyk",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _verificar_env() -> None:
    """Falla temprano y con mensaje claro si faltan credenciales en el .env.

    Sin esto, los scripts arman una URL como `...//None:None@None:None/None`
    y revientan con un error criptico (`int('None')`) recien en reset_dw.
    """
    faltantes = [v for v in REQUIRED_ENV if not os.getenv(v)]
    if faltantes:
        raise RuntimeError(
            "Faltan variables de entorno: "
            + ", ".join(faltantes)
            + f". Crea un archivo .env en {PROJECT_ROOT} a partir de "
            ".env.example y completa los datos de Neon."
        )


def _escribir_log(rel_path: str, result: subprocess.CompletedProcess) -> Path:
    """Guarda stdout/stderr de un paso en `Dagster Logs/`.

    Crea un archivo por ejecucion: `Dagster Logs/AAAAMMDD_HHMMSS_<script>.log`.
    Ademas agrega una linea de resumen al log maestro `Dagster Logs/etl.log`.
    Devuelve la ruta del archivo creado.
    """
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre = Path(rel_path).stem
    log_file = LOG_DIR / f"{ts}_{nombre}.log"

    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"# script        : {rel_path}\n")
        f.write(f"# fecha/hora    : {datetime.datetime.now().isoformat()}\n")
        f.write(f"# codigo salida : {result.returncode}\n\n")
        f.write("=== STDOUT ===\n")
        f.write(result.stdout or "")
        f.write("\n\n=== STDERR ===\n")
        f.write(result.stderr or "")

    estado = "OK" if result.returncode == 0 else f"FALLO({result.returncode})"
    with open(LOG_DIR / "etl.log", "a", encoding="utf-8") as f:
        f.write(
            f"{datetime.datetime.now().isoformat()}  {estado:12}  "
            f"{rel_path}  -> {log_file.name}\n"
        )
    return log_file


def run_script(context: AssetExecutionContext, rel_path: str) -> None:
    """Ejecuta un script del repo como subproceso, desde la raiz del proyecto.

    Usa el mismo interprete de Python con el que corre Dagster (sys.executable)
    para respetar el entorno virtual activo. Manda la salida a los logs de
    Dagster (UI) y tambien a un archivo en `Dagster Logs/`. Si el script falla,
    levanta excepcion para que el asset quede marcado como fallido.
    """
    _verificar_env()

    script = PROJECT_ROOT / rel_path
    if not script.exists():
        raise FileNotFoundError(f"No se encontro el script: {script}")

    context.log.info(f"Ejecutando {rel_path}")
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )

    log_file = _escribir_log(rel_path, result)
    context.log.info(f"Log guardado en: Dagster Logs/{log_file.name}")

    if result.stdout:
        context.log.info(result.stdout.strip())
    if result.returncode != 0:
        context.log.error(result.stderr.strip())
        raise RuntimeError(f"{rel_path} termino con codigo {result.returncode}")
    context.log.info(f"OK: {rel_path}")


def _get_engine():
    """Crea un engine de SQLAlchemy hacia Neon usando variables de entorno."""
    _verificar_env()
    url = (
        f"postgresql+psycopg2://"
        f"{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    return create_engine(url)


def _hash_sheet(sheet_id: str) -> str:
    """Descarga una Google Sheet como CSV y devuelve su hash MD5."""
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    df = pd.read_csv(url)
    return hashlib.md5(df.to_csv(index=False).encode("utf-8")).hexdigest()


# ===========================================================================
# ASSETS - cada uno envuelve un script existente
# Las dependencias (`deps`) reproducen el orden correcto de run_pipeline.py,
# pero exponen el paralelismo real (las dimensiones independientes pueden
# materializarse en paralelo).
# ===========================================================================

# --- Mantenimiento ---------------------------------------------------------
# Nota: el "gate" de no reconstruir si no cambio nada vive en el SENSOR
# (sensor_cambio_en_fuentes), que saltea limpio (tick "Skipped", sin rojo y sin
# tocar la base) cuando las fuentes no cambiaron. El rebuild MANUAL no tiene
# gate: reconstruye siempre (es una accion intencional).
@asset(
    group_name="mantenimiento",
    description="Descarga las Google Sheets a data/raw/ antes de reconstruir, "
                "para que el rebuild use siempre la fuente mas reciente.",
)
def sincronizar_fuentes(context: AssetExecutionContext) -> None:
    run_script(context, "automation/download_sources.py")


@asset(
    deps=[sincronizar_fuentes],
    group_name="mantenimiento",
    description="TRUNCATE de todas las tablas del DW (rebuild completo).",
)
def reset_dw(context: AssetExecutionContext) -> None:
    run_script(context, "automation/reset_dw.py")


# --- Dimensiones -----------------------------------------------------------
@asset(deps=[reset_dw], group_name="dimensiones", description="dim_fecha")
def dim_fecha(context: AssetExecutionContext) -> None:
    run_script(context, "etl/load_dim_fecha.py")


@asset(deps=[reset_dw], group_name="dimensiones",
       description="dim_organismo (desde convocatorias)")
def dim_organismo(context: AssetExecutionContext) -> None:
    run_script(context, "etl/etl_dim_organismo.py")


@asset(deps=[reset_dw], group_name="dimensiones",
       description="dim_proveedor (SCD Tipo 2: merge versionado, no se trunca)")
def dim_proveedor(context: AssetExecutionContext) -> None:
    run_script(context, "etl/etl_dim_proveedor.py")


@asset(deps=[reset_dw], group_name="dimensiones", description="dim_rubro")
def dim_rubro(context: AssetExecutionContext) -> None:
    run_script(context, "etl/etl_dim_rubro.py")


@asset(deps=[reset_dw], group_name="dimensiones",
       description="dim_procedimiento (base, desde convocatorias)")
def dim_procedimiento(context: AssetExecutionContext) -> None:
    run_script(context, "etl/etl_dim_procedimiento.py")


@asset(deps=[dim_procedimiento], group_name="dimensiones",
       description="Completa procedimientos referenciados por adjudicaciones "
                   "que no estaban en convocatorias.")
def completar_procedimientos(context: AssetExecutionContext) -> None:
    run_script(context, "etl/etl_completar_procedimientos_faltantes.py")


# --- Hechos ----------------------------------------------------------------
@asset(
    deps=[dim_organismo, dim_fecha, completar_procedimientos],
    group_name="hechos",
    description="fact_convocatoria (FK a organismo, fecha y procedimiento).",
)
def fact_convocatoria(context: AssetExecutionContext) -> None:
    run_script(context, "etl/etl_fact_convocatoria.py")


@asset(
    deps=[dim_proveedor, dim_fecha, completar_procedimientos],
    group_name="hechos",
    description="fact_adjudicacion (FK a proveedor, fecha y procedimiento).",
)
def fact_adjudicacion(context: AssetExecutionContext) -> None:
    run_script(context, "etl/etl_fact_adjudicacion.py")


# --- Bridge ----------------------------------------------------------------
@asset(
    deps=[fact_adjudicacion, dim_rubro],
    group_name="hechos",
    description="bridge_adjudicacion_rubro (M:N entre adjudicaciones y rubros).",
)
def bridge_adjudicacion_rubro(context: AssetExecutionContext) -> None:
    run_script(context, "etl/etl_bridge_adjudicacion_rubro.py")


# --- Cierre del loop -------------------------------------------------------
@asset(
    deps=[fact_convocatoria, bridge_adjudicacion_rubro],
    group_name="control",
    description="Registra el hash actual de cada fuente en dw.etl_control. "
                "Evita que el sensor vuelva a disparar por el mismo cambio.",
)
def registrar_control_hashes(context: AssetExecutionContext) -> None:
    engine = _get_engine()
    with engine.begin() as conn:
        # Garantiza que la tabla de control exista con PK en `fuente`,
        # requisito del ON CONFLICT de abajo. Idempotente.
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS dw.etl_control (
                    fuente              TEXT PRIMARY KEY,
                    hash_actual         TEXT,
                    fecha_actualizacion TIMESTAMP
                )
                """
            )
        )
        for fuente, sheet_id in SHEETS.items():
            h = _hash_sheet(sheet_id)
            conn.execute(
                text(
                    """
                    INSERT INTO dw.etl_control (fuente, hash_actual, fecha_actualizacion)
                    VALUES (:fuente, :hash, CURRENT_TIMESTAMP)
                    ON CONFLICT (fuente)
                    DO UPDATE SET
                        hash_actual = EXCLUDED.hash_actual,
                        fecha_actualizacion = CURRENT_TIMESTAMP
                    """
                ),
                {"fuente": fuente, "hash": h},
            )
            context.log.info(f"etl_control actualizado: {fuente} -> {h}")


# ===========================================================================
# JOB - materializa todo el grafo (rebuild completo del DW)
# ===========================================================================
rebuild_dw_job = define_asset_job(
    name="rebuild_dw_job",
    selection=AssetSelection.all(),
    description="Reconstruye el DW completo: sync -> reset -> dimensiones -> "
                "hechos -> bridge -> control.",
)

# Rebuild forzado: mismo grafo, pensado para lanzarlo a mano desde la UI
# (Jobs -> rebuild_forzado -> Launch Run) cuando querés reconstruir si o si
# (por ejemplo para aplicar cambios que ya guardaste en las sheets). No tiene
# gate; el "no reconstruir si no cambio nada" lo maneja el sensor.
rebuild_forzado_job = define_asset_job(
    name="rebuild_forzado",
    selection=AssetSelection.all(),
    description="Rebuild completo forzado (manual, sin gate).",
)


# ===========================================================================
# SCHEDULE - rebuild diario (apagado por defecto)
# ===========================================================================
rebuild_diario_schedule = ScheduleDefinition(
    name="rebuild_diario",
    job=rebuild_dw_job,
    cron_schedule="0 6 * * *",  # todos los dias 06:00
    default_status=DefaultScheduleStatus.STOPPED,
)


# ===========================================================================
# SENSOR - dispara el rebuild cuando cambian las fuentes
# ===========================================================================
# Esta APAGADO por defecto: encendelo desde la UI (pestana Automation) cuando
# tengas el .env y dw.etl_control listos. Compara el hash actual de cada
# Google Sheet contra lo guardado en dw.etl_control; si difiere, dispara
# rebuild_dw_job. El run_key evita lanzar dos veces por el mismo cambio.
@sensor(
    name="sensor_cambio_en_fuentes",
    job=rebuild_dw_job,
    minimum_interval_seconds=60,
    default_status=DefaultSensorStatus.STOPPED,
    description="Detecta cambios (por hash) en las fuentes y dispara el rebuild.",
)
def sensor_cambio_en_fuentes(context):
    try:
        engine = _get_engine()
        guardados = pd.read_sql(
            "SELECT fuente, hash_actual FROM dw.etl_control", engine
        )
        guardados = dict(zip(guardados["fuente"], guardados["hash_actual"]))

        actuales = {}
        cambios = []
        for fuente, sheet_id in SHEETS.items():
            h = _hash_sheet(sheet_id)
            actuales[fuente] = h
            if guardados.get(fuente) != h:
                cambios.append(fuente)
    except Exception as e:  # noqa: BLE001 - no queremos tumbar el daemon
        yield SkipReason(f"No se pudieron verificar las fuentes: {e}")
        return

    if not cambios:
        yield SkipReason("Sin cambios en las fuentes.")
        return

    context.log.info(f"Cambios detectados en: {', '.join(cambios)}")
    run_key = "-".join(f"{k}:{v}" for k, v in sorted(actuales.items()))
    yield RunRequest(run_key=run_key)


# ===========================================================================
# DEFINITIONS - punto de entrada que Dagster carga
# ===========================================================================
defs = Definitions(
    assets=[
        sincronizar_fuentes,
        reset_dw,
        dim_fecha,
        dim_organismo,
        dim_proveedor,
        dim_rubro,
        dim_procedimiento,
        completar_procedimientos,
        fact_convocatoria,
        fact_adjudicacion,
        bridge_adjudicacion_rubro,
        registrar_control_hashes,
    ],
    jobs=[rebuild_dw_job, rebuild_forzado_job],
    schedules=[rebuild_diario_schedule],
    sensors=[sensor_cambio_en_fuentes],
)
