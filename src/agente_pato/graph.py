"""Agente de gimnasio de Pato en LangGraph: Gemini, anatomía, rutinas con evidencia y memoria por contexto."""

import os
import re
import unicodedata
import uuid

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver

from .prompts import SYSTEM_PROMPT
from .tools import musculo, rutina


load_dotenv()

MODELO = os.getenv("MODELO", "gemini-3.5-flash-lite")

if not os.getenv("GOOGLE_API_KEY"):
    raise RuntimeError("Falta GOOGLE_API_KEY: cópiala en el archivo .env.")

modelo = ChatGoogleGenerativeAI(model=MODELO)

graph = create_agent(
    modelo,
    tools=[musculo, rutina],
    system_prompt=SYSTEM_PROMPT,
    checkpointer=MemorySaver(),
)


def _texto(mensaje: BaseMessage) -> str:
    """Extrae texto de un mensaje del modelo, sea texto plano o bloques."""
    texto = getattr(mensaje, "text", None)
    if texto:
        return texto
    contenido = getattr(mensaje, "content", "")
    if isinstance(contenido, list):
        return " ".join(
            bloque.get("text", "") if isinstance(bloque, dict) else str(bloque)
            for bloque in contenido
        ).strip()
    return str(contenido)


# Línea de ejercicio que arma la herramienta rutina: "1. Press de banca (barra o mancuernas): 2 × 5-8".
_EJERCICIO = re.compile(r"^\d+\.\s*(?P<nombre>[^:(]+?)\s*(?:\([^)]*\))?\s*:\s*(?P<series>\d+)\s*×\s*(?P<reps>[\d-]+)", re.M)


def _plano(texto: str) -> str:
    """Minúsculas, sin tildes ni markdown, para comparar sin importar el formato."""
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return " ".join(re.sub(r"[*_`#]", "", sin_tildes).lower().split())


def _rutina_del_turno(mensajes: list[BaseMessage]) -> str | None:
    """Última salida de la herramienta rutina después del último mensaje de la persona."""
    for mensaje in reversed(mensajes):
        if isinstance(mensaje, HumanMessage):
            return None
        if isinstance(mensaje, ToolMessage) and mensaje.name == "rutina":
            return _texto(mensaje)
    return None


def _falta_algun_ejercicio(rutina_herramienta: str, respuesta: str) -> bool:
    """True si la respuesta no trae algún ejercicio con sus series y repeticiones."""
    plano = _plano(respuesta)
    for ejercicio in _EJERCICIO.finditer(rutina_herramienta):
        nombre = _plano(ejercicio["nombre"])
        if nombre not in plano or ejercicio["series"] not in plano or ejercicio["reps"] not in plano:
            return True
    return False


def completar_respuesta(mensajes: list[BaseMessage]) -> str:
    """Texto final del turno; si el modelo omitió la rutina, se agrega tal como la armó la herramienta.

    Gemini a veces responde solo "Aquí tienes tu rutina..." sin copiar los ejercicios.
    La pauta pide que la respuesta final no pierda ni altere cifras, así que no se
    confía solo en el prompt.
    """
    respuesta = _texto(mensajes[-1]).strip()
    rutina_herramienta = _rutina_del_turno(mensajes)
    if rutina_herramienta and _falta_algun_ejercicio(rutina_herramienta, respuesta):
        return f"{respuesta}\n\n{rutina_herramienta}".strip()
    return respuesta


async def responder(texto: str, context_id: str) -> str:
    """Responde y reutiliza `context_id` como `thread_id` de LangGraph."""
    resultado = await graph.ainvoke(
        {"messages": [{"role": "user", "content": texto}]},
        config={"configurable": {"thread_id": context_id}},
    )
    return completar_respuesta(resultado["messages"])


async def saltos(texto: str) -> None:
    """Muestra nodos y herramientas usados por una consulta nueva."""
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    total = 0
    herramientas = []
    respuesta = ""
    async for actualizacion in graph.astream(
        {"messages": [{"role": "user", "content": texto}]},
        config=config,
        stream_mode="updates",
    ):
        for nodo, datos in actualizacion.items():
            total += 1
            print(f"nodo: {nodo}")
            mensajes = datos.get("messages", []) if isinstance(datos, dict) else []
            for mensaje in mensajes:
                llamadas = getattr(mensaje, "tool_calls", None) or []
                for llamada in llamadas:
                    herramientas.append(llamada["name"])
                    print(f"  herramienta: {llamada['name']}({llamada['args']})")
                if nodo == "model" and not llamadas:
                    respuesta = _texto(mensaje)
    print(f"Saltos: {total} · Herramientas: {', '.join(herramientas) or 'ninguna'}")
    print(f"Respuesta: {respuesta}")


def diagrama() -> None:
    """Imprime el diagrama Mermaid sin ejecutar el modelo."""
    print(graph.get_graph().draw_mermaid())
