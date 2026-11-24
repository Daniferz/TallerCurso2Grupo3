"""Servidor A2A del agente de sitios turísticos de Cristian."""

from src.comun.registro import CATALOGO
from src.comun.servidor import crear_app
from src.comun.tarjeta import crear_tarjeta

from .graph import responder


agente = CATALOGO["cristian"]

tarjeta = crear_tarjeta(
    agente.nombre,
    agente.descripcion,
    agente.url,
    [
        (
            "listado_sitios_turisticos",
            "Recomendar lugares",
            "Devuelve lugares para visitar en Santiago, Lima, Bogotá, Cusco y Valparaíso, con descripción, ubicación, precio e imagen referenciales.",
            "Voy a Lima el sábado, ¿qué lugares turísticos me recomiendas?",
        ),
        (
            "horario_atencion",
            "Consultar horarios",
            "Indica el horario registrado de un lugar turístico para el día consultado.",
            "¿A qué hora puedo visitar el Cerro San Cristóbal el domingo?",
        ),
    ],
)

app = crear_app(tarjeta, responder, agente.variable_clave)
