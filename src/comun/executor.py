"""Ejecutor común: traduce los mensajes A2A al contrato responder(texto, context_id).

Cada agente trae su propia función `responder`; esta clase la envuelve para que
el servidor de a2a-sdk la pueda llamar sin que el agente sepa nada del protocolo.
"""

import inspect
import uuid

from collections.abc import Awaitable, Callable

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import Message, Part, Role
from a2a.utils.errors import UnsupportedOperationError

from .errores import en_una_linea


# Un agente puede responder de forma directa (sync) o con una corrutina (async).
FuncionResponder = Callable[[str, str], str | Awaitable[str]]


class Executor(AgentExecutor):
    """Adapta la función `responder(texto, context_id)` de un agente al protocolo A2A."""

    def __init__(self, responder: FuncionResponder) -> None:
        """Guarda la función del agente que va a producir la respuesta."""
        self._responder = responder

    async def execute(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        """Toma el mensaje del usuario, llama al agente y encola su respuesta."""
        texto = context.get_user_input()
        # Si el cliente no mandó conversación, inventamos una para no perder el hilo.
        context_id = context.context_id or str(uuid.uuid4())

        try:
            respuesta = self._responder(texto, context_id)
            if inspect.isawaitable(respuesta):
                respuesta = await respuesta
            contenido = str(respuesta)
        except Exception as error:
            # Nunca rompemos el servidor: el cliente recibe el motivo en el texto.
            contenido = f"No se pudo responder: {en_una_linea(error)}"

        await event_queue.enqueue_event(
            Message(
                message_id=str(uuid.uuid4()),
                context_id=context_id,
                role=Role.ROLE_AGENT,
                parts=[Part(text=contenido)],
            )
        )

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        """Cancelar no aplica: cada respuesta es inmediata y no queda nada corriendo."""
        raise UnsupportedOperationError(
            "Cancelar no está soportado: este agente responde de inmediato."
        )
