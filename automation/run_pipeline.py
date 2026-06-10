import subprocess

PIPELINE = [
    "automation/reset_dw.py",
    "etl/load_dim_fecha.py",
    "etl/etl_dim_organismo.py",
    "etl/etl_dim_proveedor.py",
    "etl/etl_dim_rubro.py",
    "etl/etl_dim_procedimiento.py",
    "etl/etl_completar_procedimientos_faltantes.py",
    "etl/etl_fact_convocatoria.py",
    "etl/etl_fact_adjudicacion.py",
    "etl/etl_bridge_adjudicacion_rubro.py"
]

for script in PIPELINE:

    print("\n" + "=" * 60)
    print(f"Ejecutando: {script}")
    print("=" * 60)

    subprocess.run(
        ["python", script],
        check=True
    )

print("\nPipeline completado correctamente.")