import pandas as pd

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

print(
    "Rubros distintos encontrados:",
    rubros.nunique()
)

print(
    sorted(rubros.unique())[:20]
)