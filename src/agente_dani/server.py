"""Servidor A2A del Agente de Maleta de Dani."""

from src.comun.registro import CATALOGO
from src.comun.servidor import crear_app
from src.comun.tarjeta import crear_tarjeta

from .graph import responder


agente = CATALOGO["dani"]

tarjeta = crear_tarjeta(
    agente.nombre,
    agente.descripcion,
    agente.url,
    [
        (
            "lista_equipaje",
            "Lista de equipaje",
            "Arma una lista por categorías para Punta Arenas, Pucón o Iquique, según los días y la temporada, usando guías estáticas.",
            "Voy cinco días a Punta Arenas en julio, ¿qué debería llevar?",
        ),
    ],
)

app = crear_app(tarjeta, responder)
