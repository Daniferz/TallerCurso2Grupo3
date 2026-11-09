"""Cliente A2A del coordinador: habla con otros agentes usando el cliente de a2a-sdk.

El coordinador no arma JSON a mano: descarga la ficha del agente con
A2ACardResolver, arma un cliente con create_client (sin streaming, por
JSON-RPC) y reutiliza ese cliente para no bajar la ficha cada vez.
"""

import asyncio
import os
import time
import uuid

import httpx

from dotenv import load_dotenv

from a2a.client import A2ACardResolver, Client, ClientConfig, ClientCallContext, create_client
from a2a.client.errors import A2AClientError, AgentCardResolutionError
from a2a.types import (
    AgentCard,
    GetTaskRequest,
    Message,
    Part,
    Role,
    SendMessageRequest,
    Task,
    TaskState,
)


# Se lee el .env antes que nada: los timeouts salen de ahí.
load_dotenv()

# El agente del otro lado usa un modelo: hay que darle tiempo de responder.
TIEMPO_ESPERA = float(os.getenv("TIEMPO_ESPERA_A2A", "120"))

# La ficha es un JSON chico: si tarda más, es que el servidor no está.
TIEMPO_FICHA = float(os.getenv("TIEMPO_FICHA_A2A", "3"))

# url -> cliente ya armado, para no descargar la ficha en cada pregunta.
_clientes: dict[str, Client] = {}
_tarjetas: dict[str, AgentCard] = {}

# Un solo HTTP para ficha y mensajes; con timeout explícito desde el inicio.
_http = httpx.AsyncClient(timeout=TIEMPO_ESPERA)


def _traducir_ficha(url: str, error: Exception) -> str:
    """Pasa el fallo de la ficha a una frase corta en español."""
    causa = error.__cause__
    if isinstance(causa, httpx.HTTPStatusError):
        codigo = causa.response.status_code
        return f"El agente en {url} respondió HTTP {codigo} al publicar su ficha."
    if isinstance(causa, httpx.RequestError):
        return f"No se pudo conectar con el agente en {url}."
    return f"No se pudo leer la ficha del agente en {url}."


def _traducir(error: Exception) -> str:
    """Pasa el error del cliente A2A a una frase corta en español."""
    causa = error.__cause__
    if isinstance(causa, httpx.TimeoutException):
        return f"El agente no respondió en {TIEMPO_ESPERA:.0f} segundos."
    if isinstance(causa, httpx.HTTPStatusError):
        return f"El agente respondió HTTP {causa.response.status_code}."
    if isinstance(causa, httpx.RequestError):
        return "No se pudo conectar con el agente."
    return str(error)


def _texto_de_partes(partes) -> str:
    """Une las partes de texto de un mensaje o de un artefacto (las demás se ignoran)."""
    fragmentos = []
    for parte in partes:
        if parte.WhichOneof("content") == "text" and parte.text:
            fragmentos.append(parte.text)
    return " ".join(fragmentos).strip()


async def obtener_cliente(url: str) -> Client:
    """Descarga la ficha del agente que vive en `url` y arma su cliente.

    El cliente queda guardado en un diccionario: la segunda pregunta a la
    misma URL no vuelve a bajar la ficha.
    """
    destino = url.rstrip("/")
    if destino in _clientes:
        return _clientes[destino]

    try:
        ficha = await A2ACardResolver(_http, destino).get_agent_card(
            http_kwargs={"timeout": TIEMPO_FICHA}
        )
        cliente = await create_client(
            ficha,
            ClientConfig(streaming=False, httpx_client=_http),
        )
    except AgentCardResolutionError as error:
        raise A2AClientError(_traducir_ficha(destino, error)) from None

    _clientes[destino] = cliente
    _tarjetas[destino] = ficha
    return cliente


def obtener_tarjeta_cacheada(url: str) -> AgentCard | None:
    """Devuelve la ficha ya descargada por `obtener_cliente`, sin otra llamada de red."""
    return _tarjetas.get(url.rstrip("/"))


def _estado_de(tarea: Task) -> int:
    """Estado actual de la tarea (SUBMITTED, WORKING, COMPLETED...)."""
    return tarea.status.state


def _texto_de_tarea(tarea: Task) -> str:
    """Junta el texto de todos los artefactos de la tarea terminada."""
    for artefacto in tarea.artifacts:
        texto = _texto_de_partes(artefacto.parts)
        if texto:
            return texto
    # Sin artefactos, la respuesta puede venir en el mensaje de estado.
    return _texto_de_partes(tarea.status.message.parts)


async def _esperar_tarea(cliente: Client, tarea: Task, contexto: ClientCallContext) -> Task:
    """Pregunta por la tarea hasta que deje de estar en curso o se acabe el tiempo."""
    limite = time.monotonic() + TIEMPO_ESPERA
    while _estado_de(tarea) in (TaskState.TASK_STATE_SUBMITTED, TaskState.TASK_STATE_WORKING):
        if time.monotonic() > limite:
            raise A2AClientError(
                f"La tarea {tarea.id} no terminó en {TIEMPO_ESPERA:.0f} segundos."
            )
        await asyncio.sleep(0.5)
        tarea = await cliente.get_task(
            GetTaskRequest(id=tarea.id, history_length=0),
            context=contexto,
        )
    return tarea


async def preguntar(cliente: Client, texto: str, context_id: str) -> str:
    """Manda `texto` como mensaje de usuario con ese `context_id` y devuelve la respuesta.

    La respuesta puede venir como mensaje directo (se toma su texto) o como
    tarea: en ese caso se espera a que termine y se junta el texto de sus
    artefactos.
    """
    solicitud = SendMessageRequest(
        message=Message(
            message_id=str(uuid.uuid4()),
            context_id=context_id,
            role=Role.ROLE_USER,
            parts=[Part(text=texto)],
        )
    )
    contexto = ClientCallContext(timeout=TIEMPO_ESPERA)

    try:
        async for respuesta in cliente.send_message(solicitud, context=contexto):
            if respuesta.HasField("message"):
                return _texto_de_partes(respuesta.message.parts)

            if respuesta.HasField("task"):
                tarea = await _esperar_tarea(cliente, respuesta.task, contexto)
                if _estado_de(tarea) != TaskState.TASK_STATE_COMPLETED:
                    raise A2AClientError(
                        f"La tarea {tarea.id} terminó en "
                        f"{TaskState.Name(_estado_de(tarea))}."
                    )
                return _texto_de_tarea(tarea)
    except A2AClientError as error:
        # Sin causa conocida (errores que lanzamos nosotros) se dejan como están.
        if error.__cause__ is None:
            raise
        raise A2AClientError(_traducir(error)) from None

    raise A2AClientError("El agente no devolvió ni mensaje ni tarea.")
