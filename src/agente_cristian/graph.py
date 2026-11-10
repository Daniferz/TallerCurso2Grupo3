"""Agente de sitios turísticos con LangGraph y modelo Gemini."""

import os
import uuid

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver

from .prompts import SYSTEM_PROMPT
from .tools import horario_atencion, listado_sitios_turisticos


load_dotenv()

MODELO = os.getenv("MODELO", "gemini-3.5-flash-lite")

if not os.getenv("GOOGLE_API_KEY"):
    raise RuntimeError("Falta GOOGLE_API_KEY: cópiala en el archivo .env.")

# Se omite `temperature`: algunos modelos de Gemini muestran una alerta al
# recibir ese parámetro y utilizan su valor predeterminado correctamente.
modelo = ChatGoogleGenerativeAI(model=MODELO)

graph = create_agent(
    modelo,
    tools=[listado_sitios_turisticos, horario_atencion],
    system_prompt=SYSTEM_PROMPT,
    checkpointer=MemorySaver(),
)


def _texto(mensaje: BaseMessage) -> str:
    """Saca el texto de un mensaje, sea string o lista de bloques."""
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
    """Envía una consulta al agente y devuelve su última respuesta."""
    resultado = await graph.ainvoke(
        {"messages": [{"role": "user", "content": texto}]},
        config={"configurable": {"thread_id": context_id}},
    )
    return _texto(resultado["messages"][-1])


async def saltos(texto: str) -> None:
    """Muestra cada nodo y herramienta por los que pasa la consulta."""
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
    """Imprime el grafo en Mermaid sin llamar al modelo."""
    print(graph.get_graph().draw_mermaid())
