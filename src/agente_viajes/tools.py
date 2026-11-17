"""Herramientas del agente de viajes: vuelos y hoteles de mentira, pero creíbles."""

import unicodedata

from langchain_core.tools import tool


# Código IATA -> ciudad, para aceptar tanto "SCL" como "Santiago".
AEROPUERTOS = {
    "SCL": "Santiago",
    "LIM": "Lima",
    "BOG": "Bogotá",
    "EZE": "Buenos Aires",
}

# Vuelos inventados. Cada ruta tiene dos opciones en cada sentido.
VUELOS = [
    {"origen": "SCL", "destino": "LIM", "aerolinea": "LATAM", "numero": "LA2410", "salida": "07:20", "llegada": "09:50", "precio_clp": 189000},
    {"origen": "SCL", "destino": "LIM", "aerolinea": "Sky Airline", "numero": "H2 1502", "salida": "15:40", "llegada": "18:10", "precio_clp": 165000},
    {"origen": "LIM", "destino": "SCL", "aerolinea": "LATAM", "numero": "LA2411", "salida": "11:10", "llegada": "16:00", "precio_clp": 195000},
    {"origen": "LIM", "destino": "SCL", "aerolinea": "JetSmart", "numero": "JA771", "salida": "19:30", "llegada": "00:20", "precio_clp": 178000},
    {"origen": "SCL", "destino": "BOG", "aerolinea": "Avianca", "numero": "AV116", "salida": "06:05", "llegada": "10:40", "precio_clp": 389000},
    {"origen": "SCL", "destino": "BOG", "aerolinea": "LATAM", "numero": "LA572", "salida": "14:20", "llegada": "19:05", "precio_clp": 415000},
    {"origen": "BOG", "destino": "SCL", "aerolinea": "Avianca", "numero": "AV117", "salida": "11:50", "llegada": "19:20", "precio_clp": 395000},
    {"origen": "BOG", "destino": "SCL", "aerolinea": "Copa Airlines", "numero": "CM348", "salida": "21:15", "llegada": "04:50", "precio_clp": 372000},
    {"origen": "SCL", "destino": "EZE", "aerolinea": "LATAM", "numero": "LA533", "salida": "08:15", "llegada": "10:35", "precio_clp": 215000},
    {"origen": "SCL", "destino": "EZE", "aerolinea": "Sky Airline", "numero": "H2 1201", "salida": "17:00", "llegada": "19:20", "precio_clp": 198000},
    {"origen": "EZE", "destino": "SCL", "aerolinea": "LATAM", "numero": "LA534", "salida": "12:05", "llegada": "14:30", "precio_clp": 228000},
    {"origen": "EZE", "destino": "SCL", "aerolinea": "JetSmart", "numero": "JA991", "salida": "20:10", "llegada": "22:35", "precio_clp": 205000},
    {"origen": "LIM", "destino": "BOG", "aerolinea": "Avianca", "numero": "AV074", "salida": "05:40", "llegada": "08:55", "precio_clp": 312000},
    {"origen": "LIM", "destino": "BOG", "aerolinea": "Wingo", "numero": "P5 7312", "salida": "16:25", "llegada": "19:40", "precio_clp": 289000},
    {"origen": "BOG", "destino": "LIM", "aerolinea": "Avianca", "numero": "AV075", "salida": "09:45", "llegada": "13:05", "precio_clp": 318000},
    {"origen": "BOG", "destino": "LIM", "aerolinea": "LATAM", "numero": "LA2447", "salida": "18:30", "llegada": "21:50", "precio_clp": 335000},
    {"origen": "LIM", "destino": "EZE", "aerolinea": "LATAM", "numero": "LA637", "salida": "01:15", "llegada": "07:45", "precio_clp": 349000},
    {"origen": "LIM", "destino": "EZE", "aerolinea": "Aerolíneas Argentinas", "numero": "AR1361", "salida": "13:20", "llegada": "20:00", "precio_clp": 368000},
    {"origen": "EZE", "destino": "LIM", "aerolinea": "LATAM", "numero": "LA638", "salida": "09:10", "llegada": "13:50", "precio_clp": 355000},
    {"origen": "EZE", "destino": "LIM", "aerolinea": "Sky Airline", "numero": "H2 5102", "salida": "22:40", "llegada": "03:20", "precio_clp": 332000},
    {"origen": "BOG", "destino": "EZE", "aerolinea": "Avianca", "numero": "AV217", "salida": "07:30", "llegada": "15:20", "precio_clp": 448000},
    {"origen": "BOG", "destino": "EZE", "aerolinea": "Aerolíneas Argentinas", "numero": "AR1363", "salida": "23:55", "llegada": "07:45", "precio_clp": 472000},
    {"origen": "EZE", "destino": "BOG", "aerolinea": "Avianca", "numero": "AV218", "salida": "16:40", "llegada": "22:15", "precio_clp": 455000},
    {"origen": "EZE", "destino": "BOG", "aerolinea": "Copa Airlines", "numero": "CM802", "salida": "09:05", "llegada": "16:40", "precio_clp": 430000},
]

# Hoteles inventados por ciudad.
HOTELES = {
    "SCL": [
        {"hotel": "Hotel Plaza San Francisco", "estrellas": 4, "barrio": "Centro", "precio_noche_clp": 98000},
        {"hotel": "Hotel Boutique Lastarria", "estrellas": 3, "barrio": "Lastarria", "precio_noche_clp": 82000},
    ],
    "LIM": [
        {"hotel": "Hotel Costa del Sol Miraflores", "estrellas": 4, "barrio": "Miraflores", "precio_noche_clp": 76000},
        {"hotel": "Casa Andina San Isidro", "estrellas": 3, "barrio": "San Isidro", "precio_noche_clp": 64000},
    ],
    "BOG": [
        {"hotel": "Hotel Bogotá Plaza", "estrellas": 5, "barrio": "Zona Rosa", "precio_noche_clp": 112000},
        {"hotel": "Casa Real Chapinero", "estrellas": 3, "barrio": "Chapinero", "precio_noche_clp": 59000},
    ],
    "EZE": [
        {"hotel": "Alvear Art Hotel", "estrellas": 4, "barrio": "Retiro", "precio_noche_clp": 108000},
        {"hotel": "Palermo Soho Loft", "estrellas": 3, "barrio": "Palermo", "precio_noche_clp": 74000},
    ],
}


def _sin_tildes(texto: str) -> str:
    """Deja el texto comparable: "Bogotá" y "Bogota" deben encontrar lo mismo."""
    descompuesto = unicodedata.normalize("NFD", texto)
    return "".join(letra for letra in descompuesto if unicodedata.category(letra) != "Mn")


def _codigo_aeropuerto(valor: str) -> str:
    """Convierte "scl" o "Santiago" al código IATA; devuelve "" si no lo conoce."""
    limpio = (valor or "").strip()
    if not limpio:
        return ""
    if limpio.upper() in AEROPUERTOS:
        return limpio.upper()
    for codigo, ciudad in AEROPUERTOS.items():
        if _sin_tildes(ciudad).lower() == _sin_tildes(limpio).lower():
            return codigo
    return ""


def _codigo_ciudad(valor: str) -> str:
    """Igual que el anterior, pero para el campo ciudad de los hoteles."""
    return _codigo_aeropuerto(valor)


@tool
def buscar_vuelos(origen: str, destino: str, fecha: str) -> list[dict]:
    """Busca vuelos entre dos aeropuertos y devuelve opciones con precio en pesos chilenos.

    Args:
        origen: Código IATA (SCL, LIM, BOG, EZE) o nombre de la ciudad de salida.
        destino: Código IATA (SCL, LIM, BOG, EZE) o nombre de la ciudad de llegada.
        fecha: Fecha del viaje, tal como la pidió la persona (por ejemplo "15 de marzo").
    """
    codigo_origen = _codigo_aeropuerto(origen)
    codigo_destino = _codigo_aeropuerto(destino)
    if not codigo_origen or not codigo_destino or codigo_origen == codigo_destino:
        # No hay ruta: lista vacía, nunca una excepción.
        return []

    return [
        {
            "origen": vuelo["origen"],
            "destino": vuelo["destino"],
            "fecha": fecha,
            "aerolinea": vuelo["aerolinea"],
            "numero": vuelo["numero"],
            "salida": vuelo["salida"],
            "llegada": vuelo["llegada"],
            "precio_clp": vuelo["precio_clp"],
        }
        for vuelo in VUELOS
        if vuelo["origen"] == codigo_origen and vuelo["destino"] == codigo_destino
    ]


@tool
def buscar_hoteles(ciudad: str, noches: int) -> list[dict]:
    """Busca hoteles en una ciudad y calcula cuánto cuesta la estadía completa.

    Args:
        ciudad: Código IATA (SCL, LIM, BOG, EZE) o nombre de la ciudad.
        noches: Cantidad de noches que se va a quedar la persona.
    """
    codigo = _codigo_ciudad(ciudad)
    if not codigo:
        return []

    noches_validas = max(int(noches), 1)
    return [
        {
            "ciudad": AEROPUERTOS[codigo],
            "hotel": hotel["hotel"],
            "estrellas": hotel["estrellas"],
            "barrio": hotel["barrio"],
            "noches": noches_validas,
            "precio_noche_clp": hotel["precio_noche_clp"],
            "precio_total_clp": hotel["precio_noche_clp"] * noches_validas,
        }
        for hotel in HOTELES.get(codigo, [])
    ]
