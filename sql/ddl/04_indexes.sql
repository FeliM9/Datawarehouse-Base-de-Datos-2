-- =========================================
-- INDEXES FACT_CONVOCATORIA
-- =========================================

CREATE INDEX IF NOT EXISTS idx_fact_convocatoria_procedimiento
ON dw.fact_convocatoria(procedimiento_id);

CREATE INDEX IF NOT EXISTS idx_fact_convocatoria_organismo
ON dw.fact_convocatoria(organismo_id);

CREATE INDEX IF NOT EXISTS idx_fact_convocatoria_fecha
ON dw.fact_convocatoria(fecha_publicacion_id);

-- =========================================
-- INDEXES FACT_ADJUDICACION
-- =========================================

CREATE INDEX IF NOT EXISTS idx_fact_adjudicacion_procedimiento
ON dw.fact_adjudicacion(procedimiento_id);

CREATE INDEX IF NOT EXISTS idx_fact_adjudicacion_proveedor
ON dw.fact_adjudicacion(proveedor_id);

CREATE INDEX IF NOT EXISTS idx_fact_adjudicacion_rubro
ON dw.fact_adjudicacion(rubro_id);

CREATE INDEX IF NOT EXISTS idx_fact_adjudicacion_fecha
ON dw.fact_adjudicacion(fecha_adjudicacion_id);

-- =========================================
-- INDEXES DIMENSIONES
-- =========================================

CREATE INDEX IF NOT EXISTS idx_dim_fecha_anio
ON dw.dim_fecha(anio);

CREATE INDEX IF NOT EXISTS idx_dim_fecha_mes
ON dw.dim_fecha(mes);

CREATE INDEX IF NOT EXISTS idx_dim_proveedor_cuit
ON dw.dim_proveedor(cuit);