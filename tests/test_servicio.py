import pytest

import dominio
import servicio as modulo_servicio
from dominio import ACTIVA, CANCELADA, ErrorValidacion
from inventario import cargar_inventario
from repositorio import Repositorio
from servicio import ErrorReserva, Servicio

DIA = "2026-11-02"


@pytest.fixture
def ruta(tmp_path):
    return tmp_path / "reservas.db"


@pytest.fixture
def servicio(ruta):
    with Repositorio(ruta) as repo:
        yield Servicio(repo, cargar_inventario())


def reservar(servicio, unidad="MIC-01", inicio="10:00", fin="11:00", solicitante="Ana Ficticia"):
    return servicio.reservar(unidad, solicitante, f"{DIA} {inicio}", f"{DIA} {fin}")


def disponible(servicio, unidad="MIC-01", inicio="10:00", fin="11:00"):
    return servicio.consultar_disponibilidad(unidad, f"{DIA} {inicio}", f"{DIA} {fin}") == []


# --- R1 ---

def test_r1_lista_las_5_unidades(servicio):
    assert len(servicio.unidades()) == 5


# --- R2 ---

def test_r2_reserva_valida_queda_activa_con_id_unico(servicio):
    a = reservar(servicio)
    b = reservar(servicio, unidad="MIC-02")
    assert a.estado == ACTIVA and b.estado == ACTIVA
    assert a.id != b.id
    assert a.solicitante == "Ana Ficticia"


def test_r2_solicitante_se_guarda_sin_espacios_extremos(servicio):
    assert reservar(servicio, solicitante="  Ana Ficticia  ").solicitante == "Ana Ficticia"


# --- R3, R4, R5 ---

def test_r3_superposicion_en_la_misma_unidad_se_rechaza(servicio):
    reservar(servicio)
    with pytest.raises(ErrorReserva, match="MIC-01"):
        reservar(servicio, inicio="10:30", fin="11:30")


def test_r4_turno_consecutivo_se_acepta(servicio):
    # Caso obligatorio de AGENTS.md: 10:00-11:00 contra 11:00-12:00.
    reservar(servicio)
    assert reservar(servicio, inicio="11:00", fin="12:00").estado == ACTIVA


def test_r5_otra_unidad_en_el_mismo_horario_se_acepta(servicio):
    reservar(servicio)
    assert reservar(servicio, unidad="MIC-02").estado == ACTIVA


def test_rechazo_no_guarda_nada(servicio):
    reservar(servicio)
    with pytest.raises(ErrorReserva):
        reservar(servicio, inicio="10:30", fin="11:30")
    assert len(servicio.listar()) == 1


# --- R6 ---

@pytest.mark.parametrize(
    "unidad, solicitante, inicio, fin, mensaje",
    [
        ("XYZ-99", "Ana Ficticia", f"{DIA} 10:00", f"{DIA} 11:00", "unidad desconocida"),
        ("MIC-01", "", f"{DIA} 10:00", f"{DIA} 11:00", "solicitante"),
        ("MIC-01", "   ", f"{DIA} 10:00", f"{DIA} 11:00", "solicitante"),
        ("MIC-01", "Ana Ficticia", "2026-13-01 10:00", f"{DIA} 11:00", "fecha"),
        ("MIC-01", "Ana Ficticia", f"{DIA} 10:00", f"{DIA} 24:00", "fecha"),
        ("MIC-01", "Ana Ficticia", f"{DIA} 11:00", f"{DIA} 11:00", "inicio"),
        ("MIC-01", "Ana Ficticia", f"{DIA} 12:00", f"{DIA} 11:00", "inicio"),
        ("MIC-01", "Ana Ficticia", f"{DIA} 08:00", f"{DIA} 17:00", "8 horas"),
    ],
)
def test_r6_entradas_invalidas_se_rechazan(servicio, unidad, solicitante, inicio, fin, mensaje):
    with pytest.raises(ErrorValidacion, match=mensaje):
        servicio.reservar(unidad, solicitante, inicio, fin)
    assert servicio.listar() == []


def test_r6_disponibilidad_valida_las_entradas(servicio):
    with pytest.raises(ErrorValidacion, match="unidad desconocida"):
        servicio.consultar_disponibilidad("XYZ-99", f"{DIA} 10:00", f"{DIA} 11:00")
    with pytest.raises(ErrorValidacion, match="inicio"):
        servicio.consultar_disponibilidad("MIC-01", f"{DIA} 11:00", f"{DIA} 10:00")


# --- R7 ---

def test_r7_cancelar_conserva_el_registro(servicio):
    original = reservar(servicio)
    cancelada = servicio.cancelar(original.id)
    assert cancelada.estado == CANCELADA
    assert cancelada == dominio.Reserva(
        original.id, original.unidad, original.solicitante, original.inicio, original.fin, CANCELADA
    )
    assert servicio.listar() == [cancelada]


def test_r7_cancelar_libera_el_intervalo(servicio):
    original = reservar(servicio)
    servicio.cancelar(original.id)
    assert disponible(servicio)
    assert reservar(servicio).estado == ACTIVA


def test_cancelar_dos_veces_da_error_explicito(servicio):
    original = reservar(servicio)
    servicio.cancelar(original.id)
    with pytest.raises(ErrorReserva, match="ya está cancelada"):
        servicio.cancelar(original.id)


def test_cancelar_inexistente_da_error(servicio):
    with pytest.raises(ErrorReserva, match="no existe"):
        servicio.cancelar(999)


# --- R8 ---

def test_r8_disponibilidad_coincide_con_reservar(servicio):
    reservar(servicio)
    assert not disponible(servicio, inicio="10:30", fin="11:30")
    assert disponible(servicio, inicio="11:00", fin="12:00")
    assert disponible(servicio, unidad="MIC-02")


def test_r8_disponibilidad_devuelve_las_reservas_que_bloquean(servicio):
    bloqueante = reservar(servicio)
    assert servicio.consultar_disponibilidad("MIC-01", f"{DIA} 10:30", f"{DIA} 11:30") == [
        bloqueante
    ]


def test_r8_reservar_y_consultar_usan_la_misma_funcion(servicio, monkeypatch):
    llamadas = []

    def espia(nuevo, existentes):
        llamadas.append(nuevo)
        return dominio.conflictos(nuevo, existentes)

    monkeypatch.setattr(modulo_servicio, "conflictos", espia)
    servicio.consultar_disponibilidad("MIC-01", f"{DIA} 10:00", f"{DIA} 11:00")
    reservar(servicio)
    assert len(llamadas) == 2


# --- R9 ---

def test_r9_reservas_y_estados_persisten_al_reiniciar(ruta):
    with Repositorio(ruta) as repo:
        s = Servicio(repo, cargar_inventario())
        activa = reservar(s)
        cancelada = reservar(s, unidad="OSC-01")
        s.cancelar(cancelada.id)

    with Repositorio(ruta) as repo:
        s = Servicio(repo, cargar_inventario())
        estados = {r.id: r.estado for r in s.listar()}
        assert estados == {activa.id: ACTIVA, cancelada.id: CANCELADA}
        # La activa sigue bloqueando y la cancelada no, tras reiniciar.
        with pytest.raises(ErrorReserva):
            reservar(s)
        assert reservar(s, unidad="OSC-01").estado == ACTIVA
