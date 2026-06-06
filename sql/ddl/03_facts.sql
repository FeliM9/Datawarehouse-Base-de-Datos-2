-- =========================================
-- FACT: CONVOCATORIA
-- =========================================

CREATE TABLE IF NOT EXISTS dw.fact_convocatoria (
    fact_convocatoria_id BIGSERIAL PRIMARY KEY,

    procedimiento_id VARCHAR(100) NOT NULL,
    organismo_id INTEGER NOT NULL,
    fecha_publicacion_id INTEGER NOT NULL,

    monto_estimado NUMERIC(18,2),

    etapa VARCHAR(100),
    tipo_operacion VARCHAR(100),

    CONSTRAINT fk_fact_convocatoria_procedimiento
        FOREIGN KEY (procedimiento_id)
        REFERENCES dw.dim_procedimiento(procedimiento_id),

    CONSTRAINT fk_fact_convocatoria_organismo
        FOREIGN KEY (organismo_id)
        REFERENCES dw.dim_organismo(organismo_id),

    CONSTRAINT fk_fact_convocatoria_fecha
        FOREIGN KEY (fecha_publicacion_id)
        REFERENCES dw.dim_fecha(fecha_id)
);

-- =========================================
-- FACT: ADJUDICACION
-- =========================================

CREATE TABLE IF NOT EXISTS dw.fact_adjudicacion (
    fact_adjudicacion_id BIGSERIAL PRIMARY KEY,

    nro_orden_compra VARCHAR(100) NOT NULL,

    procedimiento_id VARCHAR(100) NOT NULL,
    proveedor_id INTEGER NOT NULL,
    rubro_id INTEGER NOT NULL,
    fecha_adjudicacion_id INTEGER NOT NULL,

    monto_adjudicado NUMERIC(18,2),

    moneda VARCHAR(20),
    tipo_orden VARCHAR(100),

    CONSTRAINT uq_fact_adjudicacion_nro_oc
        UNIQUE (nro_orden_compra),

    CONSTRAINT fk_fact_adjudicacion_procedimiento
        FOREIGN KEY (procedimiento_id)
        REFERENCES dw.dim_procedimiento(procedimiento_id),

    CONSTRAINT fk_fact_adjudicacion_proveedor
        FOREIGN KEY (proveedor_id)
        REFERENCES dw.dim_proveedor(proveedor_id),

    CONSTRAINT fk_fact_adjudicacion_rubro
        FOREIGN KEY (rubro_id)
        REFERENCES dw.dim_rubro(rubro_id),

    CONSTRAINT fk_fact_adjudicacion_fecha
        FOREIGN KEY (fecha_adjudicacion_id)
        REFERENCES dw.dim_fecha(fecha_id)
);