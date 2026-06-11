import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

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
# Reset DW
# -----------------------

# NOTA: dw.dim_proveedor NO se trunca a proposito.
# Es una dimension SCD Tipo 2: su historial (versiones por CUIT) debe
# sobrevivir a cada rebuild. Su carga es un merge versionado
# (ver etl/etl_dim_proveedor.py), no truncate + recarga.
sql = """
TRUNCATE TABLE
    dw.bridge_adjudicacion_rubro,
    dw.fact_adjudicacion,
    dw.fact_convocatoria,
    dw.dim_rubro,
    dw.dim_procedimiento,
    dw.dim_organismo,
    dw.dim_fecha
RESTART IDENTITY CASCADE;
"""

with engine.begin() as conn:
    conn.execute(text(sql))

print("DW reiniciado correctamente.")