"""Interfaz de consola del sistema de reservas."""

import argparse
import sys

from dominio import FORMATO_FECHA_HORA, ErrorValidacion, Reserva
from inventario import cargar_inventario
from repositorio import RUTA_DB, Repositorio
from servicio import ErrorReserva, Servicio


def formatear(reserva: Reserva) -> str:
    inicio = reserva.inicio.strftime(FORMATO_FECHA_HORA)
    fin = reserva.fin.strftime(FORMATO_FECHA_HORA)
    return (
        f"#{reserva.id}  {reserva.unidad}  {inicio} -> {fin}  "
        f"{reserva.solicitante}  [{reserva.estado}]"
    )


def crear_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cli.py", description="Reservas de equipos de laboratorio."
    )
    parser.add_argument(
        "--db", default=str(RUTA_DB), help=f"archivo SQLite (por defecto {RUTA_DB})"
    )
    comandos = parser.add_subparsers(dest="comando", required=True)

    comandos.add_parser("unidades", help="lista las unidades del inventario")

    listar = comandos.add_parser("listar", help="lista reservas activas y canceladas")
    listar.add_argument("--unidad")

    fecha = "fecha y hora 'YYYY-MM-DD HH:MM'"
    disponibilidad = comandos.add_parser(
        "disponibilidad", help="consulta si una unidad está libre en un intervalo"
    )
    disponibilidad.add_argument("--unidad", required=True)
    disponibilidad.add_argument("--inicio", required=True, help=fecha)
    disponibilidad.add_argument("--fin", required=True, help=fecha)

    reservar = comandos.add_parser("reservar", help="crea una reserva")
    reservar.add_argument("--unidad", required=True)
    reservar.add_argument("--solicitante", required=True)
    reservar.add_argument("--inicio", required=True, help=fecha)
    reservar.add_argument("--fin", required=True, help=fecha)

    cancelar = comandos.add_parser("cancelar", help="cancela una reserva por ID")
    cancelar.add_argument("id", type=int)

    return parser


def ejecutar(servicio: Servicio, args) -> None:
    if args.comando == "unidades":
        for unidad in servicio.unidades():
            print(f"{unidad.id}  {unidad.equipo}")

    elif args.comando == "listar":
        reservas = servicio.listar(args.unidad)
        if not reservas:
            print("No hay reservas.")
        for reserva in reservas:
            print(formatear(reserva))

    elif args.comando == "disponibilidad":
        bloqueantes = servicio.consultar_disponibilidad(args.unidad, args.inicio, args.fin)
        if not bloqueantes:
            print(f"{args.unidad} disponible de {args.inicio} a {args.fin}.")
        else:
            print(f"{args.unidad} no disponible de {args.inicio} a {args.fin}. Ocupada por:")
            for reserva in bloqueantes:
                print(f"  {formatear(reserva)}")

    elif args.comando == "reservar":
        reserva = servicio.reservar(args.unidad, args.solicitante, args.inicio, args.fin)
        print(f"Reserva {reserva.id} creada: {formatear(reserva)}")

    elif args.comando == "cancelar":
        reserva = servicio.cancelar(args.id)
        print(f"Reserva {reserva.id} cancelada: {formatear(reserva)}")


def main(argv=None) -> int:
    args = crear_parser().parse_args(argv)
    try:
        with Repositorio(args.db) as repo:
            ejecutar(Servicio(repo, cargar_inventario()), args)
    except (ErrorValidacion, ErrorReserva) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
