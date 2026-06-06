

"""Seccion para que python se conecte con Neon"""
from dotenv import load_dotenv
from sqlalchemy import create_engine
import os


"""Creacion del dataframe"""
from datetime import date, timedelta
import pandas as pd

MESES = [
    "Enero", "Febrero", "Marzo", "Abril",
    "Mayo", "Junio", "Julio", "Agosto",
    "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

DIAS = [
    "Lunes", "Martes", "Miércoles",
    "Jueves", "Viernes", "Sábado", "Domingo"
]

fecha_inicio = date(2020, 1, 1)
fecha_fin = date(2030, 12, 31)

registros = []

fecha_actual = fecha_inicio

while fecha_actual <= fecha_fin:

    registros.append({
        "fecha_id": int(fecha_actual.strftime("%Y%m%d")),
        "fecha": fecha_actual,
        "dia": fecha_actual.day,
        "mes": fecha_actual.month,
        "anio": fecha_actual.year,
        "trimestre": (fecha_actual.month - 1) // 3 + 1,
        "semana": fecha_actual.isocalendar().week,
        "nombre_mes": MESES[fecha_actual.month - 1],
        "nombre_dia": DIAS[fecha_actual.weekday()],
        "es_feriado": False,
        "es_fin_semana": fecha_actual.weekday() >= 5
    })

    fecha_actual += timedelta(days=1)

df = pd.DataFrame(registros)

print(df.head())
print()
print("Cantidad de registros:", len(df))


"""Bloque para conectar con Neon y cargar los datos al DW"""
load_dotenv()

host = os.getenv("DB_HOST")
db = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
port = os.getenv("DB_PORT")

url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"

engine = create_engine(url)

df.to_sql(
    name="dim_fecha",
    schema="dw",
    con=engine,
    if_exists="append",
    index=False
)

print("Carga completada")