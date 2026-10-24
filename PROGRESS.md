# Progreso

Registro de tareas según el flujo de `AGENTS.md`: qué se hizo, comando de
prueba ejecutado y su resultado real. Solo se anotan comandos que se
ejecutaron.

## Estructura prevista

```
reservas-lab/
├── dominio.py        # superposición (única función) y validaciones
├── inventario.py     # carga de inventario.json
├── repositorio.py    # persistencia SQLite en data/reservas.db
├── servicio.py       # reservar, cancelar, disponibilidad
├── cli.py            # interfaz de consola (argparse)
├── inventario.json
└── tests/
```

## Tareas

### Paso 0 — Preparación (2026-10-24)

- **Qué se hizo:** se creó este `PROGRESS.md` y se instaló pytest (aprobado
  por el humano). Se definió la estructura prevista de arriba; todavía no se
  creó ningún módulo.
- **Entorno:** Python 3.13.17, pytest 9.1.1.
- **Comando ejecutado:** `python3 -m pytest`
- **Resultado real:** `collected 0 items` — `no tests ran in 0.01s` (todavía
  no hay pruebas).

### Tarea 1 — `dominio.py`: superposición y validaciones (2026-10-24)

- **Qué se hizo:** primero se escribió `tests/test_dominio.py` y se lo corrió
  sin implementación. Después se creó `dominio.py` con la única función de
  superposición `se_superponen` (solo reservas activas de la misma unidad),
  `conflictos` (la usa), y validaciones de fecha/hora, solicitante, unidad e
  intervalo (inicio < fin, máximo 8 horas). Se agregó `pyproject.toml` para
  que pytest encuentre los módulos de la raíz.
- **Requisitos cubiertos:** R3, R4 (incluye el caso 10:00-11:00 contra
  11:00-12:00), R5, R6, regla de canceladas que no bloquean. R8 queda
  preparado: `conflictos` es la función que deberán usar reservar y consultar.
- **Comando ejecutado (antes de implementar):** `python3 -m pytest`
- **Resultado real:** `ModuleNotFoundError: No module named 'dominio'` —
  `1 error during collection` (falla esperada).
- **Comando ejecutado (después de implementar):** `python3 -m pytest`
- **Resultado real:** `28 passed in 0.05s`.
- **Pendientes / decisiones:** la validación de unidad recibe el conjunto de
  IDs válidos; se conectará con el inventario en la tarea 2. Se exige el
  formato exacto `YYYY-MM-DD HH:MM` con ceros a la izquierda (se rechaza
  `2026-1-2 10:00`). Una duración de exactamente 8 horas se acepta.

### Tarea 2 — `inventario.py`: carga de `inventario.json` (2026-10-24)

- **Qué se hizo:** primero se escribió `tests/test_inventario.py` y se lo
  corrió sin implementación. Después se creó `inventario.py` con `Unidad` y
  `cargar_inventario(ruta)`, que por defecto lee `inventario.json` junto al
  módulo (no depende del directorio desde donde se ejecute).
- **Requisitos cubiertos:** R1. Se verificó además que los IDs cargados sirven
  para `validar_unidad` (unidad desconocida de R6).
- **Comando ejecutado (antes de implementar):** `python3 -m pytest`
- **Resultado real:** `ModuleNotFoundError: No module named 'inventario'` —
  `1 error during collection` (falla esperada).
- **Comando ejecutado (después de implementar):** `python3 -m pytest`
- **Resultado real:** `32 passed in 0.06s` (28 de la tarea 1 + 4 nuevas).
- **Pendientes / decisiones:** no se validan IDs duplicados ni campos
  faltantes en el JSON, porque la administración del inventario está fuera de
  alcance y el archivo es precargado.

### Tarea 3 — `repositorio.py`: persistencia SQLite (2026-10-24)

- **Qué se hizo:** primero se escribió `tests/test_repositorio.py` y se lo
  corrió sin implementación. Después se creó `repositorio.py` con la clase
  `Repositorio` (por defecto `data/reservas.db`, crea la carpeta si falta):
  `guardar_nueva`, `obtener`, `listar` (filtro opcional por unidad, orden por
  inicio) y `cambiar_estado`. No existe ninguna operación de borrado.
- **Requisitos cubiertos:** R9 (activas y canceladas siguen presentes al
  reabrir el archivo con una instancia nueva), base de R2 (ID único,
  estado `activa`) y de R7 (cambiar estado conserva ID y datos).
- **Comando ejecutado (antes de implementar):** `python3 -m pytest`
- **Resultado real:** `ModuleNotFoundError: No module named 'repositorio'` —
  `1 error in 0.11s` (falla esperada).
- **Comando ejecutado (después de implementar):** `python3 -m pytest`
- **Resultado real:** `41 passed in 0.09s` (32 anteriores + 9 nuevas).
  Las pruebas usan una base temporal (`tmp_path`); se comprobó con `ls data`
  que no se creó la base real.
- **Pendientes / decisiones:** ID autoincremental de SQLite (fácil de escribir
  en consola). Fechas guardadas como texto `YYYY-MM-DD HH:MM`, que ordena
  cronológicamente. Una restricción `CHECK` impide estados distintos de
  `activa` y `cancelada`. La regla de superposición no está en SQL: sigue
  siendo solo la de `dominio.py`, que se aplicará en el servicio (tarea 4).

### Tarea 4 — `servicio.py`: reservar, cancelar y disponibilidad (2026-10-24)

- **Qué se hizo:** primero se escribió `tests/test_servicio.py` y se lo corrió
  sin implementación. Después se creó `servicio.py` con la clase `Servicio`
  (`unidades`, `listar`, `consultar_disponibilidad`, `reservar`, `cancelar`) y
  el error `ErrorReserva` para superposición, reserva inexistente y reserva
  ya cancelada. Reservar y consultar validan con el mismo método privado y
  obtienen los bloqueos con el mismo método privado, que llama a
  `dominio.conflictos`.
- **Requisitos cubiertos:** R1 a R9 de punta a punta sobre una base temporal,
  incluido el caso 10:00-11:00 contra 11:00-12:00 en reservar y en consultar.
  R8 se verifica con un espía sobre `conflictos`: reservar y consultar lo
  llaman. R9: tras reabrir, la activa sigue bloqueando y la cancelada no.
- **Comando ejecutado (antes de implementar):** `python3 -m pytest`
- **Resultado real:** `ModuleNotFoundError: No module named 'servicio'` —
  `1 error in 0.11s` (falla esperada).
- **Comando ejecutado (después de implementar):** `python3 -m pytest`
- **Resultado real:** `65 passed in 0.21s` (41 anteriores + 24 nuevas).
  Se comprobó con `ls data` que no se creó la base real.
- **Pendientes / decisiones:** consultar disponibilidad devuelve la lista de
  reservas que ocupan el intervalo (vacía = disponible), para poder mostrar
  qué bloquea. Limitación: verificar e insertar no es atómico entre procesos;
  es suficiente para una CLI de un solo usuario a la vez.

<!-- Plantilla para cada tarea:

### Tarea N — Título (AAAA-MM-DD)

- **Qué se hizo:**
- **Requisitos cubiertos:**
- **Comando ejecutado:**
- **Resultado real:**
- **Pendientes / decisiones:**
-->
