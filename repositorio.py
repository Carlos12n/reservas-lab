"""Persistencia de reservas en SQLite. Las reservas nunca se borran."""

import sqlite3
from datetime import datetime
from pathlib import Path

from dominio import ACTIVA, CANCELADA, FORMATO_FECHA_HORA, Reserva

RUTA_DB = Path(__file__).parent / "data" / "reservas.db"

_ESQUEMA = f"""
CREATE TABLE IF NOT EXISTS reservas (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    unidad      TEXT NOT NULL,
    solicitante TEXT NOT NULL,
    inicio      TEXT NOT NULL,
    fin         TEXT NOT NULL,
    estado      TEXT NOT NULL CHECK (estado IN ('{ACTIVA}', '{CANCELADA}'))
)
"""


class Repositorio:
    def __init__(self, ruta=RUTA_DB):
        ruta = Path(ruta)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        self._conexion = sqlite3.connect(ruta)
        self._conexion.execute(_ESQUEMA)
        self._conexion.commit()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.cerrar()

    def cerrar(self) -> None:
        self._conexion.close()

    def guardar_nueva(
        self, unidad: str, solicitante: str, inicio: datetime, fin: datetime
    ) -> Reserva:
        with self._conexion:
            cursor = self._conexion.execute(
                "INSERT INTO reservas (unidad, solicitante, inicio, fin, estado)"
                " VALUES (?, ?, ?, ?, ?)",
                (unidad, solicitante, _a_texto(inicio), _a_texto(fin), ACTIVA),
            )
        return Reserva(cursor.lastrowid, unidad, solicitante, inicio, fin, ACTIVA)

    def obtener(self, id_reserva: int) -> Reserva | None:
        fila = self._conexion.execute(
            "SELECT id, unidad, solicitante, inicio, fin, estado"
            " FROM reservas WHERE id = ?",
            (id_reserva,),
        ).fetchone()
        return _a_reserva(fila) if fila else None

    def listar(self, unidad: str | None = None) -> list[Reserva]:
        consulta = "SELECT id, unidad, solicitante, inicio, fin, estado FROM reservas"
        parametros = ()
        if unidad is not None:
            consulta += " WHERE unidad = ?"
            parametros = (unidad,)
        consulta += " ORDER BY inicio, id"
        return [_a_reserva(f) for f in self._conexion.execute(consulta, parametros)]

    def cambiar_estado(self, id_reserva: int, estado: str) -> None:
        with self._conexion:
            self._conexion.execute(
                "UPDATE reservas SET estado = ? WHERE id = ?", (estado, id_reserva)
            )


def _a_texto(momento: datetime) -> str:
    return momento.strftime(FORMATO_FECHA_HORA)


def _a_reserva(fila) -> Reserva:
    id_reserva, unidad, solicitante, inicio, fin, estado = fila
    return Reserva(
        id=id_reserva,
        unidad=unidad,
        solicitante=solicitante,
        inicio=datetime.strptime(inicio, FORMATO_FECHA_HORA),
        fin=datetime.strptime(fin, FORMATO_FECHA_HORA),
        estado=estado,
    )
