"""Servidor A2A del coordinador, más la ruta POST /chat para los canales (Telegram)."""

import uuid

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.comun.errores import en_una_linea
from src.comun.registro import CATALOGO
from src.comun.servidor import crear_app
from src.comun.tarjeta import crear_tarjeta

from .catalogo import descubrir
from .graph import graph, responder


agente = CATALOGO["coordinador"]

tarjeta = crear_tarjeta(
    agente.nombre,
    agente.descripcion,
    agente.url,
    [
        (
            "elegir_agente",
            "Elegir un agente por tema",
            "Lee las fichas de los agentes de Maleta, Entrenamiento y Sitios turísticos, elige el adecuado y explica brevemente el motivo.",
            "¿Qué llevo en la maleta para Pucón 3 días en invierno?",
        ),
        (
            "sin_agente",
            "Detectar temas fuera de catálogo",
            "Indica cuando ningún agente del catálogo corresponde a la pregunta y muestra los temas disponibles.",
            "¿Quién ganó el mundial de 1962?",
        ),
    ],
    usar_url_publica=False,
)

app = crear_app(tarjeta, responder, agente.variable_clave)


@app.on_event("startup")
async def iniciar_supervisor() -> None:
    """Lee las fichas al arrancar; las que fallen se reintentan después (ver catalogo.py)."""
    agentes = await descubrir()
    print(f"Supervisor con {len(agentes)} agentes")


class MensajeChat(BaseModel):
    """Lo que manda un canal: el texto y el hilo de la conversación (en Telegram, el chat_id)."""

    texto: str
    conversacion_id: str | None = None


async def _agente_elegido(conversacion_id: str) -> str:
    """Agente que el supervisor eligió en el último turno de esa conversación."""
    estado = await graph.aget_state({"configurable": {"thread_id": conversacion_id}})
    return (estado.values or {}).get("agente") or "ninguno"


@app.post("/chat")
async def chat(datos: MensajeChat):
    """Recibe {texto, conversacion_id} y devuelve {respuesta}. Exige X-API-Key = CLAVE_COORDINADOR.

    La clave la valida el middleware de crear_app, igual que en "/".
    """
    texto = datos.texto.strip()
    if not texto:
        raise HTTPException(status_code=422, detail="El texto está vacío: escribe una pregunta.")

    conversacion_id = (datos.conversacion_id or "").strip() or str(uuid.uuid4())
    try:
        respuesta = await responder(texto, conversacion_id)
    except Exception as error:
        # Una falla no se disfraza de respuesta: 502 con el motivo en una línea.
        motivo = f"El coordinador no pudo responder: {en_una_linea(error)}"
        print(f"[chat] conversación {conversacion_id}: {motivo}", flush=True)
        return JSONResponse(status_code=502, content={"detail": motivo})

    agente = await _agente_elegido(conversacion_id)
    print(f"[chat] conversación {conversacion_id} -> agente: {agente}", flush=True)
    return {"respuesta": respuesta, "conversacion_id": conversacion_id, "agente": agente}
