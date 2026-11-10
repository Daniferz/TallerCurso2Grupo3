"""Pruebas de las herramientas y la publicación A2A del agente de Cristian."""

import importlib
import sys

from src.agente_cristian.tools import horario_atencion, listado_sitios_turisticos
from src.comun.registro import CATALOGO


def test_listado_acepta_ciudad_con_tilde_y_entrega_datos_referenciales():
    sitios = listado_sitios_turisticos.invoke(
        {"ciudad": "Bogotá", "fecha": "miércoles"}
    )

    assert len(sitios) == 3
    assert sitios[0]["nombre"] == "Museo del Oro"
    assert sitios[0]["ciudad"] == "Bogotá"
    assert sitios[0]["fecha"] == "miércoles"
    assert sitios[0]["precio_referencial"]


def test_listado_normaliza_cuzco_y_ciudad_sin_datos_en_una_linea():
    sitios = listado_sitios_turisticos.invoke({"ciudad": "Cuzco", "fecha": "sábado"})
    desconocidos = listado_sitios_turisticos.invoke(
        {"ciudad": "Valparaíso", "fecha": "sábado"}
    )

    assert sitios[0]["nombre"] == "Sacsayhuamán"
    assert desconocidos == "No tengo sitios turísticos registrados para Valparaíso."
    assert "\n" not in desconocidos


def test_horario_distingue_dia_cerrado_y_dia_sin_registro():
    cerrado = horario_atencion.invoke(
        {"nombre_sitio": "Museo Botero", "dia": "lunes"}
    )
    dia_invalido = horario_atencion.invoke(
        {"nombre_sitio": "Museo Botero", "dia": "feriado"}
    )

    assert cerrado == "No tengo horario registrado para Museo Botero el lunes."
    assert dia_invalido == "No tengo horario registrado para Museo Botero el día indicado."


def test_cristian_esta_registrado_como_agente_local():
    agente = CATALOGO["cristian"]

    assert agente.paquete == "src.agente_cristian"
    assert agente.url == agente.url.rstrip("/")
    assert "lugares para visitar" in agente.descripcion


def test_agent_card_de_cristian_publica_url_publica(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "clave-de-prueba")
    monkeypatch.setenv("URL_PUBLICA", "https://tunel-cristian.trycloudflare.com/")
    sys.modules.pop("src.agente_cristian.server", None)

    servidor = importlib.import_module("src.agente_cristian.server")

    assert (
        servidor.tarjeta.supported_interfaces[0].url
        == "https://tunel-cristian.trycloudflare.com"
    )
