"""Casos de uso: reservar, cancelar y consultar disponibilidad."""

from dominio import (
    CANCELADA,
    Intervalo,
    Reserva,
    conflictos,
    parsear_fecha_hora,
    validar_intervalo,
    validar_solicitante,
    validar_unidad,
)
from inventario import Unidad
from repositorio import Repositorio


class ErrorReserva(Exception):
    """Operación imposible por el estado actual (superposición, cancelación)."""


class Servicio:
    def __init__(self, repositorio: Repositorio, unidades: list[Unidad]):
        self._repo = repositorio
        self._unidades = unidades
        self._ids = {u.id for u in unidades}

    def unidades(self) -> list[Unidad]:
        return list(self._unidades)

    def listar(self, unidad: str | None = None) -> list[Reserva]:
        return self._repo.listar(unidad)

    def consultar_disponibilidad(self, unidad: str, inicio: str, fin: str) -> list[Reserva]:
        """Reservas que ocupan el intervalo; lista vacía si está disponible."""
        return self._bloqueantes(self._intervalo(unidad, inicio, fin))

    def reservar(self, unidad: str, solicitante: str, inicio: str, fin: str) -> Reserva:
        intervalo = self._intervalo(unidad, inicio, fin)
        solicitante = validar_solicitante(solicitante)
        bloqueantes = self._bloqueantes(intervalo)
        if bloqueantes:
            ids = ", ".join(str(r.id) for r in bloqueantes)
            raise ErrorReserva(
                f"{intervalo.unidad} ya está reservada en ese horario (reserva {ids})"
            )
        return self._repo.guardar_nueva(
            intervalo.unidad, solicitante, intervalo.inicio, intervalo.fin
        )

    def cancelar(self, id_reserva: int) -> Reserva:
        reserva = self._repo.obtener(id_reserva)
        if reserva is None:
            raise ErrorReserva(f"la reserva {id_reserva} no existe")
        if reserva.estado == CANCELADA:
            raise ErrorReserva(f"la reserva {id_reserva} ya está cancelada")
        self._repo.cambiar_estado(id_reserva, CANCELADA)
        return self._repo.obtener(id_reserva)

    def _intervalo(self, unidad: str, inicio: str, fin: str) -> Intervalo:
        validar_unidad(unidad, self._ids)
        momento_inicio = parsear_fecha_hora(inicio)
        momento_fin = parsear_fecha_hora(fin)
        validar_intervalo(momento_inicio, momento_fin)
        return Intervalo(unidad, momento_inicio, momento_fin)

    def _bloqueantes(self, intervalo: Intervalo) -> list[Reserva]:
        # Reservar y consultar pasan por aquí: misma regla de dominio (R8).
        return conflictos(intervalo, self._repo.listar(intervalo.unidad))
