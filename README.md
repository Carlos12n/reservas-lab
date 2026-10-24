# Sistema de reservas de equipos de laboratorio

## 1. Especificación breve

### Problema
La coordinación de un laboratorio registra pedidos en mensajes y una planilla.
A veces se confirma la misma unidad para horarios superpuestos, y otras veces
una cancelación sigue bloqueando el horario. Se necesita consultar
disponibilidad, reservar y cancelar sin perder el historial.

### Alcance
- Leer el inventario precargado (`inventario.json`) y consultar disponibilidad
  por unidad e intervalo.
- Crear reservas de una unidad, con solicitante ficticio, inicio y fin.
- Cancelar conservando identificador y datos, y liberando el intervalo.
- Persistir reservas y estados para recuperarlos al reiniciar.

Fuera de alcance: administración del inventario, autenticación y roles,
notificaciones, pagos, integraciones externas, interfaz gráfica, despliegue.

### Inventario inicial
| ID | Equipo |
|---|---|
| MIC-01 | Microscopio digital |
| MIC-02 | Microscopio digital |
| OSC-01 | Osciloscopio |
| MUL-01 | Multímetro |
| FUE-01 | Fuente de alimentación |

Cada ID identifica una unidad física distinta.

### Requisitos verificables
| ID | Requisito | Criterio de aceptación |
|---|---|---|
| R1 | Cargar el inventario desde `inventario.json` | El listado de unidades muestra las 5 unidades |
| R2 | Crear reserva con unidad, solicitante, inicio y fin | Devuelve un ID único y la reserva queda `activa` |
| R3 | Rechazar superposición en la misma unidad | Con MIC-01 10:00-11:00 reservado, 10:30-11:30 se rechaza |
| R4 | Permitir límites consecutivos | Con MIC-01 10:00-11:00 reservado, 11:00-12:00 se acepta |
| R5 | Permitir unidades distintas en el mismo horario | MIC-02 10:00-11:00 se acepta aunque MIC-01 esté ocupado |
| R6 | Validar entradas | Se rechazan con error claro: unidad desconocida, solicitante vacío o solo espacios, fecha u hora inválida, inicio igual o posterior al fin |
| R7 | Cancelar conservando el registro | La reserva pasa a `cancelada`, conserva ID y datos, y el intervalo queda libre |
| R8 | Disponibilidad con las mismas reglas que reservar | Reservar y consultar usan la misma función de superposición |
| R9 | Persistir al reiniciar | Reservas activas y canceladas siguen presentes tras detener y reiniciar |

### Reglas
- Una reserva activa ocupa el intervalo; una cancelada no bloquea.
- Hay superposición si `nuevo.inicio < existente.fin` y
  `nuevo.fin > existente.inicio`, solo entre reservas activas de la misma unidad.

### Supuestos
- Zona horaria: America/Argentina/Buenos_Aires (UTC-3). Las horas son locales,
  sin offset.
- Formato de fecha y hora: `YYYY-MM-DD HH:MM`.
- Fechas pasadas: se permiten, para que las pruebas no dependan del reloj
  (limitación declarada).
- Duración máxima de una reserva: 8 horas. Sin límite de anticipación.
- Cancelar una reserva ya cancelada devuelve un error explícito.
- Interfaz: consola (CLI).

### Criterios de aceptación generales
- Las pruebas automáticas cubren: creación válida, rechazo de superposición,
  límites consecutivos, unidades distintas simultáneas, entradas inválidas y
  cancelación que conserva el registro y libera el horario.
- La persistencia se comprueba tras detener y reiniciar sin borrar datos.

## 2. Solución

*Pendiente: se completa cuando exista el código. Incluir estructura, decisiones
técnicas, requisitos previos y versiones, instalación, carga inicial y reinicio
de datos, comandos de aplicación y pruebas, ejemplo de entrada y salida, dónde
persisten los datos, advertencia sobre borrado en el reinicio, pendientes y
limitaciones.*

## 3. Preparación del agente

*Pendiente: se completa con evidencia real. Incluir entorno, versión y modelo
(o indicar "no visible"), instrucciones usadas (ver `AGENTS.md`), contexto
suministrado y excluido, permisos y aprobaciones, la adaptación específica con
evidencia de uso, y cómo se conserva el progreso (ver `PROGRESS.md`).*

## 4. Registro de decisiones y delegación

*Pendiente: se completa a medida que ocurran los hechos. Incluir decisiones
significativas con motivos y alternativas, y tres episodios de delegación
(objetivo y requisito, contexto e instrucción, resultado del agente, decisión
humana con motivo, enlace a evidencia).*