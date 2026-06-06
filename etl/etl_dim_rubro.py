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

# Obtener todos los rubros únicos
rubros_unicos = set()

for valor in df["Rubros"].dropna():

    for rubro in str(valor).split(";"):

        rubro = rubro.strip()

        if rubro != "":
            rubros_unicos.add(rubro)

# Convertir a DataFrame
df_rubro = pd.DataFrame(
    sorted(rubros_unicos),
    columns=["descripcion_rubro"]
)

print(f"Rubros únicos encontrados: {len(df_rubro)}")

# Cargar en PostgreSQL
df_rubro.to_sql(
    "dim_rubro",
    engine,
    schema="dw",
    if_exists="append",
    index=False
)

print("Carga finalizada.")