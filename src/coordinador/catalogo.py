"""Descubrimiento de los agentes A2A disponibles para el supervisor."""

from dataclasses import dataclass

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


def _en_una_linea(error: Exception) -> str:
    """Reduce cualquier error a una frase para la terminal."""
    texto = " ".join(str(error).split())
    return texto or error.__class__.__name__


async def descubrir() -> list[AgenteDescubierto]:
    """Lee una vez las fichas de viajes y restaurantes y arma los clientes A2A.

    Si un agente no responde, lo informa en una línea y continúa con los demás.
    El resultado se conserva para no volver a consultar las fichas durante el proceso.
    """
    global _agentes
    if _agentes is not None:
        return list(_agentes)

    encontrados: list[AgenteDescubierto] = []
    for clave in ("viajes", "restaurantes"):
        url = CATALOGO[clave].url
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
