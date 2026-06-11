# Orquestación del DW con Dagster

Esta carpeta envuelve el ETL existente (`etl/` + `automation/`) en un proyecto
de **Dagster**, sin reescribir la lógica de los scripts. Cada script se ejecuta
como subproceso dentro de un *asset*, con dependencias explícitas, logs,
reintentos y un sensor que dispara el rebuild cuando cambian las fuentes.

## 1. Requisitos previos

1. Tener el `.env` en la raíz del repo con las credenciales de Neon:

   ```
   DB_HOST=...
   DB_PORT=5432
   DB_NAME=...
   DB_USER=...
   DB_PASSWORD=...
   ```

2. Tener el esquema creado en Neon. Si todavía no lo corriste, aplicá los DDL en orden:

   ```
   sql/ddl/01_schemas.sql
   sql/ddl/02_dimensions.sql
   sql/ddl/03_facts.sql
   sql/ddl/04_etl_control.sql   <- nuevo, necesario para el sensor
   sql/ddl/05_bridge.sql
   ```

3. Instalar dependencias (incluye Dagster):

   ```bash
   pip install -r requierements.txt
   ```

## 2. Levantar Dagster

Desde la **raíz del repo**:

```bash
dagster dev -f orchestration/definitions.py
```

Abrí http://localhost:3000.

- **Assets** → botón **Materialize all** = rebuild completo del DW.
- Cada asset muestra sus logs (el `print` de cada script aparece ahí).
- Si un paso falla, queda en rojo y el resto no avanza.

## 3. El grafo de assets

El orden lo determinan las dependencias, no una lista lineal. Esto reproduce el
orden correcto de `automation/run_pipeline.py` pero deja ver el linaje real del
DW (útil para defender el modelo dimensional):

```
reset_dw
   ├─ dim_fecha ─────────────┐
   ├─ dim_organismo ─────────┤
   ├─ dim_proveedor ─────────┤
   ├─ dim_rubro ─────────┐   │
   └─ dim_procedimiento  │   │
          └─ completar_procedimientos
                 ├─ fact_convocatoria   (organismo, fecha, procedimiento)
                 └─ fact_adjudicacion   (proveedor, fecha, procedimiento)
                         └─ bridge_adjudicacion_rubro  (+ dim_rubro)
                                 └─ registrar_control_hashes
```

Las dimensiones independientes pueden materializarse en paralelo.

## 4. Disparo automático por cambio en la fuente (sensor)

`sensor_cambio_en_fuentes` compara el hash MD5 actual de cada Google Sheet
contra lo guardado en `dw.etl_control`. Si difiere, lanza `rebuild_dw_job`.
El asset final `registrar_control_hashes` actualiza `dw.etl_control` al terminar,
así no se vuelve a disparar por el mismo cambio.

- Viene **apagado** por defecto. Encendelo en la UI: pestaña **Sensors** →
  `sensor_cambio_en_fuentes` → toggle **Running**.
- Hace polling cada 60 s (configurable con `minimum_interval_seconds`).
- Reemplaza el bucle manual de `automation/check_changes.py`.

> Nota: el sensor necesita que `dagster dev` (o `dagster-daemon`) esté corriendo.
> `dagster dev` ya levanta el daemon junto con la UI.

## 5. Futuro: trigger por webhook (Google Drive)

El sensor cubre el caso "polling". Cuando muevas las fuentes a Google Drive y
quieras disparo **por webhook** (push), hay dos caminos, de menor a mayor
esfuerzo:

1. **Sensor + push a un archivo de señal** (mínimo cambio): el webhook de Drive
   escribe un registro/flag (en una tabla, un archivo, una cola). El sensor lee
   ese flag en vez de hashear las sheets. Sigue siendo polling pero barato.

2. **Lanzar el run vía la API GraphQL de Dagster** (push real): Dagster expone un
   endpoint GraphQL. Un pequeño servicio (Cloud Function / FastAPI) recibe el
   webhook de Drive y ejecuta la mutación `launchRun` apuntando a
   `rebuild_dw_job`. Esquema:

   ```
   Google Drive  --webhook-->  tu endpoint  --GraphQL launchRun-->  Dagster
   ```

   En **Dagster+ (Cloud)** esto es aún más directo porque hay endpoints de
   ingesta de eventos listos para automatizaciones.

Ambos caminos reutilizan exactamente el mismo `rebuild_dw_job`, así que migrar
de polling a webhook no toca el ETL.

## 6. Archivos

| Archivo | Rol |
| --- | --- |
| `orchestration/definitions.py` | Assets, job y sensor. Punto de entrada de Dagster. |
| `sql/ddl/04_etl_control.sql` | Tabla `dw.etl_control` que usa el sensor. |
| `requierements.txt` | Se agregó `dagster` y `dagster-webserver`. |

Los scripts de `etl/` y `automation/` **no se modificaron**: Dagster los ejecuta
tal cual.
