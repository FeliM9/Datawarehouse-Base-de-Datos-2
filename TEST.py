
'''CONVOCATORIAS'''
'''import pandas as pd
df = pd.read_csv("data/raw/convocatorias-2020.csv")
print(df.columns.tolist())'''


'''ADJUDICACIONES'''
'''import pandas as pd
df = pd.read_csv("data/raw/adjudicaciones-2020.csv")
print(df.columns.tolist())'''

'''
import pandas as pd
df = pd.read_csv("data/raw/adjudicaciones-2020.csv")
print(df["Rubros"].dropna().head(20).tolist())'''

'''
import pandas as pd
df = pd.read_csv("data/raw/adjudicaciones-2020.csv")
print(df[["CUIT", "Descripción Proveedor"]].head(20))


print(df["CUIT"].isna().sum())
print(df["Descripción Proveedor"].isna().sum())'''

'''
import pandas as pd
df = pd.read_csv("data/raw/adjudicaciones-2020.csv")
print(
    df[["CUIT", "Descripción Proveedor"]]
    .drop_duplicates()
    .shape[0]
)
print(df.shape[0])'''

'''
import pandas as pd
df = pd.read_csv("data/raw/adjudicaciones-2020.csv")
duplicados = (
    df.groupby("CUIT")["Descripción Proveedor"]
    .nunique()
    .reset_index()
)
duplicados = duplicados[
    duplicados["Descripción Proveedor"] > 1
]
print(duplicados.head(20))
print()
print("Cantidad de CUIT conflictivos:", len(duplicados))'''


'''
import pandas as pd
df = pd.read_csv("data/raw/adjudicaciones-2020.csv")
cuit_conflictivo = "30-71477506-1"
print(
    df.loc[
        df["CUIT"] == cuit_conflictivo,
        ["CUIT", "Descripción Proveedor"]
    ].drop_duplicates()
)'''


'''
import pandas as pd
df = pd.read_csv("data/raw/convocatorias-2020.csv")
print(df["Fecha de Publicación"].head(10).tolist())
print()
print(df["Monto Estimado"].head(10).tolist())'''


'''
import pandas as pd
df = pd.read_csv("data/raw/convocatorias-2020.csv")
print(
    df[
        ["Nro SAF", "Nro UOC"]
    ]
    .drop_duplicates()
    .shape[0]
)'''

'''
import pandas as pd
df = pd.read_csv("data/raw/convocatorias-2020.csv")
organismos = (
    df[["Nro SAF", "Nro UOC"]]
    .drop_duplicates()
    .sort_values(["Nro SAF", "Nro UOC"])
)
print(organismos.head(20))
print()
print("Total:", len(organismos))'''


'''
import pandas as pd
df = pd.read_csv("data/raw/convocatorias-2020.csv")
print(df.columns.tolist())'''

'''
conteo = (
    merged
    .groupby("Número Procedimiento")
    .size()
    .sort_values(ascending=False)
)

print(conteo.head(20))'''



'''
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
# Leer CSV adjudicaciones
# -----------------------

df = pd.read_csv(
    "data/raw/adjudicaciones-2020.csv"
)

print("Filas adjudicaciones:", len(df))

# =====================================================
# TEST 1 - PROVEEDORES
# =====================================================

dim_proveedor = pd.read_sql(
    """
    SELECT
        proveedor_id,
        cuit
    FROM dw.dim_proveedor
    """,
    engine
)

test_proveedor = df.merge(
    dim_proveedor,
    left_on="CUIT",
    right_on="cuit",
    how="left"
)

print(
    "Proveedores sin match:",
    test_proveedor["proveedor_id"].isna().sum()
)

# =====================================================
# TEST 2 - RUBROS
# =====================================================

dim_rubro = pd.read_sql(
    """
    SELECT
        rubro_id,
        descripcion_rubro
    FROM dw.dim_rubro
    """,
    engine
)

test_rubro = df.merge(
    dim_rubro,
    left_on="Rubros",
    right_on="descripcion_rubro",
    how="left"
)

print(
    "Rubros sin match:",
    test_rubro["rubro_id"].isna().sum()
)

# =====================================================
# TEST 3 - PROCEDIMIENTOS
# =====================================================

dim_proc = pd.read_sql(
    """
    SELECT
        procedimiento_id
    FROM dw.dim_procedimiento
    """,
    engine
)

test_proc = df.merge(
    dim_proc,
    left_on="Número Procedimiento",
    right_on="procedimiento_id",
    how="left"
)

print(
    "Procedimientos sin match:",
    test_proc["procedimiento_id"].isna().sum()
)

sin_match = test_proc[
    test_proc["procedimiento_id"].isna()
]

print(
    sin_match["Número Procedimiento"]
    .head(20)
    .tolist()
)

print("Filas totales:", len(df))

print(
    "Órdenes distintas:",
    df["Nro Orden de Compra"].nunique()
)'''


'''import os

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

# -----------------------
# dim_procedimiento
# -----------------------

dim_proc = pd.read_sql(
    """
    SELECT procedimiento_id
    FROM dw.dim_procedimiento
    """,
    engine
)

test_proc = df.merge(
    dim_proc,
    left_on="Número Procedimiento",
    right_on="procedimiento_id",
    how="left"
)

sin_match = test_proc[
    test_proc["procedimiento_id"].isna()
]

print("Procedimientos sin match:", len(sin_match))

print(
    sin_match["Número Procedimiento"]
    .str.extract(r'(\d{2})$')[0]
    .value_counts()
)


dim_proc = pd.read_sql(
    """
    SELECT procedimiento_id
    FROM dw.dim_procedimiento
    """,
    engine
)

print("Procedimientos en dimensión:",
      len(dim_proc))

print("Procedimientos distintos:",
      dim_proc["procedimiento_id"].nunique())


sin_match = test_proc[
    test_proc["procedimiento_id"].isna()
]

print(
    "Procedimientos faltantes distintos:",
    sin_match["Número Procedimiento"].nunique()
)

sin_match = test_proc[
    test_proc["procedimiento_id"].isna()
]
faltantes = (
    sin_match[
        [
            "Número Procedimiento",
            "Ejercicio",
            "Modalidad",
            "Tipo de Procedimiento"
        ]
    ]
    .drop_duplicates()
)
print("Registros:", len(faltantes))
print(
    "Procedimientos distintos:",
    faltantes["Número Procedimiento"].nunique()
)

faltantes_dim = (
    sin_match[
        [
            "Número Procedimiento",
            "Ejercicio",
            "Modalidad",
            "Tipo de Procedimiento"
        ]
    ]
    .drop_duplicates()
)
faltantes_dim = faltantes_dim.rename(
    columns={
        "Número Procedimiento": "procedimiento_id",
        "Ejercicio": "ejercicio",
        "Modalidad": "modalidad",
        "Tipo de Procedimiento": "tipo_procedimiento"
    }
)

faltantes_dim["nombre_procedimiento"] = "DESCONOCIDO"
faltantes_dim["objeto_procedimiento"] = "DESCONOCIDO"
print(faltantes_dim.head())
print(len(faltantes_dim))


print(
    faltantes_dim["procedimiento_id"]
    .head(20)
    .tolist()
)'''


'''import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

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

df = pd.read_csv(
    "data/raw/adjudicaciones-2020.csv"
)

dim_proveedor = pd.read_sql(
    """
    SELECT
        proveedor_id,
        cuit
    FROM dw.dim_proveedor
    """,
    engine
)

test = df.merge(
    dim_proveedor,
    left_on="CUIT",
    right_on="cuit",
    how="left"
)

print(
    "Proveedores sin match:",
    test["proveedor_id"].isna().sum()
)

print(
    "CUIT distintos sin match:",
    test.loc[
        test["proveedor_id"].isna(),
        "CUIT"
    ].nunique()
)'''


'''
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

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
# Adjudicaciones
# -----------------------

df = pd.read_csv(
    "data/raw/adjudicaciones-2020.csv"
)

# -----------------------
# Convertir fecha
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
df["fecha_tmp"] = pd.to_datetime(
    df["Fecha de Adjudicación"],
    format="mixed",
    dayfirst=True,
    errors="coerce"
)

print(
    "Fechas inválidas:",
    df["fecha_tmp"].isna().sum()
)

print(
    df.loc[
        df["fecha_tmp"].isna(),
        "Fecha de Adjudicación"
    ]
    .drop_duplicates()
    .tolist()
)

# -----------------------
# Dim fecha
# -----------------------

dim_fecha = pd.read_sql(
    """
    SELECT fecha_id
    FROM dw.dim_fecha
    """,
    engine
)

# -----------------------
# Test
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
)'''


import pandas as pd

df = pd.read_csv(
    "data/raw/adjudicaciones-2020.csv"
)

print(
    df.loc[
        df["Fecha de Adjudicación"].isna(),
        [
            "Número Procedimiento",
            "CUIT",
            "Documento Contractual",
            "Fecha de Adjudicación"
        ]
    ]
)