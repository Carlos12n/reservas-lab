from datetime import datetime
from pathlib import Path

import pytest

from dominio import ACTIVA, CANCELADA, Reserva
from repositorio import RUTA_DB, Repositorio

INICIO = datetime(2026, 11, 2, 10, 0)
FIN = datetime(2026, 11, 2, 11, 0)


@pytest.fixture
def ruta(tmp_path):
    return tmp_path / "data" / "reservas.db"


def test_ruta_por_defecto_es_data_reservas_db():
    assert RUTA_DB == Path(__file__).parent.parent / "data" / "reservas.db"


def test_crea_la_carpeta_si_no_existe(ruta):
    with Repositorio(ruta):
        pass
    assert ruta.exists()


def test_guardar_devuelve_reserva_activa_con_id(ruta):
    with Repositorio(ruta) as repo:
        reserva = repo.guardar_nueva("MIC-01", "Ana Ficticia", INICIO, FIN)
    assert reserva == Reserva(
        id=reserva.id,
        unidad="MIC-01",
        solicitante="Ana Ficticia",
        inicio=INICIO,
        fin=FIN,
        estado=ACTIVA,
    )


def test_ids_son_unicos(ruta):
    with Repositorio(ruta) as repo:
        a = repo.guardar_nueva("MIC-01", "Ana Ficticia", INICIO, FIN)
        b = repo.guardar_nueva("MIC-02", "Beto Ficticio", INICIO, FIN)
    assert a.id != b.id


def test_obtener_inexistente_devuelve_none(ruta):
    with Repositorio(ruta) as repo:
        assert repo.obtener(999) is None


def test_cambiar_estado_conserva_los_datos(ruta):
    with Repositorio(ruta) as repo:
        original = repo.guardar_nueva("MIC-01", "Ana Ficticia", INICIO, FIN)
        repo.cambiar_estado(original.id, CANCELADA)
        cancelada = repo.obtener(original.id)
    assert cancelada.estado == CANCELADA
    assert (cancelada.id, cancelada.unidad, cancelada.solicitante) == (
        original.id,
        original.unidad,
        original.solicitante,
    )
    assert (cancelada.inicio, cancelada.fin) == (original.inicio, original.fin)


def test_listar_filtra_por_unidad_y_ordena_por_inicio(ruta):
    with Repositorio(ruta) as repo:
        tarde = repo.guardar_nueva(
            "MIC-01", "Ana Ficticia", datetime(2026, 11, 2, 14, 0), datetime(2026, 11, 2, 15, 0)
        )
        temprano = repo.guardar_nueva("MIC-01", "Beto Ficticio", INICIO, FIN)
        otra = repo.guardar_nueva("OSC-01", "Ana Ficticia", INICIO, FIN)
        assert repo.listar() == [temprano, otra, tarde]
        assert repo.listar("MIC-01") == [temprano, tarde]


def test_r9_reservas_persisten_al_reiniciar(ruta):
    with Repositorio(ruta) as repo:
        activa = repo.guardar_nueva("MIC-01", "Ana Ficticia", INICIO, FIN)
        cancelada = repo.guardar_nueva("MIC-02", "Beto Ficticio", INICIO, FIN)
        repo.cambiar_estado(cancelada.id, CANCELADA)

    # Nueva instancia sobre el mismo archivo: simula detener y reiniciar.
    with Repositorio(ruta) as repo:
        assert repo.obtener(activa.id).estado == ACTIVA
        assert repo.obtener(cancelada.id).estado == CANCELADA
        assert len(repo.listar()) == 2


def test_no_existe_operacion_de_borrado(ruta):
    with Repositorio(ruta) as repo:
        assert not any("borrar" in n or "eliminar" in n or "delete" in n for n in dir(repo))
