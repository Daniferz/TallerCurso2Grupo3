"""Herramientas del agente Cristian: sitios turísticos con datos de ejemplo."""

import unicodedata

from langchain_core.tools import tool


SITIOS = {
    "santiago": [
        {
            "nombre": "Cerro San Cristóbal",
            "descripcion": "Mirador del valle de Santiago con áreas verdes y vistas de la cordillera.",
            "ubicacion": "Parque Metropolitano, Providencia",
            "horario": "Martes a domingo, 06:00 a 20:30",
            "dias_cerrados": ["lunes"],
            "precio_referencial": "Entrada al parque gratuita; funicular desde $2.000 CLP",
            "imagen": "https://ejemplo.com/imagenes/cerro-san-cristobal.jpg",
        },
        {
            "nombre": "Museo Chileno de Arte Precolombino",
            "descripcion": "Colección de piezas y culturas originarias de América Latina.",
            "ubicacion": "Bandera 361, Santiago Centro",
            "horario": "Martes a domingo, 10:00 a 18:00",
            "dias_cerrados": ["lunes"],
            "precio_referencial": "$5.000 CLP entrada general",
            "imagen": "https://ejemplo.com/imagenes/museo-precolombino.jpg",
        },
        {
            "nombre": "Barrio Lastarria",
            "descripcion": "Barrio cultural con arquitectura histórica, cafés, librerías y galerías.",
            "ubicacion": "Entre el centro y el cerro Santa Lucía",
            "horario": "Recorrido exterior disponible todo el día",
            "precio_referencial": "Acceso gratuito; consumo según el local",
            "imagen": "https://ejemplo.com/imagenes/barrio-lastarria.jpg",
        },
    ],
    "lima": [
        {
            "nombre": "Centro Histórico de Lima",
            "descripcion": "Recorrido por plazas, balcones coloniales e iglesias del centro de la ciudad.",
            "ubicacion": "Plaza Mayor y alrededores, Cercado de Lima",
            "horario": "Recorrido exterior disponible todo el día",
            "precio_referencial": "Acceso gratuito; entradas según el lugar visitado",
            "imagen": "https://ejemplo.com/imagenes/centro-historico-lima.jpg",
        },
        {
            "nombre": "Huaca Pucllana",
            "descripcion": "Complejo arqueológico prehispánico de adobe en medio del distrito de Miraflores.",
            "ubicacion": "Calle General Borgoño 800, Miraflores",
            "horario": "Miércoles a lunes, 09:00 a 17:00",
            "dias_cerrados": ["martes"],
            "precio_referencial": "S/ 15 entrada general",
            "imagen": "https://ejemplo.com/imagenes/huaca-pucllana.jpg",
        },
        {
            "nombre": "Malecón de Miraflores",
            "descripcion": "Paseo frente al océano con parques, miradores y vistas de la Costa Verde.",
            "ubicacion": "Malecón Cisneros, Miraflores",
            "horario": "Recorrido exterior disponible todo el día",
            "precio_referencial": "Acceso gratuito",
            "imagen": "https://ejemplo.com/imagenes/malecon-miraflores.jpg",
        },
    ],
    "bogota": [
        {
            "nombre": "Museo del Oro",
            "descripcion": "Museo con una importante colección de piezas de orfebrería prehispánica.",
            "ubicacion": "Carrera 6 # 15-88, La Candelaria",
            "horario": "Martes a sábado, 09:00 a 18:00; domingo, 10:00 a 16:00",
            "dias_cerrados": ["lunes"],
            "precio_referencial": "Desde $5.000 COP entrada general",
            "imagen": "https://ejemplo.com/imagenes/museo-del-oro-bogota.jpg",
        },
        {
            "nombre": "Cerro de Monserrate",
            "descripcion": "Mirador de Bogotá con santuario y panorámica de la ciudad desde la montaña.",
            "ubicacion": "Carrera 2 Este, Bogotá",
            "horario": "Lunes a sábado, 06:30 a 22:00; domingo, 05:30 a 18:00",
            "dias_cerrados": [],
            "precio_referencial": "Desde $29.000 COP transporte ida y vuelta",
            "imagen": "https://ejemplo.com/imagenes/monserrate-bogota.jpg",
        },
        {
            "nombre": "Museo Botero",
            "descripcion": "Museo de arte con obras de Fernando Botero y una colección internacional.",
            "ubicacion": "Calle 11 # 4-41, La Candelaria",
            "horario": "Lunes cerrado; martes a domingo, 09:00 a 19:00",
            "dias_cerrados": ["lunes"],
            "precio_referencial": "Entrada gratuita",
            "imagen": "https://ejemplo.com/imagenes/museo-botero.jpg",
        },
    ],
    "cusco": [
        {
            "nombre": "Sacsayhuamán",
            "descripcion": "Complejo arqueológico de enormes muros de piedra sobre la ciudad.",
            "ubicacion": "A 2 km de la Plaza de Armas de Cusco",
            "horario": "Todos los días, 07:00 a 17:30",
            "precio_referencial": "Desde S/ 70; referencial, sujeto al tipo de boleto",
            "imagen": "https://ejemplo.com/imagenes/sacsayhuaman.jpg",
        },
        {
            "nombre": "Barrio de San Blas",
            "descripcion": "Barrio tradicional de calles empedradas y talleres de artesanía.",
            "ubicacion": "A 10 minutos a pie de la Plaza de Armas",
            "horario": "Recorrido exterior disponible todo el día",
            "precio_referencial": "Acceso gratuito; consumo según el local",
            "imagen": "https://ejemplo.com/imagenes/san-blas-cusco.jpg",
        },
    ],
}


def _sin_tildes(texto: str) -> str:
    """Normaliza ciudades como "Cusco" y "Cuzco" para la búsqueda."""
    descompuesto = unicodedata.normalize("NFD", texto or "")
    return "".join(
        letra for letra in descompuesto if unicodedata.category(letra) != "Mn"
    ).lower().strip()


@tool
def listado_sitios_turisticos(ciudad: str, fecha: str) -> list[dict] | str:
    """Devuelve sitios turísticos disponibles para una ciudad y una fecha.

    Args:
        ciudad: Ciudad que la persona quiere visitar.
        fecha: Fecha o día del viaje, tal como lo indicó la persona.
    """
    ciudad_normalizada = _sin_tildes(ciudad)
    if ciudad_normalizada == "cuzco":
        ciudad_normalizada = "cusco"

    sitios = SITIOS.get(ciudad_normalizada)
    if not sitios:
        return f"No tengo sitios turísticos registrados para {ciudad or 'esa ciudad'}."

    return [{**sitio, "ciudad": ciudad, "fecha": fecha} for sitio in sitios]


@tool
def horario_atencion(nombre_sitio: str, dia: str) -> str:
    """Indica el horario registrado de un sitio para el día consultado."""
    buscado = _sin_tildes(nombre_sitio)
    dia_normalizado = _sin_tildes(dia)
    dias_validos = {
        "lunes",
        "martes",
        "miercoles",
        "jueves",
        "viernes",
        "sabado",
        "domingo",
    }
    sin_dia = {
        "",
        "no especificado",
        "no indicado",
        "sin especificar",
        "hoy",
    }
    for sitios in SITIOS.values():
        for sitio in sitios:
            nombre_normalizado = _sin_tildes(sitio["nombre"])
            if nombre_normalizado == buscado or nombre_normalizado in buscado:
                if dia_normalizado in sin_dia:
                    return f"{sitio['nombre']}: {sitio['horario']}."
                if dia_normalizado not in dias_validos:
                    return f"No tengo horario registrado para {sitio['nombre']} el día indicado."
                if dia_normalizado in sitio.get("dias_cerrados", []):
                    return f"No tengo horario registrado para {sitio['nombre']} el {dia}."
                return f"{sitio['nombre']}: {sitio['horario']} ({dia})."
    return f"No tengo horario registrado para {nombre_sitio or 'ese sitio'}."
