"""Descubrimiento de los agentes A2A que usa el supervisor.

El catálogo sale solo de URLS_AGENTES (Maleta, Entrenamiento y Sitios turísticos).
Un agente que no respondió al arrancar no se descarta para siempre: se vuelve a
intentar cada REINTENTO_AGENTES_SEG segundos (60 por defecto), sin reiniciar el
coordinador. La ficha de un agente que ya respondió una vez se conserva, aunque
después se caiga, para que el supervisor lo siga eligiendo y la persona reciba
un aviso claro en vez de "no tengo un agente para eso".
"""

import asyncio
import os
import time
from dataclasses import dataclass

from a2a.client import Client

from .cliente import obtener_cliente, obtener_tarjeta_cacheada


@dataclass(frozen=True)
class AgenteDescubierto:
    """Ficha mínima y cliente A2A de un agente remoto disponible."""

    nombre: str
    descripcion: str
    cliente: Client
    url: str


# Cada cuánto se vuelve a intentar un agente que no respondió (segundos).
REINTENTO_SEGUNDOS = float(os.getenv("REINTENTO_AGENTES_SEG", "60"))

# url -> agente cuya ficha ya se leyó (se conserva aunque después se caiga).
_conocidos: dict[str, AgenteDescubierto] = {}

# url -> momento (time.monotonic) del último intento fallido.
_ultimo_intento: dict[str, float] = {}


def _urls_a_descubrir() -> list[str]:
    """URLs de URLS_AGENTES, sin espacios, sin barra final y sin duplicados."""
    urls = (
        url.strip().rstrip("/")
        for url in os.getenv("URLS_AGENTES", "").split(",")
    )
    return list(dict.fromkeys(url for url in urls if url))


def _en_una_linea(error: Exception) -> str:
    """Reduce cualquier error a una frase para la terminal."""
    texto = " ".join(str(error).split())
    return texto or error.__class__.__name__


def _toca_intentar(url: str, ahora: float) -> bool:
    """True si nunca se intentó o si ya pasó el tiempo de reintento."""
    anterior = _ultimo_intento.get(url)
    return anterior is None or ahora - anterior >= REINTENTO_SEGUNDOS


async def _leer_ficha(url: str) -> None:
    """Descarga la ficha de `url` y la suma al catálogo; si falla, lo avisa en una línea."""
    try:
        cliente = await obtener_cliente(url)
        tarjeta = obtener_tarjeta_cacheada(url)
        if tarjeta is None:
            raise RuntimeError("el cliente no conservó la ficha descargada")
    except Exception as error:
        _ultimo_intento[url] = time.monotonic()
        print(
            f"Aviso: no se pudo sumar el agente en {url}: {_en_una_linea(error)} "
            f"(se reintenta en {REINTENTO_SEGUNDOS:.0f} s)",
            flush=True,
        )
        return

    _ultimo_intento.pop(url, None)
    _conocidos[url] = AgenteDescubierto(
        nombre=tarjeta.name,
        descripcion=tarjeta.description or "Sin descripción.",
        cliente=cliente,
        url=url,
    )
    print(f"Agente sumado al catálogo: {tarjeta.name} ({url})", flush=True)


async def descubrir() -> list[AgenteDescubierto]:
    """Devuelve los agentes conocidos, en el orden de URLS_AGENTES.

    Lee las fichas que faltan; las que fallaron se vuelven a pedir solo cuando
    pasó REINTENTO_SEGUNDOS desde el último intento, y todas en paralelo.
    """
    urls = _urls_a_descubrir()
    ahora = time.monotonic()
    pendientes = [
        url for url in urls if url not in _conocidos and _toca_intentar(url, ahora)
    ]
    for url in pendientes:
        # Se marca antes de esperar: otra pregunta simultánea no repite el intento.
        _ultimo_intento[url] = ahora
    if pendientes:
        await asyncio.gather(*(_leer_ficha(url) for url in pendientes))

    return [_conocidos[url] for url in urls if url in _conocidos]
