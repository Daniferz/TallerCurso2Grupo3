"""Compara la respuesta de un agente preguntándole directo vs. a través del coordinador (T07).

Uso, desde la raíz del proyecto, con el agente y el coordinador levantados:
    python scripts/comparar_directo_coordinador.py pato "Arma una rutina de pecho para fuerza, 5 días"
    python scripts/comparar_directo_coordinador.py dani "Qué llevo en la maleta para Pucón 3 días en invierno"
    python scripts/comparar_directo_coordinador.py cristian "¿A qué hora abre el Cerro San Cristóbal el domingo?"

Las dos respuestas salen de llamadas distintas al modelo, así que la redacción
puede variar; lo que debe ser idéntico son las cifras (series, repeticiones,
días, horarios, precios...). El coordinador solo agrega la etiqueta [Nombre]
al inicio y el "Motivo de selección" al final.
"""

import asyncio
import re
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.comun.errores import en_una_linea  # noqa: E402
from src.comun.registro import CATALOGO  # noqa: E402
from src.portal.cliente import ErrorAgente, enviar_mensaje  # noqa: E402

# Cifras: "8-12", "1,5", "06:00", "2017", "5"...
CIFRA = re.compile(r"\d+(?:[:.,-]\d+)*")
MOTIVO = "Motivo de selección:"


def sin_envoltorio(respuesta: str, nombre: str) -> tuple[str, bool]:
    """Quita la etiqueta [Nombre] y el motivo que agrega el coordinador; dice si la etiqueta estaba."""
    etiqueta = f"[{nombre}]"
    tiene_etiqueta = respuesta.startswith(etiqueta)
    texto = respuesta[len(etiqueta):] if tiene_etiqueta else respuesta
    return texto.split(MOTIVO)[0].strip(), tiene_etiqueta


def cifras(texto: str) -> list[str]:
    """Cifras del texto, sin repetir y en orden de aparición."""
    return list(dict.fromkeys(CIFRA.findall(texto)))


async def comparar(clave: str, pregunta: str) -> bool:
    agente = CATALOGO[clave]
    print(f"### {agente.nombre} · LOCAL · {datetime.now():%Y-%m-%d %H:%M}")
    print(f"Pregunta: {pregunta}\n")
    try:
        directo = (await enviar_mensaje(agente, pregunta))["respuesta"]
        via = (await enviar_mensaje(CATALOGO["coordinador"], pregunta))["respuesta"]
    except ErrorAgente as error:
        print(f"Error: {en_una_linea(error)}")
        return False

    via_limpia, tiene_etiqueta = sin_envoltorio(via, agente.nombre)
    cifras_directo, cifras_via = cifras(directo), cifras(via_limpia)
    solo_directo = [c for c in cifras_directo if c not in cifras_via]
    solo_via = [c for c in cifras_via if c not in cifras_directo]

    print(f"**Directo al agente:**\n\n{directo}\n")
    print(f"**Vía coordinador:**\n\n{via}\n")
    print(f"- Etiqueta [{agente.nombre}] al inicio: {'sí' if tiene_etiqueta else 'NO'}")
    print(f"- Cifras directo: {', '.join(cifras_directo) or '(ninguna)'}")
    print(f"- Cifras vía coordinador: {', '.join(cifras_via) or '(ninguna)'}")
    iguales = not solo_directo and not solo_via
    if not iguales:
        print(f"- Solo directo: {', '.join(solo_directo) or '-'} · Solo vía coordinador: {', '.join(solo_via) or '-'}")
    resultado = tiene_etiqueta and iguales
    print(f"- Resultado: {'PASA (mismas cifras, solo cambia la etiqueta)' if resultado else 'FALLA'}\n")
    return resultado


def main() -> int:
    if len(sys.argv) < 3 or sys.argv[1] not in CATALOGO:
        print(__doc__)
        return 2
    return 0 if asyncio.run(comparar(sys.argv[1], " ".join(sys.argv[2:]))) else 1


if __name__ == "__main__":
    raise SystemExit(main())
