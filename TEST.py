
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



import pandas as pd
df = pd.read_csv("data/raw/convocatorias-2020.csv")
print(df.columns.tolist())