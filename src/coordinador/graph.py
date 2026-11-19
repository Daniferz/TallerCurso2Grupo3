"""Supervisor LangGraph: elige un agente del catálogo y delega por A2A."""

import os
import re
import unicodedata
import uuid
from html import escape

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from pydantic import BaseModel, Field

from src.comun.errores import en_una_linea

from .catalogo import AgenteDescubierto, descubrir
from .cliente import AgenteNoDisponible, preguntar
from .prompts import (
    FRASES_PROTEGIDAS,
    LARGO_MAXIMO_MOTIVO,
    MOTIVO_POR_DEFECTO,
    PROMPT_SUPERVISOR,
)


load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    raise RuntimeError("Falta GOOGLE_API_KEY: cópiala en el archivo .env.")

MODELO = os.getenv("MODELO", "gemini-3.5-flash-lite")
modelo = ChatGoogleGenerativeAI(model=MODELO)


class Decision(BaseModel):
    """Selección estructurada del supervisor entre las fichas disponibles."""

    agente: str = Field(
        description="Nombre exacto de un agente del catálogo disponible o 'ninguno'."
    )
    motivo: str = Field(description="Motivo breve de la selección, en una frase.")


modelo_decision = modelo.with_structured_output(Decision)


class EstadoSupervisor(MessagesState, total=False):
    """Estado conversacional más la decisión de enrutamiento del supervisor."""

    agente: str
    motivo: str


def _texto(mensaje: BaseMessage) -> str:
    """Extrae el texto de un mensaje del modelo, sea string o bloques."""
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


def _normalizar_para_saludo(texto: str) -> str:
    """Normaliza acentos y signos para reconocer saludos simples."""
    descompuesto = unicodedata.normalize("NFD", texto or "")
    sin_tildes = "".join(
        letra for letra in descompuesto if unicodedata.category(letra) != "Mn"
    )
    return re.sub(r"[^a-z0-9 ]", "", sin_tildes.lower()).strip()


def _es_saludo(texto: str) -> bool:
    """Indica si el mensaje es un saludo sin una consulta adicional."""
    return _normalizar_para_saludo(texto) in {
        "hola",
        "holi",
        "hello",
        "hey",
        "buen dia",
        "buenos dias",
        "buenas tardes",
        "buenas noches",
        "saludos",
    }


def ruta_inicial(estado: EstadoSupervisor) -> str:
    """Envía los saludos al nodo informativo y el resto al supervisor."""
    ultimo = _texto(estado["messages"][-1])
    return "saludo" if _es_saludo(ultimo) else "supervisor"


def _prompt_catalogo(agentes: list[AgenteDescubierto]) -> str:
    """Incluye las fichas como datos delimitados, nunca como instrucciones."""
    fichas = "\n".join(
        "<agente>\n"
        f"<nombre>{escape(agente.nombre)}</nombre>\n"
        f"<descripcion>{escape(agente.descripcion)}</descripcion>\n"
        "</agente>"
        for agente in agentes
    )
    return PROMPT_SUPERVISOR.format(catalogo=fichas or "No hay agentes disponibles.")


def motivo_seguro(motivo: str, agentes: list[AgenteDescubierto]) -> str:
    """Deja el motivo en una frase breve y sin texto de las instrucciones ni de las fichas.

    El motivo se le muestra a la persona: aunque el prompt prohíbe revelar las
    instrucciones, se revisa también en código por si el modelo obedece una inyección.
    """
    texto = " ".join(str(motivo or "").split())
    bajo = texto.lower()
    filtra_prompt = any(frase.lower() in bajo for frase in FRASES_PROTEGIDAS)
    filtra_ficha = any(
        len(agente.descripcion) > 40 and agente.descripcion[:40].lower() in bajo
        for agente in agentes
    )
    if not texto or filtra_prompt or filtra_ficha:
        return MOTIVO_POR_DEFECTO
    if len(texto) > LARGO_MAXIMO_MOTIVO:
        texto = texto[:LARGO_MAXIMO_MOTIVO].rstrip() + "..."
    return texto


async def supervisor(estado: EstadoSupervisor) -> dict:
    """Elige con salida estructurada a partir de las fichas descubiertas."""
    agentes = await descubrir()
    if not agentes:
        return {"agente": "ninguno", "motivo": "No hay agentes disponibles."}

    try:
        historial = list(estado["messages"])
        decision = await modelo_decision.ainvoke(
            [
                SystemMessage(content=_prompt_catalogo(agentes)),
                *historial,
            ]
        )
    except Exception as error:
        # Si el modelo falla no hay decisión: se informa el error, no "sin agente".
        raise RuntimeError(
            f"el coordinador no pudo evaluar la pregunta: {en_una_linea(error)}"
        ) from None

    disponibles = {agente.nombre for agente in agentes}
    if decision.agente != "ninguno" and decision.agente not in disponibles:
        return {
            "agente": "ninguno",
            "motivo": "El agente elegido no está disponible en el catálogo actual.",
        }
    return {"agente": decision.agente, "motivo": motivo_seguro(decision.motivo, agentes)}


async def saludo(estado: EstadoSupervisor) -> dict:
    """Lista los agentes disponibles y el tema que cubre cada uno."""
    agentes = await descubrir()
    if not agentes:
        respuesta = "Hola. En este momento no hay agentes disponibles."
    else:
        temas = "\n".join(
            f"- {agente.nombre}: {agente.descripcion}" for agente in agentes
        )
        respuesta = f"Hola. Estos son los agentes disponibles:\n{temas}"
    return {"messages": [AIMessage(content=respuesta)]}


def aviso_no_disponible(nombre: str) -> str:
    """Mensaje para la persona cuando el agente elegido no contesta (sin detalles técnicos)."""
    return (
        f"La parte de {nombre} no está disponible en este momento. "
        "Puedes seguir preguntando sobre los otros temas."
    )


def siguiente(estado: EstadoSupervisor) -> str:
    """Enruta la decisión hacia el agente remoto o la respuesta sin agente."""
    return "sin_agente" if estado.get("agente") == "ninguno" else "agente_remoto"


async def agente_remoto(estado: EstadoSupervisor, config) -> dict:
    """Pregunta al agente elegido y etiqueta la respuesta con nombre y motivo."""
    agentes = await descubrir()
    elegido = next(
        (agente for agente in agentes if agente.nombre == estado.get("agente")),
        None,
    )
    if elegido is None:
        return await sin_agente(estado)

    pregunta = _texto(estado["messages"][-1])
    thread_id = (config.get("configurable") or {}).get("thread_id")
    context_id = thread_id or str(uuid.uuid4())
    try:
        respuesta = await preguntar(elegido.cliente, pregunta, context_id)
    except AgenteNoDisponible as error:
        # Agente apagado o dormido: aviso claro a la persona y el detalle solo en la terminal.
        print(f"Aviso: {elegido.nombre} ({elegido.url}) no respondió: {en_una_linea(error)}", flush=True)
        return {"messages": [AIMessage(content=aviso_no_disponible(elegido.nombre))]}
    except Exception as error:
        # La falla del agente remoto se propaga como error, no como respuesta.
        raise RuntimeError(
            f"{elegido.nombre} no pudo responder: {en_una_linea(error)}"
        ) from None

    contenido = (
        f"[{elegido.nombre}] {respuesta}\n"
        f"Motivo de selección: {estado.get('motivo', 'Sin motivo informado.')}"
    )
    return {"messages": [AIMessage(content=contenido)]}


async def sin_agente(estado: EstadoSupervisor) -> dict:
    """Responde con los temas cubiertos por los agentes disponibles."""
    agentes = await descubrir()
    nombres = ", ".join(agente.nombre for agente in agentes) or "ninguno disponible"
    motivo = estado.get("motivo", "La pregunta no corresponde a los agentes disponibles.")
    respuesta = (
        f"No tengo un agente para eso. Puedo ayudarte con: {nombres}.\n"
        f"Motivo de selección: {motivo}"
    )
    return {"messages": [AIMessage(content=respuesta)]}


grafo = StateGraph(EstadoSupervisor)
grafo.add_node("saludo", saludo)
grafo.add_node("supervisor", supervisor)
grafo.add_node("agente_remoto", agente_remoto)
grafo.add_node("sin_agente", sin_agente)
grafo.add_conditional_edges(
    START,
    ruta_inicial,
    {"saludo": "saludo", "supervisor": "supervisor"},
)
grafo.add_edge("saludo", END)
grafo.add_conditional_edges(
    "supervisor",
    siguiente,
    {"agente_remoto": "agente_remoto", "sin_agente": "sin_agente"},
)
grafo.add_edge("agente_remoto", END)
grafo.add_edge("sin_agente", END)
graph = grafo.compile(checkpointer=MemorySaver())


async def responder(texto: str, context_id: str) -> str:
    """Procesa una pregunta y devuelve el texto final del coordinador."""
    resultado = await graph.ainvoke(
        {"messages": [{"role": "user", "content": texto}]},
        config={"configurable": {"thread_id": context_id}},
    )
    return _texto(resultado["messages"][-1])


async def saltos(texto: str) -> None:
    """Muestra supervisor, agente elegido, motivo y nodo final recorrido."""
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
            if nodo == "supervisor":
                print(f"  agente elegido: {datos.get('agente', 'ninguno')}")
                print(f"  motivo: {datos.get('motivo', 'Sin motivo informado.')}")
            elif nodo == "agente_remoto":
                for mensaje in datos.get("messages", []):
                    print(f"  respuesta: {_texto(mensaje)}")
            elif nodo == "sin_agente":
                for mensaje in datos.get("messages", []):
                    print(f"  respuesta: {_texto(mensaje)}")
    print(f"Saltos: {total}")


def diagrama() -> None:
    """Imprime la estructura del supervisor en Mermaid."""
    print(graph.get_graph().draw_mermaid())
