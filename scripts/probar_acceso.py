"""Evidencia del control de acceso: tres llamadas reales a un agente levantado.

Uso:
    python scripts/probar_acceso.py                      # viajes, pregunta por defecto
    python scripts/probar_acceso.py pato "rutina de pecho para principiante"

1) sin X-API-Key -> debe dar 401
2) con una clave incorrecta -> debe dar 401
3) con CLAVE_API del .env -> debe dar 200 y la respuesta del agente

Nunca imprime la clave: sirve para capturas de evidencia.
"""

import argparse
import sys
import uuid
from datetime import datetime
from pathlib import Path

import httpx

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from src.comun.acceso import ENCABEZADO, clave_configurada
from src.comun.registro import CATALOGO
from src.portal.cliente import TIEMPO_ESPERA, extraer_texto

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def _peticion(texto: str) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "message/send",
        "params": {
            "message": {
                "kind": "message",
                "messageId": str(uuid.uuid4()),
                "role": "user",
                "contextId": str(uuid.uuid4()),
                "parts": [{"kind": "text", "text": texto}],
            }
        },
    }


def main() -> int:
    analizador = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analizador.add_argument("agente", nargs="?", default="viajes", choices=sorted(CATALOGO))
    analizador.add_argument("pregunta", nargs="?", default="¿Cuánto cuesta volar de Santiago a Lima?")
    argumentos = analizador.parse_args()

    agente = CATALOGO[argumentos.agente]
    if not clave_configurada():
        print("Falta CLAVE_API en .env.")
        return 1

    print(f"Entorno: LOCAL · {datetime.now():%Y-%m-%d %H:%M:%S}")
    print(f"Agente: {agente.nombre} en {agente.url}\n")

    casos = [
        ("1. Sin clave", {}),
        ("2. Clave incorrecta", {ENCABEZADO: "clave-incorrecta"}),
        ("3. Clave correcta (CLAVE_API, oculta)", {ENCABEZADO: clave_configurada()}),
    ]
    with httpx.Client(timeout=TIEMPO_ESPERA) as cliente:
        for titulo, encabezados in casos:
            try:
                respuesta = cliente.post(agente.url, json=_peticion(argumentos.pregunta), headers=encabezados)
            except httpx.HTTPError as error:
                print(f"{titulo}: no se pudo conectar ({' '.join(str(error).split())}).")
                return 1
            print(f"{titulo} -> HTTP {respuesta.status_code}")
            datos = respuesta.json() if respuesta.headers.get("content-type", "").startswith("application/json") else {}
            if respuesta.status_code == 200:
                if datos.get("error"):
                    print(f"   Error del agente: {datos['error']}")
                else:
                    print(f"   Pregunta: {argumentos.pregunta}")
                    print(f"   Respuesta: {extraer_texto(datos.get('result') or {})}")
            else:
                print(f"   Detalle: {datos.get('detail', respuesta.text[:200])}")
            print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
