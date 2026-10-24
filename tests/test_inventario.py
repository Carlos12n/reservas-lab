import json

import pytest

from dominio import ErrorValidacion, validar_unidad
from inventario import Unidad, cargar_inventario


def test_r1_carga_las_5_unidades():
    unidades = cargar_inventario()
    assert [u.id for u in unidades] == [
        "MIC-01",
        "MIC-02",
        "OSC-01",
        "MUL-01",
        "FUE-01",
    ]


def test_r1_cada_unidad_tiene_su_equipo():
    unidades = cargar_inventario()
    assert unidades[0] == Unidad(id="MIC-01", equipo="Microscopio digital")
    assert unidades[4] == Unidad(id="FUE-01", equipo="Fuente de alimentación")


def test_ids_del_inventario_sirven_para_validar_unidad():
    ids = {u.id for u in cargar_inventario()}
    assert validar_unidad("OSC-01", ids) == "OSC-01"
    with pytest.raises(ErrorValidacion, match="XYZ-99"):
        validar_unidad("XYZ-99", ids)


def test_carga_desde_otra_ruta(tmp_path):
    ruta = tmp_path / "otro.json"
    ruta.write_text(
        json.dumps([{"id": "TST-01", "equipo": "Equipo de prueba"}]),
        encoding="utf-8",
    )
    assert cargar_inventario(ruta) == [Unidad(id="TST-01", equipo="Equipo de prueba")]
