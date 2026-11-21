"""Servidor A2A común: monta el agente sobre FastAPI una sola vez para los tres agentes."""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import (
    add_a2a_routes_to_fastapi,
    create_agent_card_routes,
    create_jsonrpc_routes,
)
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard

from .acceso import ENCABEZADO, motivo_rechazo, registrar_acceso
from .executor import Executor, FuncionResponder


RUTA_MENSAJES = "/"
RUTA_SALUD = "/salud"
RUTA_FICHA = "/.well-known/agent-card.json"

# Rutas públicas: la salud y la ficha A2A (la spec pide que la ficha sea descubrible).
# Todo lo demás, en especial los mensajes JSON-RPC en "/", exige X-API-Key.
RUTAS_PUBLICAS = {RUTA_SALUD, RUTA_FICHA}


class _SinStackTrace(logging.Filter):
    """Deja el aviso de a2a-sdk en una línea: el motivo ya lo imprimió el Executor."""

    def filter(self, registro: logging.LogRecord) -> bool:
        registro.exc_info = None
        registro.exc_text = None
        registro.stack_info = None
        return True


# Cuando un agente falla (cuota o clave de Gemini, por ejemplo), a2a-sdk registra la excepción
# con su stack trace. La regla del proyecto es una sola línea entendible, sin stack trace.
logging.getLogger("a2a.server.agent_execution").addFilter(_SinStackTrace())
logging.getLogger("a2a.server.agent_execution.active_task").addFilter(_SinStackTrace())


def crear_app(
    tarjeta: AgentCard, responder: FuncionResponder, variable_clave: str
) -> FastAPI:
    """Devuelve la app FastAPI lista para `uvicorn src.agente_x.server:app`.

    Queda escuchando mensajes A2A en "/" y publicando la ficha en
    "/.well-known/agent-card.json". Los mensajes exigen X-API-Key igual a la
    variable `variable_clave` del .env (ej.: CLAVE_PATO): cada agente tiene la suya.
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

    @app.middleware("http")
    async def exigir_clave(request: Request, siguiente):
        """Rechaza con 401 cualquier llamada no pública sin una X-API-Key válida."""
        ruta = request.url.path
        if request.method == "GET" and ruta in RUTAS_PUBLICAS:
            return await siguiente(request)

        cliente = request.client.host if request.client else "desconocido"
        rechazo = motivo_rechazo(request.headers.get(ENCABEZADO), variable_clave)
        if rechazo:
            codigo, mensaje = rechazo
            registrar_acceso(tarjeta.name, f"{request.method} {ruta}", cliente, False, mensaje)
            return JSONResponse(status_code=codigo, content={"detail": mensaje})

        registrar_acceso(tarjeta.name, f"{request.method} {ruta}", cliente, True)
        return await siguiente(request)

    @app.get(RUTA_SALUD)
    async def salud() -> dict[str, bool]:
        """Confirma que el proceso está vivo (no valida que el agente responda)."""
        return {"ok": True}

    return app
