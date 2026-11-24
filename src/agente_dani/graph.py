"""Agente de maleta en LangGraph: Gemini, guía de equipaje y memoria por contexto."""

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
from .tools import lista_equipaje


load_dotenv()

MODELO = os.getenv("MODELO", "gemini-3.5-flash-lite")

if not os.getenv("GOOGLE_API_KEY"):
    raise RuntimeError("Falta GOOGLE_API_KEY: cópiala en el archivo .env.")

modelo = ChatGoogleGenerativeAI(model=MODELO, temperature=0)

graph = create_agent(
    modelo,
    tools=[lista_equipaje],
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


# Línea de ítem que arma la herramienta lista_equipaje: "- 4 × ropa interior" o "- gorro".
_ITEM = re.compile(r"^-\s+(?:(?P<cantidad>\d+)\s*×\s*)?(?P<nombre>.+?)\s*$", re.M)


def _plano(texto: str) -> str:
    """Minúsculas, sin tildes ni markdown, para comparar sin importar el formato."""
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return " ".join(re.sub(r"[*_`#]", "", sin_tildes).lower().split())


def _lista_del_turno(mensajes: list[BaseMessage]) -> str | None:
    """Última salida de lista_equipaje posterior al mensaje más reciente de la persona."""
    for mensaje in reversed(mensajes):
        if isinstance(mensaje, HumanMessage):
            return None
        if isinstance(mensaje, ToolMessage) and mensaje.name == "lista_equipaje":
            return _texto(mensaje)
    return None


def _falta_algun_item(lista_herramienta: str, respuesta: str) -> bool:
    """True si la respuesta no trae algún ítem (o su cantidad) de la herramienta."""
    plano = _plano(respuesta)
    for item in _ITEM.finditer(lista_herramienta):
        nombre = _plano(item["nombre"])
        if not nombre or nombre not in plano:
            return True
        if item["cantidad"] and not re.search(
            rf"(?<!\d){re.escape(item['cantidad'])}(?!\d)", plano
        ):
            return True
    return False


def _pide_datos_faltantes(respuesta: str) -> bool:
    """Evita agregar una lista si el modelo está aclarando datos antes de responder."""
    plano = _plano(respuesta)
    campos = ("dia", "temporada", "mes", "destino")
    return "?" in respuesta and any(campo in plano for campo in campos)


def completar_respuesta(mensajes: list[BaseMessage]) -> str:
    """Si el modelo omite ítems, agrega la lista exacta de la herramienta."""
    respuesta = _texto(mensajes[-1]).strip()
    lista_herramienta = _lista_del_turno(mensajes)
    if (
        lista_herramienta
        and not _pide_datos_faltantes(respuesta)
        and _falta_algun_item(lista_herramienta, respuesta)
    ):
        return f"{respuesta}\n\n{lista_herramienta}".strip()
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
