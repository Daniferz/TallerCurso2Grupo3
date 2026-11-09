"""Registro de agentes del proyecto: una sola lista para la terminal y la consola web."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


RAIZ = Path(__file__).resolve().parents[2]

# Se lee el .env del proyecto aunque uvicorn se lance desde otra carpeta.
load_dotenv(RAIZ / ".env")

# Un agente puede estar hecho con LangGraph (graph.py) o con CrewAI (crew.py).
MODULOS_AGENTE = ("graph", "crew")


@dataclass(frozen=True)
class Agente:
    """Ficha mínima de un agente: cómo se llama, qué hace y dónde escucha."""

    clave: str
    nombre: str
    descripcion: str
    paquete: str
    url: str

    @property
    def carpeta(self) -> Path:
        """Carpeta del paquete donde vive el agente."""
        return RAIZ / self.paquete.replace(".", "/")

    @property
    def disponible(self) -> bool:
        """True solo si ya existen el agente y su servidor A2A."""
        tiene_agente = any(
            (self.carpeta / f"{modulo}.py").exists() for modulo in MODULOS_AGENTE
        )
        return tiene_agente and (self.carpeta / "server.py").exists()


def _url(variable: str, defecto: str) -> str:
    """Lee la URL del .env y le quita la barra final para no armar rutas dobles."""
    return os.getenv(variable, defecto).rstrip("/")


CATALOGO: dict[str, Agente] = {
    "viajes": Agente(
        clave="viajes",
        nombre="Agente de viajes",
        descripcion=(
            "Busca vuelos y hoteles entre SCL, LIM, BOG y EZE con precios en CLP. "
            "No reserva ni cobra."
        ),
        paquete="src.agente_viajes",
        url=_url("URL_VIAJES", "http://127.0.0.1:8000"),
    ),
    "restaurantes": Agente(
        clave="restaurantes",
        nombre="Agente de restaurantes",
        descripcion=(
            "Recomienda restaurantes en LIM, BOG y EZE por zona y tipo de comida. "
            "No reserva."
        ),
        paquete="src.agente_restaurantes",
        url=_url("URL_RESTAURANTES", "http://127.0.0.1:8001"),
    ),
    "dani": Agente(
        clave="dani",
        nombre="Agente de Maleta de Dani",
        descripcion=(
            "Prepara listas de equipaje con ropa, documentos, tecnología y botiquín para Punta Arenas, Pucón e Iquique, según los días y la temporada. "
            "No busca ni compara vuelos, hoteles o precios, ni informa clima, visas o políticas de equipaje de aerolíneas."
        ),
        paquete="src.agente_dani",
        url=_url("URL_DANI", "http://127.0.0.1:8003"),
    ),
    "coordinador": Agente(
        clave="coordinador",
        nombre="Coordinador",
        descripcion=(
            "Recibe preguntas y elige entre viajes, restaurantes y agentes de compañeros configurados por URLS_AGENTES. "
            "Si ninguno corresponde, informa qué temas están disponibles."
        ),
        paquete="src.coordinador",
        url=_url("URL_COORDINADOR", "http://127.0.0.1:8002"),
    ),
}

# Nombre corto -> paquete donde vive el agente (es lo que consume main.py).
AGENTES = {clave: agente.paquete for clave, agente in CATALOGO.items()}
