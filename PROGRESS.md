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

<!-- Plantilla para cada tarea:

### Tarea N — Título (AAAA-MM-DD)

- **Qué se hizo:**
- **Requisitos cubiertos:**
- **Comando ejecutado:**
- **Resultado real:**
- **Pendientes / decisiones:**
-->
