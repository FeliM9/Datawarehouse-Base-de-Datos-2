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

df_adj = pd.read_csv(
    "data/raw/adjudicaciones-2020.csv"
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
# Detectar faltantes
# -----------------------

test_proc = df_adj.merge(
    dim_proc,
    left_on="Número Procedimiento",
    right_on="procedimiento_id",
    how="left"
)

sin_match = test_proc[
    test_proc["procedimiento_id"].isna()
]

print(
    "Procedimientos faltantes distintos:",
    sin_match["Número Procedimiento"].nunique()
)

# -----------------------
# Construir dataframe
# -----------------------

faltantes_dim = (
    sin_match[
        [
            "Número Procedimiento",
            "Modalidad",
            "Tipo de Procedimiento"
        ]
    ]
    .drop_duplicates()
)

faltantes_dim = faltantes_dim.rename(
    columns={
        "Número Procedimiento": "procedimiento_id",
        "Modalidad": "modalidad",
        "Tipo de Procedimiento": "tipo_procedimiento"
    }
)

# Ejercicio inferido desde el código
faltantes_dim["ejercicio"] = (
    "20"
    + faltantes_dim["procedimiento_id"]
    .str.extract(r"(\d{2})$")[0]
)

# Campos no disponibles
faltantes_dim["nombre_procedimiento"] = "DESCONOCIDO"
faltantes_dim["objeto_procedimiento"] = "DESCONOCIDO"

# Orden de columnas igual a dim_procedimiento
faltantes_dim = faltantes_dim[
    [
        "procedimiento_id",
        "nombre_procedimiento",
        "objeto_procedimiento",
        "ejercicio",
        "modalidad",
        "tipo_procedimiento"
    ]
]

print(
    "Procedimientos a insertar:",
    len(faltantes_dim)
)

print(faltantes_dim.head())

# -----------------------
# Carga
# -----------------------

faltantes_dim.to_sql(
    "dim_procedimiento",
    engine,
    schema="dw",
    if_exists="append",
    index=False
)

print("Carga finalizada.")
