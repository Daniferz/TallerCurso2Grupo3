"""POST /chat del coordinador: clave propia, texto vacío y fallas como error."""

import pytest
from fastapi.testclient import TestClient


CLAVE = "clave-coordinador-de-prueba"


@pytest.fixture
def servidor(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "clave-de-prueba")
    monkeypatch.setenv("CLAVE_COORDINADOR", CLAVE)
    from src.coordinador import server

    llamadas = []

    async def responder(texto, conversacion_id):
        llamadas.append((texto, conversacion_id))
        return f"[Agente de prueba] eco: {texto}"

    async def agente_elegido(conversacion_id):
        return "Agente de prueba"

    monkeypatch.setattr(server, "responder", responder)
    monkeypatch.setattr(server, "_agente_elegido", agente_elegido)
    # Sin "with": no corre el arranque, así no se buscan agentes reales.
    return TestClient(server.app), llamadas, server


def test_chat_sin_clave_es_401(servidor):
    cliente, llamadas, _ = servidor
    respuesta = cliente.post("/chat", json={"texto": "hola", "conversacion_id": "1"})
    assert respuesta.status_code == 401
    assert llamadas == []


def test_chat_con_clave_de_otro_agente_es_401(servidor, monkeypatch):
    cliente, llamadas, _ = servidor
    monkeypatch.setenv("CLAVE_PATO", "clave-de-pato")
    respuesta = cliente.post(
        "/chat", json={"texto": "hola"}, headers={"X-API-Key": "clave-de-pato"}
    )
    assert respuesta.status_code == 401
    assert llamadas == []


def test_chat_con_clave_responde_y_usa_la_conversacion(servidor):
    cliente, llamadas, _ = servidor
    respuesta = cliente.post(
        "/chat",
        json={"texto": "  rutina de pecho  ", "conversacion_id": "12345"},
        headers={"X-API-Key": CLAVE},
    )
    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "respuesta": "[Agente de prueba] eco: rutina de pecho",
        "conversacion_id": "12345",
        "agente": "Agente de prueba",
    }
    assert llamadas == [("rutina de pecho", "12345")]


def test_chat_texto_vacio_es_422_con_mensaje_claro(servidor):
    cliente, llamadas, _ = servidor
    respuesta = cliente.post(
        "/chat", json={"texto": "   ", "conversacion_id": "1"}, headers={"X-API-Key": CLAVE}
    )
    assert respuesta.status_code == 422
    assert respuesta.json()["detail"] == "El texto está vacío: escribe una pregunta."
    assert llamadas == []


def test_chat_falla_del_coordinador_no_es_200(servidor, monkeypatch):
    cliente, _, server = servidor

    async def responder(texto, conversacion_id):
        raise RuntimeError("el coordinador no pudo evaluar la pregunta:\n cuota agotada")

    monkeypatch.setattr(server, "responder", responder)
    respuesta = cliente.post("/chat", json={"texto": "hola"}, headers={"X-API-Key": CLAVE})
    assert respuesta.status_code == 502
    detalle = respuesta.json()["detail"]
    assert detalle.startswith("El coordinador no pudo responder:")
    assert "\n" not in detalle


def test_webhook_sin_secreto_es_401(servidor, monkeypatch):
    cliente, _, _ = servidor
    monkeypatch.setenv("TELEGRAM_SECRETO_WEBHOOK", "secreto-webhook-de-prueba")
    respuesta = cliente.post("/telegram", json={"update_id": 1})
    assert respuesta.status_code == 401
    assert respuesta.json()["detail"] == "Secreto de webhook inválido."


def test_webhook_con_secreto_procesa_update(servidor, monkeypatch):
    cliente, _, server = servidor
    secreto = "secreto-webhook-de-prueba"
    monkeypatch.setenv("TELEGRAM_SECRETO_WEBHOOK", secreto)
    recibidos = []

    async def atender_prueba(http, actualizacion):
        recibidos.append(actualizacion)

    monkeypatch.setattr(server, "atender", atender_prueba)
    actualizacion = {"update_id": 7, "message": {"text": "hola"}}
    respuesta = cliente.post(
        "/telegram",
        json=actualizacion,
        headers={"X-Telegram-Bot-Api-Secret-Token": secreto},
    )
    assert respuesta.status_code == 200
    assert respuesta.json() == {"ok": True}
    assert recibidos == [actualizacion]
