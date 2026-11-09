"""Descubrimiento de los agentes A2A disponibles para el supervisor."""

from dataclasses import dataclass
import os

from a2a.client import Client

from src.comun.registro import CATALOGO

from .cliente import obtener_cliente, obtener_tarjeta_cacheada


@dataclass(frozen=True)
class AgenteDescubierto:
    """Ficha mínima y cliente A2A de un agente remoto disponible."""

    nombre: str
    descripcion: str
    cliente: Client
    url: str


_agentes: list[AgenteDescubierto] | None = None


def _urls_a_descubrir() -> list[str]:
    """Combina las URLs base y las de compañeros, eliminando duplicados."""
    urls = [CATALOGO[clave].url for clave in ("viajes", "restaurantes")]
    urls_companeros = os.getenv("URLS_AGENTES", "")
    urls.extend(
        url.strip().rstrip("/")
        for url in urls_companeros.split(",")
        if url.strip()
    )
    return list(dict.fromkeys(url for url in urls if url))


def _en_una_linea(error: Exception) -> str:
    """Reduce cualquier error a una frase para la terminal."""
    texto = " ".join(str(error).split())
    return texto or error.__class__.__name__


async def descubrir() -> list[AgenteDescubierto]:
    """Lee una vez las fichas base y las de compañeros configurados, y arma clientes A2A.

    Si un agente no responde, lo informa en una línea y continúa con los demás.
    El resultado se conserva para no volver a consultar las fichas durante el proceso.
    """
    global _agentes
    if _agentes is not None:
        return list(_agentes)

    encontrados: list[AgenteDescubierto] = []
    for url in _urls_a_descubrir():
        try:
            cliente = await obtener_cliente(url)
            tarjeta = obtener_tarjeta_cacheada(url)
            if tarjeta is None:
                raise RuntimeError("el cliente no conservó la ficha descargada")
            encontrados.append(
                AgenteDescubierto(
                    nombre=tarjeta.name,
                    descripcion=tarjeta.description or "Sin descripción.",
                    cliente=cliente,
                    url=url,
                )
            )
        except Exception as error:
            print(f"Aviso: no se pudo sumar el agente en {url}: {_en_una_linea(error)}")

    _agentes = encontrados
    return list(_agentes)
