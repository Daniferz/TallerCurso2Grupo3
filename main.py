"""Entrada única por terminal para los tres agentes.

Uso:
    python main.py viajes "pregunta"
    python main.py restaurantes "pregunta" --saltos
    python main.py pato "pregunta" --saltos
    python main.py coordinador "pregunta" --diagrama
"""

import argparse
import asyncio
import importlib
import inspect
import sys
import uuid
from pathlib import Path

from src.comun.errores import en_una_linea
from src.comun.registro import AGENTES, MODULOS_AGENTE

# En Windows la consola no siempre usa UTF-8: forzamos la salida para que los acentos se vean bien.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path(__file__).resolve().parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))


def cargar_modulo_agente(nombre):
    """Devuelve el módulo graph.py o crew.py del agente, o None si todavía no existe."""
    paquete = AGENTES[nombre]
    carpeta = RAIZ / paquete.replace(".", "/")
    for modulo in MODULOS_AGENTE:
        if (carpeta / f"{modulo}.py").exists():
            return importlib.import_module(f"{paquete}.{modulo}")
    return None


def ejecutar(funcion, *argumentos):
    """Llama a la función y espera el resultado si es async."""
    resultado = funcion(*argumentos)
    if inspect.isawaitable(resultado):
        return asyncio.run(resultado)
    return resultado


def main():
    analizador = argparse.ArgumentParser(
        description="Conversa con uno de los agentes del proyecto."
    )
    analizador.add_argument("agente", choices=sorted(AGENTES), help="Agente a consultar.")
    analizador.add_argument("pregunta", nargs="?", default="", help="Texto de la consulta.")
    analizador.add_argument(
        "--saltos",
        action="store_true",
        help="Muestra por qué nodos y herramientas pasó el agente.",
    )
    analizador.add_argument(
        "--diagrama",
        action="store_true",
        help="Imprime la estructura del agente en Mermaid, sin ejecutarlo.",
    )
    argumentos = analizador.parse_args()

    try:
        modulo = cargar_modulo_agente(argumentos.agente)
    except Exception as error:
        # Por ejemplo, falta GOOGLE_API_KEY en .env: un renglón y listo.
        print(f"No se pudo cargar el agente {argumentos.agente}: {en_una_linea(error)}")
        return 1

    if modulo is None:
        print(f"Ese agente todavía no existe: {argumentos.agente}.")
        return 1

    try:
        if argumentos.diagrama:
            resultado = ejecutar(modulo.diagrama)
        elif argumentos.saltos:
            resultado = ejecutar(modulo.saltos, argumentos.pregunta)
        else:
            resultado = ejecutar(modulo.responder, argumentos.pregunta, str(uuid.uuid4()))
    except Exception as error:
        # Un solo renglón, sin stack trace.
        print(f"No se pudo completar la consulta: {en_una_linea(error)}")
        return 1

    # responder() devuelve texto; saltos() y diagrama() ya imprimen lo suyo.
    if resultado is not None:
        print(resultado)

    return 0


if __name__ == "__main__":
    sys.exit(main())
