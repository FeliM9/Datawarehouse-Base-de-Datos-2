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
# CSV adjudicaciones
# -----------------------

df = pd.read_csv(
    "data/raw/adjudicaciones-2020.csv"
)

# Mismo filtro que usamos en fact_adjudicacion

df = df[
    df["Fecha de Adjudicación"].notna()
].copy()

print("Filas CSV:", len(df))

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

print("Filas fact:", len(fact))

# -----------------------
# Match
# -----------------------

test = df.merge(
    fact,
    left_on="Documento Contractual",
    right_on="nro_orden_compra",
    how="left"
)

print(
    "Fact sin match:",
    test["fact_adjudicacion_id"].isna().sum()
)

print(
    "Fact distintos encontrados:",
    test["fact_adjudicacion_id"].nunique()
)