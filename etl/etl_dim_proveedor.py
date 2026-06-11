import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# ===========================================================================
# dim_proveedor - SCD Tipo 2 RECONSTRUIDO desde el historial (effective-dated)
# ---------------------------------------------------------------------------
# Clave de negocio: cuit. Surrogate key: proveedor_id (PK).
# Atributos versionados: razon_social y provincia (Provincia Operativa
# Proveedor del CSV; si la columna no existe, queda NULL y no rompe).
#
# En vez de quedarse con el estado mas reciente, se RECONSTRUYE la linea de
# tiempo completa de cada CUIT: se recorren sus adjudicaciones por fecha y se
# arma una "corrida" (version) por cada periodo en que (razon_social,
# provincia) se mantiene constante. Cada version tiene su vigencia REAL
# (fecha_desde / fecha_hasta) tomada de las fechas de adjudicacion.
#
# La carga es un UPSERT idempotente por (cuit, fecha_desde): NO trunca.
#   - version nueva (cuit, fecha_desde) que no esta -> INSERT.
#   - version ya presente cuya vigencia/atributos cambiaron -> UPDATE.
# Asi, correr sin cambios no agrega nada; editar el sheet agrega las versiones
# nuevas y cierra la anterior. El historial nunca se pisa.
#
# NOTA: requiere arrancar con dim_proveedor vacia (reset unico, no por rebuild)
# porque las filas viejas tenian fecha de carga en vez de fecha real.
# ===========================================================================

load_dotenv()

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)

engine = create_engine(DATABASE_URL)

COL_PROVINCIA = "Provincia Operativa Proveedor"


def _k(serie: pd.Series) -> pd.Series:
    """Normaliza texto para comparar (None/NaN -> '', recorta espacios)."""
    return serie.fillna("").astype(str).str.strip()


def _kf(serie: pd.Series) -> pd.Series:
    """Normaliza timestamps para comparar (NaT -> '')."""
    return serie.dt.strftime("%Y-%m-%d %H:%M:%S").fillna("")


# -----------------------
# 1) Reconstruir la linea de tiempo por CUIT desde adjudicaciones
# -----------------------
df = pd.read_csv("data/raw/adjudicaciones-2020.csv")

src = pd.DataFrame()
src["cuit"] = df["CUIT"]
src["razon_social"] = df["Descripción Proveedor"]
src["provincia"] = df[COL_PROVINCIA] if COL_PROVINCIA in df.columns else None
src["fecha"] = pd.to_datetime(
    df["Fecha de Adjudicación"], format="mixed", dayfirst=True, errors="coerce"
)
src = src.dropna(subset=["fecha"]).sort_values(["cuit", "fecha"]).reset_index(drop=True)

# Una "corrida" arranca cuando cambia (razon_social, provincia) dentro del CUIT.
src["attr"] = _k(src["razon_social"]) + " || " + _k(src["provincia"])
src["prev"] = src.groupby("cuit")["attr"].shift()
src["nueva_corrida"] = src["attr"] != src["prev"]

# Las filas que inician corrida son las versiones; la fecha de inicio = su fecha.
runs = src[src["nueva_corrida"]].copy()
runs["fecha_desde"] = runs["fecha"]
runs["fecha_hasta"] = runs.groupby("cuit")["fecha_desde"].shift(-1)
runs["es_vigente"] = runs["fecha_hasta"].isna()

target = runs[
    ["cuit", "razon_social", "provincia", "fecha_desde", "fecha_hasta", "es_vigente"]
].reset_index(drop=True)

# -----------------------
# 2) Estado actual de la dimension
# -----------------------
dim = pd.read_sql(
    """
    SELECT proveedor_id, cuit, razon_social, provincia,
           fecha_desde, fecha_hasta, es_vigente
    FROM dw.dim_proveedor
    """,
    engine,
)

# -----------------------
# 3) UPSERT por (cuit, fecha_desde)
# -----------------------
m = target.merge(
    dim, on=["cuit", "fecha_desde"], how="left", suffixes=("", "_dim")
)

# Inserts: versiones del target sin contraparte en la dimension
nuevas = m[m["proveedor_id"].isna()][
    ["cuit", "razon_social", "provincia", "fecha_desde", "fecha_hasta", "es_vigente"]
].copy()

# Updates: versiones ya presentes cuya vigencia o atributos cambiaron
ex = m[m["proveedor_id"].notna()].copy()
cambiadas = ex.iloc[0:0]
if len(ex):
    dif = (
        (_k(ex["razon_social"]) != _k(ex["razon_social_dim"]))
        | (_k(ex["provincia"]) != _k(ex["provincia_dim"]))
        | (_kf(ex["fecha_hasta"]) != _kf(ex["fecha_hasta_dim"]))
        | (ex["es_vigente"].astype(bool) != ex["es_vigente_dim"].astype(bool))
    )
    cambiadas = ex[dif]

with engine.begin() as conn:
    for _, r in cambiadas.iterrows():
        conn.execute(
            text(
                """
                UPDATE dw.dim_proveedor
                SET razon_social = :rs,
                    provincia    = :pv,
                    fecha_hasta  = :fh,
                    es_vigente   = :ev
                WHERE proveedor_id = :pid
                """
            ),
            {
                "rs": None if pd.isna(r["razon_social"]) else r["razon_social"],
                "pv": None if pd.isna(r["provincia"]) else r["provincia"],
                "fh": None if pd.isna(r["fecha_hasta"]) else r["fecha_hasta"].to_pydatetime(),
                "ev": bool(r["es_vigente"]),
                "pid": int(r["proveedor_id"]),
            },
        )

    if len(nuevas):
        nuevas.to_sql(
            "dim_proveedor", conn, schema="dw", if_exists="append", index=False
        )

print(f"Proveedores (CUIT) en la fuente: {target['cuit'].nunique()}")
print(f"Versiones reconstruidas (target): {len(target)}")
print(f"Versiones nuevas insertadas: {len(nuevas)}")
print(f"Versiones actualizadas (vigencia/atributos): {len(cambiadas)}")
print("Carga SCD Tipo 2 (reconstruccion) finalizada.")
