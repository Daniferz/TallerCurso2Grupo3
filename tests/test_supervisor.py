import asyncio
from types import SimpleNamespace

from src.coordinador import catalogo


def test_descubrir_omite_agente_caido_y_cachea_el_catalogo(monkeypatch, capsys):
    llamadas = []
    direcciones = {
        "viajes": "http://viajes",
        "restaurantes": "http://restaurantes",
    }
    monkeypatch.setattr(
        catalogo,
        "CATALOGO",
        {clave: SimpleNamespace(url=url) for clave, url in direcciones.items()},
    )
    monkeypatch.setattr(catalogo, "_agentes", None)

    async def obtener_cliente(url):
        llamadas.append(url)
        if url == "http://restaurantes":
            raise RuntimeError("servidor fuera de línea\nreintentar")
        return object()

    monkeypatch.setattr(catalogo, "obtener_cliente", obtener_cliente)
    monkeypatch.setattr(
        catalogo,
        "obtener_tarjeta_cacheada",
        lambda url: SimpleNamespace(name="Agente de viajes", description="Vuelos y hoteles."),
    )

    primera = asyncio.run(catalogo.descubrir())
    segunda = asyncio.run(catalogo.descubrir())

    assert [agente.nombre for agente in primera] == ["Agente de viajes"]
    assert [agente.nombre for agente in segunda] == ["Agente de viajes"]
    assert llamadas == ["http://viajes", "http://restaurantes"]
    assert "servidor fuera de línea reintentar" in capsys.readouterr().out


def test_grafo_supervisor_tiene_rama_para_sin_agente(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "clave-de-prueba")
    from src.coordinador.graph import Decision, graph

    assert Decision(agente="ninguno", motivo="Fuera de tema.").agente == "ninguno"
    assert {"supervisor", "agente_remoto", "sin_agente"}.issubset(graph.get_graph().nodes)
