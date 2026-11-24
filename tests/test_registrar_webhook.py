import asyncio
from argparse import Namespace

import httpx

from scripts import registrar_webhook


class ClienteTelegramFalso:
    """Cliente HTTP simulado para probar el script sin red."""

    def __init__(self, timeout):
        self.timeout = timeout
        self.llamadas = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def post(self, url, json, timeout):
        self.llamadas.append((url, json, timeout))
        return httpx.Response(
            200,
            json={
                "ok": True,
                "result": {"url": json.get("url", ""), "pending_update_count": 0},
            },
        )


def test_llamar_telegram_usa_timeout_y_devuelve_resultado(monkeypatch):
    clientes = []

    def crear_cliente(timeout):
        cliente = ClienteTelegramFalso(timeout)
        clientes.append(cliente)
        return cliente

    monkeypatch.setattr(registrar_webhook.httpx, "AsyncClient", crear_cliente)
    monkeypatch.setenv("TELEGRAM_TOKEN", "token-simulado")

    resultado = asyncio.run(
        registrar_webhook.llamar("setWebhook", {"url": "https://ejemplo.test/telegram"})
    )

    assert resultado["url"] == "https://ejemplo.test/telegram"
    assert clientes[0].timeout == registrar_webhook.TIEMPO_TELEGRAM
    assert clientes[0].llamadas[0][2] == registrar_webhook.TIEMPO_TELEGRAM


def test_llamar_telegram_convierte_timeout_en_error_de_una_linea(monkeypatch):
    class ClienteQueExpira(ClienteTelegramFalso):
        async def post(self, url, json, timeout):
            raise httpx.ReadTimeout("detalle interno\nsegunda línea")

    monkeypatch.setattr(
        registrar_webhook.httpx,
        "AsyncClient",
        lambda timeout: ClienteQueExpira(timeout),
    )
    monkeypatch.setenv("TELEGRAM_TOKEN", "token-simulado")

    try:
        asyncio.run(registrar_webhook.llamar("setWebhook", {}))
    except RuntimeError as error:
        assert str(error) == "Telegram no respondió a setWebhook a tiempo."
    else:
        raise AssertionError("Se esperaba un error de timeout.")


def test_ejecutar_registrar_usa_url_y_secreto_sin_mostrarlos(monkeypatch, capsys):
    llamadas = []

    async def llamar(metodo, datos=None):
        llamadas.append((metodo, datos))
        return {"url": datos["url"]}

    monkeypatch.setattr(
        registrar_webhook,
        "_configuracion",
        lambda: ("token-simulado", "secreto-simulado"),
    )
    monkeypatch.setattr(registrar_webhook, "llamar", llamar)
    monkeypatch.setenv("URL_PUBLICA", "https://coordinador.example.com/")

    asyncio.run(
        registrar_webhook.ejecutar(Namespace(accion="registrar", url=None))
    )

    assert llamadas == [
        (
            "setWebhook",
            {
                "url": "https://coordinador.example.com/telegram",
                "secret_token": "secreto-simulado",
            },
        )
    ]
    salida = capsys.readouterr().out
    assert "https://coordinador.example.com/telegram" in salida
    assert "secreto-simulado" not in salida
    assert "token-simulado" not in salida
