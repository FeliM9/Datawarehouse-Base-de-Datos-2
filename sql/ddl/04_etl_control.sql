-- Tabla de control del ETL.
-- Guarda el hash de la última versión cargada de cada fuente, para que el
-- sensor de Dagster (y automation/check_changes.py) puedan detectar cambios.

CREATE TABLE IF NOT EXISTS dw.etl_control (
    fuente              TEXT PRIMARY KEY,
    hash_actual         TEXT,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Semillas: una fila por fuente. hash_actual NULL => primer rebuild siempre
-- se considera "cambio".
INSERT INTO dw.etl_control (fuente, hash_actual)
VALUES
    ('adjudicaciones', NULL),
    ('convocatorias',  NULL)
ON CONFLICT (fuente) DO NOTHING;
