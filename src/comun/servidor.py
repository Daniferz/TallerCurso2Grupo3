"""Servidor A2A común: monta el agente sobre FastAPI una sola vez para los tres agentes."""

from fastapi import FastAPI

from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import (
    add_a2a_routes_to_fastapi,
    create_agent_card_routes,
    create_jsonrpc_routes,
)
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard

from .executor import Executor, FuncionResponder


RUTA_MENSAJES = "/"
RUTA_SALUD = "/salud"


def crear_app(tarjeta: AgentCard, responder: FuncionResponder) -> FastAPI:
    """Devuelve la app FastAPI lista para `uvicorn src.agente_x.server:app`.

    Queda escuchando mensajes A2A en "/" y publicando la ficha en
    "/.well-known/agent-card.json".
    """
    manejador = DefaultRequestHandler(
        agent_executor=Executor(responder),
        # En memoria: el historial de tareas se pierde al reiniciar el proceso.
        task_store=InMemoryTaskStore(),
        agent_card=tarjeta,
    )

    app = FastAPI(
        title=tarjeta.name,
        description=tarjeta.description,
        version=tarjeta.version,
    )

    add_a2a_routes_to_fastapi(
        app,
        agent_card_routes=create_agent_card_routes(tarjeta),
        jsonrpc_routes=create_jsonrpc_routes(
            manejador,
            rpc_url=RUTA_MENSAJES,
            # Acepta clientes nuevos (SendMessage) y antiguos (message/send de v0.3).
            enable_v0_3_compat=True,
        ),
    )

    @app.get(RUTA_SALUD)
    async def salud() -> dict[str, bool]:
        """Confirma que el proceso está vivo (no valida que el agente responda)."""
        return {"ok": True}

    return app
