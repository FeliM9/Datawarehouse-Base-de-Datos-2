-- ============================================================
-- Verificación de presencia y consistencia de datos en el DW
-- Ejecutar en Neon (DBeaver) sobre el esquema dw.
-- Objetivo: confirmar que los datos EXISTEN (filas pobladas),
-- no solo que las columnas estén creadas.
-- ============================================================

-- 1) Conteo de filas por tabla -------------------------------
SELECT 'dim_fecha'                  AS tabla, count(*) AS filas FROM dw.dim_fecha
UNION ALL SELECT 'dim_organismo',          count(*) FROM dw.dim_organismo
UNION ALL SELECT 'dim_proveedor',          count(*) FROM dw.dim_proveedor
UNION ALL SELECT 'dim_rubro',              count(*) FROM dw.dim_rubro
UNION ALL SELECT 'dim_procedimiento',      count(*) FROM dw.dim_procedimiento
UNION ALL SELECT 'fact_convocatoria',      count(*) FROM dw.fact_convocatoria
UNION ALL SELECT 'fact_adjudicacion',      count(*) FROM dw.fact_adjudicacion
UNION ALL SELECT 'bridge_adj_rubro',       count(*) FROM dw.bridge_adjudicacion_rubro
ORDER BY tabla;

-- 2) fact_adjudicacion: que los MONTOS y FKs existan ---------
SELECT
    count(*)                                            AS filas,
    count(monto_adjudicado)                             AS monto_no_nulo,
    count(*) FILTER (WHERE monto_adjudicado > 0)        AS monto_positivo,
    count(DISTINCT proveedor_id)                        AS proveedores_distintos,
    count(DISTINCT procedimiento_id)                    AS procedimientos_distintos,
    count(DISTINCT fecha_adjudicacion_id)               AS fechas_distintas,
    count(DISTINCT moneda)                              AS monedas
FROM dw.fact_adjudicacion;

-- Monto por moneda (NO sumar entre monedas en los análisis)
SELECT moneda,
       count(*)                AS filas,
       sum(monto_adjudicado)   AS monto_total
FROM dw.fact_adjudicacion
GROUP BY moneda
ORDER BY monto_total DESC NULLS LAST;

-- 3) fact_convocatoria: montos estimados y FKs ---------------
SELECT
    count(*)                            AS filas,
    count(monto_estimado)               AS monto_estimado_no_nulo,
    count(DISTINCT organismo_id)        AS organismos_distintos,
    count(DISTINCT procedimiento_id)    AS procedimientos_distintos,
    count(DISTINCT fecha_publicacion_id) AS fechas_distintas
FROM dw.fact_convocatoria;

-- 4) bridge: que relacione hechos con rubros -----------------
SELECT
    count(*)                              AS filas,
    count(DISTINCT fact_adjudicacion_id)  AS adjudicaciones_con_rubro,
    count(DISTINCT rubro_id)              AS rubros_distintos
FROM dw.bridge_adjudicacion_rubro;

-- 5) Integridad referencial: huérfanos (deberían dar 0) ------
-- fact_adjudicacion -> dimensiones
SELECT 'adj sin proveedor' AS chequeo, count(*) AS huerfanos
FROM dw.fact_adjudicacion f
LEFT JOIN dw.dim_proveedor d ON f.proveedor_id = d.proveedor_id
WHERE d.proveedor_id IS NULL
UNION ALL
SELECT 'adj sin procedimiento', count(*)
FROM dw.fact_adjudicacion f
LEFT JOIN dw.dim_procedimiento d ON f.procedimiento_id = d.procedimiento_id
WHERE d.procedimiento_id IS NULL
UNION ALL
SELECT 'adj sin fecha', count(*)
FROM dw.fact_adjudicacion f
LEFT JOIN dw.dim_fecha d ON f.fecha_adjudicacion_id = d.fecha_id
WHERE d.fecha_id IS NULL
UNION ALL
SELECT 'conv sin organismo', count(*)
FROM dw.fact_convocatoria f
LEFT JOIN dw.dim_organismo d ON f.organismo_id = d.organismo_id
WHERE d.organismo_id IS NULL
UNION ALL
SELECT 'conv sin procedimiento', count(*)
FROM dw.fact_convocatoria f
LEFT JOIN dw.dim_procedimiento d ON f.procedimiento_id = d.procedimiento_id
WHERE d.procedimiento_id IS NULL
UNION ALL
SELECT 'bridge sin adjudicacion', count(*)
FROM dw.bridge_adjudicacion_rubro b
LEFT JOIN dw.fact_adjudicacion f ON b.fact_adjudicacion_id = f.fact_adjudicacion_id
WHERE f.fact_adjudicacion_id IS NULL
UNION ALL
SELECT 'bridge sin rubro', count(*)
FROM dw.bridge_adjudicacion_rubro b
LEFT JOIN dw.dim_rubro d ON b.rubro_id = d.rubro_id
WHERE d.rubro_id IS NULL;

-- 6) Vista rápida de negocio: top 10 proveedores por monto (ARS)
SELECT p.razon_social,
       sum(f.monto_adjudicado) AS monto_ars
FROM dw.fact_adjudicacion f
JOIN dw.dim_proveedor p ON f.proveedor_id = p.proveedor_id
WHERE f.moneda = 'Peso Argentino'
GROUP BY p.razon_social
ORDER BY monto_ars DESC
LIMIT 10;
