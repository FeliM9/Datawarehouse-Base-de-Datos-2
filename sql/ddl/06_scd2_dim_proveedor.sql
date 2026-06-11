-- =========================================================================
-- Migracion: SCD Tipo 2 en dw.dim_proveedor
-- =========================================================================
-- Aplicar UNA vez sobre la base existente en Neon (DBeaver).
--
-- Diseno:
--   - proveedor_id (serial) = SURROGATE KEY -> sigue siendo la PRIMARY KEY.
--   - cuit                  = BUSINESS KEY  -> deja de ser UNIQUE: habra
--                             varias filas (versiones) por CUIT.
--   - fecha_desde/fecha_hasta/es_vigente = control de vigencia de cada version.
-- =========================================================================

-- 1) La clave de negocio ya no puede ser unica (varias versiones por CUIT).
ALTER TABLE dw.dim_proveedor
    DROP CONSTRAINT IF EXISTS dim_proveedor_cuit_key;

-- 2) Columnas de versionado SCD2.
ALTER TABLE dw.dim_proveedor
    ADD COLUMN IF NOT EXISTS fecha_desde timestamp;
ALTER TABLE dw.dim_proveedor
    ADD COLUMN IF NOT EXISTS fecha_hasta timestamp;
ALTER TABLE dw.dim_proveedor
    ADD COLUMN IF NOT EXISTS es_vigente boolean DEFAULT true;

-- 3) Backfill: las filas que ya existen quedan como version vigente.
UPDATE dw.dim_proveedor
SET es_vigente  = COALESCE(es_vigente, true),
    fecha_desde = COALESCE(fecha_desde, CURRENT_TIMESTAMP)
WHERE es_vigente IS NULL
   OR fecha_desde IS NULL;

-- 4) Indice parcial para acelerar el lookup de la version vigente por CUIT.
CREATE INDEX IF NOT EXISTS idx_dim_proveedor_cuit_vigente
    ON dw.dim_proveedor (cuit)
    WHERE es_vigente;

-- =========================================================================
-- OPCIONAL (recomendado) - re-seed limpio para arrancar el historial parejo.
-- Deja la dimension sembrada con la version 1 de cada proveedor usando el
-- criterio de dedup deterministico del nuevo ETL. Evita versiones "ruido" en
-- el primer rebuild para CUIT con varias grafias de razon social.
-- CASCADE tambien vacia fact_adjudicacion y el bridge, que se reconstruyen
-- en el siguiente "Materialize all".
--
--   TRUNCATE dw.dim_proveedor RESTART IDENTITY CASCADE;
--
-- Despues de esto, corre el pipeline (Materialize all) y la dimension se
-- siembra sola.
-- =========================================================================
