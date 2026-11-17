"""Herramienta del agente de maleta con guías de referencia estáticas."""

from math import ceil
import unicodedata

from langchain_core.tools import tool


# Guías ilustrativas por destino y temporada. No representan pronósticos del clima.
GUIAS = {
    ("punta arenas", "invierno"): {
        "ropa": [
            "ropa interior", "calcetines", "primera capa térmica",
            "polar o suéter abrigado", "chaqueta impermeable", "pantalones",
            "gorro", "guantes", "bufanda",
        ],
        "documentos": ["documento de identidad", "reservas y pasajes descargados"],
        "tecnologia": ["teléfono y cargador", "batería externa"],
        "botiquin": ["medicamentos personales", "artículos básicos de primeros auxilios"],
        "no_te_olvides": ["bolsa para separar ropa húmeda", "revisar documentos antes de salir"],
    },
    ("punta arenas", "verano"): {
        "ropa": [
            "ropa interior", "calcetines", "poleras", "pantalones cómodos",
            "chaqueta cortaviento", "capa impermeable ligera", "gorro",
        ],
        "documentos": ["documento de identidad", "reservas y pasajes descargados"],
        "tecnologia": ["teléfono y cargador", "batería externa"],
        "botiquin": ["medicamentos personales", "artículos básicos de primeros auxilios"],
        "no_te_olvides": ["bolsa para separar ropa usada", "revisar documentos antes de salir"],
    },
    ("pucon", "invierno"): {
        "ropa": [
            "ropa interior", "calcetines", "primera capa térmica",
            "polar o suéter abrigado", "chaqueta impermeable",
            "pantalones cómodos", "gorro", "guantes",
        ],
        "documentos": ["documento de identidad", "reservas y pasajes descargados"],
        "tecnologia": ["teléfono y cargador", "batería externa"],
        "botiquin": ["medicamentos personales", "artículos básicos de primeros auxilios"],
        "no_te_olvides": ["bolsa para ropa húmeda", "revisar documentos antes de salir"],
    },
    ("pucon", "verano"): {
        "ropa": [
            "ropa interior", "calcetines", "poleras", "pantalones cómodos",
            "traje de baño", "chaqueta ligera", "calzado cómodo",
        ],
        "documentos": ["documento de identidad", "reservas y pasajes descargados"],
        "tecnologia": ["teléfono y cargador", "batería externa"],
        "botiquin": ["medicamentos personales", "artículos básicos de primeros auxilios"],
        "no_te_olvides": ["bolsa para ropa usada", "revisar documentos antes de salir"],
    },
    ("iquique", "verano"): {
        "ropa": [
            "ropa interior", "calcetines", "poleras ligeras",
            "pantalones cómodos", "traje de baño", "sombrero o gorra", "sandalias",
        ],
        "documentos": ["documento de identidad", "reservas y pasajes descargados"],
        "tecnologia": ["teléfono y cargador", "batería externa"],
        "botiquin": ["medicamentos personales", "artículos básicos de primeros auxilios"],
        "no_te_olvides": ["bolsa para ropa húmeda", "revisar documentos antes de salir"],
    },
}

TITULOS = {
    "ropa": "Ropa",
    "documentos": "Documentos",
    "tecnologia": "Tecnología",
    "botiquin": "Botiquín",
    "no_te_olvides": "No te olvides",
}

MESES_CHILE = {
    "diciembre": "verano", "enero": "verano", "febrero": "verano",
    "marzo": "otoño", "abril": "otoño", "mayo": "otoño",
    "junio": "invierno", "julio": "invierno", "agosto": "invierno",
    "septiembre": "primavera", "octubre": "primavera", "noviembre": "primavera",
}


def _normalizar(valor: str) -> str:
    """Normaliza mayúsculas, espacios y tildes para buscar en las guías."""
    texto = unicodedata.normalize("NFD", valor.strip().lower())
    return "".join(letra for letra in texto if unicodedata.category(letra) != "Mn")


def _cantidad(item: str, dias: int) -> int:
    """Calcula cantidades orientativas de prendas según la duración."""
    if item in {"ropa interior", "calcetines"}:
        return dias + 1
    if item in {"poleras", "poleras ligeras", "primera capa térmica"}:
        return min(dias, 5)
    if item in {"pantalones", "pantalones cómodos"}:
        return min(3, max(1, ceil(dias / 3)))
    return 1


@tool
def lista_equipaje(destino: str, dias: int, temporada: str) -> str:
    """Devuelve una lista de equipaje agrupada por categoría desde guías estáticas.

    Destinos cubiertos: Punta Arenas (invierno y verano), Pucón (invierno y verano)
    e Iquique (verano). También acepta meses del calendario chileno. No consulta
    clima, vuelos, hoteles, precios, visas ni políticas de equipaje de aerolíneas.

    Args:
        destino: Punta Arenas, Pucón o Iquique.
        dias: Cantidad de días del viaje, entre 1 y 30.
        temporada: Invierno, verano o un mes del calendario chileno.
    """
    try:
        cantidad_dias = int(dias)
    except (TypeError, ValueError):
        return "Indícame la cantidad de días como un número entero entre 1 y 30."
    if not 1 <= cantidad_dias <= 30:
        return "La cantidad de días debe estar entre 1 y 30."
    if not isinstance(destino, str) or not destino.strip():
        return "Indícame el destino para consultar una guía de equipaje."
    if not isinstance(temporada, str) or not temporada.strip():
        return "Indícame la temporada para consultar una guía de equipaje."

    lugar = _normalizar(destino)
    estacion = _normalizar(temporada)
    estacion = MESES_CHILE.get(estacion, estacion)
    guia = GUIAS.get((lugar, estacion))
    if guia is None:
        return "No tengo una guía estática para ese destino y temporada; no puedo armar una lista fiable."

    lineas = [
        f"Lista de referencia para {destino.strip()}, {cantidad_dias} día(s), "
        f"temporada {temporada.strip()}:",
    ]
    for categoria, elementos in guia.items():
        lineas.append(f"{TITULOS[categoria]}:")
        for item in elementos:
            cantidad = _cantidad(item, cantidad_dias)
            lineas.append(f"- {cantidad} × {item}" if cantidad > 1 else f"- {item}")
    return "\n".join(lineas)
