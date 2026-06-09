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
# Rubros desde adjudicaciones
# -----------------------

df = pd.read_csv(
    "data/raw/adjudicaciones-2020.csv"
)

df = df[
    df["Fecha de Adjudicación"].notna()
].copy()

rubros = (
    df["Rubros"]
    .fillna("")
    .str.split(";")
    .explode()
    .str.strip()
)

rubros = rubros[
    rubros != ""
]

rubros_df = pd.DataFrame({
    "descripcion_rubro": rubros.unique()
})

# -----------------------
# dim_rubro
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

# -----------------------
# Match
# -----------------------

test = rubros_df.merge(
    dim_rubro,
    on="descripcion_rubro",
    how="left"
)

print(
    "Rubros sin match:",
    test["rubro_id"].isna().sum()
)

if test["rubro_id"].isna().sum() > 0:
    print(
        test.loc[
            test["rubro_id"].isna(),
            "descripcion_rubro"
        ].tolist()
    )