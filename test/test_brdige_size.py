import pandas as pd

df = pd.read_csv(
    "data/raw/adjudicaciones-2020.csv"
)

df = df[
    df["Fecha de Adjudicación"].notna()
].copy()

cantidad = (
    df["Rubros"]
    .fillna("")
    .str.split(";")
    .apply(
        lambda x: len(
            [r for r in x if r.strip() != ""]
        )
    )
)

print("Filas fact:", len(df))
print("Filas bridge estimadas:", cantidad.sum())

print()
print(cantidad.describe())