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

<!-- Plantilla para cada tarea:

### Tarea N — Título (AAAA-MM-DD)

- **Qué se hizo:**
- **Requisitos cubiertos:**
- **Comando ejecutado:**
- **Resultado real:**
- **Pendientes / decisiones:**
-->
