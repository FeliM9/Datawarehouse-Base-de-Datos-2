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

# -----------------------
# Eliminar registros sin fecha
# -----------------------

filas_originales = len(df)

df = df[
    df["Fecha de Adjudicación"].notna()
].copy()

print(
    "Registros excluidos por fecha nula:",
    filas_originales - len(df)
)

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
# Leer dim_fecha
# -----------------------

dim_fecha = pd.read_sql(
    """
    SELECT fecha_id
    FROM dw.dim_fecha
    """,
    engine
)

# -----------------------
# Test de integridad
# -----------------------

test_fecha = df.merge(
    dim_fecha,
    left_on="fecha_adjudicacion_id",
    right_on="fecha_id",
    how="left"
)

print(
    "Fechas sin match:",
    test_fecha["fecha_id"].isna().sum()
)

print(
    "Fechas distintas sin match:",
    test_fecha.loc[
        test_fecha["fecha_id"].isna(),
        "fecha_adjudicacion_id"
    ].nunique()
)