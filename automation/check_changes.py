import pandas as pd
import hashlib
import subprocess
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy import text

SHEETS = {
    "adjudicaciones": "12xT8rHIfRv8BPIG7iTArgD0mztNwZU3GN5Ap66_3sDk",
    "convocatorias": "16OULzb0pizK5PXbYXc3tZDm_JfCJwoNIf-K4YuxLYyk"
}

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


def calcular_hash(sheet_id):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    df = pd.read_csv(url)
    contenido = df.to_csv(index=False)
    return hashlib.md5(
        contenido.encode("utf-8")
    ).hexdigest()


def cargar_hashes():
    query = """
    SELECT
        fuente,
        hash_actual
    FROM dw.etl_control
    """
    df = pd.read_sql(
        query,
        engine
    )
    return dict(
        zip(
            df["fuente"],
            df["hash_actual"]
        )
    )
    
def guardar_hashes(hashes):
    with engine.begin() as conn:
        for fuente, hash_actual in hashes.items():
            conn.execute(
                text("""
                    UPDATE dw.etl_control
                    SET
                        hash_actual = :hash_actual,
                        fecha_actualizacion = CURRENT_TIMESTAMP
                    WHERE fuente = :fuente
                """),
                {
                    "fuente": fuente,
                    "hash_actual": hash_actual
                }
            )

def verificar_cambios():
    hashes_guardados = cargar_hashes()
    hashes_actuales = {}
    cambios_detectados = []
    for nombre, sheet_id in SHEETS.items():
        hash_actual = calcular_hash(sheet_id)
        hashes_actuales[nombre] = hash_actual
        hash_guardado = hashes_guardados[nombre]
        if hash_actual == hash_guardado:
            print(f"✅ {nombre}: SIN CAMBIOS")
        else:
            print(f"🚨 {nombre}: CAMBIO DETECTADO")
            cambios_detectados.append(nombre)
    return cambios_detectados, hashes_actuales


if __name__ == "__main__":
    cambios, hashes_actuales = verificar_cambios()
    print("\nResumen:")
    if cambios:
        print("Fuentes modificadas:")
        for fuente in cambios:
            print(f"- {fuente}")
        print("\nSincronizando fuentes...")
        subprocess.run(
            ["python", "automation/download_sources.py"],
            check=True
        )
        print("\nReconstruyendo DW...")
        subprocess.run(
            ["python", "automation/run_pipeline.py"],
            check=True
        )
        guardar_hashes(hashes_actuales)
        print("\nHashes actualizados.")
        print("Pipeline finalizado correctamente.")
    else:
        print("No se detectaron cambios.")