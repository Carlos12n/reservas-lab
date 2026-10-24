# Instrucciones para el agente

## Objetivo
CLI local de reservas de equipos de laboratorio. La especificación está en la
sección 1 de `README.md`. No agregar requisitos que no estén ahí.

## Reglas del proyecto
- Python 3.11 o más nuevo. Solo librería estándar, más pytest para pruebas.
- Persistencia en SQLite, en `data/reservas.db` (ignorado por git).
- Una única función de superposición en `dominio.py`:
  `nuevo.inicio < existente.fin and nuevo.fin > existente.inicio`,
  aplicada solo a reservas ACTIVAS de la MISMA unidad. Reservar y consultar
  disponibilidad deben usar esa misma función.
- Nunca borrar reservas: cancelar solo cambia el estado a `cancelada`.
- Solicitantes siempre ficticios. Sin secretos, tokens ni datos reales.

## Flujo de trabajo (adaptación específica)
1. Antes de escribir código, escribir la prueba que falla.
2. Turnos consecutivos: toda prueba de superposición debe incluir el caso
   10:00-11:00 contra 11:00-12:00, que debe permitirse.
3. Al terminar cada tarea, actualizar `PROGRESS.md` con: qué se hizo, el
   comando de prueba ejecutado y su resultado real. No registrar resultados
   que no se ejecutaron.
4. Trabajar en tareas chicas. No tocar archivos fuera de lo pedido.

## Permisos
- Permitido: leer y editar archivos del repositorio, ejecutar pytest y la CLI.
- Requiere aprobación humana: instalar dependencias, borrar archivos,
  ejecutar git commit o push, tocar archivos fuera del repositorio.

## Fuera de alcance
Autenticación, pagos, notificaciones, integraciones externas, interfaz gráfica.