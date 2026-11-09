"""Servidor A2A del agente de restaurantes."""

from src.comun.registro import CATALOGO
from src.comun.servidor import crear_app
from src.comun.tarjeta import crear_tarjeta

from .crew import responder


agente = CATALOGO["restaurantes"]

tarjeta = crear_tarjeta(
    agente.nombre,
    agente.descripcion,
    agente.url,
    [
        (
            "buscar_restaurantes",
            "Buscar restaurantes",
            "Encuentra restaurantes por ciudad y tipo de comida, con zona, precio medio en CLP y horario.",
            "Busca parrillas en Buenos Aires.",
        ),
        (
            "detalle_restaurante",
            "Detalle de restaurante",
            "Entrega la ficha completa de un restaurante: zona, tipo, precio, horario y plato recomendado.",
            "Dame más datos de Don Julio.",
        ),
    ],
)

app = crear_app(tarjeta, responder)
