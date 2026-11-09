"""Consola web: lista los agentes registrados y les envía mensajes por A2A."""

import asyncio
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from src.comun.registro import CATALOGO, Agente

from .cliente import (
    METODO,
    ErrorAgente,
    enviar_mensaje,
    esta_en_linea,
    obtener_ficha,
)


CARPETA_ESTATICA = Path(__file__).resolve().parent / "estatico"

app = FastAPI(
    title="Consola de agentes",
    description=(
        "Muestra los agentes registrados y les envía mensajes A2A "
        "con el método message/send."
    ),
    version="1.0.0",
)

app.mount("/estatico", StaticFiles(directory=CARPETA_ESTATICA), name="estatico")


class MensajeEntrante(BaseModel):
    """Lo que manda la página: a quién, qué texto y en qué conversación."""

    agente: str = Field(description="Clave del agente en el registro.")
    texto: str = Field(description="Mensaje para el agente.")
    context_id: str | None = Field(
        default=None, description="Conversación previa, si existe."
    )

    @field_validator("texto")
    @classmethod
    def _no_vacio(cls, valor: str) -> str:
        """Rechaza mensajes que solo tienen espacios."""
        limpio = valor.strip()
        if not limpio:
            raise ValueError("El mensaje no puede estar vacío.")
        return limpio


def _aviso_de_url(agente: Agente, ficha: dict | None) -> str | None:
    """Avisa si la URL de la ficha no coincide con la del registro."""
    interfaz = (ficha or {}).get("interfaz") or {}
    publicada = interfaz.get("url", "").rstrip("/")
    if publicada and publicada != agente.url.rstrip("/"):
        return f"La ficha publica otra URL: {publicada}"
    return None


def _ficha(agente: Agente, en_linea: bool, ficha: dict | None) -> dict:
    """Arma lo que la página necesita para pintar cada agente."""
    return {
        "clave": agente.clave,
        "nombre": agente.nombre,
        "descripcion": agente.descripcion,
        "url": agente.url,
        "disponible": agente.disponible,
        "en_linea": en_linea,
        "metodo": METODO,
        "ficha": ficha,
        "aviso_url": _aviso_de_url(agente, ficha),
    }


@app.get("/")
async def inicio() -> FileResponse:
    """Sirve la página de la consola."""
    return FileResponse(CARPETA_ESTATICA / "index.html")


@app.get("/api/agentes")
async def listar_agentes() -> list[dict]:
    """Devuelve el registro de agentes, su estado en línea y su Agent Card."""
    agentes = list(CATALOGO.values())
    # Dos grupos en paralelo: estados de /salud y fichas, sin esperar de a uno.
    estados, fichas = await asyncio.gather(
        asyncio.gather(*(esta_en_linea(agente) for agente in agentes)),
        asyncio.gather(*(obtener_ficha(agente) for agente in agentes)),
    )
    return [
        _ficha(agente, en_linea, ficha)
        for agente, en_linea, ficha in zip(agentes, estados, fichas, strict=True)
    ]


@app.post("/api/mensajes")
async def mandar_mensaje(datos: MensajeEntrante) -> dict:
    """Reenvía el texto al agente elegido usando JSON-RPC message/send."""
    agente = CATALOGO.get(datos.agente)
    if agente is None:
        raise HTTPException(status_code=404, detail="Ese agente no está registrado.")
    if not agente.disponible:
        raise HTTPException(
            status_code=409,
            detail=f"Ese agente todavía no existe: {agente.clave}.",
        )

    try:
        return await enviar_mensaje(agente, datos.texto, datos.context_id)
    except ErrorAgente as error:
        raise HTTPException(status_code=502, detail=str(error)) from None
