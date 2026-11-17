"""Herramientas del agente de restaurantes: datos inventados de tres ciudades."""

import unicodedata

from crewai.tools import tool


CIUDADES = {
    "LIM": "Lima",
    "BOG": "Bogotá",
    "EZE": "Buenos Aires",
}

# Precios medios por persona, en pesos chilenos.
RESTAURANTES = [
    {
        "nombre": "La Mar de Barranco",
        "ciudad": "LIM",
        "zona": "Barranco",
        "tipo": "peruana y mariscos",
        "precio_medio_clp": 28000,
        "horario": "12:00 a 17:00",
        "plato_recomendado": "ceviche mixto",
    },
    {
        "nombre": "Isolina",
        "ciudad": "LIM",
        "zona": "Barranco",
        "tipo": "criolla",
        "precio_medio_clp": 24000,
        "horario": "12:30 a 22:30",
        "plato_recomendado": "lomo saltado",
    },
    {
        "nombre": "Maido",
        "ciudad": "LIM",
        "zona": "Miraflores",
        "tipo": "nikkei",
        "precio_medio_clp": 65000,
        "horario": "13:00 a 21:30",
        "plato_recomendado": "menú nikkei de degustación",
    },
    {
        "nombre": "Punto Azul",
        "ciudad": "LIM",
        "zona": "Miraflores",
        "tipo": "cevichería",
        "precio_medio_clp": 19000,
        "horario": "11:30 a 17:00",
        "plato_recomendado": "arroz con mariscos",
    },
    {
        "nombre": "El Pan de la Chola",
        "ciudad": "LIM",
        "zona": "Miraflores",
        "tipo": "café y panadería",
        "precio_medio_clp": 9000,
        "horario": "07:00 a 20:00",
        "plato_recomendado": "pan de masa madre con palta",
    },
    {
        "nombre": "Andrés Carne de Res",
        "ciudad": "BOG",
        "zona": "Usaquén",
        "tipo": "parrilla",
        "precio_medio_clp": 85000,
        "horario": "12:00 a 02:00",
        "plato_recomendado": "punta de anca a la parrilla",
    },
    {
        "nombre": "El Chato",
        "ciudad": "BOG",
        "zona": "Chapinero",
        "tipo": "colombiana de autor",
        "precio_medio_clp": 62000,
        "horario": "12:30 a 23:00",
        "plato_recomendado": "carne de cerdo con puré de arracacha",
    },
    {
        "nombre": "La Puerta Falsa",
        "ciudad": "BOG",
        "zona": "La Candelaria",
        "tipo": "santafereña",
        "precio_medio_clp": 15000,
        "horario": "07:00 a 21:00",
        "plato_recomendado": "ajiaco con tamal",
    },
    {
        "nombre": "Salvo Patria",
        "ciudad": "BOG",
        "zona": "Chapinero",
        "tipo": "contemporánea",
        "precio_medio_clp": 45000,
        "horario": "12:00 a 22:00",
        "plato_recomendado": "menú del día de autor",
    },
    {
        "nombre": "Wok",
        "ciudad": "BOG",
        "zona": "Zona Rosa",
        "tipo": "asiática",
        "precio_medio_clp": 38000,
        "horario": "12:00 a 23:00",
        "plato_recomendado": "ramen de cerdo",
    },
    {
        "nombre": "Don Julio",
        "ciudad": "EZE",
        "zona": "Palermo",
        "tipo": "parrilla",
        "precio_medio_clp": 42000,
        "horario": "12:00 a 00:00",
        "plato_recomendado": "bife de chorizo",
    },
    {
        "nombre": "El Sanjuanino",
        "ciudad": "EZE",
        "zona": "Recoleta",
        "tipo": "norteña",
        "precio_medio_clp": 18000,
        "horario": "11:30 a 23:30",
        "plato_recomendado": "empanada salteña",
    },
    {
        "nombre": "La Cabrera",
        "ciudad": "EZE",
        "zona": "Palermo",
        "tipo": "parrilla",
        "precio_medio_clp": 38000,
        "horario": "12:00 a 00:30",
        "plato_recomendado": "ojo de bife con guarniciones",
    },
    {
        "nombre": "Café Tortoni",
        "ciudad": "EZE",
        "zona": "Montserrat",
        "tipo": "café y cocina porteña",
        "precio_medio_clp": 12000,
        "horario": "08:00 a 00:00",
        "plato_recomendado": "medialunas con café",
    },
    {
        "nombre": "Osaka",
        "ciudad": "EZE",
        "zona": "Palermo",
        "tipo": "nikkei",
        "precio_medio_clp": 52000,
        "horario": "12:30 a 23:30",
        "plato_recomendado": "tiradito nikkei",
    },
]


def _sin_tildes(texto: str) -> str:
    """Deja el texto comparable: "Bogotá" y "Bogota" deben encontrar lo mismo."""
    descompuesto = unicodedata.normalize("NFD", texto)
    return "".join(letra for letra in descompuesto if unicodedata.category(letra) != "Mn")


def _codigo_ciudad(valor: str) -> str:
    """Convierte "lim" o "Lima" al código de ciudad; devuelve "" si no la conoce."""
    limpio = (valor or "").strip()
    if not limpio:
        return ""
    if limpio.upper() in CIUDADES:
        return limpio.upper()
    for codigo, ciudad in CIUDADES.items():
        if _sin_tildes(ciudad).lower() == _sin_tildes(limpio).lower():
            return codigo
    return ""


@tool
def buscar_restaurantes(ciudad: str, tipo: str) -> list[dict]:
    """Busca restaurantes en una ciudad, opcionalmente filtrando por tipo de comida.

    Args:
        ciudad: Código (LIM, BOG, EZE) o nombre de la ciudad.
        tipo: Tipo de comida a buscar, por ejemplo "parrilla", "nikkei" o "criolla". Vacío para ver todos.
    """
    codigo = _codigo_ciudad(ciudad)
    if not codigo:
        return []

    filtro = _sin_tildes((tipo or "").strip()).lower()
    encontrados = []
    for restaurante in RESTAURANTES:
        if restaurante["ciudad"] != codigo:
            continue
        if filtro and filtro not in _sin_tildes(restaurante["tipo"]).lower():
            continue
        encontrados.append(
            {
                "nombre": restaurante["nombre"],
                "ciudad": CIUDADES[codigo],
                "zona": restaurante["zona"],
                "tipo": restaurante["tipo"],
                "precio_medio_clp": restaurante["precio_medio_clp"],
                "horario": restaurante["horario"],
            }
        )
    return encontrados


@tool
def detalle_restaurante(nombre: str) -> dict:
    """Devuelve la ficha completa de un restaurante: zona, tipo, precio, horario y plato recomendado.

    Args:
        nombre: Nombre del restaurante, completo o parcial.
    """
    buscado = _sin_tildes((nombre or "").strip()).lower()
    if not buscado:
        return {}

    # Primero coincidencia exacta; si no, el nombre buscado dentro del nombre real.
    for restaurante in RESTAURANTES:
        if _sin_tildes(restaurante["nombre"]).lower() == buscado:
            return {
                **restaurante,
                "ciudad": CIUDADES[restaurante["ciudad"]],
            }

    for restaurante in RESTAURANTES:
        if buscado in _sin_tildes(restaurante["nombre"]).lower():
            return {
                **restaurante,
                "ciudad": CIUDADES[restaurante["ciudad"]],
            }

    return {}
