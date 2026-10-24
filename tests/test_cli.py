import subprocess
import sys
from pathlib import Path

import pytest

from cli import main

RAIZ = Path(__file__).parent.parent
DIA = "2026-11-02"


@pytest.fixture
def db(tmp_path):
    return str(tmp_path / "reservas.db")


def ejecutar(capsys, db, *args):
    codigo = main(["--db", db, *args])
    salida = capsys.readouterr()
    return codigo, salida.out, salida.err


def reservar(capsys, db, unidad="MIC-01", inicio="10:00", fin="11:00", solicitante="Ana Ficticia"):
    return ejecutar(
        capsys, db, "reservar",
        "--unidad", unidad, "--solicitante", solicitante,
        "--inicio", f"{DIA} {inicio}", "--fin", f"{DIA} {fin}",
    )


def test_r1_unidades_muestra_las_5(capsys, db):
    codigo, out, _ = ejecutar(capsys, db, "unidades")
    assert codigo == 0
    for id_unidad in ["MIC-01", "MIC-02", "OSC-01", "MUL-01", "FUE-01"]:
        assert id_unidad in out
    assert "Microscopio digital" in out


def test_r2_reservar_muestra_id_y_estado(capsys, db):
    codigo, out, _ = reservar(capsys, db)
    assert codigo == 0
    assert "Reserva 1 creada" in out
    assert "activa" in out


def test_r3_superposicion_se_rechaza_con_error(capsys, db):
    reservar(capsys, db)
    codigo, out, err = reservar(capsys, db, inicio="10:30", fin="11:30")
    assert codigo == 1
    assert out == ""
    assert "Error:" in err and "MIC-01 ya está reservada" in err


def test_r4_turno_consecutivo_se_acepta(capsys, db):
    reservar(capsys, db)
    codigo, out, _ = reservar(capsys, db, inicio="11:00", fin="12:00")
    assert codigo == 0 and "Reserva 2 creada" in out


def test_r5_otra_unidad_mismo_horario_se_acepta(capsys, db):
    reservar(capsys, db)
    codigo, _, _ = reservar(capsys, db, unidad="MIC-02")
    assert codigo == 0


@pytest.mark.parametrize(
    "cambios, mensaje",
    [
        ({"unidad": "XYZ-99"}, "unidad desconocida"),
        ({"solicitante": "   "}, "solicitante"),
        ({"inicio": "25:00"}, "fecha u hora inválida"),
        ({"inicio": "11:00"}, "inicio debe ser anterior"),
    ],
)
def test_r6_entradas_invalidas_dan_error_claro(capsys, db, cambios, mensaje):
    codigo, _, err = reservar(capsys, db, **cambios)
    assert codigo == 1
    assert mensaje in err


def test_r7_cancelar_conserva_y_libera(capsys, db):
    reservar(capsys, db)
    codigo, out, _ = ejecutar(capsys, db, "cancelar", "1")
    assert codigo == 0 and "Reserva 1 cancelada" in out

    _, out, _ = ejecutar(capsys, db, "listar")
    assert "#1" in out and "Ana Ficticia" in out and "cancelada" in out

    codigo, _, _ = reservar(capsys, db)
    assert codigo == 0


def test_cancelar_dos_veces_da_error(capsys, db):
    reservar(capsys, db)
    ejecutar(capsys, db, "cancelar", "1")
    codigo, _, err = ejecutar(capsys, db, "cancelar", "1")
    assert codigo == 1 and "ya está cancelada" in err


def test_r8_disponibilidad(capsys, db):
    reservar(capsys, db)
    consulta = ["disponibilidad", "--unidad", "MIC-01"]

    codigo, out, _ = ejecutar(capsys, db, *consulta, "--inicio", f"{DIA} 10:30", "--fin", f"{DIA} 11:30")
    assert codigo == 0 and "no disponible" in out and "#1" in out

    _, out, _ = ejecutar(capsys, db, *consulta, "--inicio", f"{DIA} 11:00", "--fin", f"{DIA} 12:00")
    assert "MIC-01 disponible" in out


def test_listar_filtra_por_unidad(capsys, db):
    reservar(capsys, db)
    reservar(capsys, db, unidad="OSC-01", solicitante="Beto Ficticio")
    _, out, _ = ejecutar(capsys, db, "listar", "--unidad", "OSC-01")
    assert "Beto Ficticio" in out and "Ana Ficticia" not in out


def test_listar_sin_reservas(capsys, db):
    _, out, _ = ejecutar(capsys, db, "listar")
    assert "No hay reservas" in out


def test_r9_persiste_entre_procesos_distintos(db):
    # Cada comando es un proceso nuevo: detener y reiniciar la aplicación.
    def cli(*args):
        return subprocess.run(
            [sys.executable, str(RAIZ / "cli.py"), "--db", db, *args],
            capture_output=True, text=True, check=True,
        ).stdout

    cli("reservar", "--unidad", "MIC-01", "--solicitante", "Ana Ficticia",
        "--inicio", f"{DIA} 10:00", "--fin", f"{DIA} 11:00")
    cli("reservar", "--unidad", "OSC-01", "--solicitante", "Beto Ficticio",
        "--inicio", f"{DIA} 10:00", "--fin", f"{DIA} 11:00")
    cli("cancelar", "2")

    salida = cli("listar")
    assert "#1" in salida and "activa" in salida
    assert "#2" in salida and "cancelada" in salida
