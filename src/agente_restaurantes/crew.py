"""Agente de restaurantes con CrewAI.

CrewAI no recuerda conversaciones por sí solo, así que el historial se guarda
en `_historial`, un diccionario indexado por context_id, y se inyecta en cada Task.
"""

import asyncio
import logging
import os
import uuid

from dotenv import load_dotenv

from crewai import Agent, Crew, LLM, Task
from crewai.events.event_bus import crewai_event_bus
from crewai.events.types.tool_usage_events import (
    ToolUsageFinishedEvent,
    ToolUsageStartedEvent,
)

from .prompts import HISTORIA, OBJETIVO, ROL
from .tools import buscar_restaurantes, detalle_restaurante


load_dotenv()

# CrewAI avisa en cada llamada que cuenta los tokens "a ojo"; no es un error.
logging.getLogger("crewai.llms.base_llm").setLevel(logging.ERROR)

MODELO = os.getenv("MODELO", "gemini-3.5-flash-lite")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    # Error entendible en vez del que lanzaría el modelo más abajo.
    raise RuntimeError("Falta GOOGLE_API_KEY: cópiala en el archivo .env.")

modelo = LLM(model=f"gemini/{MODELO}", api_key=GOOGLE_API_KEY)

agente = Agent(
    role=ROL,
    goal=OBJETIVO,
    backstory=HISTORIA,
    tools=[buscar_restaurantes, detalle_restaurante],
    llm=modelo,
    verbose=False,
    allow_delegation=False,
)

# context_id -> líneas de la conversación ("Usuario: ...", "Agente: ...").
_historial: dict[str, list[str]] = {}
MAX_LINEAS = 12


def _conversacion(context_id: str) -> str:
    """Devuelve lo hablado antes en este hilo, listo para pegar en la Task."""
    lineas = _historial.get(context_id, [])
    return "\n".join(lineas) if lineas else "(todavía no hay mensajes anteriores)"


def _recordar(context_id: str, autor: str, texto: str) -> None:
    """Agrega una línea al historial y descarta lo más viejo."""
    lineas = _historial.setdefault(context_id, [])
    lineas.append(f"{autor}: {texto}")
    del lineas[:-MAX_LINEAS]


def _crear_tarea(pregunta: str, context_id: str) -> Task:
    """La Task lleva la pregunta y todo lo hablado antes en esa conversación."""
    return Task(
        description=(
            "Conversación anterior:\n"
            f"{_conversacion(context_id)}\n\n"
            f"Pregunta actual: {pregunta}\n\n"
            "Usa buscar_restaurantes para encontrar opciones y detalle_restaurante "
            "si necesitas más datos de uno en particular. Responde solo con lo que "
            "devuelvan las herramientas, en español y breve, con precios en CLP."
        ),
        expected_output=(
            "Una respuesta breve en español con los restaurantes encontrados: nombre, "
            "zona, tipo de comida, precio medio en CLP y horario. Si no hay resultados, "
            "una frase diciendo que no hay opciones con esos criterios."
        ),
        agent=agente,
    )


def _crear_crew(tarea: Task, verbose: bool = False, step_callback=None) -> Crew:
    """Un crew de un solo agente y una sola tarea."""
    return Crew(
        agents=[agente],
        tasks=[tarea],
        verbose=verbose,
        step_callback=step_callback,
    )


async def _ejecutar(crew: Crew):
    """Usa kickoff_async si existe; si no, corre kickoff en otro hilo."""
    if hasattr(crew, "kickoff_async"):
        return await crew.kickoff_async()
    return await asyncio.to_thread(crew.kickoff)


def _texto(resultado) -> str:
    """CrewOutput guarda el texto en .raw; si no, convertimos a string."""
    crudo = getattr(resultado, "raw", None)
    return str(crudo) if crudo is not None else str(resultado)


async def responder(texto: str, context_id: str) -> str:
    """Responde la pregunta recordando lo anterior de la misma conversación."""
    tarea = _crear_tarea(texto, context_id)
    resultado = await _ejecutar(_crear_crew(tarea))
    respuesta = _texto(resultado)
    _recordar(context_id, "Usuario", texto)
    _recordar(context_id, "Agente", respuesta)
    return respuesta


# CrewAI llama al step_callback con tres cosas distintas: AgentAction (el agente
# decide llamar una herramienta), ToolResult (lo que devolvió) y AgentFinish
# (la respuesta final). Con function calling nativo, en cambio, las herramientas
# no pasan por el step_callback: por eso además escuchamos el bus de eventos.
_traza = {"activa": False, "herramientas": 0}
MAX_CARACTERES_SALIDA = 400


def _recortar(valor) -> str:
    """Deja la salida en una línea corta para que la terminal no se llene."""
    texto = " ".join(str(valor).split())
    if len(texto) > MAX_CARACTERES_SALIDA:
        return texto[:MAX_CARACTERES_SALIDA] + "..."
    return texto


def _mostrar_paso(paso) -> None:
    """step_callback: qué pensó el agente y qué respondió al final."""
    if not _traza["activa"]:
        return

    pensamiento = getattr(paso, "thought", "") or ""
    if pensamiento:
        print(f"piensa: {_recortar(pensamiento)}")

    respuesta = getattr(paso, "output", "") or ""
    if respuesta:
        print(f"respuesta: {_recortar(respuesta)}")


@crewai_event_bus.on(ToolUsageStartedEvent)
def _al_usar_herramienta(fuente, evento) -> None:
    """Muestra la herramienta y sus argumentos en cuanto el agente la llama."""
    if not _traza["activa"]:
        return
    _traza["herramientas"] += 1
    print(f"herramienta: {evento.tool_name} {_recortar(evento.tool_args)}")


@crewai_event_bus.on(ToolUsageFinishedEvent)
def _al_volver_de_herramienta(fuente, evento) -> None:
    """Muestra lo que devolvió la herramienta."""
    if not _traza["activa"]:
        return
    print(f"devolvió: {_recortar(evento.output)}")


async def saltos(texto: str) -> None:
    """Ejecuta el crew mostrando cada paso y cuenta las herramientas usadas."""
    _traza["activa"] = True
    _traza["herramientas"] = 0
    try:
        tarea = _crear_tarea(texto, str(uuid.uuid4()))
        crew = _crear_crew(tarea, verbose=True, step_callback=_mostrar_paso)
        await _ejecutar(crew)
    finally:
        _traza["activa"] = False
    print(f"\nHerramientas usadas: {_traza['herramientas']}")


def diagrama() -> None:
    """Dibuja a mano la estructura del crew (CrewAI no trae grafo)."""
    print(
        "graph TD\n"
        "    Tarea[Buscar y recomendar restaurantes] --> Agente[Agente de restaurantes]\n"
        "    Agente --> buscar_restaurantes[buscar_restaurantes]\n"
        "    Agente --> detalle_restaurante[detalle_restaurante]"
    )
