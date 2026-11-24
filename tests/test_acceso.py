"""Control de acceso: los servidores A2A y la consola exigen X-API-Key válida."""

import pytest
from fastapi.testclient import TestClient

from src.comun.servidor import crear_app
from src.comun.tarjeta import crear_tarjeta


CLAVE = "clave-de-prueba-123"


def _mensaje(texto="hola"):
    return {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "message/send",
        "params": {
            "message": {
                "kind": "message",
                "messageId": "m1",
                "role": "user",
                "contextId": "c1",
                "parts": [{"kind": "text", "text": texto}],
            }
        },
    }


@pytest.fixture
def cliente(monkeypatch):
    monkeypatch.setenv("CLAVE_API", CLAVE)
    monkeypatch.setenv("URL_PUBLICA", "")

    async def eco(texto, context_id):
        return f"eco: {texto}"

    tarjeta = crear_tarjeta(
        "Agente eco", "Prueba", "http://127.0.0.1:9999",
        [("eco", "Eco", "Repite el mensaje.", "hola")],
    )
    return TestClient(crear_app(tarjeta, eco))


def test_salud_y_ficha_son_publicas(cliente):
    assert cliente.get("/salud").status_code == 200
    assert cliente.get("/.well-known/agent-card.json").status_code == 200


def test_rechaza_mensaje_sin_clave(cliente):
    respuesta = cliente.post("/", json=_mensaje())
    assert respuesta.status_code == 401
    assert "X-API-Key" in respuesta.json()["detail"]


def test_rechaza_mensaje_con_clave_incorrecta(cliente):
    respuesta = cliente.post("/", json=_mensaje(), headers={"X-API-Key": "otra"})
    assert respuesta.status_code == 401
    assert respuesta.json()["detail"] == "Clave de acceso inválida."


def test_acepta_mensaje_con_clave_correcta(cliente):
    respuesta = cliente.post("/", json=_mensaje("hola"), headers={"X-API-Key": CLAVE})
    assert respuesta.status_code == 200
    assert "eco: hola" in respuesta.text


def test_sin_clave_configurada_no_acepta_nada(cliente, monkeypatch):
    monkeypatch.setenv("CLAVE_API", "")
    respuesta = cliente.post("/", json=_mensaje(), headers={"X-API-Key": CLAVE})
    assert respuesta.status_code == 503


def test_consola_exige_clave(monkeypatch):
    monkeypatch.setenv("CLAVE_API", CLAVE)
    from src.portal.app import app

    consola = TestClient(app)
    cuerpo = {"agente": "viajes", "texto": "hola"}
    assert consola.post("/api/mensajes", json=cuerpo).status_code == 401
    assert (
        consola.post("/api/mensajes", json=cuerpo, headers={"X-API-Key": "mala"}).status_code
        == 401
    )


def test_falla_del_agente_sale_como_error_y_no_como_respuesta(monkeypatch):
    """Si el agente falla (modelo, clave, red), el cliente recibe un error JSON-RPC."""
    monkeypatch.setenv("CLAVE_API", CLAVE)
    monkeypatch.setenv("URL_PUBLICA", "")

    async def roto(texto, context_id):
        raise RuntimeError("API key not valid")

    tarjeta = crear_tarjeta(
        "Agente roto", "Prueba", "http://127.0.0.1:9999",
        [("eco", "Eco", "Repite el mensaje.", "hola")],
    )
    servidor = TestClient(crear_app(tarjeta, roto))
    datos = servidor.post("/", json=_mensaje(), headers={"X-API-Key": CLAVE}).json()

    assert "result" not in datos
    assert "No se pudo responder" in datos["error"]["message"]
    assert "clave de Gemini" in datos["error"]["message"]
