from datetime import datetime

import pytest

from dominio import (
    ACTIVA,
    CANCELADA,
    ErrorValidacion,
    Intervalo,
    Reserva,
    conflictos,
    parsear_fecha_hora,
    se_superponen,
    validar_intervalo,
    validar_solicitante,
    validar_unidad,
)

UNIDADES = {"MIC-01", "MIC-02", "OSC-01", "MUL-01", "FUE-01"}


def dt(texto):
    return datetime.strptime(texto, "%Y-%m-%d %H:%M")


def reserva(unidad="MIC-01", inicio="10:00", fin="11:00", estado=ACTIVA):
    return Reserva(
        id=1,
        unidad=unidad,
        solicitante="Ana Ficticia",
        inicio=dt(f"2026-11-02 {inicio}"),
        fin=dt(f"2026-11-02 {fin}"),
        estado=estado,
    )


def intervalo(unidad="MIC-01", inicio="10:00", fin="11:00"):
    return Intervalo(
        unidad=unidad,
        inicio=dt(f"2026-11-02 {inicio}"),
        fin=dt(f"2026-11-02 {fin}"),
    )


# --- Superposición (R3, R4, R5, R8) ---

def test_r3_superposicion_parcial_se_detecta():
    assert se_superponen(intervalo(inicio="10:30", fin="11:30"), reserva())


def test_r4_turnos_consecutivos_no_se_superponen():
    # Caso obligatorio de AGENTS.md: 10:00-11:00 contra 11:00-12:00.
    assert not se_superponen(intervalo(inicio="11:00", fin="12:00"), reserva())


def test_r4_turno_consecutivo_anterior_no_se_superpone():
    assert not se_superponen(intervalo(inicio="09:00", fin="10:00"), reserva())


def test_r5_unidades_distintas_no_se_superponen():
    assert not se_superponen(intervalo(unidad="MIC-02"), reserva())


def test_mismo_intervalo_exacto_se_superpone():
    assert se_superponen(intervalo(), reserva())


def test_intervalo_que_contiene_a_otro_se_superpone():
    assert se_superponen(intervalo(inicio="09:00", fin="12:00"), reserva())


def test_reserva_cancelada_no_bloquea():
    assert not se_superponen(intervalo(), reserva(estado=CANCELADA))


def test_conflictos_usa_la_regla_de_superposicion():
    existentes = [
        reserva(inicio="10:00", fin="11:00"),
        reserva(inicio="10:00", fin="11:00", estado=CANCELADA),
        reserva(unidad="MIC-02", inicio="10:00", fin="11:00"),
        reserva(inicio="12:00", fin="13:00"),
    ]
    assert conflictos(intervalo(inicio="10:30", fin="11:30"), existentes) == [
        existentes[0]
    ]
    # Consecutivo con ambas reservas activas de MIC-01: sin conflictos.
    assert conflictos(intervalo(inicio="11:00", fin="12:00"), existentes) == []


# --- Validaciones (R6) ---

def test_parsear_fecha_hora_valida():
    assert parsear_fecha_hora("2026-11-02 10:00") == datetime(2026, 11, 2, 10, 0)


@pytest.mark.parametrize(
    "texto",
    [
        "",
        "2026-11-02",
        "2026-11-02 25:00",
        "2026-02-30 10:00",
        "2026-11-02T10:00",
        "2026-1-2 10:00",
        "02/11/2026 10:00",
        "mañana",
    ],
)
def test_parsear_fecha_hora_invalida(texto):
    with pytest.raises(ErrorValidacion, match="fecha"):
        parsear_fecha_hora(texto)


def test_solicitante_valido_se_recorta():
    assert validar_solicitante("  Ana Ficticia ") == "Ana Ficticia"


@pytest.mark.parametrize("texto", ["", "   ", "\t\n"])
def test_solicitante_vacio_o_espacios_se_rechaza(texto):
    with pytest.raises(ErrorValidacion, match="solicitante"):
        validar_solicitante(texto)


def test_unidad_conocida_se_acepta():
    assert validar_unidad("MIC-01", UNIDADES) == "MIC-01"


def test_unidad_desconocida_se_rechaza():
    with pytest.raises(ErrorValidacion, match="XYZ-99"):
        validar_unidad("XYZ-99", UNIDADES)


def test_intervalo_valido():
    validar_intervalo(dt("2026-11-02 10:00"), dt("2026-11-02 11:00"))


def test_inicio_igual_al_fin_se_rechaza():
    with pytest.raises(ErrorValidacion, match="inicio"):
        validar_intervalo(dt("2026-11-02 10:00"), dt("2026-11-02 10:00"))


def test_inicio_posterior_al_fin_se_rechaza():
    with pytest.raises(ErrorValidacion, match="inicio"):
        validar_intervalo(dt("2026-11-02 11:00"), dt("2026-11-02 10:00"))


def test_duracion_de_8_horas_se_acepta():
    validar_intervalo(dt("2026-11-02 08:00"), dt("2026-11-02 16:00"))


def test_duracion_mayor_a_8_horas_se_rechaza():
    with pytest.raises(ErrorValidacion, match="8 horas"):
        validar_intervalo(dt("2026-11-02 08:00"), dt("2026-11-02 16:01"))
