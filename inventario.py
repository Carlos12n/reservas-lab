"""Carga del inventario precargado de unidades."""

import json
from dataclasses import dataclass
from pathlib import Path

RUTA_INVENTARIO = Path(__file__).parent / "inventario.json"


@dataclass(frozen=True)
class Unidad:
    id: str
    equipo: str


def cargar_inventario(ruta=RUTA_INVENTARIO) -> list[Unidad]:
    with open(ruta, encoding="utf-8") as archivo:
        datos = json.load(archivo)
    return [Unidad(id=item["id"], equipo=item["equipo"]) for item in datos]
