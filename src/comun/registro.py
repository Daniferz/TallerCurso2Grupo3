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
    "pato": Agente(
        clave="pato",
        nombre="Agente de Entrenamiento de Pato",
        descripcion=(
            "Explica la anatomía y función de los músculos y arma rutinas de gimnasio con base científica "
            "por grupo muscular (pecho, espalda, piernas, glúteos, hombros, brazos, core o cuerpo completo), "
            "según objetivo (hipertrofia, fuerza o resistencia), nivel y días por semana. "
            "No da dietas, alimentación ni suplementos, no diagnostica ni trata lesiones o dolores existentes (sí orienta ejercicios de prevención), "
            "y no responde sobre otros deportes, viajes, restaurantes ni maletas."
        ),
        paquete="src.agente_pato",
        url=_url("URL_PATO", "http://127.0.0.1:8005"),
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
    "cristian": Agente(
        clave="cristian",
        nombre="Agente de cristian",
        descripcion=(
            "Recomienda sitios turísticos con ubicación, horarios, precios e imágenes referenciales. "
            "No busca vuelos u hoteles, no reserva, no informa el clima ni restricciones."
        ),
        paquete="src.agente_cristian",
        url=_url("URL_CRISTIAN", "http://127.0.0.1:8004"),
    ),
}

# Nombre corto -> paquete donde vive el agente (es lo que consume main.py).
AGENTES = {clave: agente.paquete for clave, agente in CATALOGO.items()}
