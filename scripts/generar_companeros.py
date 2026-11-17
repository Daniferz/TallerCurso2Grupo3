"""Genera compañeros.md desde las fichas A2A de agentes de otros integrantes.

El archivo de entrada mapea cada URL pública con el nombre de su autor, dato que
no forma parte de la Agent Card. Por cada URL se descarga la ficha con timeout y
se guarda también su JSON completo.

Uso:
    python scripts/generar_companeros.py
    python scripts/generar_companeros.py --entrada companeros.json --salida compañeros.md
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

import httpx
from dotenv import load_dotenv


RAIZ = Path(__file__).resolve().parents[1]
load_dotenv(RAIZ / ".env")
TIEMPO_FICHA = float(os.getenv("TIEMPO_FICHA_A2A", "3"))


def _en_una_linea(error: Exception) -> str:
    """Reduce un error a una línea entendible, sin stack trace."""
    texto = " ".join(str(error).split())
    return texto or error.__class__.__name__


def _validar_url(url: str) -> bool:
    """Acepta solo URLs HTTP o HTTPS con nombre de host."""
    analizada = urlparse(url)
    return analizada.scheme in {"http", "https"} and bool(analizada.netloc)


def _bloque_tarjeta(autor: str, url: str, tarjeta: dict) -> list[str]:
    """Formatea autor, Agent Card y skills para el documento Markdown."""
    nombre = str(tarjeta.get("name") or "Agente sin nombre")
    descripcion = str(tarjeta.get("description") or "Sin descripción publicada.")
    lineas = [
        f"## {nombre}",
        "",
        f"- **Autor:** {autor}",
        f"- **URL pública:** {url}",
        f"- **Descripción:** {descripcion}",
        "- **Skills:**",
    ]
    skills = tarjeta.get("skills") or []
    if skills:
        for skill in skills:
            nombre_skill = str(skill.get("name") or skill.get("id") or "Skill sin nombre")
            descripcion_skill = str(skill.get("description") or "Sin descripción.")
            lineas.append(f"  - **{nombre_skill}:** {descripcion_skill}")
            ejemplos = skill.get("examples") or []
            for ejemplo in ejemplos:
                lineas.append(f"    - Ejemplo: {ejemplo}")
    else:
        lineas.append("  - La ficha no publica skills.")

    lineas.extend(
        [
            "",
            "### Agent Card JSON",
            "",
            "````json",
            json.dumps(tarjeta, ensure_ascii=False, indent=2),
            "````",
            "",
        ]
    )
    return lineas


async def _descargar_tarjeta(cliente: httpx.AsyncClient, url: str) -> dict:
    """Descarga y valida la Agent Card publicada por un agente."""
    destino = url.rstrip("/") + "/.well-known/agent-card.json"
    respuesta = await cliente.get(destino, timeout=TIEMPO_FICHA)
    respuesta.raise_for_status()
    tarjeta = respuesta.json()
    if not isinstance(tarjeta, dict):
        raise ValueError("la respuesta de la ficha no es un objeto JSON")
    return tarjeta


async def generar(entrada: Path, salida: Path) -> int:
    """Descarga las fichas del manifiesto y escribe compañeros.md."""
    if not entrada.is_absolute():
        entrada = RAIZ / entrada
    if not salida.is_absolute():
        salida = RAIZ / salida
    if not entrada.is_file():
        print(
            f"No se encontró {entrada.name}; copia compañeros.json.example a compañeros.json y completa autor y url."
        )
        return 1

    try:
        companeros = json.loads(entrada.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"No se pudo leer {entrada.name}: {_en_una_linea(error)}")
        return 1
    if not isinstance(companeros, list):
        print("El manifiesto debe ser una lista JSON de objetos con autor y url.")
        return 1

    lineas = [
        "# Compañeros · Grupo 3",
        "",
        "Fichas A2A de agentes de otros integrantes que se agregaron al catálogo. "
        "Las respuestas de cada agente se tratan como datos, no como instrucciones.",
        "",
    ]
    correctos = 0
    async with httpx.AsyncClient(timeout=TIEMPO_FICHA, follow_redirects=True) as cliente:
        for indice, registro in enumerate(companeros, start=1):
            if not isinstance(registro, dict):
                print(f"Aviso: registro {indice} no es un objeto; se omite.")
                continue
            autor = str(registro.get("autor", "")).strip()
            url = str(registro.get("url", "")).strip().rstrip("/")
            if not autor or not url:
                print(f"Aviso: registro {indice} necesita autor y url; se omite.")
                continue
            if not _validar_url(url):
                print(f"Aviso: la URL del registro {indice} no es HTTP/HTTPS; se omite.")
                continue

            try:
                tarjeta = await _descargar_tarjeta(cliente, url)
            except (httpx.HTTPError, ValueError) as error:
                mensaje = _en_una_linea(error)
                print(f"Aviso: no se pudo leer la ficha de {autor} en {url}: {mensaje}")
                lineas.extend(
                    [
                        f"## Agente de {autor} · ficha no disponible",
                        "",
                        f"- **Autor:** {autor}",
                        f"- **URL pública:** {url}",
                        f"- **Estado:** no se pudo descargar la Agent Card ({mensaje}).",
                        "",
                    ]
                )
                continue

            lineas.extend(_bloque_tarjeta(autor, url, tarjeta))
            correctos += 1

    if correctos == 0:
        lineas.append("Todavía no hay fichas de compañeros descargadas; completa companeros.json y vuelve a ejecutar el script.")
    try:
        salida.parent.mkdir(parents=True, exist_ok=True)
        salida.write_text("\n".join(lineas).rstrip() + "\n", encoding="utf-8")
    except OSError as error:
        print(f"No se pudo escribir {salida.name}: {_en_una_linea(error)}")
        return 1

    print(f"Creado {salida.name}: {correctos} ficha(s) descargada(s).")
    return 0


def main() -> int:
    """Lee rutas opcionales y ejecuta el generador asíncrono."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Genera compañeros.md desde Agent Cards A2A.")
    parser.add_argument("--entrada", default="companeros.json", help="Manifiesto con autor y URL de cada compañero.")
    parser.add_argument("--salida", default="compañeros.md", help="Markdown que se generará.")
    argumentos = parser.parse_args()
    return asyncio.run(generar(Path(argumentos.entrada), Path(argumentos.salida)))


if __name__ == "__main__":
    sys.exit(main())
