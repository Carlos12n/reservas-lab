"""Pruebas de la ventana de demostración. Necesitan Tkinter y una pantalla
(real o virtual, por ejemplo `xvfb-run`); si no hay, se omiten."""

import pytest

tkinter = pytest.importorskip("tkinter")

from inventario import cargar_inventario
from repositorio import Repositorio
from servicio import Servicio

DIA = "2026-11-02"


@pytest.fixture
def app(tmp_path):
    from gui_demo import App

    try:
        raiz = tkinter.Tk()
    except tkinter.TclError:
        pytest.skip("no hay pantalla disponible")
    raiz.withdraw()
    with Repositorio(tmp_path / "reservas.db") as repo:
        yield App(raiz, Servicio(repo, cargar_inventario()))
    raiz.destroy()


def completar(app, unidad="MIC-01", solicitante="Ana Ficticia", inicio="10:00", fin="11:00"):
    app.unidad.set(unidad)
    app.solicitante.set(solicitante)
    app.inicio.set(f"{DIA} {inicio}")
    app.fin.set(f"{DIA} {fin}")


def filas(app):
    return [app.tabla.item(i, "values") for i in app.tabla.get_children()]


def test_ofrece_las_5_unidades(app):
    assert list(app.selector_unidad["values"]) == [
        "MIC-01", "MIC-02", "OSC-01", "MUL-01", "FUE-01",
    ]


def test_reservar_agrega_fila_activa(app):
    completar(app)
    app.reservar()
    assert "Reserva 1 creada" in app.mensaje.get()
    assert filas(app) == [
        ("1", "MIC-01", f"{DIA} 10:00", f"{DIA} 11:00", "Ana Ficticia", "activa")
    ]


def test_superposicion_muestra_error_y_no_agrega(app):
    completar(app)
    app.reservar()
    completar(app, inicio="10:30", fin="11:30")
    app.reservar()
    assert app.mensaje.get().startswith("Error:")
    assert len(filas(app)) == 1


def test_turno_consecutivo_se_acepta(app):
    # Caso obligatorio de AGENTS.md: 10:00-11:00 contra 11:00-12:00.
    completar(app)
    app.reservar()
    completar(app, inicio="11:00", fin="12:00")
    app.reservar()
    assert len(filas(app)) == 2


def test_entrada_invalida_muestra_error(app):
    completar(app, solicitante="   ")
    app.reservar()
    assert "solicitante" in app.mensaje.get()


def test_consultar_disponibilidad(app):
    completar(app)
    app.reservar()
    completar(app, inicio="10:30", fin="11:30")
    app.consultar()
    assert "no disponible" in app.mensaje.get()
    completar(app, inicio="11:00", fin="12:00")
    app.consultar()
    assert "MIC-01 disponible" in app.mensaje.get()


def test_cancelar_seleccionada_conserva_y_libera(app):
    completar(app)
    app.reservar()
    app.tabla.selection_set(app.tabla.get_children()[0])
    app.cancelar_seleccionada()
    assert "Reserva 1 cancelada" in app.mensaje.get()
    assert filas(app)[0][-1] == "cancelada"
    app.consultar()
    assert "disponible" in app.mensaje.get()


def test_cancelar_sin_seleccion_avisa(app):
    app.cancelar_seleccionada()
    assert "Seleccioná una reserva" in app.mensaje.get()
