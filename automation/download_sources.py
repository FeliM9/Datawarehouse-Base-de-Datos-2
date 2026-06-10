import pandas as pd

SHEETS = {
    "adjudicaciones-2020.csv":
        "12xT8rHIfRv8BPIG7iTArgD0mztNwZU3GN5Ap66_3sDk",

    "convocatorias-2020.csv":
        "16OULzb0pizK5PXbYXc3tZDm_JfCJwoNIf-K4YuxLYyk"
}


for archivo, sheet_id in SHEETS.items():

    url = (
        f"https://docs.google.com/spreadsheets/d/"
        f"{sheet_id}/export?format=csv"
    )

    df = pd.read_csv(url)

    destino = f"data/raw/{archivo}"

    df.to_csv(
        destino,
        index=False
    )

    print(
        f"Fuente actualizada: {archivo}"
    )

print("Sincronización finalizada.")