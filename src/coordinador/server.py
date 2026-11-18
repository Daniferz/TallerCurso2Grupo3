"""Servidor A2A del coordinador."""

from src.comun.registro import CATALOGO
from src.comun.servidor import crear_app
from src.comun.tarjeta import crear_tarjeta

from .catalogo import descubrir
from .graph import responder


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
