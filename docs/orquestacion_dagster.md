# Orquestacion del ETL con Dagster

Este documento explica como correr y operar el pipeline del Data Warehouse
usando Dagster como orquestador.

## Que se hizo

No se reescribio la logica de los scripts ETL. Cada script de `etl/` y
`automation/` se "envuelve" como un **asset** de Dagster que lo ejecuta como
subproceso desde la raiz del proyecto (igual que hacia `run_pipeline.py`), pero
ahora con grafo de dependencias visible, logs por paso, reintentos, schedule y
un sensor de cambios.

Archivos nuevos:

- `orchestration/definitions.py` - definicion de assets, job, schedule y sensor.
- `orchestration/__init__.py` - marca la carpeta como paquete.
- `workspace.yaml` - permite arrancar con solo `dagster dev`.

## Grafo de dependencias (linaje del DW)

```text
sincronizar_fuentes        (descarga las Google Sheets a data/raw/)
        |
     reset_dw              (TRUNCATE de todas las tablas)
        |
   +----+----+----+----+----------------+
   |    |    |    |                      |
 fecha org  prov rubro            procedimiento
                                          |
                              completar_procedimientos
   |    |              |    |             |
   +----+--------------+    +-------------+
        |                          |
 fact_convocatoria         fact_adjudicacion
                                   |
                         bridge_adjudicacion_rubro
                                   |
                        registrar_control_hashes   (graba hashes en dw.etl_control)
```

Las dimensiones independientes se materializan en paralelo. El orden respeta el
de `automation/run_pipeline.py`.

## Como correr

Desde la raiz del proyecto, con el entorno virtual activado:

```bash
pip install -r requierements.txt
dagster dev
```

Abrir http://localhost:3000

- **Reconstruir el DW a mano:** pestana *Assets* -> boton *Materialize all*.
- Ver logs, estados y tiempos de cada paso en cada run.

> Sugerencia: definir `DAGSTER_HOME` (carpeta donde Dagster guarda runs y estado
> de schedules/sensors) para que persista entre reinicios. Si no se define, usa
> una carpeta temporal y avisa con un warning.
>
> Windows (PowerShell): `setx DAGSTER_HOME "C:\dagster_home"` y reabrir la terminal.

## Schedule (rebuild diario)

`rebuild_diario` corre el rebuild completo todos los dias a las 06:00
(`cron: 0 6 * * *`). Viene **apagado** por defecto; se activa desde la pestana
*Automation* de la UI.

## Sensor de cambios (lo que pediste: disparo por cambio en la fuente)

`sensor_cambio_en_fuentes` reemplaza a `automation/check_changes.py`:

1. Cada 60 s calcula el hash MD5 de cada Google Sheet.
2. Lo compara contra el ultimo hash guardado en `dw.etl_control`.
3. Si algo cambio, dispara `rebuild_dw_job`. El `run_key` evita relanzar dos
   veces por el mismo cambio.
4. Al final del rebuild, el asset `registrar_control_hashes` actualiza
   `dw.etl_control`, cerrando el loop.

Tambien viene **apagado** por defecto; se enciende desde *Automation*.

## Futuro: disparo por webhook desde Google Drive

Cuando los archivos pasen a Google Drive, hay dos caminos:

1. **Seguir con el sensor (mas simple).** Apuntar el sensor a la fuente de Drive
   (o mantener las Sheets) y dejar que el polling detecte el cambio. No requiere
   exponer ningun puerto. Es lo que ya esta armado.

2. **Webhook real (push).** Drive (via Apps Script o Google Cloud) hace un POST
   cuando cambia un archivo. Ese POST puede lanzar el job llamando al endpoint
   GraphQL de Dagster (`launchRun` sobre `rebuild_dw_job`). En Dagster OSS se
   expone con `dagster-webserver`; en Dagster+ existen webhooks/automations
   nativos. Recomendacion: empezar con el sensor (camino 1) y migrar a webhook
   solo si se necesita latencia baja.

## Logs (carpeta `Dagster Logs/`)

Cada paso del ETL escribe su salida en la carpeta `Dagster Logs/` del proyecto:

- `AAAAMMDD_HHMMSS_<script>.log` - un archivo por ejecucion, con el stdout,
  el stderr y el codigo de salida de ese script.
- `etl.log` - log maestro: una linea por paso con fecha/hora, estado
  (OK / FALLO) y el nombre del archivo de detalle.

Esto es independiente de los logs internos de Dagster (que ademas se ven en la
UI). La carpeta se versiona via `.gitkeep`, pero los `.log` estan en
`.gitignore` para no subir salidas al repo.

Si ademas queres persistir los logs internos de Dagster (compute logs, historial
de runs) entre reinicios, defini `DAGSTER_HOME` a una carpeta fija; si no, usa
una temporal.

## Notas

- Los scripts usan rutas relativas (`data/raw/...`) y `.env`. Por eso los assets
  ejecutan los scripts con `cwd` = raiz del proyecto; no hace falta tocar los
  scripts.
- `sincronizar_fuentes` sobrescribe los CSV de `data/raw/` con la version actual
  de las Sheets. Si en algun momento queres construir desde CSV locales editados
  a mano, quita la dependencia `deps=[sincronizar_fuentes]` de `reset_dw`.
- Probado con Dagster 1.13. Carga sin errores: 12 assets, 1 job, 1 schedule,
  1 sensor; grafo sin ciclos.
```
