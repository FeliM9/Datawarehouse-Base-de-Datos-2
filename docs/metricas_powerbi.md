# Métricas (medidas DAX) para Power BI

Modelo estrella cargado en Neon (esquema `dw`). Este documento define el modelo
y las medidas DAX. La moneda **ya no se fija dentro de las medidas**: se controla
con una **segmentación de datos (slicer)** sobre `fact_adjudicacion[moneda]`.

> Requisito de cátedra: al menos **5 medidas por tabla de hechos que crucen un
> mínimo de 3 tablas**. Más abajo están marcadas como "(3 tablas)".

## 1. Relaciones del modelo

Importá las 8 tablas del esquema `dw` y creá estas relaciones (1:muchos,
dirección de filtro simple dim -> hecho):

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

Notas:

- Marcá `dim_fecha` como **tabla de fechas** (Table tools -> Mark as date table,
  columna `fecha`), necesario para las medidas YTD.
- `dim_rubro` se relaciona con `fact_adjudicacion` **a través del bridge** (M:N).
  Contar por rubro está bien, pero **sumar monto por rubro sobre-cuenta** el total.

## 2. Slicer de moneda

`fact_adjudicacion[monto_adjudicado]` viene en 3 monedas. En vez de fijar la
moneda en cada medida, se pone un **slicer** sobre `fact_adjudicacion[moneda]`
configurado en **selección única** (Formato del slicer -> Selección única). Así
nunca se mezclan divisas y todas las medidas de monto se recalculan según la
moneda elegida. (`fact_convocatoria` no tiene columna de moneda.)

---

## 3. Medidas de fact_adjudicacion

### 3.1 Base y de soporte

```DAX
Monto Adjudicado = SUM ( fact_adjudicacion[monto_adjudicado] )
```
```DAX
Monto Adjudicado Máximo = MAX ( fact_adjudicacion[monto_adjudicado] )
```
```DAX
Cant Adjudicaciones = COUNTROWS ( fact_adjudicacion )
```
```DAX
Cant Proveedores = DISTINCTCOUNT ( dim_proveedor[proveedor_id] )
```
```DAX
Cant Procedimientos Adjudicaciones = DISTINCTCOUNT ( dim_procedimiento[procedimiento_id] )
```
```DAX
Ticket Promedio Adjudicado = DIVIDE ( [Monto Adjudicado], [Cant Adjudicaciones] )
```
```DAX
% Monto sobre Total =
DIVIDE ( [Monto Adjudicado], CALCULATE ( [Monto Adjudicado], ALLSELECTED () ) )
```
```DAX
Ranking Proveedor =
IF (
    HASONEVALUE ( dim_proveedor[razon_social] ) && NOT ISBLANK ( [Monto Adjudicado] ),
    RANKX ( ALL ( dim_proveedor[razon_social] ), [Monto Adjudicado], , DESC, DENSE )
)
```

### 3.2 Las 5 medidas que cruzan 3 tablas

**(3 tablas)** fact_adjudicacion + bridge_adjudicacion_rubro + dim_rubro
```DAX
Cant Adjudicaciones por Rubro =
DISTINCTCOUNT ( bridge_adjudicacion_rubro[fact_adjudicacion_id] )
```

**(3 tablas)** fact_adjudicacion + dim_procedimiento + dim_fecha
```DAX
Monto Adj (Lic.Publica 2020) =
CALCULATE (
    SUM ( fact_adjudicacion[monto_adjudicado] ),
    dim_procedimiento[tipo_procedimiento] = "Licitacion Pública",
    dim_fecha[anio] = 2020
)
```

**(3 tablas)** fact_adjudicacion + bridge_adjudicacion_rubro + dim_rubro
```DAX
Monto Adj (Rubro Informatica) =
CALCULATE (
    SUM ( fact_adjudicacion[monto_adjudicado] ),
    dim_rubro[descripcion_rubro] = "INFORMATICA"
)
```

**(3 tablas)** fact_adjudicacion + dim_fecha + dim_procedimiento
```DAX
Monto Adj YTD (Lic.Publica) =
CALCULATE (
    TOTALYTD ( SUM ( fact_adjudicacion[monto_adjudicado] ), dim_fecha[fecha] ),
    dim_procedimiento[tipo_procedimiento] = "Licitacion Pública"
)
```

**(3 tablas)** fact_adjudicacion + dim_procedimiento + dim_proveedor
```DAX
Ticket Promedio (Lic.Privada x proveedor) =
DIVIDE (
    CALCULATE ( SUM ( fact_adjudicacion[monto_adjudicado] ),
        dim_procedimiento[tipo_procedimiento] = "Licitacion Privada" ),
    CALCULATE ( DISTINCTCOUNT ( dim_proveedor[proveedor_id] ),
        dim_procedimiento[tipo_procedimiento] = "Licitacion Privada" )
)
```

---

## 4. Medidas de fact_convocatoria

### 4.1 Base y de soporte

```DAX
Monto Estimado Convocatorias = SUM ( fact_convocatoria[monto_estimado] )
```
```DAX
Cant Convocatorias = COUNTROWS ( fact_convocatoria )
```
```DAX
Cant Organismos = DISTINCTCOUNT ( dim_organismo[organismo_id] )
```
```DAX
Cant Procedimientos Convocatorias = DISTINCTCOUNT ( dim_procedimiento[procedimiento_id] )
```

### 4.2 Las 5 medidas que cruzan 3 tablas

**(3 tablas)** fact_convocatoria + dim_organismo + dim_fecha
```DAX
% Monto Estimado Organismo en el Año =
DIVIDE (
    SUM ( fact_convocatoria[monto_estimado] ),
    CALCULATE ( SUM ( fact_convocatoria[monto_estimado] ),
        ALL ( dim_organismo ), VALUES ( dim_fecha[anio] ) )
)
```

**(3 tablas)** fact_convocatoria + dim_procedimiento + dim_fecha
```DAX
Monto Estimado (Lic.Publica 2020) =
CALCULATE (
    SUM ( fact_convocatoria[monto_estimado] ),
    dim_procedimiento[tipo_procedimiento] = "Licitacion Pública",
    dim_fecha[anio] = 2020
)
```

**(3 tablas)** fact_convocatoria + dim_fecha + dim_procedimiento
```DAX
Monto Estimado YTD (Lic.Publica) =
CALCULATE (
    TOTALYTD ( SUM ( fact_convocatoria[monto_estimado] ), dim_fecha[fecha] ),
    dim_procedimiento[tipo_procedimiento] = "Licitacion Pública"
)
```

**(3 tablas)** fact_convocatoria + dim_procedimiento + dim_organismo
```DAX
Ticket Promedio Estimado (Lic.Publica x organismo) =
DIVIDE (
    CALCULATE ( SUM ( fact_convocatoria[monto_estimado] ),
        dim_procedimiento[tipo_procedimiento] = "Licitacion Pública" ),
    CALCULATE ( DISTINCTCOUNT ( dim_organismo[organismo_id] ),
        dim_procedimiento[tipo_procedimiento] = "Licitacion Pública" )
)
```

**(3 tablas)** fact_convocatoria + dim_procedimiento + dim_fecha
```DAX
Cant Convocatorias (Lic.Publica 2020) =
CALCULATE (
    COUNTROWS ( fact_convocatoria ),
    dim_procedimiento[tipo_procedimiento] = "Licitacion Pública",
    dim_fecha[anio] = 2020
)
```

---

## 5. Resumen: 5 medidas de 3 tablas por hecho

| fact_adjudicacion                         | fact_convocatoria                              |
|-------------------------------------------|------------------------------------------------|
| Cant Adjudicaciones por Rubro             | % Monto Estimado Organismo en el Año           |
| Monto Adj (Lic.Publica 2020)              | Monto Estimado (Lic.Publica 2020)              |
| Monto Adj (Rubro Informatica)             | Monto Estimado YTD (Lic.Publica)               |
| Monto Adj YTD (Lic.Publica)               | Ticket Promedio Estimado (Lic.Publica x organismo) |
| Ticket Promedio (Lic.Privada x proveedor) | Cant Convocatorias (Lic.Publica 2020)          |

## 6. Notas

- Los valores de filtro tienen que coincidir exacto con la base:
  `tipo_procedimiento` = "Licitacion Pública" / "Licitacion Privada" /
  "Contratación Directa"; `descripcion_rubro` en mayúsculas (ej. "INFORMATICA").
- Las medidas YTD requieren `dim_fecha` marcada como tabla de fechas.
- Si querés que el tipo/rubro/año salgan de un slicer en vez de estar fijos en la
  medida, sacá esos filtros y poné las dimensiones como segmentación; la medida
  igual cruza 3 tablas al combinarla con las dimensiones en el visual.
