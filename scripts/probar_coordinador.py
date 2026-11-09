"""Le hace dos preguntas seguidas al coordinador con el mismo context_id.

La primera pregunta deja un dato (el nombre y el destino). La segunda pregunta
por ese dato: si el coordinador pasa el mismo context_id al agente de viajes,
la respuesta demuestra que el hilo recuerda lo anterior.

Uso:
    python scripts/probar_coordinador.py

Requiere el coordinador en URL_COORDINADOR y el agente de viajes en URL_VIAJES.
"""

import asyncio
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from src.comun.registro import CATALOGO
from src.portal.cliente import ErrorAgente, enviar_mensaje, esta_en_linea


PRIMERA_PREGUNTA = "Me llamo Dani y quiero volar a Lima el 15 de marzo."
SEGUNDA_PREGUNTA = "¿Cómo me llamo yo y a qué ciudad quiero volar?"

# Palabra que solo puede salir si la segunda respuesta usa lo de la primera.
PISTA = "dani"


def _en_una_linea(error: Exception) -> str:
    """Deja el error en un solo renglón, sin stack trace."""
    texto = " ".join(str(error).split())
    return texto or error.__class__.__name__


async def probar() -> int:
    coordinador = CATALOGO["coordinador"]
    viajes = CATALOGO["viajes"]

    if not await esta_en_linea(coordinador):
        print(f"El coordinador no está escuchando en {coordinador.url}.")
        print("Levántalo con: uvicorn src.coordinador.server:app --port 8002")
        return 1

    if not await esta_en_linea(viajes):
        # El coordinador solo repite lo que diga el agente de viajes.
        print(f"Aviso: el agente de viajes no responde en {viajes.url}.")
        print("El coordinador no podrá responder hasta que lo levantes en el 8000.")

    contexto = "hilo-de-prueba-coordinador"

    try:
        primera = await enviar_mensaje(coordinador, PRIMERA_PREGUNTA, contexto)
        segunda = await enviar_mensaje(coordinador, SEGUNDA_PREGUNTA, contexto)
    except ErrorAgente as error:
        print(f"Error: {_en_una_linea(error)}")
        return 1

    print(f"1) {PRIMERA_PREGUNTA}")
    print(f"   {primera['respuesta']}")
    print(f"   ({primera['latencia_ms']} ms)")
    print()
    print(f"2) {SEGUNDA_PREGUNTA}")
    print(f"   {segunda['respuesta']}")
    print(f"   ({segunda['latencia_ms']} ms)")
    print()
    print(f"contexto compartido: {segunda['context_id']}")

    recuerda = PISTA in segunda["respuesta"].lower()
    if recuerda:
        print("OK: la segunda respuesta recuerda la primera.")
    else:
        print("La segunda respuesta no repitió el dato de la primera.")
        print("Revisa que el agente de viajes esté corriendo en el 8000.")

    return 0 if recuerda else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(probar()))
