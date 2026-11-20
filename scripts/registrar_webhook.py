"""Registra o elimina el webhook de Telegram.

Uso:
    python scripts/registrar_webhook.py registrar https://coordinador.example.com
    python scripts/registrar_webhook.py info
    python scripts/registrar_webhook.py borrar

La URL de registro también puede venir de URL_PUBLICA. El token y el secreto
nunca se imprimen.
"""

import argparse
import os
import sys

import httpx
from dotenv import load_dotenv

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from src.comun.registro import RAIZ as RAIZ_PROYECTO  # noqa: E402


TIEMPO_TELEGRAM = 15.0


def _configuracion() -> tuple[str, str]:
    """Lee token y secreto sin exponerlos."""
    load_dotenv(RAIZ_PROYECTO / ".env")
    token = os.getenv("TELEGRAM_TOKEN", "").strip()
    secreto = os.getenv("TELEGRAM_SECRETO_WEBHOOK", "").strip()
    if not token:
        raise RuntimeError("Falta TELEGRAM_TOKEN en .env.")
    return token, secreto


def llamar(metodo: str, datos: dict | None = None) -> object:
    """Llama a Telegram con timeout y devuelve el resultado o un error breve."""
    token, _ = _configuracion()
    url = f"https://api.telegram.org/bot{token}/{metodo}"
    try:
        respuesta = httpx.post(url, json=datos or {}, timeout=TIEMPO_TELEGRAM)
    except httpx.TimeoutException:
        raise RuntimeError(f"Telegram no respondió a {metodo} a tiempo.") from None
    except httpx.RequestError:
        raise RuntimeError("No se pudo conectar con Telegram.") from None
    try:
        cuerpo = respuesta.json()
    except ValueError:
        cuerpo = {}
    if not cuerpo.get("ok"):
        raise RuntimeError(cuerpo.get("description") or f"Telegram respondió HTTP {respuesta.status_code}.")
    return cuerpo.get("result")


def ejecutar(argumentos: argparse.Namespace) -> None:
    """Ejecuta la acción solicitada."""
    token, secreto = _configuracion()
    del token
    if argumentos.accion == "registrar":
        url = (argumentos.url or os.getenv("URL_PUBLICA", "")).strip().rstrip("/")
        if not url:
            raise RuntimeError("Indica la URL pública del coordinador o configura URL_PUBLICA.")
        if not url.startswith("https://"):
            raise RuntimeError("La URL del webhook debe comenzar con https://.")
        if not secreto:
            raise RuntimeError("Falta TELEGRAM_SECRETO_WEBHOOK en .env.")
        resultado = llamar(
            "setWebhook",
            {"url": f"{url}/telegram", "secret_token": secreto},
        )
        url_registrada = (
            resultado.get("url", f"{url}/telegram")
            if isinstance(resultado, dict)
            else f"{url}/telegram"
        )
        print(f"Webhook registrado: {url_registrada}")
    elif argumentos.accion == "info":
        resultado = llamar("getWebhookInfo")
        print(
            f"Webhook: {resultado.get('url') or '(ninguno)'}; "
            f"pendientes: {resultado.get('pending_update_count', 0)}"
        )
    else:
        llamar("deleteWebhook")
        print("Webhook eliminado; el polling local puede volver a funcionar.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("accion", choices=("registrar", "info", "borrar"))
    parser.add_argument("url", nargs="?", help="URL pública base del coordinador")
    try:
        ejecutar(parser.parse_args())
    except Exception as error:
        print(f"Error: {' '.join(str(error).split())}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
