-- =========================================
-- DIMENSION: FECHA
-- =========================================
CREATE TABLE dw.dim_fecha (
	fecha_id int4 NOT NULL,
	fecha date NOT NULL,
	dia int4 NOT NULL,
	mes int4 NOT NULL,
	anio int4 NOT NULL,
	trimestre int4 NOT NULL,
	semana int4 NOT NULL,
	nombre_mes varchar(20) NULL,
	nombre_dia varchar(20) NULL,
	es_feriado bool DEFAULT false NULL,
	es_fin_semana bool DEFAULT false NULL,
	CONSTRAINT dim_fecha_fecha_key UNIQUE (fecha),
	CONSTRAINT dim_fecha_pkey PRIMARY KEY (fecha_id)
);
CREATE INDEX idx_dim_fecha_anio ON dw.dim_fecha USING btree (anio);
CREATE INDEX idx_dim_fecha_mes ON dw.dim_fecha USING btree (mes);
-- =========================================
-- DIMENSION: ORGANISMO
-- =========================================
CREATE TABLE dw.dim_organismo (
	organismo_id serial4 NOT NULL,
	nro_saf int4 NULL,
	descripcion_saf varchar(255) NULL,
	nro_uoc int4 NULL,
	descripcion_uoc varchar(255) NULL,
	CONSTRAINT dim_organismo_pkey PRIMARY KEY (organismo_id)
);
-- =========================================
-- DIMENSION: PROCEDIMIENTO
-- =========================================
CREATE TABLE dw.dim_procedimiento (
	procedimiento_id varchar(100) NOT NULL,
	nombre_procedimiento varchar(255) NULL,
	objeto_procedimiento text NULL,
	ejercicio varchar(20) NULL,
	modalidad varchar(100) NULL,
	tipo_procedimiento varchar(200) NULL,
	CONSTRAINT dim_procedimiento_pkey PRIMARY KEY (procedimiento_id)
);
-- =========================================
-- DIMENSION: PROVEEDOR
-- =========================================
CREATE TABLE dw.dim_proveedor (
	proveedor_id serial4 NOT NULL,
	cuit varchar(20) NULL,
	razon_social varchar(255) NULL,
	provincia varchar(100) NULL,
	CONSTRAINT dim_proveedor_cuit_key UNIQUE (cuit),
	CONSTRAINT dim_proveedor_pkey PRIMARY KEY (proveedor_id)
);
CREATE INDEX idx_dim_proveedor_cuit ON dw.dim_proveedor USING btree (cuit);
-- =========================================
-- DIMENSION: RUBRO
-- =========================================
CREATE TABLE dw.dim_rubro (
	rubro_id serial4 NOT NULL,
	descripcion_rubro varchar(255) NULL,
	CONSTRAINT dim_rubro_pkey PRIMARY KEY (rubro_id)
);