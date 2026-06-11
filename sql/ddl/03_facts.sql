-- =========================================
-- FACT: CONVOCATORIA
-- =========================================
CREATE TABLE dw.fact_convocatoria (
	fact_convocatoria_id bigserial NOT NULL,
	procedimiento_id varchar(100) NOT NULL,
	organismo_id int4 NOT NULL,
	fecha_publicacion_id int4 NOT NULL,
	monto_estimado numeric(18, 2) NULL,
	etapa varchar(100) NULL,
	tipo_operacion varchar(100) NULL,
	CONSTRAINT fact_convocatoria_pkey PRIMARY KEY (fact_convocatoria_id)
);
CREATE INDEX idx_fact_convocatoria_fecha ON dw.fact_convocatoria USING btree (fecha_publicacion_id);
CREATE INDEX idx_fact_convocatoria_organismo ON dw.fact_convocatoria USING btree (organismo_id);
CREATE INDEX idx_fact_convocatoria_procedimiento ON dw.fact_convocatoria USING btree (procedimiento_id);


-- dw.fact_convocatoria foreign keys

ALTER TABLE dw.fact_convocatoria ADD CONSTRAINT fk_fact_convocatoria_fecha FOREIGN KEY (fecha_publicacion_id) REFERENCES dw.dim_fecha(fecha_id);
ALTER TABLE dw.fact_convocatoria ADD CONSTRAINT fk_fact_convocatoria_organismo FOREIGN KEY (organismo_id) REFERENCES dw.dim_organismo(organismo_id);
ALTER TABLE dw.fact_convocatoria ADD CONSTRAINT fk_fact_convocatoria_procedimiento FOREIGN KEY (procedimiento_id) REFERENCES dw.dim_procedimiento(procedimiento_id);
-- =========================================
-- FACT: ADJUDICACION
-- =========================================
CREATE TABLE dw.fact_adjudicacion (
	fact_adjudicacion_id bigserial NOT NULL,
	nro_orden_compra varchar(100) NOT NULL,
	procedimiento_id varchar(100) NOT NULL,
	proveedor_id int4 NOT NULL,
	fecha_adjudicacion_id int4 NOT NULL,
	monto_adjudicado numeric(18, 2) NULL,
	moneda varchar(100) NULL,
	tipo_orden varchar(100) NULL,
	CONSTRAINT fact_adjudicacion_pkey PRIMARY KEY (fact_adjudicacion_id),
	CONSTRAINT uq_fact_adjudicacion_nro_oc UNIQUE (nro_orden_compra)
);
CREATE INDEX idx_fact_adjudicacion_fecha ON dw.fact_adjudicacion USING btree (fecha_adjudicacion_id);
CREATE INDEX idx_fact_adjudicacion_procedimiento ON dw.fact_adjudicacion USING btree (procedimiento_id);
CREATE INDEX idx_fact_adjudicacion_proveedor ON dw.fact_adjudicacion USING btree (proveedor_id);


-- dw.fact_adjudicacion foreign keys

ALTER TABLE dw.fact_adjudicacion ADD CONSTRAINT fk_fact_adjudicacion_fecha FOREIGN KEY (fecha_adjudicacion_id) REFERENCES dw.dim_fecha(fecha_id);
ALTER TABLE dw.fact_adjudicacion ADD CONSTRAINT fk_fact_adjudicacion_procedimiento FOREIGN KEY (procedimiento_id) REFERENCES dw.dim_procedimiento(procedimiento_id);
ALTER TABLE dw.fact_adjudicacion ADD CONSTRAINT fk_fact_adjudicacion_proveedor FOREIGN KEY (proveedor_id) REFERENCES dw.dim_proveedor(proveedor_id);