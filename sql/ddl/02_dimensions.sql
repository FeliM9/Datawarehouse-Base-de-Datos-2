-- =========================================
-- DIMENSION: FECHA
-- =========================================

CREATE TABLE IF NOT EXISTS dw.dim_fecha (
    fecha_id INTEGER PRIMARY KEY,
    fecha DATE NOT NULL UNIQUE,

    dia INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    anio INTEGER NOT NULL,
    trimestre INTEGER NOT NULL,
    semana INTEGER NOT NULL,

    nombre_mes VARCHAR(20),
    nombre_dia VARCHAR(20),

    es_feriado BOOLEAN DEFAULT FALSE,
    es_fin_semana BOOLEAN DEFAULT FALSE
);

-- =========================================
-- DIMENSION: ORGANISMO
-- =========================================

CREATE TABLE IF NOT EXISTS dw.dim_organismo (
    organismo_id SERIAL PRIMARY KEY,

    nro_saf INTEGER,
    descripcion_saf VARCHAR(255),

    nro_uoc INTEGER,
    descripcion_uoc VARCHAR(255)
);

-- =========================================
-- DIMENSION: PROCEDIMIENTO
-- =========================================

CREATE TABLE IF NOT EXISTS dw.dim_procedimiento (
    procedimiento_id VARCHAR(100) PRIMARY KEY,

    nombre_procedimiento VARCHAR(255),
    objeto_procedimiento TEXT,

    ejercicio VARCHAR(20),
    modalidad VARCHAR(100)
);

-- =========================================
-- DIMENSION: PROVEEDOR
-- =========================================

CREATE TABLE IF NOT EXISTS dw.dim_proveedor (
    proveedor_id SERIAL PRIMARY KEY,

    cuit VARCHAR(20) UNIQUE,
    razon_social VARCHAR(255),

    provincia VARCHAR(100)
);

-- =========================================
-- DIMENSION: RUBRO
-- =========================================

CREATE TABLE IF NOT EXISTS dw.dim_rubro (
    rubro_id SERIAL PRIMARY KEY,

    descripcion_rubro VARCHAR(255)
);