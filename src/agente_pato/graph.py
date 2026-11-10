"""Agente de gimnasio de Pato en LangGraph: Gemini, anatomía, rutinas con evidencia y memoria por contexto."""

import os
import uuid

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import BaseMessage
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


async def responder(texto: str, context_id: str) -> str:
    """Responde y reutiliza `context_id` como `thread_id` de LangGraph."""
    resultado = await graph.ainvoke(
        {"messages": [{"role": "user", "content": texto}]},
        config={"configurable": {"thread_id": context_id}},
    )
    return _texto(resultado["messages"][-1])


async def saltos(texto: str) -> None:
    """Muestra nodos y herramientas usados por una consulta nueva."""
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    total = 0
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
                for llamada in getattr(mensaje, "tool_calls", None) or []:
                    print(f"  herramienta: {llamada['name']}({llamada['args']})")
    print(f"Saltos: {total}")


def diagrama() -> None:
    """Imprime el diagrama Mermaid sin ejecutar el modelo."""
    print(graph.get_graph().draw_mermaid())
