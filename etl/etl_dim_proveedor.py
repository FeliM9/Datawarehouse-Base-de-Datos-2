import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Cargar .env
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

# Leer CSV
df = pd.read_csv("data/raw/adjudicaciones-2020.csv")

df_prov = df[
    [
        "CUIT",
        "Descripción Proveedor"
    ]
].copy()

df_prov.columns = [
    "cuit",
    "razon_social"
]

df_prov["provincia"] = None

# Un proveedor por CUIT
df_prov = (
    df_prov
    .groupby("cuit", as_index=False)
    .first()
)

print(f"Proveedores únicos encontrados: {len(df_prov)}")

# Cargar en PostgreSQL
df_prov.to_sql(
    "dim_proveedor",
    engine,
    schema="dw",
    if_exists="append",
    index=False
)

print("Carga finalizada.")