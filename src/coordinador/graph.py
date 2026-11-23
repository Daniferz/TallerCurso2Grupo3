"""Supervisor LangGraph: elige uno o varios agentes del catálogo y delega por A2A."""

import asyncio
import os
import re
import uuid
import unicodedata
from html import escape

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from pydantic import BaseModel, Field

from src.comun.errores import en_una_linea
from src.canal.telegram import avisar_chat

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


# Una pregunta puede tocar varios temas; como máximo se consulta a este número de agentes.
MAXIMO_AGENTES = 3


class Consulta(BaseModel):
    """Un agente elegido y la parte de la pregunta que le corresponde."""

    agente: str = Field(description="Nombre exacto de un agente del catálogo.")
    pregunta: str = Field(
        description=(
            "La parte de la pregunta actual que responde ese agente, escrita como pregunta "
            "completa y copiando textualmente los datos de la persona (días, ciudad, "
            "temporada, objetivo, nivel...)."
        )
    )


class Decision(BaseModel):
    """Selección estructurada del supervisor: ninguno, uno o varios agentes."""

    consultas: list[Consulta] = Field(
        default_factory=list,
        description=(
            "Un elemento por cada agente que debe responder una parte de la pregunta actual; "
            "lista vacía si ningún agente del catálogo aplica."
        ),
    )
    motivo: str = Field(description="Motivo breve de la selección, en una frase.")

    @property
    def agente(self) -> str:
        """Nombres elegidos separados por coma, o 'ninguno' (lo usan /chat y --saltos)."""
        return ", ".join(consulta.agente for consulta in self.consultas) or "ninguno"


modelo_decision = modelo.with_structured_output(Decision)


class EstadoSupervisor(MessagesState, total=False):
    """Estado conversacional más la decisión de enrutamiento del supervisor."""

    # Nombres elegidos separados por coma, o "ninguno" (lo leen /chat y --saltos).
    agente: str
    motivo: str
    # [{"agente": nombre, "pregunta": parte de la pregunta}]; vacía si no aplica ninguno.
    consultas: list[dict]


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


def _es_saludo(texto: str) -> bool:
    """Reconoce saludos simples sin desviar preguntas que además tienen un tema."""
    plano = unicodedata.normalize("NFKD", texto)
    plano = plano.encode("ascii", "ignore").decode("ascii").lower()
    plano = " ".join(re.sub(r"[^\w\s]", " ", plano).split())
    return plano in {
        "hola",
        "hola hola",
        "holi",
        "hey",
        "buenas",
        "buen dia",
        "buenos dias",
        "buenas tardes",
        "buenas noches",
        "saludos",
        "que tal",
        "como estas",
    }


def primer_nodo(estado: EstadoSupervisor) -> str:
    """Enruta un saludo simple al nodo de bienvenida y lo demás al supervisor."""
    pregunta = _texto(estado["messages"][-1])
    return "saludo" if _es_saludo(pregunta) else "supervisor"


def _nombre_para_saludo(agente: AgenteDescubierto) -> str:
    """Presenta los nombres de las tres áreas en términos reconocibles."""
    nombre = agente.nombre.lower()
    descripcion = agente.descripcion.lower()
    if "maleta" in nombre or "equipaje" in descripcion:
        return "Maleta"
    if "entrenamiento" in nombre or "rutina" in descripcion:
        return "Entrenamiento"
    if "sitio" in nombre or "cristian" in nombre or "lugares para visitar" in descripcion:
        return "Sitios turísticos"
    return agente.nombre


def _primera_frase(texto: str) -> str:
    """Reduce la descripción de una ficha a una frase para la bienvenida."""
    texto = " ".join(texto.split())
    primera = re.split(r"(?<=[.!?])\s+", texto, maxsplit=1)[0].strip()
    if primera and primera[-1] not in ".!?":
        primera += "."
    return primera


async def saludo(estado: EstadoSupervisor) -> dict:
    """Da la bienvenida y describe brevemente los agentes disponibles."""
    agentes = await descubrir()
    if not agentes:
        contenido = (
            "¡Hola! En este momento no puedo consultar qué agentes están disponibles. "
            "Inténtalo nuevamente en un momento."
        )
    else:
        lineas = [
            f"- {_nombre_para_saludo(agente)}: {_primera_frase(agente.descripcion)}"
            for agente in agentes
        ]
        contenido = "¡Hola! Puedo ayudarte con:\n" + "\n".join(lineas)
    return {"messages": [AIMessage(content=contenido)]}


def _entrada_supervisor(mensajes: list[BaseMessage]) -> str:
    """Delimita las preguntas anteriores y la actual como datos del usuario."""
    preguntas = [
        _texto(mensaje).strip()
        for mensaje in mensajes
        if isinstance(mensaje, HumanMessage) and _texto(mensaje).strip()
    ]
    if not preguntas:
        return (
            "<historial_usuario></historial_usuario>\n"
            "<pregunta_actual></pregunta_actual>"
        )
    anteriores = preguntas[:-1]
    historial = "\n".join(
        f"<mensaje>{escape(pregunta)}</mensaje>" for pregunta in anteriores
    )
    actual = escape(preguntas[-1])
    return (
        f"<historial_usuario>{historial}</historial_usuario>\n"
        f"<pregunta_actual>{actual}</pregunta_actual>"
    )


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
    entrada = _entrada_supervisor(estado["messages"])
    if not agentes:
        return {"agente": "ninguno", "consultas": [], "motivo": "No hay agentes disponibles."}

    try:
        decision = await modelo_decision.ainvoke(
            [
                SystemMessage(content=_prompt_catalogo(agentes)),
                HumanMessage(content=entrada),
            ]
        )
    except Exception as error:
        # Si el modelo falla no hay decisión: se informa el error, no "sin agente".
        raise RuntimeError(
            f"el coordinador no pudo evaluar la pregunta: {en_una_linea(error)}"
        ) from None

    consultas = consultas_validas(decision, agentes, _texto(estado["messages"][-1]))
    if decision.consultas and not consultas:
        return {
            "agente": "ninguno",
            "consultas": [],
            "motivo": "El agente elegido no está disponible en el catálogo actual.",
        }
    return {
        "agente": ", ".join(consulta["agente"] for consulta in consultas) or "ninguno",
        "consultas": consultas,
        "motivo": motivo_seguro(decision.motivo, agentes),
    }


def consultas_validas(
    decision: Decision, agentes: list[AgenteDescubierto], pregunta_original: str
) -> list[dict]:
    """Deja solo agentes del catálogo, sin repetir y como máximo MAXIMO_AGENTES.

    Si queda un solo agente, recibe la pregunta original tal cual (así su respuesta es la
    misma que si se le pregunta directo). Con varios, cada uno recibe su parte.
    """
    disponibles = {agente.nombre for agente in agentes}
    consultas: list[dict] = []
    for consulta in decision.consultas:
        nombre = consulta.agente
        if nombre in disponibles and nombre not in {c["agente"] for c in consultas}:
            parte = " ".join((consulta.pregunta or "").split()) or pregunta_original
            consultas.append({"agente": nombre, "pregunta": parte})
    consultas = consultas[:MAXIMO_AGENTES]
    if len(consultas) == 1:
        consultas[0]["pregunta"] = pregunta_original
    return consultas


def aviso_no_disponible(nombre: str) -> str:
    """Mensaje para la persona cuando el agente elegido no contesta (sin detalles técnicos)."""
    return (
        f"La parte de {nombre} no está disponible en este momento. "
        "Puedes seguir preguntando sobre los otros temas."
    )


def siguiente(estado: EstadoSupervisor) -> str:
    """Enruta la decisión hacia el agente remoto o la respuesta sin agente."""
    return "agente_remoto" if estado.get("consultas") else "sin_agente"


async def _respuesta_de(
    elegido: AgenteDescubierto, pregunta: str, context_id: str, varios: bool
) -> tuple[str, bool]:
    """(texto, respondió): respuesta etiquetada de un agente, o su aviso claro si no contesta.

    Con un solo agente, una falla distinta de "no disponible" se propaga como error (nunca
    éxito falso). Con varios, esa parte dice claramente que falló y las demás se entregan.
    """
    try:
        respuesta = await preguntar(elegido.cliente, pregunta, context_id)
    except AgenteNoDisponible as error:
        # Agente apagado o dormido: aviso claro a la persona y el detalle solo en la terminal.
        print(f"Aviso: {elegido.nombre} ({elegido.url}) no respondió: {en_una_linea(error)}", flush=True)
        return aviso_no_disponible(elegido.nombre), False
    except Exception as error:
        detalle = f"{elegido.nombre} no pudo responder: {en_una_linea(error)}"
        if not varios:
            # La falla del agente remoto se propaga como error, no como respuesta.
            raise RuntimeError(detalle) from None
        print(f"Aviso: {detalle}", flush=True)
        return f"La parte de {elegido.nombre} tuvo un error y no se pudo responder.", False
    # La respuesta del agente va tal cual: solo se agrega la etiqueta [Nombre].
    return f"[{elegido.nombre}] {respuesta}", True


async def agente_remoto(estado: EstadoSupervisor, config) -> dict:
    """Pregunta en paralelo a los agentes elegidos y junta sus respuestas sin alterarlas."""
    agentes = {agente.nombre: agente for agente in await descubrir()}
    consultas = [c for c in estado.get("consultas") or [] if c["agente"] in agentes]
    if not consultas:
        return await sin_agente(estado, config)

    thread_id = (config.get("configurable") or {}).get("thread_id")
    context_id = thread_id or str(uuid.uuid4())
    varios = len(consultas) > 1
    partes = await asyncio.gather(
        *(
            _respuesta_de(agentes[c["agente"]], c["pregunta"], context_id, varios)
            for c in consultas
        )
    )
    if not varios and not partes[0][1]:
        # Un solo agente y no contestó: solo el aviso claro, igual que antes.
        return {"messages": [AIMessage(content=partes[0][0])]}
    contenido = (
        "\n\n".join(texto for texto, _ in partes)
        + f"\nMotivo de selección: {estado.get('motivo', 'Sin motivo informado.')}"
    )
    return {"messages": [AIMessage(content=contenido)]}


async def sin_agente(estado: EstadoSupervisor, config=None) -> dict:
    """Responde con los temas cubiertos por los agentes disponibles."""
    agentes = await descubrir()
    configuracion = (config or {}).get("configurable") or {}
    conversacion_id = configuracion.get("thread_id") or "sin-contexto"
    pregunta = _texto(estado["messages"][-1])
    await avisar_chat(pregunta, conversacion_id)
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
    primer_nodo,
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
                for consulta in datos.get("consultas") or []:
                    print(f"    - {consulta['agente']} recibe: {consulta['pregunta']}")
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
