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

### Tarea 5 — `cli.py`: interfaz de consola (2026-10-24)

- **Qué se hizo:** primero se escribió `tests/test_cli.py` y se lo corrió sin
  implementación. Después se creó `cli.py` (argparse) con los comandos
  `unidades`, `listar [--unidad]`, `disponibilidad`, `reservar` y
  `cancelar ID`, y la opción global `--db` (por defecto `data/reservas.db`).
  Los errores se muestran como `Error: ...` en stderr con código de salida 1.
- **Requisitos cubiertos:** R1 a R9 desde la consola. R9 se prueba con
  procesos separados (`subprocess`): cada comando es un arranque nuevo.
- **Comando ejecutado (antes de implementar):** `python3 -m pytest`
- **Resultado real:** `ModuleNotFoundError: No module named 'cli'` —
  `1 error in 0.13s` (falla esperada).
- **Comando ejecutado (después de implementar):** `python3 -m pytest`
- **Resultado real:** `80 passed in 0.65s` (65 anteriores + 15 nuevas).
- **Prueba manual sobre la base real (`data/reservas.db`):** se ejecutaron
  `unidades` (5 unidades); `reservar` MIC-01 10:00-11:00 → `Reserva 1 creada`;
  MIC-01 10:30-11:30 → `Error: MIC-01 ya está reservada en ese horario
  (reserva 1)`, código 1; MIC-01 11:00-12:00 → `Reserva 2 creada`; MIC-02
  10:00-11:00 → `Reserva 3 creada`; XYZ-99 → `Error: unidad desconocida:
  XYZ-99`; `cancelar 1` → `[cancelada]`; `cancelar 1` otra vez → `Error: la
  reserva 1 ya está cancelada`; `disponibilidad` MIC-01 10:00-11:00 →
  `disponible`; 11:30-12:30 → `no disponible`, ocupada por #2. Cada comando
  es un proceso nuevo y `listar` mostró las 3 reservas (#1 cancelada, #2 y #3
  activas) después de todos ellos.
- **Pendientes / decisiones:** no se agregó un comando para reiniciar datos,
  porque `AGENTS.md` prohíbe borrar reservas. El reinicio se documentará en el
  README como paso manual (borrar `data/reservas.db`) con su advertencia.
  La base de la prueba manual quedó en `data/` (ignorada por git).

### Tarea 6 — README: secciones 2, 3 y 4 (2026-10-24)

- **Qué se hizo:** se reemplazaron los textos "Pendiente" de las secciones 2
  (solución), 3 (preparación del agente) y 4 (decisiones y delegación) del
  README. La sección 1 no se modificó (verificado con `git diff`). Versión de
  Claude Code y modelo tomados de la información de la sesión. Los ejemplos
  de salida son los de la prueba manual de la tarea 5.
- **Comandos ejecutados:** `python3 cli.py --help` (coincide con los
  comandos documentados) y `python3 -m pytest -q`.
- **Resultado real:** `80 passed in 0.69s`.
- **Pendientes / decisiones:** quedan marcados con **[COMPLETAR]** en la
  sección 4 los motivos de las decisiones humanas, que solo puede aportar el
  humano.

### Tarea 7 — Ajustes de instrucciones del agente (2026-10-24)

- **Qué se hizo:** a pedido del humano, `AGENTS.md` ahora permite commit y
  push a la rama de la tarea al terminarla con pruebas pasando (fusionar o
  hacer push a `main` sigue requiriendo aprobación). Se agregó `CLAUDE.md`
  con `@AGENTS.md` para que Claude Code cargue las instrucciones solo. Se
  actualizó la sección 3 del README con ambos cambios.
- **Comando ejecutado:** `python3 -m pytest -q`
- **Resultado real:** `80 passed in 0.66s`.

### Tarea 8 — Decisiones humanas en la sección 4 del README (2026-10-24)

- **Qué se hizo:** se reemplazaron los **[COMPLETAR]** de la sección 4 con las
  respuestas del humano a preguntas de opción múltiple: aceptó las tres
  tareas sin revisar el código (confiando en las pruebas del agente), mantuvo
  el formato estricto de fecha y el tope de 8 horas, los IDs numéricos sin
  borrado y el reinicio manual sin comando. Se dejó registrada la limitación
  de que no hubo revisión independiente.
- **Comando ejecutado:** `python3 -m pytest -q`
- **Resultado real:** `80 passed in 0.69s`. `grep -c COMPLETAR README.md`
  devuelve 0.

### Tarea 9 — Sección 3 del README según la consigna (2026-10-24)

- **Qué se hizo:** se reescribió la sección 3 del README para cubrir cada punto
  de la consigna: tabla de entorno con su fuente y los datos no visibles,
  función del modelo y motivo de la elección (dado por el humano), extractos
  saneados de la configuración externa (hook de cierre, clasificador de
  permisos, acceso a GitHub) y cómo se aplicaron, controles previstos frente a
  aplicados, qué se revisó antes de aceptar, y adaptaciones con enlaces fijos
  al commit `0914d0b`. Las secciones 1, 2 y 4 no se modificaron.
- **Comando ejecutado:** `python3 -m pytest -q`
- **Resultado real:** `80 passed in 0.60s`.

<!-- Plantilla para cada tarea:

### Tarea N — Título (AAAA-MM-DD)

- **Qué se hizo:**
- **Requisitos cubiertos:**
- **Comando ejecutado:**
- **Resultado real:**
- **Pendientes / decisiones:**
-->
