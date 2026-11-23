"""Servidor A2A del coordinador, más la ruta POST /chat para los canales (Telegram)."""

import hashlib
import hmac
import json
import os
import uuid

import httpx
from fastapi import Header, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError

from src.comun.errores import en_una_linea
from src.comun.registro import CATALOGO
from src.comun.servidor import crear_app
from src.comun.tarjeta import crear_tarjeta

from .catalogo import descubrir
from .graph import graph, responder
from src.canal.telegram import atender


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


FORMATO_CHAT = 'Envía JSON: {"texto": "tu pregunta", "conversacion_id": "opcional"}.'


def _leer_mensaje_chat(cuerpo: bytes) -> MensajeChat:
    """Lee el JSON de /chat con mensajes de error claros en español.

    curl en Windows suele mandar las tildes en la codificación de la consola (cp1252) y no
    en UTF-8: se acepta igual, para que "días" o "Pucón" no terminen en un error de parseo.
    """
    try:
        texto = cuerpo.decode("utf-8")
    except UnicodeDecodeError:
        texto = cuerpo.decode("cp1252", errors="replace")
    try:
        datos = json.loads(texto)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail=f"El cuerpo no es JSON válido. {FORMATO_CHAT}") from None
    try:
        return MensajeChat.model_validate(datos)
    except ValidationError:
        raise HTTPException(
            status_code=422, detail=f'Falta el campo "texto" o no es texto. {FORMATO_CHAT}'
        ) from None


@app.post("/chat")
async def chat(request: Request):
    """Recibe {texto, conversacion_id} y devuelve {respuesta}. Exige X-API-Key = CLAVE_COORDINADOR.

    La clave la valida el middleware de crear_app, igual que en "/".
    """
    datos = _leer_mensaje_chat(await request.body())
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


@app.post("/telegram")
async def telegram_webhook(
    actualizacion: dict,
    secreto: str | None = Header(
        default=None, alias="X-Telegram-Bot-Api-Secret-Token"
    ),
):
    """Recibe un update de Telegram y lo procesa con la lógica del bot local."""
    esperado = os.getenv("TELEGRAM_SECRETO_WEBHOOK", "").strip()
    if not esperado:
        raise HTTPException(
            status_code=503,
            detail="TELEGRAM_SECRETO_WEBHOOK no está configurado.",
        )
    if not secreto or not hmac.compare_digest(
        hashlib.sha256(secreto.encode()).digest(),
        hashlib.sha256(esperado.encode()).digest(),
    ):
        raise HTTPException(status_code=401, detail="Secreto de webhook inválido.")

    try:
        async with httpx.AsyncClient() as http:
            await atender(http, actualizacion)
    except Exception as error:
        motivo = en_una_linea(error)
        print(f"[telegram webhook] {motivo}", flush=True)
        raise HTTPException(
            status_code=502,
            detail=f"No se pudo procesar el update de Telegram: {motivo}",
        ) from None
    return {"ok": True}
