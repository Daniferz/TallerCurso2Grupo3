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
            "Lee las fichas de viajes, restaurantes y compañeros configurados, elige el agente adecuado y explica brevemente el motivo.",
            "¿Cuánto cuesta volar de Santiago a Lima?",
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

app = crear_app(tarjeta, responder)


@app.on_event("startup")
async def iniciar_supervisor() -> None:
    """Descubre las fichas una vez al arrancar el servidor."""
    agentes = await descubrir()
    print(f"Supervisor con {len(agentes)} agentes")
