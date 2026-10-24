"""Reglas de dominio: superposición de reservas y validación de entradas."""

import re
from dataclasses import dataclass
from datetime import datetime, timedelta

ACTIVA = "activa"
CANCELADA = "cancelada"

FORMATO_FECHA_HORA = "%Y-%m-%d %H:%M"
DURACION_MAXIMA = timedelta(hours=8)

_PATRON_FECHA_HORA = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}")


class ErrorValidacion(ValueError):
    """Entrada inválida, con un mensaje apto para mostrar al usuario."""


@dataclass(frozen=True)
class Intervalo:
    """Intervalo pedido para una unidad (al reservar o consultar)."""

    unidad: str
    inicio: datetime
    fin: datetime


@dataclass(frozen=True)
class Reserva:
    id: int
    unidad: str
    solicitante: str
    inicio: datetime
    fin: datetime
    estado: str = ACTIVA


def se_superponen(nuevo, existente: Reserva) -> bool:
    """Única regla de superposición del sistema.

    Solo una reserva ACTIVA de la MISMA unidad puede bloquear. Los límites
    consecutivos (10:00-11:00 y 11:00-12:00) no se superponen.
    """
    return (
        existente.estado == ACTIVA
        and nuevo.unidad == existente.unidad
        and nuevo.inicio < existente.fin
        and nuevo.fin > existente.inicio
    )


def conflictos(nuevo, existentes) -> list[Reserva]:
    """Reservas existentes que bloquean al intervalo nuevo."""
    return [r for r in existentes if se_superponen(nuevo, r)]


def parsear_fecha_hora(texto: str) -> datetime:
    if not _PATRON_FECHA_HORA.fullmatch(texto):
        raise ErrorValidacion(
            f"fecha u hora inválida: {texto!r} (formato esperado YYYY-MM-DD HH:MM)"
        )
    try:
        return datetime.strptime(texto, FORMATO_FECHA_HORA)
    except ValueError:
        raise ErrorValidacion(f"fecha u hora inválida: {texto!r}") from None


def validar_solicitante(texto: str) -> str:
    limpio = texto.strip()
    if not limpio:
        raise ErrorValidacion("el solicitante no puede estar vacío")
    return limpio


def validar_unidad(unidad: str, unidades_validas) -> str:
    if unidad not in unidades_validas:
        raise ErrorValidacion(f"unidad desconocida: {unidad}")
    return unidad


def validar_intervalo(inicio: datetime, fin: datetime) -> None:
    if inicio >= fin:
        raise ErrorValidacion("el inicio debe ser anterior al fin")
    if fin - inicio > DURACION_MAXIMA:
        raise ErrorValidacion("la reserva no puede durar más de 8 horas")
