# Métricas (medidas DAX) para Power BI

Modelo estrella cargado en Neon (esquema `dw`). Este documento define el modelo
de datos en Power BI y las medidas DAX listas para pegar.

> Verificado contra la fuente: todas las columnas usadas tienen datos reales
> (ver `sql/queries/verificacion_dw.sql` para confirmarlo directamente en Neon).

## 1. Relaciones a crear en el modelo

Importá las 8 tablas del esquema `dw` y creá estas relaciones (todas
1:muchos, dirección de filtro simple dim -> hecho):

| Desde (hecho)                              | Hacia (dimensión)                  |
|--------------------------------------------|------------------------------------|
| fact_adjudicacion[proveedor_id]            | dim_proveedor[proveedor_id]        |
| fact_adjudicacion[procedimiento_id]        | dim_procedimiento[procedimiento_id]|
| fact_adjudicacion[fecha_adjudicacion_id]   | dim_fecha[fecha_id]                |
| fact_convocatoria[organismo_id]            | dim_organismo[organismo_id]        |
| fact_convocatoria[procedimiento_id]        | dim_procedimiento[procedimiento_id]|
| fact_convocatoria[fecha_publicacion_id]    | dim_fecha[fecha_id]                |
| bridge_adjudicacion_rubro[fact_adjudicacion_id] | fact_adjudicacion[fact_adjudicacion_id] |
| bridge_adjudicacion_rubro[rubro_id]        | dim_rubro[rubro_id]                |

Notas de modelado:
- Marcá `dim_fecha` como **tabla de fechas** (Table tools -> Mark as date table,
  usando la columna `fecha`). Es necesario para las medidas de inteligencia
  temporal (YTD, mes anterior, etc.).
- `dim_rubro` se relaciona con `fact_adjudicacion` **a través del bridge**
  (relación muchos-a-muchos). Filtrar por rubro reparte la adjudicación entre
  sus rubros: sirve para contar, pero **sumar monto por rubro sobre-cuenta** el
  total (una adjudicación con 3 rubros aporta su monto a los 3). Ver caveat abajo.

## 2. Caveat de monedas (importante)

`fact_adjudicacion[monto_adjudicado]` viene en 3 monedas distintas. **No sumes
monto sin filtrar moneda**: mezclaría pesos con otras divisas. Las medidas de
monto de abajo filtran "Peso Argentino" (ARS). Si necesitás otra moneda, cambiá
el filtro o agregá una medida análoga.

## 3. Medidas DAX

### Conteos

```DAX
Cant Adjudicaciones = COUNTROWS ( fact_adjudicacion )
```
```DAX
Cant Convocatorias = COUNTROWS ( fact_convocatoria )
```
```DAX
Cant Proveedores = DISTINCTCOUNT ( fact_adjudicacion[proveedor_id] )
```
```DAX
Cant Organismos = DISTINCTCOUNT ( fact_convocatoria[organismo_id] )
```
```DAX
Cant Procedimientos = DISTINCTCOUNT ( fact_adjudicacion[procedimiento_id] )
```

### Montos (ARS = Peso Argentino)

```DAX
Monto Adjudicado (ARS) =
CALCULATE (
    SUM ( fact_adjudicacion[monto_adjudicado] ),
    fact_adjudicacion[moneda] = "Peso Argentino"
)
```
```DAX
-- Usar solo para diagnóstico; NO sumar entre monedas en análisis serios.
Monto Adjudicado Total (todas las monedas) =
SUM ( fact_adjudicacion[monto_adjudicado] )
```
```DAX
Monto Estimado Convocatorias =
SUM ( fact_convocatoria[monto_estimado] )
```
```DAX
Ticket Promedio Adjudicado (ARS) =
DIVIDE (
    [Monto Adjudicado (ARS)],
    CALCULATE ( COUNTROWS ( fact_adjudicacion ), fact_adjudicacion[moneda] = "Peso Argentino" )
)
```
```DAX
Monto Adjudicado Máximo (ARS) =
CALCULATE ( MAX ( fact_adjudicacion[monto_adjudicado] ), fact_adjudicacion[moneda] = "Peso Argentino" )
```

### Participación y ranking (para "top proveedores")

```DAX
% Monto sobre Total (ARS) =
DIVIDE (
    [Monto Adjudicado (ARS)],
    CALCULATE ( [Monto Adjudicado (ARS)], ALL ( dim_proveedor ) )
)
```
```DAX
Ranking Proveedor (ARS) =
IF (
    HASONEVALUE ( dim_proveedor[razon_social] ),
    RANKX ( ALL ( dim_proveedor[razon_social] ), [Monto Adjudicado (ARS)], , DESC )
)
```

### Rubros (vía bridge)

```DAX
-- Cuenta adjudicaciones distintas por rubro (no sobre-cuenta).
Cant Adjudicaciones por Rubro =
DISTINCTCOUNT ( bridge_adjudicacion_rubro[fact_adjudicacion_id] )
```

### Inteligencia temporal (requiere dim_fecha marcada como tabla de fechas)

```DAX
Monto Adjudicado YTD (ARS) =
TOTALYTD ( [Monto Adjudicado (ARS)], dim_fecha[fecha] )
```
```DAX
Monto Adj Mes Anterior (ARS) =
CALCULATE ( [Monto Adjudicado (ARS)], DATEADD ( dim_fecha[fecha], -1, MONTH ) )
```
```DAX
Var % MoM (ARS) =
DIVIDE (
    [Monto Adjudicado (ARS)] - [Monto Adj Mes Anterior (ARS)],
    [Monto Adj Mes Anterior (ARS)]
)
```

### Estimado vs Adjudicado (desvío)

```DAX
-- Tiene sentido al filtrar por procedimiento. Ambos hechos comparten
-- dim_procedimiento, así que un mismo procedimiento cruza estimado y adjudicado.
Desvío Adjudicado vs Estimado (ARS) =
[Monto Adjudicado (ARS)] - [Monto Estimado Convocatorias]
```

## 4. Ideas de visuales

- KPI cards: Monto Adjudicado (ARS), Cant Adjudicaciones, Ticket Promedio.
- Barras: Top 10 proveedores por Monto Adjudicado (ARS) (usar Ranking).
- Barras: Monto Adjudicado por organismo (dim_organismo[descripcion_saf]).
- Línea: Monto Adjudicado (ARS) por mes (dim_fecha[nombre_mes] / fecha).
- Treemap: Cant Adjudicaciones por Rubro (dim_rubro[descripcion_rubro]).
- Tabla: procedimiento con Monto Estimado vs Adjudicado y su desvío.

## 5. Medidas multi-tabla (cada una cruza 3 tablas)

Estas medidas recorren el modelo estrella a través de las relaciones, usando un
hecho + dos dimensiones (o el bridge), no una sola tabla.

### 5.1 Monto Adjudicado ARS — Licitación Pública 2020
Tablas: fact_adjudicacion + dim_procedimiento + dim_fecha.
```DAX
Monto Adj ARS (Lic.Publica 2020) =
CALCULATE (
    SUM ( fact_adjudicacion[monto_adjudicado] ),
    fact_adjudicacion[moneda] = "Peso Argentino",
    dim_procedimiento[tipo_procedimiento] = "Licitacion Pública",
    dim_fecha[anio] = 2020
)
```

### 5.2 Monto Adjudicado ARS por Rubro (vía bridge)
Tablas: fact_adjudicacion + bridge_adjudicacion_rubro + dim_rubro.
```DAX
Monto Adj ARS (Rubro Informatica) =
CALCULATE (
    SUM ( fact_adjudicacion[monto_adjudicado] ),
    fact_adjudicacion[moneda] = "Peso Argentino",
    dim_rubro[descripcion_rubro] = "INFORMATICA"
)
```
Nota: el filtro por rubro viaja fact -> bridge -> dim_rubro. Recordá que sumar
monto por rubro sobre-cuenta el total (una adjudicación con varios rubros aporta
a todos).

### 5.3 Ticket promedio ARS de Licitación Privada por proveedor
Tablas: fact_adjudicacion + dim_procedimiento + dim_proveedor.
```DAX
Ticket Promedio ARS (Lic.Privada x proveedor) =
DIVIDE (
    CALCULATE (
        SUM ( fact_adjudicacion[monto_adjudicado] ),
        fact_adjudicacion[moneda] = "Peso Argentino",
        dim_procedimiento[tipo_procedimiento] = "Licitacion Privada"
    ),
    CALCULATE (
        DISTINCTCOUNT ( dim_proveedor[proveedor_id] ),
        fact_adjudicacion[moneda] = "Peso Argentino",
        dim_procedimiento[tipo_procedimiento] = "Licitacion Privada"
    )
)
```

### 5.4 % del Monto Estimado del organismo dentro de su año
Tablas: fact_convocatoria + dim_organismo + dim_fecha.
```DAX
% Monto Estimado Organismo en el Año =
DIVIDE (
    SUM ( fact_convocatoria[monto_estimado] ),
    CALCULATE (
        SUM ( fact_convocatoria[monto_estimado] ),
        ALL ( dim_organismo ),
        VALUES ( dim_fecha[anio] )
    )
)
```

### 5.5 Monto Adjudicado ARS YTD de Licitación Pública
Tablas: fact_adjudicacion + dim_fecha + dim_procedimiento.
```DAX
Monto Adj ARS YTD (Lic.Publica) =
CALCULATE (
    TOTALYTD ( SUM ( fact_adjudicacion[monto_adjudicado] ), dim_fecha[fecha] ),
    fact_adjudicacion[moneda] = "Peso Argentino",
    dim_procedimiento[tipo_procedimiento] = "Licitacion Pública"
)
```

## 6. Versiones parametrizables (controladas por slicers)

En vez de fijar el tipo / rubro / año dentro de la medida, se dejan afuera y los
controla el usuario con slicers. La misma medida cruza 3 tablas cuando la ponés
en un visual junto a las dimensiones. Lo único que se mantiene fijo es la regla
de negocio de moneda (no mezclar divisas).

### 6.1 Base — responde a cualquier slicer de dimensión
```DAX
Monto Adjudicado (ARS) =
CALCULATE (
    SUM ( fact_adjudicacion[monto_adjudicado] ),
    fact_adjudicacion[moneda] = "Peso Argentino"
)
```
Slicers/ejes que la cruzan a 3 tablas: dim_procedimiento[tipo_procedimiento],
dim_fecha[anio], dim_rubro[descripcion_rubro] (rubro viaja por el bridge).

### 6.2 Ticket promedio — responde a slicers
Tablas: fact_adjudicacion + dim_proveedor + (la dimensión del slicer).
```DAX
Ticket Promedio (ARS) =
DIVIDE (
    [Monto Adjudicado (ARS)],
    CALCULATE (
        DISTINCTCOUNT ( dim_proveedor[proveedor_id] ),
        fact_adjudicacion[moneda] = "Peso Argentino"
    )
)
```

### 6.3 Participación sobre el total visible
Tablas: fact_adjudicacion + (la dimensión del eje) + dim_proveedor/organismo/rubro.
```DAX
% Monto del Total (ARS) =
DIVIDE (
    [Monto Adjudicado (ARS)],
    CALCULATE ( [Monto Adjudicado (ARS)], ALLSELECTED () )
)
```
ALLSELECTED respeta lo elegido en los slicers y abre el nivel del eje del visual.

### 6.4 % del organismo dentro del año (sin valores fijos)
Tablas: fact_convocatoria + dim_organismo + dim_fecha.
```DAX
% Monto Estimado Organismo (en su año) =
DIVIDE (
    SUM ( fact_convocatoria[monto_estimado] ),
    CALCULATE ( SUM ( fact_convocatoria[monto_estimado] ), ALL ( dim_organismo ) )
)
```
ALL(dim_organismo) quita el filtro de organismo; el año queda del slicer dim_fecha.

### 6.5 YTD — responde a slicers
Tablas: fact_adjudicacion + dim_fecha + (la dimensión del slicer).
```DAX
Monto Adjudicado (ARS) YTD =
TOTALYTD ( [Monto Adjudicado (ARS)], dim_fecha[fecha] )
```

### Nota: elegir el campo con un slicer (Field Parameters)
Si querés que el usuario elija *qué* dimensión analizar (proveedor vs organismo
vs rubro) desde un control, usá **Parámetros de campo** en Power BI
(Modelado -> Nuevo parámetro -> Campos). No requiere DAX y arma el slicer solo.
Para leer un valor puntual dentro de una medida, el patrón es
`SELECTEDVALUE ( dim_procedimiento[tipo_procedimiento] )`.
