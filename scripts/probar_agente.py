"""Manda una pregunta a un agente A2A levantado y muestra su respuesta.

Uso:
    python scripts/probar_agente.py restaurantes "parrillas en Buenos Aires"
    python scripts/probar_agente.py viajes "vuelo a Lima" --contexto mi-hilo

Sirve para comprobar el servidor de verdad: primero pregunta a /salud y después
habla por JSON-RPC (message/send, A2A 0.3), igual que la consola web.
"""

import argparse
import asyncio
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from src.comun.registro import CATALOGO
from src.portal.cliente import ErrorAgente, enviar_mensaje, esta_en_linea


def _en_una_linea(error: Exception) -> str:
    """Deja el error en un solo renglón, sin stack trace."""
    texto = " ".join(str(error).split())
    return texto or error.__class__.__name__


async def probar(nombre: str, pregunta: str, contexto: str | None) -> int:
    """Revisa que el agente esté en línea, le manda la pregunta y muestra la respuesta."""
    agente = CATALOGO[nombre]

    if not await esta_en_linea(agente):
        print(f"{agente.nombre} no está escuchando en {agente.url}.")
        print("Levántalo primero con uvicorn, en el entorno que le corresponde.")
        return 1

    try:
        resultado = await enviar_mensaje(agente, pregunta, contexto)
    except ErrorAgente as error:
        print(f"Error: {_en_una_linea(error)}")
        return 1

    print(resultado["respuesta"])
    print(
        f"\n(contexto: {resultado['context_id']}, "
        f"{resultado['latencia_ms']} ms)"
    )
    return 0


def main() -> int:
    analizador = argparse.ArgumentParser(
        description="Prueba un agente A2A del proyecto desde la terminal."
    )
    analizador.add_argument("agente", choices=sorted(CATALOGO), help="Agente a probar.")
    analizador.add_argument("pregunta", help="Texto que se le manda al agente.")
    analizador.add_argument(
        "--contexto",
        default=None,
        help="Identificador del hilo. Repítelo para probar que el agente recuerda.",
    )
    argumentos = analizador.parse_args()
    return asyncio.run(probar(argumentos.agente, argumentos.pregunta, argumentos.contexto))


if __name__ == "__main__":
    sys.exit(main())
