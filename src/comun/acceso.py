"""Control de acceso compartido: una clave configurable en .env que valida el servidor.

La clave vive solo en `.env` (variable CLAVE_API). Los servidores A2A y la
consola web la exigen en el encabezado `X-API-Key`; los clientes internos
(consola y coordinador) la leen del mismo `.env` y la agregan al llamar.
Nunca se escribe en el frontend ni en el repositorio.
"""

import os
import secrets
from datetime import datetime


ENCABEZADO = "X-API-Key"
VARIABLE = "CLAVE_API"


def clave_configurada() -> str:
    """Clave definida en .env, o texto vacío si falta."""
    return os.getenv(VARIABLE, "").strip()


def clave_valida(recibida: str | None) -> bool:
    """True solo si hay clave configurada y la recibida coincide (comparación en tiempo constante)."""
    esperada = clave_configurada()
    if not esperada or not recibida:
        return False
    return secrets.compare_digest(recibida.encode(), esperada.encode())


def encabezados_acceso() -> dict[str, str]:
    """Encabezado que los clientes internos agregan al hablar con un agente protegido."""
    clave = clave_configurada()
    return {ENCABEZADO: clave} if clave else {}


def motivo_rechazo(recibida: str | None) -> tuple[int, str] | None:
    """Devuelve (código HTTP, mensaje) si se debe rechazar, o None si pasa."""
    if not clave_configurada():
        return 503, f"El servidor no tiene {VARIABLE} configurada en .env; no acepta mensajes."
    if not recibida:
        return 401, f"Falta el encabezado {ENCABEZADO}."
    if not clave_valida(recibida):
        return 401, "Clave de acceso inválida."
    return None


def registrar_acceso(servicio: str, ruta: str, cliente: str, permitido: bool, motivo: str = "") -> None:
    """Deja una línea en la terminal por cada intento: sirve como evidencia sin mostrar la clave."""
    hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    estado = "PERMITIDO" if permitido else f"RECHAZADO ({motivo})"
    print(f"[acceso {hora}] {servicio} {ruta} desde {cliente}: {estado}", flush=True)
