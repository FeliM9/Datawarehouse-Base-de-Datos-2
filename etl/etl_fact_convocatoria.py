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
# Leer CSV
# -----------------------

df = pd.read_csv(
    "data/raw/convocatorias-2020.csv"
)

print("Registros CSV:", len(df))

# -----------------------
# Fecha -> fecha_id
# -----------------------

df["fecha_publicacion"] = pd.to_datetime(
    df["Fecha de Publicación"],
    format="mixed",
    dayfirst=True
)

df["fecha_publicacion_id"] = (
    df["fecha_publicacion"]
    .dt.strftime("%Y%m%d")
    .astype(int)
)

'''
print(df["fecha_publicacion"].head())
print(df["fecha_publicacion_id"].head())'''

# -----------------------
# Traer dim_organismo
# -----------------------
dim_org = pd.read_sql("""
SELECT
    organismo_id,
    nro_saf,
    descripcion_saf,
    nro_uoc,
    descripcion_uoc
FROM dw.dim_organismo
""", engine)

# -----------------------
# Join organismo
# -----------------------
df = df.merge(
    dim_org,
    left_on=[
        "Nro SAF",
        "Descripcion SAF",
        "Nro UOC",
        "Descripcion UOC"
    ],
    right_on=[
        "nro_saf",
        "descripcion_saf",
        "nro_uoc",
        "descripcion_uoc"
    ],
    how="left"
)
print("Filas luego del merge:", len(df))
print("Organismos sin match:", df["organismo_id"].isna().sum())

'''CODIGO DE DIAGNOSTICO
print("\nTOP procedimientos duplicados:")
conteo = (
    df.groupby("Número Procedimiento")
      .size()
      .sort_values(ascending=False)
)
print(conteo.head(30))


duplicados = df[
    df.duplicated(
        subset=["Número Procedimiento"],
        keep=False
    )
]
print("\nCantidad filas duplicadas:", len(duplicados))
print(
    duplicados[
        [
            "Número Procedimiento",
            "Nro SAF",
            "Nro UOC",
            "Descripcion UOC",
            "organismo_id"
        ]
    ]
    .head(50)
)'''

# -----------------------
# Fact final
# -----------------------

fact = pd.DataFrame()

fact["procedimiento_id"] = df["Número Procedimiento"]
fact["organismo_id"] = df["organismo_id"]
fact["fecha_publicacion_id"] = df["fecha_publicacion_id"]
fact["monto_estimado"] = df["Monto Estimado"]
fact["etapa"] = df["Etapa"]
fact["tipo_operacion"] = df["Tipo de Operación"]

print("Registros fact:", len(fact))




# -----------------------
# ELIMINADO DE REGISTROS EXISTENES ANTES DE CARGAR. SOLO EN FASE DESARROLLO. DESPUES ELIMINAR
# -----------------------
from sqlalchemy import text

with engine.begin() as conn:
    conn.execute(
        text("TRUNCATE TABLE dw.fact_convocatoria")
    )


# -----------------------
# Carga
# -----------------------
fact.to_sql(
    "fact_convocatoria",
    engine,
    schema="dw",
    if_exists="append",
    index=False
)

print("Carga finalizada.")