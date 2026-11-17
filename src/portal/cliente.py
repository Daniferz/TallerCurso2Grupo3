"""Cliente A2A de la consola: manda un texto por JSON-RPC y devuelve la respuesta."""

import os
import time
import uuid

import httpx

from src.comun.registro import Agente


METODO = "message/send"

# Un agente con modelo puede tardar; el tope evita que la página quede colgada.
TIEMPO_ESPERA = float(os.getenv("TIEMPO_ESPERA_A2A", "120"))

# La revisión de /salud debe ser rápida: si el servidor no está, la página no espera.
TIEMPO_SALUD = float(os.getenv("TIEMPO_SALUD_A2A", "1.5"))

# La Agent Card es un archivo chico, pero no conviene esperar mucho por ella.
TIEMPO_FICHA = float(os.getenv("TIEMPO_FICHA_A2A", "3"))

# Dónde publica a2a-sdk la ficha de cada agente.
RUTA_FICHA = "/.well-known/agent-card.json"


class ErrorAgente(Exception):
    """Falla entendible al hablar con un agente: se muestra tal cual en la web."""


def _en_una_linea(error: Exception) -> str:
    """Deja el error en un solo renglón, sin stack trace."""
    texto = " ".join(str(error).split())
    return texto or error.__class__.__name__


def _texto_de_parte(parte: object) -> str:
    """Saca el texto de una parte del mensaje (las que no son texto se ignoran)."""
    if not isinstance(parte, dict):
        return ""
    texto = parte.get("text")
    return str(texto) if texto is not None else ""


def _texto_de_mensaje(mensaje: dict) -> str:
    """Une las partes de texto de un mensaje A2A."""
    if not isinstance(mensaje, dict):
        return ""
    partes = mensaje.get("parts") or []
    return " ".join(filter(None, (_texto_de_parte(parte) for parte in partes))).strip()


def extraer_texto(resultado: dict) -> str:
    """Saca el texto de un Message o de un Task (A2A 0.3 responde en camelCase)."""
    if not isinstance(resultado, dict):
        return ""

    if resultado.get("kind") == "message":
        return _texto_de_mensaje(resultado)

    # Un Task puede traer la respuesta en status.message o en sus artifacts.
    estado = resultado.get("status") or {}
    if not isinstance(estado, dict):
        estado = {}
    texto = _texto_de_mensaje(estado.get("message") or {})
    if texto:
        return texto

    fragmentos = []
    for artefacto in resultado.get("artifacts") or []:
        if not isinstance(artefacto, dict):
            continue
        for parte in artefacto.get("parts") or []:
            fragmentos.append(_texto_de_parte(parte))
    return " ".join(filter(None, fragmentos)).strip()


async def esta_en_linea(agente: Agente) -> bool:
    """Pregunta a /salud si el servidor del agente está levantado."""
    if not agente.disponible:
        return False
    try:
        async with httpx.AsyncClient(timeout=TIEMPO_SALUD) as cliente:
            respuesta = await cliente.get(f"{agente.url}/salud")
        return respuesta.status_code == 200
    except httpx.HTTPError:
        # Sin servidor no hay nada que mostrar: la ficha queda "sin conexión".
        return False


def _normalizar_ficha(datos: dict) -> dict:
    """Deja la Agent Card en las claves que usa la consola (todo en español)."""
    interfaces = datos.get("supportedInterfaces") or []
    interfaz = interfaces[0] if interfaces and isinstance(interfaces[0], dict) else None

    habilidades = []
    for skill in datos.get("skills") or []:
        if not isinstance(skill, dict):
            continue
        habilidades.append(
            {
                "id": str(skill.get("id", "")),
                "nombre": str(skill.get("name", "")),
                "descripcion": str(skill.get("description", "")),
                "ejemplos": [
                    str(ejemplo)
                    for ejemplo in skill.get("examples") or []
                    if ejemplo
                ],
            }
        )

    capacidades = datos.get("capabilities") or {}
    if not isinstance(capacidades, dict):
        capacidades = {}

    return {
        "version": str(datos.get("version", "")),
        "streaming": bool(capacidades.get("streaming", False)),
        "modos_entrada": [str(modo) for modo in datos.get("defaultInputModes") or []],
        "modos_salida": [str(modo) for modo in datos.get("defaultOutputModes") or []],
        "interfaz": (
            {
                "url": str(interfaz.get("url", "")),
                "protocolo": str(interfaz.get("protocolBinding", "")),
                "version_protocolo": str(interfaz.get("protocolVersion", "")),
            }
            if interfaz
            else None
        ),
        "habilidades": habilidades,
    }


async def obtener_ficha(agente: Agente) -> dict | None:
    """Descarga la Agent Card que publica el agente, o None si no hay ficha."""
    if not agente.disponible:
        return None

    try:
        async with httpx.AsyncClient(timeout=TIEMPO_FICHA) as cliente:
            respuesta = await cliente.get(f"{agente.url}{RUTA_FICHA}")
        if respuesta.status_code != 200:
            return None
        datos = respuesta.json()
    except (httpx.HTTPError, ValueError):
        # Sin ficha la consola sigue funcionando: solo se ocultan esos detalles.
        return None

    if not isinstance(datos, dict):
        return None

    return _normalizar_ficha(datos)


async def enviar_mensaje(
    agente: Agente, texto: str, context_id: str | None = None
) -> dict:
    """Envía `texto` con message/send y devuelve respuesta, contexto y latencia."""
    contexto = context_id or str(uuid.uuid4())

    peticion = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": METODO,
        "params": {
            "message": {
                "kind": "message",
                "messageId": str(uuid.uuid4()),
                "role": "user",
                "contextId": contexto,
                "parts": [{"kind": "text", "text": texto}],
            }
        },
    }

    inicio = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=TIEMPO_ESPERA) as cliente:
            respuesta = await cliente.post(agente.url, json=peticion)
    except httpx.TimeoutException:
        raise ErrorAgente(
            f"{agente.nombre} no respondió en {TIEMPO_ESPERA:.0f} segundos."
        ) from None
    except httpx.HTTPError as error:
        raise ErrorAgente(
            f"No se pudo conectar con {agente.nombre} en {agente.url}: "
            f"{_en_una_linea(error)}"
        ) from None

    latencia = int((time.perf_counter() - inicio) * 1000)

    if respuesta.status_code >= 400:
        raise ErrorAgente(
            f"{agente.nombre} respondió con HTTP {respuesta.status_code}."
        )

    try:
        datos = respuesta.json()
    except ValueError:
        raise ErrorAgente(
            f"{agente.nombre} devolvió una respuesta que no es JSON."
        ) from None

    if not isinstance(datos, dict):
        raise ErrorAgente(f"{agente.nombre} devolvió una respuesta inesperada.")

    if datos.get("error"):
        detalle = datos["error"]
        if isinstance(detalle, dict):
            detalle = detalle.get("message", "error desconocido")
        raise ErrorAgente(
            f"{agente.nombre} devolvió un error: {_en_una_linea(Exception(detalle))}"
        )

    resultado = datos.get("result") or {}
    contenido = extraer_texto(resultado)
    if not contenido:
        raise ErrorAgente(f"{agente.nombre} respondió sin texto.")

    return {
        "respuesta": contenido,
        "context_id": resultado.get("contextId") or contexto,
        "latencia_ms": latencia,
    }
