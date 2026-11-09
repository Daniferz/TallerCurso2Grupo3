"""Ficha (Agent Card) que cada agente publica para que lo encuentren por A2A."""

import os
from collections.abc import Iterable
from pathlib import Path

from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill
from a2a.utils.constants import PROTOCOL_VERSION_1_0, TransportProtocol
from dotenv import load_dotenv


VERSION_AGENTE = "1.0.0"
TIPOS_TEXTO = ("text/plain",)
RAIZ = Path(__file__).resolve().parents[2]
load_dotenv(RAIZ / ".env")

# Cada skill es (id, nombre, descripción, ejemplo).
Skill = tuple[str, str, str, str]


def crear_tarjeta(
    nombre: str,
    descripcion: str,
    url: str,
    skills: Iterable[Skill],
    *,
    usar_url_publica: bool = True,
) -> AgentCard:
    """Arma una ficha; los servidores base pueden excluir el override global."""
    habilidades = list(skills)
    if not habilidades:
        # La spec A2A exige al menos un skill: sin ellos la consola no puede
        # mostrar nada de lo que sabe hacer el agente.
        raise ValueError(
            f"La ficha de {nombre} necesita al menos un skill: la spec A2A lo exige."
        )

    url_publica = os.getenv("URL_PUBLICA", "").strip().rstrip("/") if usar_url_publica else ""
    url_ficha = url_publica or url.rstrip("/")

    return AgentCard(
        name=nombre,
        description=descripcion,
        version=VERSION_AGENTE,
        # En a2a-sdk 1.3 la dirección va en las interfaces, no en un campo "url".
        supported_interfaces=[
            AgentInterface(
                url=url_ficha,
                protocol_binding=TransportProtocol.JSONRPC.value,
                protocol_version=PROTOCOL_VERSION_1_0,
            )
        ],
        capabilities=AgentCapabilities(streaming=False),
        default_input_modes=list(TIPOS_TEXTO),
        default_output_modes=list(TIPOS_TEXTO),
        skills=[
            AgentSkill(
                id=identificador,
                name=nombre_skill,
                description=descripcion_skill,
                # a2a-sdk 1.3 marca "tags" como obligatorio; usamos el id como etiqueta.
                tags=[identificador],
                examples=[ejemplo],
            )
            for identificador, nombre_skill, descripcion_skill, ejemplo in habilidades
        ],
    )
