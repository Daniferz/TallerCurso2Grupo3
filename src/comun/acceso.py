"""Control de acceso compartido: cada agente exige su propia clave en `X-API-Key`.

Cada agente lee su clave de una variable propia del `.env` (o de Heroku):
CLAVE_PATO, CLAVE_DANI, CLAVE_CRISTIAN, CLAVE_COORDINADOR... Así, en local
los agentes conviven en el mismo `.env` con claves distintas, y en Heroku
cada app tiene solo la suya. El nombre de la variable viene del registro
(`Agente.variable_clave`).

El coordinador conoce la clave de cada agente remoto por dos listas del
`.env`, en el mismo orden: URLS_AGENTES y CLAVES_AGENTES.

Las claves nunca se escriben en el frontend, en los registros ni en el repo.
"""

import os
import secrets
from datetime import datetime


ENCABEZADO = "X-API-Key"


def clave_configurada(variable: str) -> str:
    """Clave definida en esa variable del .env, o texto vacío si falta."""
    return os.getenv(variable, "").strip()


def clave_valida(recibida: str | None, variable: str) -> bool:
    """True solo si hay clave configurada y la recibida coincide (comparación en tiempo constante)."""
    esperada = clave_configurada(variable)
    if not esperada or not recibida:
        return False
    return secrets.compare_digest(recibida.encode(), esperada.encode())


def motivo_rechazo(recibida: str | None, variable: str) -> tuple[int, str] | None:
    """Devuelve (código HTTP, mensaje) si se debe rechazar, o None si pasa."""
    if not clave_configurada(variable):
        return 503, f"El servidor no tiene {variable} configurada; no acepta mensajes."
    if not recibida:
        return 401, f"Falta el encabezado {ENCABEZADO}."
    if not clave_valida(recibida, variable):
        return 401, "Clave de acceso inválida."
    return None


def _lista(variable: str) -> list[str]:
    """Lee una lista separada por comas del .env, sin espacios ni elementos vacíos."""
    return [valor.strip() for valor in os.getenv(variable, "").split(",") if valor.strip()]


def _normalizar(url: str) -> str:
    return url.strip().rstrip("/")


def claves_por_url() -> dict[str, str]:
    """Une URLS_AGENTES y CLAVES_AGENTES por posición: url -> clave."""
    urls = [_normalizar(url) for url in _lista("URLS_AGENTES")]
    claves = _lista("CLAVES_AGENTES")
    return dict(zip(urls, claves))


def aviso_listas_desparejas() -> str | None:
    """Frase de aviso si URLS_AGENTES y CLAVES_AGENTES no tienen el mismo largo."""
    urls, claves = _lista("URLS_AGENTES"), _lista("CLAVES_AGENTES")
    if len(urls) == len(claves):
        return None
    return (
        f"Aviso: URLS_AGENTES tiene {len(urls)} URL y CLAVES_AGENTES {len(claves)} claves; "
        "deben ir en el mismo orden y ser la misma cantidad."
    )


def clave_para(url: str) -> str:
    """Clave que hay que enviarle al agente que vive en `url`.

    Primero busca en URLS_AGENTES/CLAVES_AGENTES; si no está, usa la variable
    propia del agente del registro con esa URL (útil en local). Si no hay
    ninguna, devuelve texto vacío y el agente responderá 401.
    """
    destino = _normalizar(url)
    clave = claves_por_url().get(destino)
    if clave:
        return clave

    # Import tardío: registro carga el .env y no debe depender de este módulo.
    from .registro import CATALOGO

    for agente in CATALOGO.values():
        if _normalizar(agente.url) == destino:
            return clave_configurada(agente.variable_clave)
    return ""


def encabezados_para(url: str) -> dict[str, str]:
    """Encabezado X-API-Key para hablar con el agente de `url` (vacío si no hay clave)."""
    clave = clave_para(url)
    return {ENCABEZADO: clave} if clave else {}


def registrar_acceso(servicio: str, ruta: str, cliente: str, permitido: bool, motivo: str = "") -> None:
    """Deja una línea en la terminal por cada intento: sirve como evidencia sin mostrar la clave."""
    hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    estado = "PERMITIDO" if permitido else f"RECHAZADO ({motivo})"
    print(f"[acceso {hora}] {servicio} {ruta} desde {cliente}: {estado}", flush=True)
