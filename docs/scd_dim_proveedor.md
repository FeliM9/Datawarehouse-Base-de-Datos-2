# SCD Tipo 2 en dim_proveedor (historial reconstruido)

`dim_proveedor` es una **Slowly Changing Dimension Tipo 2**: conserva el
historial completo de cada proveedor. Como `adjudicaciones-2020` es un log con
fechas, el historial se **reconstruye** desde ahí (effective-dated): se recorre
cada CUIT por fecha y se crea una versión por cada período en que los atributos
versionados se mantienen iguales.

## Diseño

- `proveedor_id` (serial) = **surrogate key** → es la PRIMARY KEY.
- `cuit` = **business key** → ya NO es único (hay varias versiones por CUIT).
- `razon_social`, `provincia` = atributos versionados.
- `fecha_desde`, `fecha_hasta`, `es_vigente` = vigencia (fechas REALES del dato).

`provincia` sale de la columna **`Provincia Operativa Proveedor`** del CSV de
adjudicaciones (si la columna no existe, queda NULL y el ETL no se rompe).

## Cómo se construye (etl/etl_dim_proveedor.py)

1. Se ordenan las adjudicaciones de cada CUIT por `Fecha de Adjudicación`.
2. Se detecta una "corrida" nueva cada vez que cambia `(razon_social, provincia)`.
   Cada corrida es una versión: `fecha_desde` = fecha de la primera adjudicación
   de la corrida; `fecha_hasta` = `fecha_desde` de la corrida siguiente (NULL en
   la última); `es_vigente = true` solo en la última.
3. **Upsert idempotente por `(cuit, fecha_desde)`**, sin truncate:
   - versión nueva que no está → INSERT;
   - versión ya presente cuya vigencia/atributos cambiaron → UPDATE;
   - correr sin cambios no agrega nada.

Ejemplo (un CUIT cuya provincia fue San Luis, pasó a Tierra del Fuego el 05/11 y
volvió a San Luis el 09/11) queda con **3 filas**:

| razon_social | provincia        | fecha_desde | fecha_hasta | es_vigente |
|--------------|------------------|-------------|-------------|------------|
| ACME         | San Luis         | 03/02       | 05/11       | false      |
| ACME         | Tierra del Fuego | 05/11       | 09/11       | false      |
| ACME         | San Luis         | 09/11       | (null)      | true       |

## No se trunca en cada rebuild

`reset_dw` NO trunca `dim_proveedor` (es la única tabla excluida). Como el upsert
es idempotente, el historial persiste entre rebuilds y crece cuando aparece un
cambio nuevo. (La reconstrucción es determinística desde la fuente; lo único que
no se borra es lo ya insertado.)

## Linkage AS-WAS en los hechos (etl/etl_fact_adjudicacion.py)

Cada `fact_adjudicacion` apunta a la versión del proveedor **vigente en la fecha
de esa adjudicación**, no siempre a la actual. Se resuelve con un `merge_asof`
"backward" por CUIT sobre `fecha_desde`. Así, una métrica "monto por provincia"
respeta la historia: la adjudicación del 05/11 suma a Tierra del Fuego y las
demás a San Luis (con "siempre vigente" todo sumaría a San Luis).

## Deploy

1. DDL (una vez): `sql/ddl/06_scd2_dim_proveedor.sql` (quita el UNIQUE de `cuit`,
   agrega `fecha_desde`/`fecha_hasta`/`es_vigente`).

2. **Reset único** de `dim_proveedor` (necesario porque las filas viejas tenían
   fecha de carga, no fecha real). En Neon:

   ```sql
   TRUNCATE dw.dim_proveedor RESTART IDENTITY CASCADE;
   TRUNCATE dw.etl_control;
   ```

   Esto es por única vez (no en cada rebuild). El `CASCADE` vacía también
   `fact_adjudicacion` y el bridge, que se reconstruyen en el próximo run.
   `etl_control` se vacía para que el gate `verificar_cambios` deje correr el
   primer rebuild.

3. `dagster dev` → *Materialize all*. Se reconstruye todo el historial.

## Cómo demostrar el versionado

1. En el sheet de adjudicaciones, en un CUIT existente, cambiá la provincia
   (`Provincia Operativa Proveedor`) o la razón social. Para que aparezca como un
   cambio "a partir de" una fecha, modificá las filas desde esa fecha hasta el
   final (o una sola fila intermedia: la reconstrucción la versiona igual).
2. Dispará el rebuild (sensor o *Materialize all*).
3. Verificá en Neon:

   ```sql
   SELECT proveedor_id, cuit, razon_social, provincia,
          fecha_desde, fecha_hasta, es_vigente
   FROM dw.dim_proveedor
   WHERE cuit = 'EL-CUIT'
   ORDER BY fecha_desde;
   ```

   Vas a ver una fila por cada período de provincia distinta, con su vigencia.
