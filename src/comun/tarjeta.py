"""Ficha (Agent Card) que cada agente publica para que lo encuentren por A2A."""

from collections.abc import Iterable

from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill
from a2a.utils.constants import PROTOCOL_VERSION_1_0, TransportProtocol


VERSION_AGENTE = "1.0.0"
TIPOS_TEXTO = ("text/plain",)

# Cada skill es (id, nombre, descripción, ejemplo).
Skill = tuple[str, str, str, str]


def crear_tarjeta(
    nombre: str,
    descripcion: str,
    url: str,
    skills: Iterable[Skill],
) -> AgentCard:
    """Arma la ficha del agente: quién es, dónde vive y qué sabe hacer."""
    habilidades = list(skills)
    if not habilidades:
        # La spec A2A exige al menos un skill: sin ellos la consola no puede
        # mostrar nada de lo que sabe hacer el agente.
        raise ValueError(
            f"La ficha de {nombre} necesita al menos un skill: la spec A2A lo exige."
        )

    return AgentCard(
        name=nombre,
        description=descripcion,
        version=VERSION_AGENTE,
        # En a2a-sdk 1.3 la dirección va en las interfaces, no en un campo "url".
        supported_interfaces=[
            AgentInterface(
                url=url,
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
