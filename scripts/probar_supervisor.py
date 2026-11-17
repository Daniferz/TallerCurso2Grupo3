"""Envía seis preguntas al coordinador A2A y resume sus decisiones.

Uso:
    python scripts/probar_supervisor.py

Requiere el coordinador activo en URL_COORDINADOR y al menos un agente disponible.
"""

import asyncio
import re
import sys
import uuid
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from src.comun.registro import CATALOGO
from src.portal.cliente import ErrorAgente, enviar_mensaje, esta_en_linea


PREGUNTAS = [
    "Quiero volar de Santiago a Lima el 15 de marzo.",
    "Busca hoteles en Bogotá para dos noches.",
    "¿Dónde puedo comer parrillas en Buenos Aires?",
    "Dame más datos de Don Julio.",
    "Estoy organizando un fin de semana en Lima, ¿qué debería considerar?",
    "¿Quién ganó el mundial de fútbol de 1962?",
]


def _en_una_linea(error: Exception) -> str:
    """Deja los errores en un renglón, sin stack trace."""
    texto = " ".join(str(error).split())
    return texto or error.__class__.__name__


def _resumir(respuesta: str) -> tuple[str, str, str]:
    """Extrae agente, motivo y comienzo de la respuesta marcada por el supervisor."""
    lineas = respuesta.splitlines()
    primera = lineas[0] if lineas else ""
    coincidencia = re.match(r"^\[(.+?)\]\s*(.*)$", primera)
    if coincidencia:
        agente, inicio = coincidencia.groups()
    elif primera.startswith("No tengo un agente"):
        agente, inicio = "ninguno", primera
    else:
        agente, inicio = "sin identificar", primera

    motivo = next(
        (
            linea.split(":", 1)[1].strip()
            for linea in lineas
            if linea.startswith("Motivo de selección:")
        ),
        "No informado",
    )
    return agente, motivo, inicio[:72]


async def probar() -> int:
    """Consulta los seis casos al servidor y muestra una tabla de resultados."""
    coordinador = CATALOGO["coordinador"]
    if not await esta_en_linea(coordinador):
        print(f"El coordinador no está escuchando en {coordinador.url}.")
        print("Levántalo con: uvicorn src.coordinador.server:app --port 8002 --reload")
        return 1

    filas: list[tuple[str, str, str, str]] = []
    for pregunta in PREGUNTAS:
        try:
            resultado = await enviar_mensaje(
                coordinador,
                pregunta,
                context_id=str(uuid.uuid4()),
            )
            agente, motivo, inicio = _resumir(resultado["respuesta"])
        except ErrorAgente as error:
            agente, motivo, inicio = "error", _en_una_linea(error), "Sin respuesta"
        filas.append((pregunta, agente, motivo, inicio))

    anchos = (47, 25, 58, 72)
    encabezados = ("Pregunta", "Agente elegido", "Motivo", "Inicio de respuesta")
    print(" | ".join(texto[:ancho].ljust(ancho) for texto, ancho in zip(encabezados, anchos)))
    print("-+-".join("-" * ancho for ancho in anchos))
    for fila in filas:
        print(" | ".join(texto[:ancho].ljust(ancho) for texto, ancho in zip(fila, anchos)))
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(probar()))
