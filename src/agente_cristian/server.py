"""Servidor A2A del agente de sitios turísticos de Cristian."""

import os

from dotenv import load_dotenv

from src.comun.servidor import crear_app
from src.comun.tarjeta import crear_tarjeta

from .graph import responder


load_dotenv()

tarjeta = crear_tarjeta(
    "Agente de cristian",
    "Recomienda lugares para visitar con descripción, ubicación, horarios, precios referenciales e imágenes. "
    "No responde sobre vuelos, hoteles, reservas, clima, visas, equipaje ni restricciones de los sitios.",
    os.getenv("URL_CRISTIAN", "http://127.0.0.1:8004"),
    [
        (
            "listado_sitios_turisticos",
            "Recomendar lugares",
            "Devuelve lugares para visitar en una ciudad con descripción, ubicación, precio e imagen referenciales.",
            "Voy a Lima el sábado, ¿qué lugares turísticos me recomiendas?",
        ),
        (
            "horario_atencion",
            "Consultar horarios",
            "Indica el horario registrado de un lugar turístico para el día consultado.",
            "¿A qué hora puedo visitar el Cerro San Cristóbal el domingo?",
        ),
    ],
    usar_url_publica=False,
)

app = crear_app(tarjeta, responder)
