# Datawarehouse-Base-de-Datos-2

Proyecto académico de Data Warehouse orientado al análisis de licitaciones y adjudicaciones públicas.

## Objetivo

Diseñar e implementar un Data Warehouse utilizando arquitectura dimensional (modelo estrella) para centralizar información de:

* Convocatorias
* Adjudicaciones
* Organismos
* Proveedores
* Rubros
* Procedimientos
* Fechas

El objetivo final es permitir consultas analíticas, generación de KPIs y visualización de datos mediante dashboards.

---

# Arquitectura del Proyecto

```text
CSV / APIs
     ↓
Python ETL
     ↓
PostgreSQL (Neon)
     ↓
Metabase / SQL Analytics
```

---

# Stack Tecnológico

| Componente    | Tecnología      |
| ------------- | --------------- |
| Base de datos | PostgreSQL      |
| Hosting DB    | Neon            |
| ETL           | Python + pandas |
| Cliente SQL   | DBeaver         |
| Visualización | Metabase        |
| Versionado    | Git + GitHub    |

---

# Estructura del Proyecto

```text
dw-licitaciones/
│
├── sql/
│   ├── ddl/
│   └── queries/
│
├── etl/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── docs/
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

# Descripción de Carpetas

## sql/ddl/

Scripts SQL para creación de tablas, constraints y esquema del Data Warehouse.

Ejemplo:

* dimensiones
* tablas fact
* claves foráneas
* índices

---

## sql/queries/

Consultas analíticas y queries de validación.

Ejemplos:

* Top proveedores
* Monto adjudicado por organismo
* Análisis temporal de adjudicaciones

---

## etl/

Scripts de extracción, transformación y carga de datos.

Responsabilidades:

* lectura de CSV/APIs
* limpieza de datos
* normalización
* carga hacia PostgreSQL

---

## data/raw/

Datos originales sin modificar.

Ejemplos:

* CSV descargados
* JSON de APIs
* archivos Excel

---

## data/processed/

Datos ya transformados y listos para carga.

---

## docs/

Documentación del proyecto:

* modelo dimensional
* decisiones de diseño
* diagramas
* documentación técnica

---

# Modelo Dimensional

El Data Warehouse se compone de:

## Tablas FACT

* FACT_Convocatoria
* FACT_Adjudicacion

## Tablas DIM

* DIM_Organismo
* DIM_Proveedor
* DIM_Rubro
* DIM_Procedimiento
* DIM_Fecha

---

# Configuración del Proyecto

## 1. Clonar repositorio

```bash
git clone <repo-url>
cd dw-licitaciones
```

---

## 2. Crear entorno virtual

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

# Base de Datos

La base de datos PostgreSQL se encuentra hosteada en Neon.

La conexión se realiza mediante:

* DBeaver
* scripts Python ETL
* herramientas BI

---

# Convenciones

## Naming

* tablas en snake_case
* dimensiones: `dim_*`
* hechos: `fact_*`

Ejemplos:

* `dim_proveedor`
* `fact_adjudicacion`

---

# Objetivos del Proyecto

* Implementar un Data Warehouse funcional
* Aplicar conceptos de modelado dimensional
* Diseñar procesos ETL
* Realizar análisis de datos
* Generar dashboards analíticos

---

# Estado del Proyecto

## Fase actual

* [x] Infraestructura inicial
* [x] Configuración PostgreSQL en Neon
* [x] Configuración GitHub
* [ ] Diseño físico del DW
* [ ] Desarrollo ETL
* [ ] Dashboards y visualización

---
