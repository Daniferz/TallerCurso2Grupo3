"""Bot de Telegram en local: lee mensajes por polling y se los pasa al coordinador.

Uso:
    python -m src.canal.telegram

No necesita túnel ni webhook: pregunta a Telegram por mensajes nuevos con
getUpdates usando TELEGRAM_TOKEN, manda cada texto a POST /chat del
coordinador (con CLAVE_COORDINADOR) y responde en el mismo chat. El chat_id
es el conversacion_id, así cada chat tiene su propia memoria.

Solo atiende a los IDs de TELEGRAM_USUARIOS_PERMITIDOS. Se detiene con Ctrl+C.
"""

import asyncio
import os
import time
from datetime import datetime

import httpx
from dotenv import load_dotenv

from src.comun.acceso import ENCABEZADO
from src.comun.registro import CATALOGO, RAIZ


load_dotenv(RAIZ / ".env")

API_TELEGRAM = "https://api.telegram.org"

# getUpdates espera hasta este tiempo por mensajes nuevos (long polling).
ESPERA_POLLING = 25

# Llamadas cortas a Telegram (enviar mensaje, getMe).
TIEMPO_TELEGRAM = 15.0

# El coordinador consulta un modelo y otro agente: hay que darle tiempo.
TIEMPO_COORDINADOR = float(os.getenv("TIEMPO_ESPERA_A2A", "120"))

# Telegram no acepta mensajes de más de 4096 caracteres.
LARGO_MAXIMO = 4000

MENSAJE_BIENVENIDA = (
    "Hola. Soy el asistente para preparar tu viaje por Chile. "
    "Pregúntame qué llevar en la maleta, una rutina de entrenamiento o qué sitios visitar."
)
MENSAJE_NO_TEXTO = "No puedo leer ese tipo de mensaje. Escríbeme tu pregunta en texto."
MENSAJE_FALLA = (
    "No pude responder en este momento: el asistente no está disponible. "
    "Intenta de nuevo en unos minutos."
)


def _sin_acceso(usuario_id: int) -> str:
    """Aviso para quien no está autorizado, con su ID para que lo agreguen."""
    return (
        "No tienes acceso a este bot. "
        f"Tu ID es {usuario_id}; pídele a quien administra el bot que lo agregue."
    )


class ErrorTelegram(Exception):
    """Falla al hablar con Telegram, en una línea y sin el token."""


class ErrorCoordinador(Exception):
    """El coordinador no respondió o respondió con error."""


def _token() -> str:
    return os.getenv("TELEGRAM_TOKEN", "").strip()


_ultimo_aviso: dict[str, float] = {}


async def avisar_chat(pregunta: str, conversacion_id: str) -> bool:
    """Avisa al chat configurado sin interrumpir la conversación normal."""
    chat_aviso = os.getenv("TELEGRAM_CHAT_AVISO", "").strip()
    token = _token()
    if not chat_aviso or not token:
        return False
    try:
        minutos = max(0.0, float(os.getenv("AVISO_MINUTOS", "10")))
    except ValueError:
        minutos = 10.0
    ahora = time.monotonic()
    anterior = _ultimo_aviso.get(conversacion_id)
    if anterior is not None and ahora - anterior < minutos * 60:
        return False
    _ultimo_aviso[conversacion_id] = ahora
    texto = (
        "Aviso: el coordinador no encontró un agente para esta pregunta.\n"
        f"Pregunta: {pregunta}\nConversación: {conversacion_id}"
    )
    try:
        async with httpx.AsyncClient() as http:
            await llamar_telegram(
                http,
                "sendMessage",
                {"chat_id": chat_aviso, "text": texto[:LARGO_MAXIMO]},
            )
    except Exception as error:
        registrar(f"No se pudo enviar aviso al chat configurado: {_sin_token(error)}")
        return False
    return True


def usuarios_permitidos() -> set[int]:
    """IDs de TELEGRAM_USUARIOS_PERMITIDOS (separados por comas); ignora lo que no sea número."""
    ids = set()
    for valor in os.getenv("TELEGRAM_USUARIOS_PERMITIDOS", "").split(","):
        valor = valor.strip()
        if valor.lstrip("-").isdigit():
            ids.add(int(valor))
    return ids


def _sin_token(texto: str) -> str:
    """Quita el token de cualquier texto antes de mostrarlo (las URLs de Telegram lo incluyen)."""
    token = _token()
    texto = " ".join(str(texto).split())
    return texto.replace(token, "<token>") if token else texto


def registrar(texto: str) -> None:
    """Una línea en la terminal por evento, nunca con el token."""
    hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[telegram {hora}] {_sin_token(texto)}", flush=True)


async def llamar_telegram(
    http: httpx.AsyncClient, metodo: str, datos: dict, espera: float = TIEMPO_TELEGRAM
):
    """Llama a un método de la API de Telegram y devuelve `result`."""
    url = f"{API_TELEGRAM}/bot{_token()}/{metodo}"
    try:
        respuesta = await http.post(url, json=datos, timeout=espera)
    except httpx.TimeoutException:
        raise ErrorTelegram(f"Telegram no respondió a {metodo} a tiempo.") from None
    except httpx.RequestError:
        raise ErrorTelegram("No se pudo conectar con Telegram (¿hay internet?).") from None

    try:
        cuerpo = respuesta.json()
    except ValueError:
        cuerpo = {}
    if respuesta.status_code == 401:
        raise ErrorTelegram("Telegram rechazó TELEGRAM_TOKEN (401): revisa el token en .env.")
    if respuesta.status_code == 409:
        raise ErrorTelegram(
            "El bot tiene un webhook activo (409). Bórralo para usar polling en local."
        )
    if not cuerpo.get("ok"):
        descripcion = cuerpo.get("description") or f"HTTP {respuesta.status_code}"
        raise ErrorTelegram(f"Telegram respondió error en {metodo}: {_sin_token(descripcion)}")
    return cuerpo.get("result")


async def enviar_mensaje(http: httpx.AsyncClient, chat_id: int, texto: str) -> None:
    """Envía `texto` al chat, partido en trozos si supera el largo de Telegram."""
    for inicio in range(0, len(texto) or 1, LARGO_MAXIMO):
        await llamar_telegram(
            http, "sendMessage", {"chat_id": chat_id, "text": texto[inicio : inicio + LARGO_MAXIMO]}
        )


async def preguntar_coordinador(
    http: httpx.AsyncClient, texto: str, conversacion_id: str
) -> dict:
    """Manda el texto a POST /chat del coordinador y devuelve {respuesta, agente}."""
    url = f"{CATALOGO['coordinador'].url}/chat"
    clave = os.getenv(CATALOGO["coordinador"].variable_clave, "").strip()
    try:
        respuesta = await http.post(
            url,
            json={"texto": texto, "conversacion_id": conversacion_id},
            # Sin keep-alive: entre mensajes pasan minutos y, en Windows, cerrar una
            # conexión ociosa deja un stack trace (WinError 10054) en el coordinador.
            headers={ENCABEZADO: clave, "Connection": "close"},
            timeout=TIEMPO_COORDINADOR,
        )
    except httpx.TimeoutException:
        raise ErrorCoordinador(
            f"el coordinador no respondió en {TIEMPO_COORDINADOR:.0f} segundos"
        ) from None
    except httpx.RequestError:
        raise ErrorCoordinador(f"no se pudo conectar con el coordinador en {url}") from None

    if respuesta.status_code != 200:
        try:
            detalle = respuesta.json().get("detail")
        except ValueError:
            detalle = None
        raise ErrorCoordinador(
            f"el coordinador respondió HTTP {respuesta.status_code}: {detalle or 'sin detalle'}"
        )
    return respuesta.json()


async def atender(http: httpx.AsyncClient, actualizacion: dict) -> None:
    """Procesa un update de Telegram: valida al usuario, consulta y responde en el chat."""
    mensaje = actualizacion.get("message")
    if not mensaje:
        return  # Ediciones, reacciones y otros eventos no se responden.

    chat_id = mensaje["chat"]["id"]
    usuario_id = (mensaje.get("from") or {}).get("id")

    if usuario_id not in usuarios_permitidos():
        registrar(f"chat {chat_id} · usuario {usuario_id} · RECHAZADO (no está en TELEGRAM_USUARIOS_PERMITIDOS)")
        await enviar_mensaje(http, chat_id, _sin_acceso(usuario_id))
        return

    texto = (mensaje.get("text") or "").strip()
    if not texto:
        registrar(f"chat {chat_id} · usuario {usuario_id} · mensaje sin texto")
        await enviar_mensaje(http, chat_id, MENSAJE_NO_TEXTO)
        return

    if texto.split()[0].split("@")[0] == "/start":
        registrar(f"chat {chat_id} · usuario {usuario_id} · /start")
        await enviar_mensaje(http, chat_id, MENSAJE_BIENVENIDA)
        return

    try:
        # "Escribiendo..." mientras el coordinador piensa; si falla, no importa.
        await llamar_telegram(http, "sendChatAction", {"chat_id": chat_id, "action": "typing"})
    except ErrorTelegram:
        pass

    try:
        datos = await preguntar_coordinador(http, texto, str(chat_id))
    except ErrorCoordinador as error:
        registrar(f"chat {chat_id} · usuario {usuario_id} · ERROR: {error}")
        await enviar_mensaje(http, chat_id, MENSAJE_FALLA)
        return

    respuesta = datos.get("respuesta") or MENSAJE_FALLA
    inicio = " ".join(respuesta.split())[:120]
    registrar(
        f"chat {chat_id} · usuario {usuario_id} · agente: {datos.get('agente', 'ninguno')} · "
        f"respuesta: {inicio}..."
    )
    await enviar_mensaje(http, chat_id, respuesta)


async def escuchar() -> None:
    """Bucle de polling: pide mensajes nuevos a Telegram y los atiende de a uno."""
    if not _token():
        raise ErrorTelegram("Falta TELEGRAM_TOKEN en .env (créalo con @BotFather).")
    if not usuarios_permitidos():
        print(
            "Aviso: TELEGRAM_USUARIOS_PERMITIDOS está vacío; el bot rechazará a todos.",
            flush=True,
        )

    async with httpx.AsyncClient() as http:
        bot = await llamar_telegram(http, "getMe", {})
        print(
            f"Bot @{bot.get('username')} escuchando por polling "
            f"(coordinador en {CATALOGO['coordinador'].url}). Ctrl+C para detener.",
            flush=True,
        )
        desde = 0
        while True:
            try:
                actualizaciones = await llamar_telegram(
                    http,
                    "getUpdates",
                    {"offset": desde, "timeout": ESPERA_POLLING, "allowed_updates": ["message"]},
                    espera=ESPERA_POLLING + 10,
                )
            except ErrorTelegram as error:
                texto = str(error)
                if "401" in texto or "409" in texto:
                    raise
                registrar(f"{texto} Se reintenta en 5 s.")
                await asyncio.sleep(5)
                continue

            for actualizacion in actualizaciones:
                desde = actualizacion["update_id"] + 1
                try:
                    await atender(http, actualizacion)
                except ErrorTelegram as error:
                    registrar(f"No se pudo responder en Telegram: {error}")


def main() -> None:
    try:
        asyncio.run(escuchar())
    except KeyboardInterrupt:
        print("Bot detenido.", flush=True)
    except ErrorTelegram as error:
        print(f"Error: {error}", flush=True)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
