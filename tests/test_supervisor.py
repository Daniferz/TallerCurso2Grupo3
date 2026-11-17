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
    monkeypatch.setenv(
        "URLS_AGENTES",
        "http://viajes, https://compa-uno.trycloudflare.com, , https://compa-dos.trycloudflare.com/",
    )

    async def obtener_cliente(url):
        llamadas.append(url)
        if url in {"http://restaurantes", "https://compa-dos.trycloudflare.com"}:
            raise RuntimeError("servidor fuera de línea\nreintentar")
        return object()

    monkeypatch.setattr(catalogo, "obtener_cliente", obtener_cliente)
    monkeypatch.setattr(
        catalogo,
        "obtener_tarjeta_cacheada",
        lambda url: SimpleNamespace(
            name={
                "http://viajes": "Agente de viajes",
                "https://compa-uno.trycloudflare.com": "Agente de compañero",
            }[url],
            description="Ficha de prueba.",
        ),
    )

    primera = asyncio.run(catalogo.descubrir())
    segunda = asyncio.run(catalogo.descubrir())

    assert [agente.nombre for agente in primera] == ["Agente de viajes", "Agente de compañero"]
    assert [agente.nombre for agente in segunda] == ["Agente de viajes", "Agente de compañero"]
    assert llamadas == [
        "http://viajes",
        "http://restaurantes",
        "https://compa-uno.trycloudflare.com",
        "https://compa-dos.trycloudflare.com",
    ]
    assert capsys.readouterr().out.count("servidor fuera de línea reintentar") == 2


def test_grafo_supervisor_tiene_rama_para_sin_agente(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "clave-de-prueba")
    from src.coordinador.graph import Decision, graph

    assert Decision(agente="ninguno", motivo="Fuera de tema.").agente == "ninguno"
    assert Decision(agente="Agente de compañero", motivo="Pregunta de la persona.").agente == "Agente de compañero"
    assert {"supervisor", "agente_remoto", "sin_agente"}.issubset(graph.get_graph().nodes)
