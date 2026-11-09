"""Pruebas de la ficha (Agent Card) que arma cada agente."""

import pytest

from src.comun.tarjeta import crear_tarjeta


def test_arma_ficha_con_skills():
    tarjeta = crear_tarjeta(
        "Agente X",
        "Prueba",
        "http://127.0.0.1:8000",
        [("eco", "Eco", "Repite el mensaje.", "hola")],
    )

    assert tarjeta.name == "Agente X"
    assert tarjeta.supported_interfaces[0].url == "http://127.0.0.1:8000"
    assert [skill.id for skill in tarjeta.skills] == ["eco"]


def test_rechaza_ficha_sin_skills():
    """La spec A2A exige al menos un skill: mejor fallar al crear el agente."""
    with pytest.raises(ValueError) as error:
        crear_tarjeta("Agente X", "Prueba", "http://127.0.0.1:8000", [])

    assert "skill" in str(error.value)
