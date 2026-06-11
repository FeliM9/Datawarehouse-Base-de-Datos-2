import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Cargar variables del .env
load_dotenv()

# Conexión a Neon
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

# Leer CSV
df = pd.read_csv(
    "data/raw/convocatorias-2020.csv"
)

# Seleccionar columnas necesarias
df_org = df[
    [
        "Nro SAF",
        "Descripcion SAF",
        "Nro UOC",
        "Descripcion UOC"
    ]
].copy()

# Eliminar duplicados
df_org = df_org.drop_duplicates()

# Renombrar columnas
df_org.columns = [
    "nro_saf",
    "descripcion_saf",
    "nro_uoc",
    "descripcion_uoc"
]

print(f"Organismos únicos encontrados: {len(df_org)}")

# Insertar en PostgreSQL
df_org.to_sql(
    "dim_organismo",
    engine,
    schema="dw",
    if_exists="append",
    index=False
)

print("Carga finalizada.")