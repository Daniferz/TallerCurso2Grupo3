import asyncio
from types import SimpleNamespace

import pytest
from langchain_core.messages import HumanMessage

from src.coordinador import catalogo


def _preparar_catalogo(monkeypatch, urls, caidos, nombres):
    """Deja el catálogo vacío y simula qué URLs responden su ficha."""
    llamadas = []
    monkeypatch.setattr(catalogo, "_conocidos", {})
    monkeypatch.setattr(catalogo, "_ultimo_intento", {})
    monkeypatch.setenv("URLS_AGENTES", urls)

    async def obtener_cliente(url):
        llamadas.append(url)
        if url in caidos:
            raise RuntimeError("servidor fuera de línea\nreintentar")
        return object()

    monkeypatch.setattr(catalogo, "obtener_cliente", obtener_cliente)
    monkeypatch.setattr(
        catalogo,
        "obtener_tarjeta_cacheada",
        lambda url: SimpleNamespace(name=nombres[url], description="Ficha de prueba."),
    )
    return llamadas


def test_catalogo_usa_solo_urls_agentes_y_cachea_las_fichas(monkeypatch, capsys):
    nombres = {"http://maleta": "Maleta", "http://pato": "Entrenamiento", "http://sitios": "Sitios"}
    llamadas = _preparar_catalogo(
        monkeypatch,
        "http://maleta, http://pato/, , http://sitios, http://maleta",
        caidos=set(),
        nombres=nombres,
    )
    monkeypatch.setenv("URL_VIAJES", "http://viajes")

    primera = asyncio.run(catalogo.descubrir())
    segunda = asyncio.run(catalogo.descubrir())

    assert [agente.nombre for agente in primera] == ["Maleta", "Entrenamiento", "Sitios"]
    assert [agente.nombre for agente in segunda] == ["Maleta", "Entrenamiento", "Sitios"]
    # Ni viajes ni restaurantes: solo URLS_AGENTES, sin duplicados, y una sola lectura.
    assert sorted(llamadas) == ["http://maleta", "http://pato", "http://sitios"]


def test_agente_caido_se_reintenta_pasado_el_plazo(monkeypatch, capsys):
    nombres = {"http://maleta": "Maleta", "http://pato": "Entrenamiento"}
    caidos = {"http://pato"}
    llamadas = _preparar_catalogo(monkeypatch, "http://maleta,http://pato", caidos, nombres)
    reloj = [1000.0]
    monkeypatch.setattr(catalogo.time, "monotonic", lambda: reloj[0])
    monkeypatch.setattr(catalogo, "REINTENTO_SEGUNDOS", 60)

    assert [a.nombre for a in asyncio.run(catalogo.descubrir())] == ["Maleta"]
    assert "servidor fuera de línea reintentar" in capsys.readouterr().out

    # Antes del plazo no se vuelve a pedir la ficha.
    reloj[0] += 30
    caidos.clear()
    assert [a.nombre for a in asyncio.run(catalogo.descubrir())] == ["Maleta"]
    assert llamadas.count("http://pato") == 1

    # Pasado el plazo se reintenta y el agente vuelve, sin reiniciar nada.
    reloj[0] += 31
    assert [a.nombre for a in asyncio.run(catalogo.descubrir())] == ["Maleta", "Entrenamiento"]
    assert llamadas.count("http://pato") == 2
    assert llamadas.count("http://maleta") == 1


def test_grafo_supervisor_tiene_rama_para_sin_agente(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "clave-de-prueba")
    from src.coordinador.graph import Decision, graph

    assert Decision(agente="ninguno", motivo="Fuera de tema.").agente == "ninguno"
    assert Decision(agente="Agente de compañero", motivo="Pregunta de la persona.").agente == "Agente de compañero"
    assert {"supervisor", "agente_remoto", "sin_agente"}.issubset(graph.get_graph().nodes)


def test_agente_elegido_que_no_responde_da_aviso_claro(monkeypatch, capsys):
    monkeypatch.setenv("GOOGLE_API_KEY", "clave-de-prueba")
    from src.coordinador import graph as supervisor
    from src.coordinador.cliente import AgenteNoDisponible

    caido = catalogo.AgenteDescubierto(
        nombre="Entrenamiento", descripcion="Rutinas.", cliente=object(), url="http://pato"
    )

    async def descubrir():
        return [caido]

    async def preguntar(cliente, texto, context_id):
        raise AgenteNoDisponible("No se pudo conectar con el agente.")

    monkeypatch.setattr(supervisor, "descubrir", descubrir)
    monkeypatch.setattr(supervisor, "preguntar", preguntar)

    estado = {"messages": [HumanMessage(content="rutina de pecho")], "agente": "Entrenamiento"}
    resultado = asyncio.run(supervisor.agente_remoto(estado, {"configurable": {"thread_id": "t1"}}))

    texto = resultado["messages"][0].content
    assert texto == (
        "La parte de Entrenamiento no está disponible en este momento. "
        "Puedes seguir preguntando sobre los otros temas."
    )
    # El detalle técnico queda en la terminal, no en la respuesta.
    assert "No se pudo conectar" in capsys.readouterr().out


def test_otra_falla_del_agente_sigue_siendo_error(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "clave-de-prueba")
    from src.coordinador import graph as supervisor

    agente = catalogo.AgenteDescubierto(
        nombre="Maleta", descripcion="Equipaje.", cliente=object(), url="http://maleta"
    )

    async def descubrir():
        return [agente]

    async def preguntar(cliente, texto, context_id):
        raise RuntimeError("El agente rechazó el acceso (HTTP 401)")

    monkeypatch.setattr(supervisor, "descubrir", descubrir)
    monkeypatch.setattr(supervisor, "preguntar", preguntar)

    estado = {"messages": [HumanMessage(content="maleta")], "agente": "Maleta"}
    with pytest.raises(RuntimeError, match="401"):
        asyncio.run(supervisor.agente_remoto(estado, {"configurable": {}}))


def test_ficha_del_coordinador_no_menciona_viajes_ni_restaurantes():
    from src.comun.registro import CATALOGO

    texto = CATALOGO["coordinador"].descripcion.lower()
    servidor = (catalogo.__file__.replace("catalogo.py", "server.py"))
    skills = open(servidor, encoding="utf-8").read().lower()
    for palabra in ("restaurante", "vuelo", "volar"):
        assert palabra not in texto
        assert palabra not in skills
