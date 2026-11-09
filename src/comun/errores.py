"""Convierte cualquier error en una línea corta y entendible.

Los tres agentes comparten esta función: la consola, el servidor A2A y la
terminal muestran el mismo texto cuando algo falla.
"""

MAX_CARACTERES = 280


def en_una_linea(error: Exception) -> str:
    """Deja el error en un solo renglón, sin stack trace y sin el JSON del proveedor."""
    texto = " ".join(str(error).split())
    if not texto:
        return error.__class__.__name__

    bajo = texto.lower()

    # Gemini devuelve un JSON enorme cuando se acaba la cuota gratuita.
    if "resource_exhausted" in bajo or "quota" in bajo or "429" in bajo:
        return (
            "el modelo se quedó sin cuota (429). Revisa tu plan de Gemini "
            "o espera a que se renueve."
        )

    if (
        "api key" in bajo
        or "api_key" in bajo
        or "unauthenticated" in bajo
        or "permission" in bajo
    ):
        return "la clave de Gemini no es válida o no tiene permiso para este modelo."

    if len(texto) > MAX_CARACTERES:
        return texto[:MAX_CARACTERES].rstrip() + "..."

    return texto
