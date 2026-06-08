import pandas as pd

# -----------------------
# Leer adjudicaciones
# -----------------------

df = pd.read_csv(
    "data/raw/adjudicaciones-2020.csv"
)

print("Registros originales:", len(df))

# -----------------------
# Eliminar fechas nulas
# -----------------------

df = df[
    df["Fecha de Adjudicación"].notna()
].copy()

print("Registros luego del filtro:", len(df))

# -----------------------
# Generar fecha_adjudicacion_id
# -----------------------

df["fecha_adjudicacion_id"] = (
    pd.to_datetime(
        df["Fecha de Adjudicación"],
        format="mixed",
        dayfirst=True
    )
    .dt.strftime("%Y%m%d")
    .astype(int)
)

# -----------------------
# -----------------------

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# -----------------------
# Conexión
# -----------------------

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

# -----------------------
# Leer dim_proveedor
# -----------------------

dim_proveedor = pd.read_sql(
    """
    SELECT
        proveedor_id,
        cuit
    FROM dw.dim_proveedor
    """,
    engine
)

# -----------------------
# Merge proveedor
# -----------------------

df = df.merge(
    dim_proveedor,
    left_on="CUIT",
    right_on="cuit",
    how="left"
)

print(
    "Proveedores sin match:",
    df["proveedor_id"].isna().sum()
)

print(
    df[
        [
            "CUIT",
            "proveedor_id"
        ]
    ]
    .head()
)

# -----------------------
# Leer dim_procedimiento
# -----------------------

dim_proc = pd.read_sql(
    """
    SELECT procedimiento_id
    FROM dw.dim_procedimiento
    """,
    engine
)

# -----------------------
# Merge procedimiento
# -----------------------

df = df.merge(
    dim_proc,
    left_on="Número Procedimiento",
    right_on="procedimiento_id",
    how="left"
)

print(
    "Procedimientos sin match:",
    df["procedimiento_id"].isna().sum()
)

print(
    df[
        [
            "Número Procedimiento",
            "procedimiento_id"
        ]
    ]
    .head()
)

# -----------------------
# Verificación
# -----------------------

print(
    df[
        [
            "Fecha de Adjudicación",
            "fecha_adjudicacion_id"
        ]
    ]
    .head()
)


# -----------------------
# Construir fact_adjudicacion
# -----------------------

fact_adjudicacion = pd.DataFrame()

fact_adjudicacion["nro_orden_compra"] = (
    df["Documento Contractual"]
)

fact_adjudicacion["procedimiento_id"] = (
    df["procedimiento_id"]
)

fact_adjudicacion["proveedor_id"] = (
    df["proveedor_id"]
)

fact_adjudicacion["fecha_adjudicacion_id"] = (
    df["fecha_adjudicacion_id"]
)

fact_adjudicacion["monto_adjudicado"] = (
    df["Monto"]
)

fact_adjudicacion["moneda"] = (
    df["Moneda"]
)

fact_adjudicacion["tipo_orden"] = (
    df["Tipo"]
)

# -----------------------
# Verificaciones
# -----------------------

print(
    "Filas fact:",
    len(fact_adjudicacion)
)
print()
print(
    fact_adjudicacion.head()
)
print()
print(
    fact_adjudicacion.isna().sum()
)

print(
    fact_adjudicacion["nro_orden_compra"]
    .duplicated()
    .sum()
)

# -----------------------
# Cargar fact_adjudicacion
# -----------------------

fact_adjudicacion.to_sql(
    "fact_adjudicacion",
    engine,
    schema="dw",
    if_exists="append",
    index=False
)

print("Carga finalizada.")