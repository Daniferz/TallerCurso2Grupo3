"""Herramientas del agente de entrenamiento de Pato.

Datos estáticos con base científica: anatomía de los músculos principales y
parámetros de entrenamiento (volumen, repeticiones, descanso, cercanía al
fallo y frecuencia) tomados de revisiones y metaanálisis citados en
REFERENCIAS. Son orientativos y educativos, no un plan médico.
"""

from math import ceil
import unicodedata

from langchain_core.tools import tool


# ---------------------------------------------------------------------------
# Referencias científicas que respaldan los parámetros de las rutinas.
# ---------------------------------------------------------------------------
REFERENCIAS = {
    "volumen": (
        "Más series semanales por músculo producen más hipertrofia (relación dosis-respuesta) "
        "— Schoenfeld, Ogborn y Krieger, 2017, J Sports Sci."
    ),
    "frecuencia": (
        "Entrenar cada músculo al menos 2 veces por semana supera a 1 vez; con el mismo volumen "
        "semanal la diferencia es pequeña — Schoenfeld, Ogborn y Krieger, 2016, Sports Med; "
        "Schoenfeld, Grgic y Krieger, 2019, J Sports Sci."
    ),
    "repeticiones": (
        "Cargas altas y bajas dan hipertrofia similar si las series terminan cerca del fallo; "
        "las cargas altas ganan en fuerza máxima — Schoenfeld, Grgic, Ogborn y Krieger, 2017, J Strength Cond Res."
    ),
    "fallo": (
        "Terminar las series a pocas repeticiones del fallo favorece la hipertrofia; llegar "
        "siempre al fallo no es necesario — Refalo et al., 2023, Sports Med."
    ),
    "descanso": (
        "Descansos de unos 3 minutos dieron más hipertrofia y fuerza que 1 minuto en ejercicios "
        "multiarticulares — Schoenfeld et al., 2016, J Strength Cond Res."
    ),
    "estiramiento": (
        "Entrenar el músculo en posición alargada puede dar más crecimiento: curl femoral "
        "sentado vs. tumbado (Maeo et al., 2021, Med Sci Sports Exerc) y extensión de tríceps "
        "sobre la cabeza (Maeo et al., 2023, Eur J Sport Sci)."
    ),
    "progresion": (
        "Sobrecarga progresiva y variables según objetivo y nivel — ACSM, 2009, "
        "Progression Models in Resistance Training for Healthy Adults, Med Sci Sports Exerc."
    ),
}


# ---------------------------------------------------------------------------
# Anatomía y fisiología de los músculos principales.
# ---------------------------------------------------------------------------
MUSCULOS = {
    "pectoral mayor": {
        "origen": "mitad medial de la clavícula, esternón y cartílagos costales 1 a 6",
        "insercion": "labio lateral del surco intertubercular del húmero",
        "funcion": "aducción, rotación interna y flexión horizontal del hombro; la porción clavicular además flexiona el hombro",
        "ejercicios": ["press de banca", "press inclinado (porción clavicular)", "aperturas", "fondos en paralelas"],
        "nota": "El press inclinado enfatiza la porción clavicular (superior).",
    },
    "dorsal ancho": {
        "origen": "apófisis espinosas de T7 a L5, fascia toracolumbar, cresta ilíaca y últimas costillas",
        "insercion": "suelo del surco intertubercular del húmero",
        "funcion": "extensión, aducción y rotación interna del hombro",
        "ejercicios": ["dominadas", "jalón al pecho", "remo con barra o polea", "pullover en polea"],
        "nota": "Tirar llevando los codos hacia las caderas lo activa más que tirar con las manos.",
    },
    "trapecio": {
        "origen": "hueso occipital, ligamento nucal y apófisis espinosas de C7 a T12",
        "insercion": "tercio lateral de la clavícula, acromion y espina de la escápula",
        "funcion": "eleva, retrae y deprime la escápula y la rota hacia arriba al levantar el brazo",
        "ejercicios": ["encogimientos", "remo con barra", "face pull", "peso muerto"],
        "nota": "Tiene tres porciones (superior, media e inferior) con funciones distintas.",
    },
    "deltoides": {
        "origen": "tercio lateral de la clavícula (anterior), acromion (medio) y espina de la escápula (posterior)",
        "insercion": "tuberosidad deltoidea del húmero",
        "funcion": "anterior: flexión del hombro; medio: abducción; posterior: extensión y rotación externa",
        "ejercicios": ["press militar (anterior)", "elevaciones laterales (medio)", "pájaros y face pull (posterior)"],
        "nota": "El deltoides medio casi no trabaja en los press: necesita elevaciones laterales.",
    },
    "biceps braquial": {
        "origen": "cabeza larga: tubérculo supraglenoideo; cabeza corta: apófisis coracoides de la escápula",
        "insercion": "tuberosidad del radio y aponeurosis bicipital",
        "funcion": "flexión del codo y supinación del antebrazo; ayuda débilmente a flexionar el hombro",
        "ejercicios": ["curl con barra", "curl inclinado con mancuernas", "curl martillo (braquial y braquiorradial)"],
        "nota": "En el curl inclinado el hombro queda extendido y la cabeza larga trabaja más estirada.",
    },
    "braquial": {
        "origen": "mitad distal de la cara anterior del húmero",
        "insercion": "tuberosidad del cúbito y apófisis coronoides",
        "funcion": "flexor puro del codo, en cualquier posición del antebrazo",
        "ejercicios": ["curl martillo", "curl invertido", "curl con barra"],
        "nota": "Está debajo del bíceps; al crecer empuja al bíceps y aumenta el grosor del brazo.",
    },
    "triceps braquial": {
        "origen": "cabeza larga: tubérculo infraglenoideo de la escápula; cabezas lateral y medial: cara posterior del húmero",
        "insercion": "olécranon del cúbito",
        "funcion": "extensión del codo; la cabeza larga además extiende y aduce el hombro",
        "ejercicios": ["extensión sobre la cabeza", "press francés", "extensión en polea", "fondos"],
        "nota": "La extensión sobre la cabeza estira la cabeza larga y mostró más hipertrofia (Maeo et al., 2023).",
    },
    "cuadriceps": {
        "origen": "recto femoral: espina ilíaca anteroinferior; vastos lateral, medial e intermedio: fémur",
        "insercion": "tuberosidad de la tibia a través del tendón rotuliano",
        "funcion": "extensión de la rodilla; el recto femoral además flexiona la cadera",
        "ejercicios": ["sentadilla", "prensa de piernas", "zancadas", "extensión de cuádriceps"],
        "nota": "El recto femoral cruza la cadera: la extensión de cuádriceps lo trabaja mejor que la sentadilla.",
    },
    "isquiotibiales": {
        "origen": "tuberosidad isquiática (bíceps femoral cabeza larga, semitendinoso y semimembranoso); cabeza corta del bíceps: línea áspera del fémur",
        "insercion": "cabeza del peroné (bíceps femoral) y cara medial de la tibia (semitendinoso y semimembranoso)",
        "funcion": "flexión de la rodilla y extensión de la cadera",
        "ejercicios": ["peso muerto rumano", "curl femoral sentado", "curl femoral tumbado", "buenos días"],
        "nota": "El curl femoral sentado (cadera flexionada, músculo más estirado) dio más hipertrofia que el tumbado (Maeo et al., 2021).",
    },
    "gluteo mayor": {
        "origen": "cara posterior del ilion, sacro y cóccix",
        "insercion": "tuberosidad glútea del fémur y tracto iliotibial",
        "funcion": "extensión y rotación externa de la cadera",
        "ejercicios": ["hip thrust", "sentadilla profunda", "peso muerto rumano", "zancadas"],
        "nota": "Es el músculo más grande del cuerpo; trabaja fuerte al subir de una sentadilla profunda.",
    },
    "gluteo medio": {
        "origen": "cara externa del ilion",
        "insercion": "trocánter mayor del fémur",
        "funcion": "abducción de la cadera y estabilización de la pelvis al apoyar una sola pierna",
        "ejercicios": ["abducción de cadera en máquina", "caminata lateral con banda", "sentadilla búlgara"],
        "nota": "Si es débil, la rodilla tiende a irse hacia adentro al bajar en una pierna.",
    },
    "gastrocnemio": {
        "origen": "cóndilos medial y lateral del fémur",
        "insercion": "calcáneo a través del tendón de Aquiles",
        "funcion": "flexión plantar del tobillo (ponerse de puntillas) y ayuda a flexionar la rodilla",
        "ejercicios": ["elevación de talones de pie", "elevación de talones en prensa"],
        "nota": "Cruza la rodilla: trabaja más con la rodilla extendida (de pie).",
    },
    "soleo": {
        "origen": "cara posterior de la tibia y del peroné",
        "insercion": "calcáneo a través del tendón de Aquiles",
        "funcion": "flexión plantar del tobillo, sobre todo con la rodilla flexionada",
        "ejercicios": ["elevación de talones sentado"],
        "nota": "Con la rodilla doblada el gastrocnemio se acorta y el sóleo hace la mayor parte del trabajo.",
    },
    "erectores de la columna": {
        "origen": "sacro, cresta ilíaca y apófisis de las vértebras lumbares y torácicas",
        "insercion": "costillas, apófisis de las vértebras superiores y hueso occipital",
        "funcion": "extienden la columna y la mantienen estable al levantar peso o estar de pie",
        "ejercicios": ["peso muerto rumano", "hiperextensiones en banco", "bird dog", "puente de glúteos"],
        "nota": "Es la musculatura de la zona lumbar; se fortalece de forma progresiva y con la espalda neutra.",
    },
    "recto abdominal": {
        "origen": "cresta y sínfisis del pubis",
        "insercion": "cartílagos costales 5 a 7 y apófisis xifoides",
        "funcion": "flexión del tronco y estabilización de la columna",
        "ejercicios": ["crunch en polea", "elevación de piernas colgado", "rueda abdominal"],
        "nota": "Es un solo músculo: no existe 'abdomen alto' y 'bajo' separados, aunque se puede enfatizar cada zona.",
    },
    "oblicuos": {
        "origen": "oblicuo externo: costillas 5 a 12; oblicuo interno: fascia toracolumbar y cresta ilíaca",
        "insercion": "cresta ilíaca, línea alba y últimas costillas",
        "funcion": "rotación y flexión lateral del tronco; resisten la rotación de la columna",
        "ejercicios": ["pallof press", "plancha lateral", "leñador en polea"],
        "nota": "Trabajan mucho como 'antirrotación': evitar que el tronco gire.",
    },
}

SINONIMOS_MUSCULO = {
    "pectoral": "pectoral mayor", "pectorales": "pectoral mayor", "pecho": "pectoral mayor",
    "dorsal": "dorsal ancho", "dorsales": "dorsal ancho", "lats": "dorsal ancho",
    "trapecios": "trapecio",
    "hombro": "deltoides", "hombros": "deltoides", "deltoide": "deltoides",
    "biceps": "biceps braquial", "triceps": "triceps braquial",
    "cuadriceps femoral": "cuadriceps",
    "femoral": "isquiotibiales", "femorales": "isquiotibiales", "isquios": "isquiotibiales",
    "gluteo": "gluteo mayor", "gluteos": "gluteo mayor",
    "gemelo": "gastrocnemio", "gemelos": "gastrocnemio", "pantorrilla": "gastrocnemio",
    "pantorrillas": "gastrocnemio",
    "abdominal": "recto abdominal", "abdominales": "recto abdominal", "abdomen": "recto abdominal",
    "oblicuo": "oblicuos",
    "lumbar": "erectores de la columna", "lumbares": "erectores de la columna",
    "zona lumbar": "erectores de la columna", "espalda baja": "erectores de la columna",
    "erectores": "erectores de la columna", "erector de la columna": "erectores de la columna",
}

# Lo que escribe la persona nunca se repite en la salida de las herramientas:
# así un texto con instrucciones escondidas no vuelve al modelo como si fuera un dato.
LARGO_MAXIMO_ENTRADA = 40


# ---------------------------------------------------------------------------
# Rutinas: ejercicios por grupo y parámetros por objetivo y nivel.
# ---------------------------------------------------------------------------
GRUPOS = {
    "pecho": {
        "musculos": "pectoral mayor, deltoides anterior y tríceps",
        "ejercicios": [
            "Press de banca (barra o mancuernas)",
            "Press inclinado con mancuernas",
            "Fondos en paralelas o press en máquina",
            "Aperturas en polea o pec deck",
        ],
    },
    "espalda": {
        "musculos": "dorsal ancho, trapecio, romboides y deltoides posterior",
        "ejercicios": [
            "Jalón al pecho o dominadas",
            "Remo con barra o en máquina con apoyo de pecho",
            "Remo con mancuerna a una mano",
            "Pullover en polea alta",
        ],
    },
    "piernas": {
        "musculos": "cuádriceps, isquiotibiales, glúteos y pantorrillas",
        "ejercicios": [
            "Sentadilla (con barra o goblet)",
            "Peso muerto rumano",
            "Prensa de piernas",
            "Curl femoral sentado",
            "Elevación de talones de pie",
        ],
    },
    "gluteos": {
        "musculos": "glúteo mayor, glúteo medio e isquiotibiales",
        "ejercicios": [
            "Hip thrust con barra",
            "Sentadilla búlgara",
            "Peso muerto rumano",
            "Abducción de cadera en máquina",
        ],
    },
    "hombros": {
        "musculos": "deltoides anterior, medio y posterior, y trapecio",
        "ejercicios": [
            "Press militar (barra o mancuernas)",
            "Elevaciones laterales",
            "Pájaros o face pull",
        ],
    },
    "brazos": {
        "musculos": "bíceps braquial, braquial y tríceps braquial",
        "ejercicios": [
            "Curl inclinado con mancuernas",
            "Extensión de tríceps sobre la cabeza",
            "Curl martillo",
            "Press francés o extensión en polea",
        ],
    },
    "core": {
        "musculos": "recto abdominal, oblicuos y transverso del abdomen",
        "ejercicios": [
            "Crunch en polea",
            "Elevación de piernas colgado",
            "Pallof press",
            "Plancha frontal",
        ],
    },
    "cuerpo completo": {
        "musculos": "todos los grupos principales en una sesión",
        "ejercicios": [
            "Sentadilla",
            "Press de banca",
            "Remo con barra o en máquina",
            "Peso muerto rumano",
            "Press militar",
            "Jalón al pecho",
        ],
    },
}

SINONIMOS_GRUPO = {
    "pecho": "pecho", "pectoral": "pecho", "pectorales": "pecho",
    "espalda": "espalda", "dorsales": "espalda", "dorsal": "espalda",
    "piernas": "piernas", "pierna": "piernas", "cuadriceps": "piernas",
    "isquiotibiales": "piernas", "femorales": "piernas", "tren inferior": "piernas",
    "gluteos": "gluteos", "gluteo": "gluteos", "cola": "gluteos",
    "hombros": "hombros", "hombro": "hombros", "deltoides": "hombros",
    "brazos": "brazos", "brazo": "brazos", "biceps": "brazos", "triceps": "brazos",
    "core": "core", "abdomen": "core", "abdominales": "core", "abs": "core",
    "cuerpo completo": "cuerpo completo", "full body": "cuerpo completo",
    "fullbody": "cuerpo completo", "todo el cuerpo": "cuerpo completo",
}

# Parámetros por (objetivo, nivel). series_semanales es por grupo muscular.
PARAMETROS = {
    ("hipertrofia", "principiante"): {
        "series_semanales": 10, "frecuencia": 2, "repeticiones": "8-12",
        "fallo": "terminar a 2-3 repeticiones del fallo", "descanso": "2 minutos (1-1,5 en aislamiento)",
        "referencias": ["volumen", "frecuencia", "fallo", "progresion"],
    },
    ("hipertrofia", "intermedio"): {
        "series_semanales": 16, "frecuencia": 2, "repeticiones": "6-15",
        "fallo": "terminar a 0-2 repeticiones del fallo", "descanso": "2-3 minutos en multiarticulares, 1,5 en aislamiento",
        "referencias": ["volumen", "repeticiones", "fallo", "descanso", "estiramiento"],
    },
    ("fuerza", "principiante"): {
        "series_semanales": 12, "frecuencia": 3, "repeticiones": "5-8",
        "fallo": "dejar 2-3 repeticiones en reserva y priorizar la técnica", "descanso": "2-3 minutos",
        "referencias": ["repeticiones", "frecuencia", "progresion"],
    },
    ("fuerza", "intermedio"): {
        "series_semanales": 12, "frecuencia": 2, "repeticiones": "3-6 (más del 80 % de tu máximo)",
        "fallo": "dejar 1-3 repeticiones en reserva", "descanso": "3-5 minutos",
        "referencias": ["repeticiones", "descanso", "progresion"],
    },
    ("resistencia", "principiante"): {
        "series_semanales": 8, "frecuencia": 2, "repeticiones": "15-20",
        "fallo": "terminar a 2-3 repeticiones del fallo", "descanso": "30-60 segundos",
        "referencias": ["progresion", "repeticiones"],
    },
    ("resistencia", "intermedio"): {
        "series_semanales": 12, "frecuencia": 3, "repeticiones": "15-25",
        "fallo": "terminar a 1-2 repeticiones del fallo", "descanso": "30-60 segundos",
        "referencias": ["progresion", "repeticiones"],
    },
}

SINONIMOS_OBJETIVO = {
    "hipertrofia": "hipertrofia", "masa": "hipertrofia", "masa muscular": "hipertrofia",
    "musculo": "hipertrofia", "ganar musculo": "hipertrofia", "volumen": "hipertrofia",
    "fuerza": "fuerza", "fuerza maxima": "fuerza", "powerlifting": "fuerza",
    "resistencia": "resistencia", "resistencia muscular": "resistencia", "tonificar": "resistencia",
}

SINONIMOS_NIVEL = {
    "principiante": "principiante", "basico": "principiante", "inicial": "principiante",
    "novato": "principiante", "intermedio": "intermedio", "medio": "intermedio",
    "avanzado": "intermedio",
}


def _normalizar(texto: str) -> str:
    """Pasa a minúsculas, quita tildes y espacios de más."""
    sin_tildes = unicodedata.normalize("NFKD", str(texto or ""))
    sin_tildes = "".join(c for c in sin_tildes if not unicodedata.combining(c))
    return " ".join(sin_tildes.lower().split())


def _citar(texto: str) -> str:
    """Devuelve el texto entre comillas solo si es corto y simple; si no, uno genérico.

    Evita que una entrada larga o con símbolos (por ejemplo, instrucciones
    escondidas) se copie en la salida de la herramienta.
    """
    limpio = " ".join(str(texto or "").split())
    simple = all(c.isalnum() or c in " -" for c in limpio)
    if limpio and simple and len(limpio) <= LARGO_MAXIMO_ENTRADA:
        return f"'{limpio}'"
    return "ese dato"


@tool
def musculo(nombre: str) -> str:
    """Explica la anatomía y la función de un músculo y qué ejercicios lo trabajan.

    Args:
        nombre: el músculo, por ejemplo pectoral mayor, dorsal ancho, trapecio,
            deltoides, bíceps, braquial, tríceps, cuádriceps, isquiotibiales,
            glúteo mayor, glúteo medio, gemelos, sóleo, erectores de la columna (zona lumbar), recto abdominal u oblicuos.

    Devuelve origen, inserción, función, ejercicios recomendados y una nota
    práctica. Si el músculo no está en los datos, lo dice en una línea.
    """
    clave = _normalizar(nombre)
    clave = clave if clave in MUSCULOS else SINONIMOS_MUSCULO.get(clave)
    if clave is None:
        disponibles = ", ".join(sorted(MUSCULOS))
        return f"No tengo datos del músculo {_citar(nombre)}. Músculos disponibles: {disponibles}."

    datos = MUSCULOS[clave]
    return "\n".join([
        f"Músculo: {clave}",
        f"Origen: {datos['origen']}.",
        f"Inserción: {datos['insercion']}.",
        f"Función: {datos['funcion']}.",
        f"Ejercicios: {', '.join(datos['ejercicios'])}.",
        f"Nota: {datos['nota']}",
    ])


@tool
def rutina(
    grupo_muscular: str,
    objetivo: str = "hipertrofia",
    nivel: str = "principiante",
    dias_por_semana: int = 3,
) -> str:
    """Arma una rutina de gimnasio basada en evidencia científica.

    Args:
        grupo_muscular: pecho, espalda, piernas, glúteos, hombros, brazos,
            core o cuerpo completo (acepta sinónimos como abdomen o bíceps).
        objetivo: hipertrofia (ganar músculo), fuerza o resistencia.
            Si no lo dicen, usa hipertrofia.
        nivel: principiante o intermedio. Si no lo dicen, usa principiante.
        dias_por_semana: días que la persona puede entrenar (1 a 7).

    Devuelve ejercicios con series × repeticiones, cercanía al fallo,
    descanso, cuántas veces por semana entrenar ese grupo y el porqué con
    sus referencias científicas. Si algún dato no es válido, lo dice en una línea.
    """
    grupo = SINONIMOS_GRUPO.get(_normalizar(grupo_muscular))
    if grupo is None:
        return (
            f"No tengo rutina para {_citar(grupo_muscular)}. Grupos disponibles: "
            "pecho, espalda, piernas, glúteos, hombros, brazos, core y cuerpo completo."
        )

    clave_objetivo = SINONIMOS_OBJETIVO.get(_normalizar(objetivo) or "hipertrofia")
    if clave_objetivo is None:
        return (
            f"No tengo rutinas con el objetivo {_citar(objetivo)}. "
            "Objetivos disponibles: hipertrofia, fuerza y resistencia."
        )

    clave_nivel = SINONIMOS_NIVEL.get(_normalizar(nivel) or "principiante")
    if clave_nivel is None:
        return f"No tengo rutinas de nivel {_citar(nivel)}. Niveles disponibles: principiante e intermedio."

    try:
        dias = int(dias_por_semana)
    except (TypeError, ValueError):
        return "Los días por semana deben ser un número entre 1 y 7."
    if not 1 <= dias <= 7:
        return "Los días por semana deben ser un número entre 1 y 7."

    datos = GRUPOS[grupo]
    parametros = PARAMETROS[(clave_objetivo, clave_nivel)]
    sesiones = min(parametros["frecuencia"], dias)

    # En fuerza se priorizan los primeros ejercicios (multiarticulares).
    ejercicios = datos["ejercicios"]
    if clave_objetivo == "fuerza":
        ejercicios = ejercicios[:3]

    if grupo == "cuerpo completo":
        # Cada ejercicio trabaja un grupo distinto: series fijas por ejercicio.
        series_por_ejercicio = [3 if clave_nivel == "principiante" else 4] * len(ejercicios)
        resumen_volumen = (
            f"{sesiones} sesión(es) de cuerpo completo por semana; cada ejercicio con "
            f"{series_por_ejercicio[0]} series."
        )
    else:
        series_por_sesion = ceil(parametros["series_semanales"] / sesiones)
        # Mínimo 2 series por ejercicio: con poco volumen se usan menos ejercicios.
        ejercicios = ejercicios[: max(1, min(len(ejercicios), series_por_sesion // 2))]
        base, resto = divmod(series_por_sesion, len(ejercicios))
        series_por_ejercicio = [base + (1 if i < resto else 0) for i in range(len(ejercicios))]
        resumen_volumen = (
            f"{parametros['series_semanales']} series semanales para {grupo}, repartidas en "
            f"{sesiones} sesión(es) por semana ({series_por_sesion} series por sesión)."
        )

    lineas = [
        f"Rutina de {grupo} · objetivo {clave_objetivo} · nivel {clave_nivel} · {dias} día(s) disponibles",
        f"Músculos trabajados: {datos['musculos']}.",
        f"Volumen: {resumen_volumen}",
        "Ejercicios por sesión:",
    ]
    numero = 0
    for nombre, series in zip(ejercicios, series_por_ejercicio):
        if series == 0:
            continue
        numero += 1
        lineas.append(f"{numero}. {nombre}: {series} × {parametros['repeticiones']}")
    lineas.append(f"Intensidad: {parametros['fallo']}.")
    lineas.append(f"Descanso entre series: {parametros['descanso']}.")
    lineas.append("Progresión: cuando completes todas las series en el tope del rango, sube un poco el peso.")
    if dias < parametros["frecuencia"]:
        lineas.append(
            f"Aviso: lo ideal para este objetivo es entrenar el grupo {parametros['frecuencia']} veces "
            "por semana; con menos días el volumen por sesión es mayor."
        )
    lineas.append("Por qué funciona:")
    for clave in parametros["referencias"]:
        lineas.append(f"- {REFERENCIAS[clave]}")
    return "\n".join(lineas)
