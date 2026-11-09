"""Pruebas de la ficha (Agent Card) que arma cada agente."""

import pytest

from src.comun.tarjeta import crear_tarjeta


def test_arma_ficha_con_skills(monkeypatch):
    monkeypatch.setenv("URL_PUBLICA", "")
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


def test_url_publica_reemplaza_la_local_en_la_ficha(monkeypatch):
    monkeypatch.setenv("URL_PUBLICA", "https://azul-rio-123.trycloudflare.com/")
    tarjeta = crear_tarjeta(
        "Agente X",
        "Prueba",
        "http://127.0.0.1:8003",
        [("eco", "Eco", "Repite el mensaje.", "hola")],
    )

    assert tarjeta.supported_interfaces[0].url == "https://azul-rio-123.trycloudflare.com"


def test_url_local_se_conserva_si_url_publica_esta_vacia(monkeypatch):
    monkeypatch.setenv("URL_PUBLICA", "")
    tarjeta = crear_tarjeta(
        "Agente X",
        "Prueba",
        "http://127.0.0.1:8003/",
        [("eco", "Eco", "Repite el mensaje.", "hola")],
    )

    assert tarjeta.supported_interfaces[0].url == "http://127.0.0.1:8003"


def test_url_publica_no_reemplaza_la_url_del_agente_base(monkeypatch):
    monkeypatch.setenv("URL_PUBLICA", "https://tunnel-de-otro-agente.trycloudflare.com")
    tarjeta = crear_tarjeta(
        "Agente de viajes",
        "Busca vuelos.",
        "http://127.0.0.1:8000",
        [("vuelos", "Buscar vuelos", "Encuentra vuelos.", "Vuelo a Lima")],
        usar_url_publica=False,
    )

    assert tarjeta.supported_interfaces[0].url == "http://127.0.0.1:8000"
