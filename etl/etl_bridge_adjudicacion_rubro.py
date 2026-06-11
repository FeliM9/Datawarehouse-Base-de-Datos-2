import os

import pandas as pd
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
# Leer adjudicaciones
# -----------------------

df = pd.read_csv(
    "data/raw/adjudicaciones-2020.csv"
)

# Mismo filtro usado en fact_adjudicacion

df = df[
    df["Fecha de Adjudicación"].notna()
].copy()

print("Filas adjudicaciones:", len(df))

# -----------------------
# Explode rubros
# -----------------------

df["Rubros"] = (
    df["Rubros"]
    .fillna("")
    .str.split(";")
)

df = df.explode("Rubros")

df["Rubros"] = (
    df["Rubros"]
    .str.strip()
)

df = df[
    df["Rubros"] != ""
].copy()

print("Filas luego de explode:", len(df))

# -----------------------
# Fact adjudicacion
# -----------------------

fact = pd.read_sql(
    """
    SELECT
        fact_adjudicacion_id,
        nro_orden_compra
    FROM dw.fact_adjudicacion
    """,
    engine
)

df = df.merge(
    fact,
    left_on="Documento Contractual",
    right_on="nro_orden_compra",
    how="left"
)

print(
    "Fact sin match:",
    df["fact_adjudicacion_id"].isna().sum()
)

# -----------------------
# Dim rubro
# -----------------------

dim_rubro = pd.read_sql(
    """
    SELECT
        rubro_id,
        descripcion_rubro
    FROM dw.dim_rubro
    """,
    engine
)

df = df.merge(
    dim_rubro,
    left_on="Rubros",
    right_on="descripcion_rubro",
    how="left"
)

print(
    "Rubros sin match:",
    df["rubro_id"].isna().sum()
)

# -----------------------
# Construir bridge
# -----------------------

bridge = df[
    [
        "fact_adjudicacion_id",
        "rubro_id"
    ]
].copy()

bridge = bridge.drop_duplicates()

print(
    "Filas bridge:",
    len(bridge)
)

print()

print(
    bridge.isna().sum()
)

# -----------------------
# Carga
# -----------------------

bridge.to_sql(
    "bridge_adjudicacion_rubro",
    engine,
    schema="dw",
    if_exists="append",
    index=False
)

print("Carga finalizada.")