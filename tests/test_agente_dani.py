from src.agente_dani.tools import lista_equipaje


def test_lista_equipaje_con_guia_estatica_y_cantidades():
    resultado = lista_equipaje.invoke(
        {"destino": "Punta Arenas", "dias": 5, "temporada": "julio"}
    )

    assert "Ropa:" in resultado
    assert "6 × ropa interior" in resultado
    assert "Documentos:" in resultado
    assert "Tecnología:" in resultado
    assert "Botiquín:" in resultado
    assert "No te olvides:" in resultado


def test_destino_o_temporada_sin_guia_no_inventa():
    resultado = lista_equipaje.invoke(
        {"destino": "Tokio", "dias": 4, "temporada": "otoño"}
    )

    assert resultado == (
        "No tengo una guía estática para ese destino y temporada; "
        "no puedo armar una lista fiable."
    )


def test_dias_invalidos_se_informan_en_una_linea():
    resultado = lista_equipaje.invoke(
        {"destino": "Punta Arenas", "dias": 0, "temporada": "invierno"}
    )

    assert resultado == "La cantidad de días debe estar entre 1 y 30."


def test_grafo_dani_se_compila_sin_invocar_gemini(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "clave-de-prueba")
    from src.agente_dani.graph import graph

    nodos = set(graph.get_graph().nodes)
    assert {"__start__", "model", "tools", "__end__"}.issubset(nodos)


def test_ficha_a2a_de_dani_tiene_nombre_url_y_skill(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "clave-de-prueba")
    monkeypatch.setenv("URL_PUBLICA", "")
    from src.agente_dani.server import tarjeta

    assert tarjeta.name == "Agente de Maleta de Dani"
    assert tarjeta.supported_interfaces[0].url.endswith(":8003")
    assert [skill.id for skill in tarjeta.skills] == ["lista_equipaje"]
