"""Control de acceso: cada agente exige su propia X-API-Key; la consola, la del coordinador."""

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
    monkeypatch.setenv("CLAVE_ECO", CLAVE)
    monkeypatch.setenv("URL_PUBLICA", "")
    return TestClient(_app_eco("CLAVE_ECO"))


def _app_eco(variable_clave):
    async def eco(texto, context_id):
        return f"eco: {texto}"

    tarjeta = crear_tarjeta(
        "Agente eco", "Prueba", "http://127.0.0.1:9999",
        [("eco", "Eco", "Repite el mensaje.", "hola")],
    )
    return crear_app(tarjeta, eco, variable_clave)


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
    monkeypatch.setenv("CLAVE_ECO", "")
    respuesta = cliente.post("/", json=_mensaje(), headers={"X-API-Key": CLAVE})
    assert respuesta.status_code == 503


def test_consola_exige_clave(monkeypatch):
    monkeypatch.setenv("CLAVE_COORDINADOR", CLAVE)
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
    monkeypatch.setenv("CLAVE_ROTO", CLAVE)
    monkeypatch.setenv("URL_PUBLICA", "")

    async def roto(texto, context_id):
        raise RuntimeError("API key not valid")

    tarjeta = crear_tarjeta(
        "Agente roto", "Prueba", "http://127.0.0.1:9999",
        [("eco", "Eco", "Repite el mensaje.", "hola")],
    )
    servidor = TestClient(crear_app(tarjeta, roto, "CLAVE_ROTO"))
    datos = servidor.post("/", json=_mensaje(), headers={"X-API-Key": CLAVE}).json()

    assert "result" not in datos
    assert "No se pudo responder" in datos["error"]["message"]
    assert "clave de Gemini" in datos["error"]["message"]


def test_cada_agente_rechaza_la_clave_de_otro(monkeypatch):
    """En local los agentes comparten .env, pero cada uno exige SU clave."""
    monkeypatch.setenv("CLAVE_PATO", "clave-pato")
    monkeypatch.setenv("CLAVE_DANI", "clave-dani")
    monkeypatch.setenv("URL_PUBLICA", "")
    pato = TestClient(_app_eco("CLAVE_PATO"))
    dani = TestClient(_app_eco("CLAVE_DANI"))

    con_clave_pato = {"X-API-Key": "clave-pato"}
    assert pato.post("/", json=_mensaje(), headers=con_clave_pato).status_code == 200
    assert dani.post("/", json=_mensaje(), headers=con_clave_pato).status_code == 401


def test_clave_para_une_urls_y_claves_por_posicion(monkeypatch):
    from src.comun.acceso import aviso_listas_desparejas, clave_para

    monkeypatch.setenv("URLS_AGENTES", "https://pato.example/, https://dani.example")
    monkeypatch.setenv("CLAVES_AGENTES", "k-pato,k-dani")
    assert clave_para("https://pato.example") == "k-pato"
    assert clave_para("https://dani.example/") == "k-dani"
    assert aviso_listas_desparejas() is None

    monkeypatch.setenv("CLAVES_AGENTES", "k-pato")
    assert "mismo orden" in aviso_listas_desparejas()


def test_clave_para_usa_la_variable_del_registro_en_local(monkeypatch):
    from src.comun.acceso import clave_para
    from src.comun.registro import CATALOGO

    monkeypatch.setenv("URLS_AGENTES", "")
    monkeypatch.setenv("CLAVES_AGENTES", "")
    monkeypatch.setenv("CLAVE_PATO", "k-local")
    assert clave_para(CATALOGO["pato"].url) == "k-local"
    assert clave_para("http://nadie.example") == ""
