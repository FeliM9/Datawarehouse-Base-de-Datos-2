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
df = pd.read_csv("data/raw/convocatorias-2020.csv")

# Seleccionar columnas
df_proc = df[
    [
        "Número Procedimiento",
        "Nombre del Procedimiento",
        "Objeto del Procedimiento",
        "Ejercicio",
        "Modalidad",
        "Tipo de Procedimiento"
    ]
].copy()

# Renombrar columnas
df_proc.columns = [
    "procedimiento_id",
    "nombre_procedimiento",
    "objeto_procedimiento",
    "ejercicio",
    "modalidad",
    "tipo_procedimiento"
]

# Eliminar duplicados
df_proc = df_proc.drop_duplicates()

print(f"Procedimientos únicos encontrados: {len(df_proc)}")

# Cargar dimensión
df_proc.to_sql(
    "dim_procedimiento",
    engine,
    schema="dw",
    if_exists="append",
    index=False
)

print("Carga finalizada.")