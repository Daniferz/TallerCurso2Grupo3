"""Servidor A2A del agente de viajes."""

from src.comun.registro import CATALOGO
from src.comun.servidor import crear_app
from src.comun.tarjeta import crear_tarjeta

from .graph import responder


agente = CATALOGO["viajes"]

tarjeta = crear_tarjeta(
    agente.nombre,
    agente.descripcion,
    agente.url,
    [
        (
            "buscar_vuelos",
            "Buscar vuelos",
            "Encuentra vuelos entre Santiago, Lima, Bogotá y Buenos Aires con horarios y precios en pesos chilenos.",
            "¿Cuánto cuesta volar de Santiago a Lima el 15 de marzo?",
        ),
        (
            "buscar_hoteles",
            "Buscar hoteles",
            "Encuentra hoteles por ciudad y calcula el total según las noches de estadía.",
            "Busca hoteles en Lima para tres noches.",
        ),
    ],
    usar_url_publica=False,
)

app = crear_app(tarjeta, responder)
